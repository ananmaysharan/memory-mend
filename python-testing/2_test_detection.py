"""
Test ArUco marker detection
Simple script to detect markers in an image and show results
"""
import cv2
import numpy as np
import sys

# ArUco detector setup
ARUCO_DICT = cv2.aruco.DICT_4X4_50
aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

def test_image(image_path):
    """Detect ArUco markers in an image and show results"""
    print(f"\n📷 Loading image: {image_path}")

    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ ERROR: Could not read image!")
        print(f"   Make sure the file exists and is a valid image")
        return

    h, w = image.shape[:2]
    print(f"   Image size: {w} × {h} pixels")

    # Convert to grayscale for detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect markers
    print("\n🔍 Detecting ArUco markers...")
    corners, ids, rejected = detector.detectMarkers(gray)

    # Show results
    print("\n" + "=" * 50)
    if ids is None or len(ids) == 0:
        print("❌ NO MARKERS DETECTED")
        print(f"   Rejected candidates: {len(rejected)}")
        print("\n💡 Tips:")
        print("   - Make sure markers are clearly visible")
        print("   - Check lighting (avoid glare/shadows)")
        print("   - Ensure markers are not blurry")
        print("   - Try getting closer or farther from markers")
    else:
        detected_ids = ids.flatten().tolist()
        print(f"✅ DETECTED {len(ids)} MARKER(S)")
        print(f"   IDs found: {detected_ids}")

        # Check if we have all 4 required markers
        required = [0, 1, 2, 3]
        missing = [id for id in required if id not in detected_ids]
        extra = [id for id in detected_ids if id not in required]

        if missing:
            print(f"\n⚠️  Missing markers: {missing}")
            print(f"   Need all 4 markers (IDs 0, 1, 2, 3) for calibration")
        else:
            print(f"\n🎉 ALL 4 REQUIRED MARKERS DETECTED!")
            print(f"   Ready for homography calculation")

        if extra:
            print(f"\n⚠️  Extra markers detected: {extra}")
            print(f"   (These will be ignored)")

        if rejected:
            print(f"\n   Note: {len(rejected)} rejected candidates")

        # Draw markers on image
        result = image.copy()
        cv2.aruco.drawDetectedMarkers(result, corners, ids)

        # Add marker ID labels
        for i, corner in enumerate(corners):
            # Get center of marker
            center = corner[0].mean(axis=0).astype(int)
            marker_id = ids[i][0]

            # Draw ID text
            cv2.putText(result, f"ID {marker_id}",
                       tuple(center - [0, 20]),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       1.5, (0, 255, 0), 3)

        # Save result
        output_path = image_path.replace('.', '_detected.')
        cv2.imwrite(output_path, result)
        print(f"\n💾 Saved result to: {output_path}")

        # Display
        print(f"\n👀 Displaying result (press any key to close)...")

        # Resize if image is too large
        max_display_size = 1200
        if max(h, w) > max_display_size:
            scale = max_display_size / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            result = cv2.resize(result, (new_w, new_h))

        cv2.imshow("ArUco Detection Result", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print("=" * 50)

def test_webcam():
    """Test detection with live webcam feed"""
    print("\n📷 Opening webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ ERROR: Could not open webcam")
        return

    print("✅ Webcam opened")
    print("\n📝 Controls:")
    print("   'c' = Capture and save frame")
    print("   's' = Save current frame")
    print("   'q' = Quit")
    print("\nStarting live detection...\n")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        # Detect markers
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = detector.detectMarkers(gray)

        # Draw detected markers
        if ids is not None and len(ids) > 0:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            # Show count and IDs
            detected_ids = ids.flatten().tolist()
            cv2.putText(frame, f"Markers: {len(ids)} {detected_ids}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                       0.8, (0, 255, 0), 2)

            # Check if all 4 required markers present
            if set(detected_ids) >= {0, 1, 2, 3}:
                cv2.putText(frame, "ALL 4 MARKERS DETECTED!",
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                           1, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "No markers detected",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                       0.8, (0, 0, 255), 2)

        # Display
        cv2.imshow("Live ArUco Detection (c=capture, s=save, q=quit)", frame)

        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n👋 Quitting...")
            break
        elif key == ord('c') or key == ord('s'):
            filename = f"webcam_frame_{frame_count:03d}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 Saved: {filename}")
            frame_count += 1

            if key == ord('c'):
                print("📸 Frame captured! Analyzing...")
                cap.release()
                cv2.destroyAllWindows()
                test_image(filename)
                return

    cap.release()
    cv2.destroyAllWindows()

def show_usage():
    """Show usage instructions"""
    print("\nArUco Marker Detection Test")
    print("=" * 50)
    print("\nUsage:")
    print("  python 2_test_detection.py <image_path>  - Test with image file")
    print("  python 2_test_detection.py webcam        - Test with live webcam")
    print("\nExamples:")
    print("  python 2_test_detection.py my_photo.jpg")
    print("  python 2_test_detection.py webcam")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    arg = sys.argv[1]

    if arg.lower() == "webcam":
        test_webcam()
    else:
        test_image(arg)
