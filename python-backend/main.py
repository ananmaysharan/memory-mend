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


def detect_corner_markers(image_gray: np.ndarray) -> dict:
    """
    Find 4 corner markers using contour detection.
    Returns dict with corner positions: {tl, tr, bl, br}
    """
    # Apply binary threshold
    _, binary = cv2.threshold(image_gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return {}

    # Sort by area and get largest contours
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Get the centers of the 4 largest contours
    corners_found = []
    for contour in contours[:10]:  # Check top 10 contours
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            corners_found.append((cx, cy))

    if len(corners_found) < 4:
        return {}

    # Sort corners by position to identify which is which
    # TL = smallest x+y, TR = largest x-y, BL = smallest x-y, BR = largest x+y
    corners_found = sorted(corners_found, key=lambda p: p[0] + p[1])
    tl = corners_found[0]  # Top-left (smallest x+y)

    corners_found = sorted(corners_found, key=lambda p: p[0] - p[1], reverse=True)
    tr = corners_found[0]  # Top-right (largest x-y)

    corners_found = sorted(corners_found, key=lambda p: p[0] - p[1])
    bl = corners_found[0]  # Bottom-left (smallest x-y)

    corners_found = sorted(corners_found, key=lambda p: p[0] + p[1], reverse=True)
    br = corners_found[0]  # Bottom-right (largest x+y)

    return {
        "tl": tl,
        "tr": tr,
        "bl": bl,
        "br": br
    }


def extract_grid_from_corners(image_gray: np.ndarray, corners: dict) -> List[List[bool]]:
    """
    Extract 7x7 grid using perspective transform.
    Returns 2D list of booleans (True = stitch/dark, False = no stitch/light)
    """
    # Get corner points
    src_points = np.float32([
        corners["tl"],
        corners["tr"],
        corners["bl"],
        corners["br"]
    ])

    # Target size for the warped pattern (larger for better sampling)
    target_size = 700  # 100px per cell
    dst_points = np.float32([
        [0, 0],
        [target_size, 0],
        [0, target_size],
        [target_size, target_size]
    ])

    # Compute perspective transform
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    warped = cv2.warpPerspective(image_gray, matrix, (target_size, target_size))

    # Apply threshold
    _, binary = cv2.threshold(warped, 127, 255, cv2.THRESH_BINARY_INV)

    # Sample 7x7 grid
    grid = []
    cell_size = target_size // 7

    for row in range(7):
        grid_row = []
        for col in range(7):
            # Sample from center of cell
            y = row * cell_size + cell_size // 2
            x = col * cell_size + cell_size // 2

            # Get pixel value (0 = white/no stitch, 255 = black/stitch)
            pixel = binary[y, x]
            grid_row.append(bool(pixel > 127))

        grid.append(grid_row)

    return grid


@app.post("/detect-pattern", response_model=PatternDetectionResponse)
async def detect_pattern(request: PatternDetectionRequest):
    """
    Detect embroidery pattern from photo and extract 7x7 grid.

    Args:
        request: PatternDetectionRequest with base64 image

    Returns:
        PatternDetectionResponse with grid and confidence
    """
    try:
        # Decode image
        image = decode_base64_image(request.image)

        # Convert to grayscale numpy array for OpenCV
        image_np = np.array(image)
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        print(f"Processing pattern detection on {image.size} image...")

        # Detect corner markers
        corners = detect_corner_markers(image_gray)
        corners_found = len(corners)

        if corners_found < 4:
            print(f"⚠️  Only found {corners_found} corners (need 4)")
            return PatternDetectionResponse(
                grid=[[False] * 7 for _ in range(7)],
                confidence=0.0,
                corner_markers_found=corners_found
            )

        # Extract grid
        grid = extract_grid_from_corners(image_gray, corners)

        # Calculate confidence based on corners found and grid validity
        confidence = 1.0 if corners_found == 4 else 0.5

        print(f"✅ Pattern detected with {corners_found} corners, confidence: {confidence}")

        return PatternDetectionResponse(
            grid=grid,
            confidence=confidence,
            corner_markers_found=corners_found
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"❌ Pattern detection error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Pattern detection failed: {str(e)}"
        )


# Run with: uvicorn main:app --reload --port 5001
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
