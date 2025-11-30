# ArUco Marker Integration Plan for Memory Mend

## End Goal Vision

Enable **perspective-corrected, real-world size measurements** of fabric damage by using ArUco markers positioned around/within an embroidery hoop. This will allow the system to:

1. **Accurate Size Estimation:** Calculate the true dimensions (width, height, area) of holes/damage in millimeters, accounting for camera angle and perspective distortion
2. **Automatic Pattern Scaling:** Scale generated embroidery patterns to exactly match the hole dimensions
3. **Machine-Ready Output:** Export G-code with precise coordinates for embroidery machines
4. **Consistent Positioning:** Enable repeatable, calibrated captures across multiple mending sessions

### Key Difference from Simple Scaling

**Simple approach (original plan):** Measure one marker, get pixel-to-mm ratio, multiply bounding box dimensions
L **Problem:** Assumes camera is perfectly perpendicular to fabric - fails with angled shots

**Homography approach (correct method):** Use 4 markers with known positions to reconstruct the plane, apply perspective transformation
 **Benefit:** Works with downward/angled camera shots, corrects for perspective distortion

---

## Physical Setup

### Embroidery Hoop Configuration

```
      [Marker ID 0]
           |
           |
[ID 3] -- HOOP -- [ID 1]
           |
           |
      [Marker ID 2]
```

**Two Marker Placement Options:**

### Option A: Markers on Hoop Frame
- 4 markers attached directly to the outer embroidery hoop
- Positioned at cardinal points (top, right, bottom, left)
- Distance from center = hoop radius
- **Pros:** No extra card needed, minimal setup
- **Cons:** Markers might interfere with hoop handling, need to re-attach for different hoops

### Option B: Markers on Card Within Hoop
- 4 markers printed on a card (e.g., 150mm × 150mm)
- Card placed inside the hoop, under the fabric
- Markers at card corners or specific positions
- **Pros:** Easy to swap cards for different hoop sizes, reusable
- **Cons:** Requires card insertion, markers might be partially occluded by fabric

**Current Decision:** Test both options, choose based on detection reliability and UX

---

## Technical Approach: Homography-Based Perspective Correction

### Mathematical Foundation

**Homography** is a transformation that maps points from one plane to another, accounting for perspective distortion.

```
Original Image (perspective view)        Warped Image (top-down view)

     [0]-----[1]                              [0]----[1]
      /       \                               |      |
     /  HOLE   \              Homography      | HOLE |
    /           \            ------------>    |      |
  [3]-----------[2]                          [3]----[2]

  Bounding box appears                    Bounding box shows
  trapezoid (distorted)                   true rectangle (corrected)
```

### Detection Pipeline

```
1. Capture Image (downward angle, 20-40cm distance)
   “
2. Detect ArUco Markers (OpenCV)
   - Find marker IDs [0, 1, 2, 3]
   - Extract corner coordinates in pixel space
   “
3. Define World Coordinates
   - Map marker IDs to known real-world positions
   - Example: ID 0 at (0, 0), ID 1 at (150, 0), etc.
   “
4. Calculate Homography Matrix (cv2.findHomography)
   - Input: 4 marker pixel positions
   - Output: 3×3 transformation matrix H
   “
5. Apply Perspective Transform (cv2.warpPerspective)
   - Transform entire image to "top-down" view
   - OR: Transform just the bounding box corners
   “
6. Run YOLOv8 Detection
   - Detect damage in original OR warped image
   - Get bounding box coordinates
   “
7. Calculate Real-World Dimensions
   - If warped image: direct pixel-to-mm mapping
   - If original image: transform bbox corners, then measure
   “
8. Return Results
   - Bounding box (pixels in original image)
   - Real-world measurements (mm)
   - Calibration metadata (markers found, confidence)
```

---

## Integration into Memory Mend App

### Backend Changes (FastAPI - python-backend/main.py)

#### New Endpoint: POST /detect

**Enhanced Detection Flow:**
```python
@app.post("/detect", response_model=DetectionResponse)
async def detect_damage(request: DetectionRequest):
    """
    Detect fabric damage with perspective-corrected size measurements.

    Steps:
    1. Decode base64 image
    2. Detect ArUco markers (4 required: IDs 0-3)
    3. Calculate homography matrix if markers found
    4. Run YOLOv8 damage detection
    5. Transform bounding box to real-world coordinates
    6. Return detection + calibration data
    """
    image = decode_base64_image(request.image)
    image_np = np.array(image)

    # Step 1: ArUco Detection
    calibration = detect_aruco_markers_with_homography(
        image_np,
        hoop_config=request.hoop_config  # NEW: hoop size/type
    )

    # Step 2: YOLOv8 Detection
    yolo_results = model.predict(image, conf=request.confidence_threshold)

    # Step 3: Apply Homography to Bounding Box
    if calibration['homography_matrix'] is not None:
        real_measurements = transform_bbox_to_real_world(
            yolo_bbox,
            calibration['homography_matrix'],
            calibration['pixel_to_mm_ratio']
        )

    return DetectionResponse(
        detections=[...],
        calibration=calibration,
        real_world=real_measurements
    )
```

#### Key Functions to Implement

**1. ArUco Detection with Homography**
```python
def detect_aruco_markers_with_homography(
    image_np: np.ndarray,
    hoop_config: HoopConfig
) -> dict:
    """
    Detect markers and calculate homography transformation.

    Returns:
        {
            'markers_found': bool,
            'marker_count': int,
            'detected_ids': [0, 1, 2, 3],
            'marker_corners': [...],  # Pixel coordinates
            'homography_matrix': np.ndarray (3x3) or None,
            'pixel_to_mm_ratio': float or None,
            'confidence': float  # 0-1, quality of homography
        }
    """
    # Detect markers
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    corners, ids, rejected = ARUCO_DETECTOR.detectMarkers(gray)

    # Validate we have all 4 required markers
    if ids is None or len(ids) != 4:
        return {'markers_found': False, ...}

    # Sort markers by ID and extract corners
    marker_positions = sort_markers_by_id(corners, ids)

    # Get world coordinates from hoop config
    world_coords = get_world_coordinates(hoop_config)

    # Calculate homography
    H, mask = cv2.findHomography(
        marker_positions,  # Source points (pixels)
        world_coords,      # Destination points (mm)
        cv2.RANSAC
    )

    # Calculate pixel-to-mm ratio from warped marker size
    pixel_to_mm = calculate_scale_from_homography(H, world_coords)

    return {
        'markers_found': True,
        'homography_matrix': H.tolist(),
        'pixel_to_mm_ratio': pixel_to_mm,
        ...
    }
```

**2. Bounding Box Transformation**
```python
def transform_bbox_to_real_world(
    bbox: BoundingBox,
    H: np.ndarray,
    pixel_to_mm: float
) -> RealWorldMeasurements:
    """
    Transform bounding box corners using homography, calculate real dimensions.

    Args:
        bbox: YOLOv8 bounding box (x, y, width, height)
        H: 3×3 homography matrix
        pixel_to_mm: Calibration ratio

    Returns:
        RealWorldMeasurements with corrected width_mm, height_mm, area_mm2
    """
    # Convert bbox to 4 corner points
    corners = np.array([
        [bbox.x, bbox.y],                          # Top-left
        [bbox.x + bbox.width, bbox.y],             # Top-right
        [bbox.x + bbox.width, bbox.y + bbox.height], # Bottom-right
        [bbox.x, bbox.y + bbox.height]             # Bottom-left
    ], dtype=np.float32)

    # Apply homography transformation
    transformed_corners = cv2.perspectiveTransform(
        corners.reshape(-1, 1, 2),
        H
    ).reshape(-1, 2)

    # Calculate real-world dimensions from transformed corners
    width_mm = np.linalg.norm(
        transformed_corners[1] - transformed_corners[0]
    ) * pixel_to_mm

    height_mm = np.linalg.norm(
        transformed_corners[3] - transformed_corners[0]
    ) * pixel_to_mm

    area_mm2 = width_mm * height_mm

    return RealWorldMeasurements(
        width_mm=round(width_mm, 2),
        height_mm=round(height_mm, 2),
        area_mm2=round(area_mm2, 2)
    )
```

**3. Hoop Configuration**
```python
class HoopConfig(BaseModel):
    """Configuration for embroidery hoop and marker placement"""
    hoop_type: str  # "8inch_circular", "10inch_circular", "custom"
    marker_placement: str  # "on_frame" or "on_card"
    marker_size_mm: float = 25.0  # Physical marker size

    # For "on_frame" placement
    hoop_diameter_mm: Optional[float] = None  # e.g., 203mm for 8-inch

    # For "on_card" placement
    card_width_mm: Optional[float] = None
    card_height_mm: Optional[float] = None

def get_world_coordinates(config: HoopConfig) -> np.ndarray:
    """
    Get real-world marker positions based on hoop configuration.

    Returns 4×2 array of (x, y) coordinates in mm.
    """
    if config.marker_placement == "on_card":
        # Card with markers at corners
        w, h = config.card_width_mm, config.card_height_mm
        return np.array([
            [0, 0],      # ID 0: Top-left
            [w, 0],      # ID 1: Top-right
            [w, h],      # ID 2: Bottom-right
            [0, h]       # ID 3: Bottom-left
        ], dtype=np.float32)

    elif config.marker_placement == "on_frame":
        # Markers on circular hoop at cardinal points
        r = config.hoop_diameter_mm / 2  # Radius
        return np.array([
            [r, 0],      # ID 0: Top (12 o'clock)
            [2*r, r],    # ID 1: Right (3 o'clock)
            [r, 2*r],    # ID 2: Bottom (6 o'clock)
            [0, r]       # ID 3: Left (9 o'clock)
        ], dtype=np.float32)
```

### Frontend Changes

#### 1. Type Extensions (src/lib/types/mend.ts)
```typescript
export interface HoopConfig {
    hoopType: '8inch_circular' | '10inch_circular' | 'custom';
    markerPlacement: 'on_frame' | 'on_card';
    markerSizeMm: number;
    hoopDiameterMm?: number;
    cardWidthMm?: number;
    cardHeightMm?: number;
}

export interface CalibrationData {
    markersFound: boolean;
    markerCount: number;
    detectedIds: number[];
    homographyMatrix?: number[][];  // 3×3 matrix
    pixelToMmRatio?: number;
    confidence?: number;  // Quality of calibration (0-1)
}
```

#### 2. Capture Page - Hoop Selection
Add UI to select hoop configuration before capture:
```svelte
<!-- src/routes/capture/+page.svelte -->
<select bind:value={hoopConfig.hoopType}>
    <option value="8inch_circular">8-inch Circular Hoop</option>
    <option value="10inch_circular">10-inch Circular Hoop</option>
    <option value="custom">Custom Size</option>
</select>

<select bind:value={hoopConfig.markerPlacement}>
    <option value="on_card">Markers on Card (inside hoop)</option>
    <option value="on_frame">Markers on Hoop Frame</option>
</select>
```

#### 3. Detection Page - Enhanced Display
Show perspective correction quality and real measurements:
```svelte
{#if detection?.calibration?.homographyMatrix}
    <div class="calibration-success">
         Perspective Correction Active
        <div>Calibration Quality: {(detection.calibration.confidence * 100).toFixed(0)}%</div>
        <div>Real Dimensions: {measurements.widthMm}mm × {measurements.heightMm}mm</div>
    </div>
{/if}
```

---

## Standalone Python Testing Guide

### Purpose

Test the ArUco detection and homography approach **before** integrating into the FastAPI backend. This allows you to:

- Validate marker detection with different sizes (25mm, 30mm, 35mm)
- Test both marker placement options (on frame vs. on card)
- Experiment with camera distances and angles
- Measure accuracy of homography transformation
- Identify optimal marker size and placement

### Setup

#### 1. Create Test Environment
```bash
# Create a new directory for testing
mkdir aruco_testing
cd aruco_testing

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install opencv-contrib-python numpy matplotlib
```

#### 2. Generate Test Markers

Create `generate_markers.py`:
```python
import cv2
import numpy as np

# ArUco dictionary (same as will be used in app)
ARUCO_DICT = cv2.aruco.DICT_4X4_50
aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)

def generate_marker(marker_id, size_mm, dpi=300):
    """
    Generate a single ArUco marker.

    Args:
        marker_id: Marker ID (0-49 for DICT_4X4_50)
        size_mm: Marker size in millimeters
        dpi: Printer resolution (300 DPI standard)

    Returns:
        numpy array with marker image
    """
    # Convert mm to pixels at given DPI
    # 1 inch = 25.4mm, so pixels = (mm / 25.4) * dpi
    size_px = int((size_mm / 25.4) * dpi)

    # Generate marker
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size_px)

    return marker_image

def generate_calibration_card(
    marker_size_mm=25,
    card_size_mm=150,
    dpi=300,
    output_file="calibration_card.png"
):
    """
    Generate a calibration card with 4 markers at corners.

    Args:
        marker_size_mm: Size of each marker
        card_size_mm: Size of the card (square)
        dpi: Print resolution
        output_file: Output filename
    """
    # Convert to pixels
    card_size_px = int((card_size_mm / 25.4) * dpi)
    marker_size_px = int((marker_size_mm / 25.4) * dpi)

    # Create white canvas
    card = np.ones((card_size_px, card_size_px), dtype=np.uint8) * 255

    # Calculate positions (markers at corners with small margin)
    margin_px = int((5 / 25.4) * dpi)  # 5mm margin

    positions = {
        0: (margin_px, margin_px),  # Top-left
        1: (card_size_px - margin_px - marker_size_px, margin_px),  # Top-right
        2: (card_size_px - margin_px - marker_size_px,
            card_size_px - margin_px - marker_size_px),  # Bottom-right
        3: (margin_px, card_size_px - margin_px - marker_size_px)  # Bottom-left
    }

    # Place markers
    for marker_id, (x, y) in positions.items():
        marker = generate_marker(marker_id, marker_size_mm, dpi)
        card[y:y+marker_size_px, x:x+marker_size_px] = marker

    # Add labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(card, f"{marker_size_mm}mm markers - {card_size_mm}mm card",
                (50, 50), font, 1, (0, 0, 0), 2)

    # Save
    cv2.imwrite(output_file, card)
    print(f" Calibration card saved: {output_file}")
    print(f"   Card size: {card_size_mm}mm × {card_size_mm}mm")
    print(f"   Marker size: {marker_size_mm}mm")
    print(f"   Print at 100% scale ({dpi} DPI)")

    return card

if __name__ == "__main__":
    # Generate different sizes for testing
    generate_calibration_card(marker_size_mm=25, card_size_mm=150,
                             output_file="card_25mm.png")
    generate_calibration_card(marker_size_mm=30, card_size_mm=150,
                             output_file="card_30mm.png")
    generate_calibration_card(marker_size_mm=35, card_size_mm=150,
                             output_file="card_35mm.png")

    print("\n=Ë Next steps:")
    print("1. Print these cards at 100% scale")
    print("2. Verify marker size with a ruler")
    print("3. Use test_detection.py to test detection")
```

#### 3. Test Detection & Homography

Create `test_detection.py`:
```python
import cv2
import numpy as np
import sys

# ArUco detector setup
ARUCO_DICT = cv2.aruco.DICT_4X4_50
aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

def detect_and_visualize(image_path, card_size_mm=150):
    """
    Detect ArUco markers, calculate homography, and visualize results.

    Args:
        image_path: Path to test image
        card_size_mm: Physical card size in mm
    """
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"L Could not read image: {image_path}")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = image.shape[:2]
    print(f"=÷ Image size: {w}×{h} pixels")

    # Detect markers
    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is None or len(ids) == 0:
        print("L No markers detected!")
        print(f"   Rejected candidates: {len(rejected)}")
        return

    print(f" Detected {len(ids)} marker(s): {ids.flatten().tolist()}")

    # Check if we have all 4 required markers
    required_ids = [0, 1, 2, 3]
    detected_ids = ids.flatten().tolist()
    missing = [id for id in required_ids if id not in detected_ids]

    if missing:
        print(f"   Missing markers: {missing}")
        print("   Cannot calculate homography (need all 4 markers)")
    else:
        print(" All 4 markers detected - calculating homography...")

        # Sort markers by ID and extract corners
        marker_corners = []
        for target_id in required_ids:
            idx = detected_ids.index(target_id)
            # Get center of marker
            center = corners[idx][0].mean(axis=0)
            marker_corners.append(center)

        src_points = np.array(marker_corners, dtype=np.float32)

        # Define world coordinates (card corners in mm)
        # Assuming markers are at corners of a square card
        dst_points = np.array([
            [0, 0],                      # ID 0: Top-left
            [card_size_mm, 0],           # ID 1: Top-right
            [card_size_mm, card_size_mm], # ID 2: Bottom-right
            [0, card_size_mm]            # ID 3: Bottom-left
        ], dtype=np.float32)

        # Calculate homography
        H, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC)

        if H is not None:
            print(" Homography matrix calculated:")
            print(H)

            # Warp image to top-down view
            warped = cv2.warpPerspective(
                image, H,
                (int(card_size_mm * 10), int(card_size_mm * 10))  # Scale up for visibility
            )

            # Calculate pixel-to-mm ratio in warped image
            # Since we warped to card_size_mm dimensions, ratio is 10 (scaled up by 10)
            pixel_to_mm = 1 / 10  # Adjust based on warped image size

            print(f"=Ï Pixel-to-mm ratio: {pixel_to_mm:.4f}")

            # Display results
            # Draw detected markers on original image
            result_img = image.copy()
            cv2.aruco.drawDetectedMarkers(result_img, corners, ids)

            # Draw marker IDs
            for i, corner in enumerate(corners):
                center = corner[0].mean(axis=0).astype(int)
                cv2.putText(result_img, f"ID {ids[i][0]}",
                           tuple(center), cv2.FONT_HERSHEY_SIMPLEX,
                           1, (0, 255, 0), 2)

            # Show original with markers
            cv2.imshow("Detected Markers", result_img)

            # Show warped (perspective-corrected) image
            cv2.imshow("Warped (Top-Down View)", warped)

            print("\n=Ë Press any key to close windows...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        else:
            print("L Failed to calculate homography matrix")

    # Also show rejected candidates for debugging
    if len(rejected) > 0:
        print(f"\n= {len(rejected)} rejected marker candidates detected")
        print("   (These are potential markers that didn't pass validation)")

def test_with_webcam(card_size_mm=150):
    """
    Live testing with webcam feed.
    """
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("L Could not open webcam")
        return

    print("=÷ Webcam opened - showing live detection")
    print("   Press 'q' to quit, 'c' to capture and analyze")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = detector.detectMarkers(gray)

        # Draw detected markers
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            # Show count
            cv2.putText(frame, f"Markers: {len(ids)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Live Detection (press 'c' to capture, 'q' to quit)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            # Save frame and analyze
            cv2.imwrite("captured_frame.jpg", frame)
            print("\n=ø Frame captured - analyzing...")
            cap.release()
            cv2.destroyAllWindows()
            detect_and_visualize("captured_frame.jpg", card_size_mm)
            return

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("ArUco Marker Detection Test")
    print("="*50)
    print("\nOptions:")
    print("1. Test with image file: python test_detection.py <image_path>")
    print("2. Test with webcam: python test_detection.py webcam")
    print()

    if len(sys.argv) > 1:
        if sys.argv[1] == "webcam":
            test_with_webcam()
        else:
            detect_and_visualize(sys.argv[1])
    else:
        print("Please provide an image path or use 'webcam' mode")
        print("Example: python test_detection.py test_image.jpg")
```

#### 4. Test Bounding Box Transformation

Create `test_homography_transform.py`:
```python
import cv2
import numpy as np

def simulate_damage_detection(card_size_mm=150):
    """
    Simulate the full pipeline: detect markers, calculate homography,
    transform a bounding box, calculate real-world size.
    """
    # Load a test image
    image_path = input("Enter image path with markers and damage: ")
    image = cv2.imread(image_path)

    if image is None:
        print(f"L Could not read image")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 1: Detect markers
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    aruco_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

    corners, ids, _ = detector.detectMarkers(gray)

    if ids is None or len(ids) < 4:
        print("L Need all 4 markers for homography")
        return

    # Extract marker centers
    required_ids = [0, 1, 2, 3]
    detected_ids = ids.flatten().tolist()

    marker_corners = []
    for target_id in required_ids:
        if target_id not in detected_ids:
            print(f"L Missing marker ID {target_id}")
            return
        idx = detected_ids.index(target_id)
        center = corners[idx][0].mean(axis=0)
        marker_corners.append(center)

    src_points = np.array(marker_corners, dtype=np.float32)

    # World coordinates
    dst_points = np.array([
        [0, 0],
        [card_size_mm, 0],
        [card_size_mm, card_size_mm],
        [0, card_size_mm]
    ], dtype=np.float32)

    # Calculate homography
    H, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC)

    if H is None:
        print("L Homography calculation failed")
        return

    print(" Homography calculated")

    # Step 2: Simulate bounding box (or let user draw one)
    print("\n=æ Draw a bounding box on the image (damage area)")
    print("   Click and drag to draw, press ENTER when done")

    bbox = cv2.selectROI("Draw Bounding Box (ENTER when done)", image, False)
    cv2.destroyAllWindows()

    x, y, w, h = bbox
    print(f"\n=Ï Bounding box in pixels: x={x}, y={y}, width={w}, height={h}")

    # Step 3: Transform bounding box corners
    bbox_corners = np.array([
        [x, y],              # Top-left
        [x + w, y],          # Top-right
        [x + w, y + h],      # Bottom-right
        [x, y + h]           # Bottom-left
    ], dtype=np.float32).reshape(-1, 1, 2)

    transformed_corners = cv2.perspectiveTransform(bbox_corners, H).reshape(-1, 2)

    # Step 4: Calculate real-world dimensions
    # Since homography maps to mm coordinates directly
    width_mm = np.linalg.norm(transformed_corners[1] - transformed_corners[0])
    height_mm = np.linalg.norm(transformed_corners[3] - transformed_corners[0])
    area_mm2 = width_mm * height_mm

    print(f"\n Real-world dimensions:")
    print(f"   Width: {width_mm:.2f} mm")
    print(f"   Height: {height_mm:.2f} mm")
    print(f"   Area: {area_mm2:.2f} mm²")

    # Visualize
    result = image.copy()
    cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(result, f"{width_mm:.1f}mm x {height_mm:.1f}mm",
                (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Result", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    simulate_damage_detection()
```

### Testing Workflow

#### Phase 1: Marker Generation & Printing
```bash
python generate_markers.py
# Prints: card_25mm.png, card_30mm.png, card_35mm.png
```

- Print all three sizes at **100% scale**
- Verify with ruler: markers should be exactly 25mm, 30mm, 35mm
- Optional: laminate for durability

#### Phase 2: Detection Testing
```bash
# Test with webcam (live)
python test_detection.py webcam

# Or test with a photo
python test_detection.py path/to/test_image.jpg
```

**What to test:**
- Different marker sizes (25mm vs 30mm vs 35mm)
- Different distances (20cm, 30cm, 40cm, 50cm)
- Different angles (perpendicular, 30°, 45°, 60° from vertical)
- Different lighting conditions
- Both marker placements (card vs hoop frame)

**Expected results:**
- All 4 markers should be detected
- Homography matrix should be calculated
- Warped image should look "top-down"

#### Phase 3: Measurement Accuracy
```bash
python test_homography_transform.py
```

**Accuracy validation:**
1. Create a known-size damage area (e.g., cut a 20mm × 30mm hole in fabric)
2. Place in hoop with markers
3. Capture photo
4. Run test script
5. Compare measured dimensions with actual dimensions
6. **Target: <5% error**

### What to Validate Before Integration

 **Detection Reliability**
- [ ] All 4 markers detected in >95% of test captures
- [ ] Detection works from 20-40cm distance
- [ ] Detection works at 30-45° downward angle
- [ ] Minimal false positives (rejected candidates)

 **Marker Size Selection**
- [ ] 25mm markers: detectable at target distance?
- [ ] 30mm markers: better detection but too large?
- [ ] Final decision based on reliability vs. size trade-off

 **Measurement Accuracy**
- [ ] Width measurement error <5%
- [ ] Height measurement error <5%
- [ ] Area measurement error <10%
- [ ] Consistent across different camera angles

 **Marker Placement**
- [ ] "On card" vs "on frame": which is more reliable?
- [ ] Does fabric occlude card-based markers?
- [ ] Are frame-based markers interfering with hoop handling?

 **Edge Cases**
- [ ] Partial marker occlusion: system fails gracefully?
- [ ] Wrong markers in frame: ignored correctly?
- [ ] Poor lighting: still detectable?
- [ ] Shadows: affect detection?

### Integration Checklist

Once standalone testing validates the approach:

1. **Finalize Configuration**
   - [ ] Marker size: 25mm or 30mm?
   - [ ] Placement method: card or frame?
   - [ ] Hoop sizes to support: 8", 10", custom?

2. **Backend Integration**
   - [ ] Add homography functions to main.py
   - [ ] Add HoopConfig to request model
   - [ ] Enhance /detect endpoint
   - [ ] Add response models for calibration data

3. **Frontend Integration**
   - [ ] Add hoop selection UI to capture page
   - [ ] Update types with CalibrationData
   - [ ] Add calibration status display to detection page
   - [ ] Store hoop config in mendStore

4. **End-to-End Testing**
   - [ ] Test full workflow: capture ’ detect ’ memory ’ pattern
   - [ ] Verify measurements persist through workflow
   - [ ] Test on mobile devices (if supported)

---

## Next Steps

1. **Run standalone tests** using the scripts above
2. **Determine optimal marker size** (25mm vs 30mm vs 35mm)
3. **Choose marker placement** (card vs frame)
4. **Validate accuracy** with known-size damage areas
5. **Document findings** and update this plan
6. **Integrate into backend** following the implementation plan
7. **Update frontend** to display calibration data
8. **Test pattern scaling** with real-world measurements

---

## Future Enhancements

### Phase 2: Advanced Calibration
- Camera distortion correction (lens calibration)
- Multiple hoop size presets
- Automatic marker placement detection (card vs frame)
- Calibration quality scoring

### Phase 3: G-code Integration
- Export embroidery patterns with exact dimensions
- Machine coordinate mapping
- Multi-color pattern support with size constraints

### Phase 4: UX Improvements
- AR guides for marker placement
- Real-time calibration feedback during capture
- Automatic hoop size detection
- Measurement history and comparison
