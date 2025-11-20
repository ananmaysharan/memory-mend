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
        "https://*.vercel.app",  # Vercel preview deployments
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


# Run with: uvicorn main:app --reload --port 5001
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
