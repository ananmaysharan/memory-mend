"""
Memory Mend - FastAPI Backend for YOLOv8 Damage Detection

This server handles fabric damage detection using a fine-tuned YOLOv8 model.
It accepts base64-encoded images and returns bounding box coordinates.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import base64
import io
import os
from typing import List, Optional

# Initialize FastAPI app
app = FastAPI(
    title="Memory Mend Detection API",
    description="YOLOv8-based fabric damage detection service",
    version="1.0.0"
)

# Configure CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # SvelteKit dev server
        "https://localhost:5173",  # SvelteKit dev server with HTTPS
        "https://memory-mend.vercel.app",  # Vercel preview deployments
        # Add your production domain here when deployed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLOv8 model once at startup
MODEL_PATH = os.getenv("MODEL_PATH", "best.pt")
print(f"Loading YOLOv8 model from {MODEL_PATH}...")
try:
    model = YOLO(MODEL_PATH)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("⚠️  Server will start but /detect endpoint will fail")
    model = None


# Request/Response models
class DetectionRequest(BaseModel):
    image: str  # base64-encoded image
    confidence_threshold: Optional[float] = 0.3  # Min confidence for detections


class BoundingBox(BaseModel):
    x: int  # Top-left x coordinate
    y: int  # Top-left y coordinate
    width: int  # Box width
    height: int  # Box height


class Detection(BaseModel):
    bbox: BoundingBox
    confidence: float
    class_name: str


class DetectionResponse(BaseModel):
    detections: List[Detection]
    image_width: int
    image_height: int


class PatternDetectionRequest(BaseModel):
    image: str  # base64-encoded image
    debug: Optional[bool] = False


class PatternDetectionResponse(BaseModel):
    grid: List[List[bool]]  # 7x7 grid
    confidence: float  # 0-1
    corner_markers_found: int  # Should be 4
    debug_image: Optional[str] = None


# Helper function to decode base64 image
def decode_base64_image(base64_string: str) -> Image.Image:
    """
    Decode base64 string to PIL Image.
    Handles data URI format (e.g., "data:image/jpeg;base64,...")
    """
    try:
        # Remove data URI prefix if present
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]

        # Decode base64
        image_bytes = base64.b64decode(base64_string)

        # Open as PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")

        return image

    except Exception as e:
        raise ValueError(f"Failed to decode image: {str(e)}")


# API Endpoints
@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "Memory Mend Detection API",
        "status": "running",
        "model_loaded": model is not None
    }


@app.get("/health")
def health():
    """Detailed health check"""
    return {
        "status": "healthy" if model is not None else "degraded",
        "model_path": MODEL_PATH,
        "model_loaded": model is not None
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect_damage(request: DetectionRequest):
    """
    Detect fabric damage in uploaded image using YOLOv8.

    Args:
        request: DetectionRequest with base64 image

    Returns:
        DetectionResponse with bounding boxes and metadata
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Check server logs for errors."
        )

    try:
        # Decode image
        image = decode_base64_image(request.image)
        image_width, image_height = image.size

        # Run YOLOv8 inference
        print(f"Running detection on {image_width}x{image_height} image...")
        results = model.predict(
            image,
            conf=request.confidence_threshold,
            verbose=False
        )

        # Parse results
        detections = []

        # YOLOv8 returns a list of Results objects
        if len(results) > 0:
            result = results[0]

            # Extract bounding boxes
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    # Get box coordinates in xyxy format
                    xyxy = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]

                    # Convert to x, y, width, height
                    x1, y1, x2, y2 = map(int, xyxy)
                    width = x2 - x1
                    height = y2 - y1

                    # Get confidence and class
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]

                    detections.append(Detection(
                        bbox=BoundingBox(x=x1, y=y1, width=width, height=height),
                        confidence=confidence,
                        class_name=class_name
                    ))

        print(f"✅ Found {len(detections)} detection(s)")

        return DetectionResponse(
            detections=detections,
            image_width=image_width,
            image_height=image_height
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"❌ Detection error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )


# ==================== HELPER FUNCTIONS ====================

def order_points(pts):
    """
    Order points: [top-left, top-right, bottom-right, bottom-left]
    Essential for consistent perspective transform.
    """
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect


def four_point_transform(image, pts):
    """
    Apply perspective transform to crop and straighten region.
    """
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # Calculate dimensions
    width_top = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    width_bottom = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    max_width = max(int(width_top), int(width_bottom))

    height_left = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    height_right = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    max_height = max(int(height_left), int(height_right))

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))

    return warped


# ==================== PATTERN DETECTION FUNCTIONS ====================

def find_fiducials(image_gray: np.ndarray) -> dict:
    """
    Find the 4 corner fiducials by searching each corner region separately.
    Uses Otsu threshold and region-based detection.
    Returns dict with {tl, tr, bl, br} containing bounding box info.
    """
    h, w = image_gray.shape[:2]

    # Use Otsu threshold instead of hard-coded
    blurred = cv2.GaussianBlur(image_gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Apply morphological closing for larger images only
    if min(h, w) > 800:
        kernel_size = max(3, int(min(h, w) * 0.008))
        if kernel_size % 2 == 0:
            kernel_size += 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Define corner regions with 18% margin
    margin = int(min(h, w) * 0.18)
    corners = {
        'tl': (0, margin, 0, margin),
        'tr': (0, margin, w - margin, w),
        'bl': (h - margin, h, 0, margin),
        'br': (h - margin, h, w - margin, w)
    }

    fiducials = {}

    for corner, (y1, y2, x1, x2) in corners.items():
        region = binary[y1:y2, x1:x2]
        contours, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            continue

        # Merge nearby contours if multiple exist
        if len(contours) > 1:
            contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:3]
            all_points = np.vstack(contours_sorted)
            bx, by, bw, bh = cv2.boundingRect(all_points)
        else:
            best = max(contours, key=cv2.contourArea)
            bx, by, bw, bh = cv2.boundingRect(best)

        # Adjust coordinates back to full image
        bx += x1
        by += y1

        fiducials[corner] = {'bbox': (bx, by, bw, bh)}

    # Normalize fiducial sizes
    if len(fiducials) >= 2:
        fiducials = normalize_fiducial_sizes(fiducials)

    return fiducials


def normalize_fiducial_sizes(fiducials: dict) -> dict:
    """
    Normalize fiducial bounding boxes to be square.
    Fixes cases where one fiducial picks up extra artifacts.
    """
    fid_info = []
    for corner, fid in fiducials.items():
        bx, by, bw, bh = fid['bbox']
        aspect = max(bw, bh) / min(bw, bh) if min(bw, bh) > 0 else 999
        size = (bw + bh) / 2
        fid_info.append((corner, aspect, size, bw, bh))

    # Find fiducials with good aspect ratios (< 1.3)
    square_fids = [(c, a, s, w, h) for c, a, s, w, h in fid_info if a < 1.3]

    if not square_fids:
        square_fids = sorted(fid_info, key=lambda x: x[1])[:1]

    target_size = int(sum(s for _, _, s, _, _ in square_fids) / len(square_fids))

    normalized = {}
    for corner, fid in fiducials.items():
        bx, by, bw, bh = fid['bbox']
        aspect = max(bw, bh) / min(bw, bh) if min(bw, bh) > 0 else 999

        if aspect > 1.3:
            # Non-square: normalize to target size, keep center
            cx, cy = bx + bw // 2, by + bh // 2
            new_bx = cx - target_size // 2
            new_by = cy - target_size // 2
            normalized[corner] = {'bbox': (new_bx, new_by, target_size, target_size)}
        else:
            # Square: keep but make it square using average size
            own_size = (bw + bh) // 2
            cx, cy = bx + bw // 2, by + bh // 2
            new_bx = cx - own_size // 2
            new_by = cy - own_size // 2
            normalized[corner] = {'bbox': (new_bx, new_by, own_size, own_size)}

    return normalized

def decode_grid_from_fiducials(image_gray: np.ndarray, fiducials: dict) -> List[List[bool]]:
    """
    Decode 7x7 grid using fiducials to determine grid bounds.
    Uses dark pixel ratio analysis instead of single pixel sampling.
    Returns 2D list of booleans (True = stitch/dark, False = no stitch/light)
    """
    if 'tl' not in fiducials:
        raise ValueError("TL fiducial not found - cannot decode grid")

    h, w = image_gray.shape

    # Get TL fiducial
    tl_x, tl_y, tl_w, tl_h = fiducials['tl']['bbox']

    # Calculate grid bounds using all available fiducials
    if all(k in fiducials for k in ['tl', 'tr', 'bl', 'br']):
        # Best case: all 4 fiducials found
        tr_x, tr_y, tr_w, tr_h = fiducials['tr']['bbox']
        bl_x, bl_y, bl_w, bl_h = fiducials['bl']['bbox']
        br_x, br_y, br_w, br_h = fiducials['br']['bbox']

        grid_left = max(tl_x + tl_w, bl_x + bl_w)
        grid_right = min(tr_x, br_x)
        grid_top = max(tl_y + tl_h, tr_y + tr_h)
        grid_bottom = min(bl_y, br_y)

        grid_width = grid_right - grid_left
        grid_height = grid_bottom - grid_top
        cell_size = int((grid_width + grid_height) / 14)
    else:
        # Fallback: use TL fiducial size to estimate
        fiducial_size = (tl_w + tl_h) // 2
        cell_size = int(fiducial_size * 1.30)
        grid_left = tl_x + tl_w + int(fiducial_size * 0.1)
        grid_top = tl_y + tl_h + int(fiducial_size * 0.1)

    # Get binary image using Otsu threshold
    blurred = cv2.GaussianBlur(image_gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    grid = np.zeros((7, 7), dtype=bool)
    scores = np.zeros((7, 7))

    # Calculate dark pixel ratio for each cell
    for row in range(7):
        for col in range(7):
            x1 = grid_left + col * cell_size
            y1 = grid_top + row * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size

            # Clip to image bounds
            x1c, x2c = max(0, x1), min(w, x2)
            y1c, y2c = max(0, y1), min(h, y2)

            if x2c <= x1c or y2c <= y1c:
                continue

            cell = binary[y1c:y2c, x1c:x2c]
            dark_ratio = np.sum(cell > 0) / cell.size if cell.size > 0 else 0
            scores[row, col] = dark_ratio

    # Adaptive threshold: find natural gap in scores
    all_scores = sorted(scores.flatten())
    best_gap = 0
    threshold = 0.15  # Default fallback

    for i in range(len(all_scores) - 1):
        gap = all_scores[i + 1] - all_scores[i]
        if gap > best_gap:
            best_gap = gap
            threshold = (all_scores[i] + all_scores[i + 1]) / 2

    # Clamp threshold to reasonable range
    threshold = max(0.10, min(0.50, threshold))

    # Apply threshold to create boolean grid
    for row in range(7):
        for col in range(7):
            grid[row, col] = scores[row, col] > threshold

    # Convert to Python list with explicit bool conversion
    return [[bool(cell) for cell in row] for row in grid.tolist()]


@app.post("/detect-pattern", response_model=PatternDetectionResponse)
async def detect_pattern(request: PatternDetectionRequest):
    """
    Detect embroidery pattern from photo and extract 7x7 grid.
    Uses improved fiducial detection with Otsu thresholding and dark pixel ratio analysis.

    Args:
        request: PatternDetectionRequest with base64 image

    Returns:
        PatternDetectionResponse with grid and confidence
    """
    try:
        # Decode image
        image = decode_base64_image(request.image)
        image_np = np.array(image)
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        # Find fiducials using improved method
        fiducials = find_fiducials(image_gray)
        corners_found = len(fiducials)

        if 'tl' not in fiducials:
            print(f"TL fiducial not found ({corners_found} corners detected)")
            return PatternDetectionResponse(
                grid=[[False] * 7 for _ in range(7)],
                confidence=0.0,
                corner_markers_found=corners_found
            )

        # Decode grid using improved method
        grid = decode_grid_from_fiducials(image_gray, fiducials)

        # Calculate confidence based on fiducials found
        if corners_found == 4:
            confidence = 1.0
        elif corners_found >= 2:
            confidence = 0.7
        else:
            confidence = 0.5

        # Debug: Check grid data
        filled_count = sum(sum(1 for cell in row if cell) for row in grid)
        print(f"Pattern detected: {corners_found} corners, confidence: {confidence}, filled cells: {filled_count}/49")
        print(f"Grid sample row 0: {grid[0]}")

        return PatternDetectionResponse(
            grid=grid,
            confidence=confidence,
            corner_markers_found=corners_found
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"Pattern detection error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Pattern detection failed: {str(e)}"
        )


# Run with: uvicorn main:app --reload --port 5001
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
