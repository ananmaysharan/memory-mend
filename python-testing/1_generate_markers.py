"""
Generate ArUco markers for testing
Simple script to create printable marker images on letter-sized page
"""
import cv2
import numpy as np

# ArUco dictionary - same as will be used in the app
ARUCO_DICT = cv2.aruco.DICT_4X4_50
aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)

def generate_calibration_card_letter(marker_size_mm=100, dpi=300):
    """
    Generate a letter-sized page (8.5" × 11") with 4 markers at corners
    Ready to print at actual size
    """
    # Letter size in pixels at 300 DPI
    # 8.5" × 11" = 215.9mm × 279.4mm
    width_px = int(8.5 * dpi)   # 2550 pixels
    height_px = int(11 * dpi)   # 3300 pixels

    # Convert marker size to pixels
    marker_size_px = int((marker_size_mm / 25.4) * dpi)

    # Create white canvas
    page = np.ones((height_px, width_px), dtype=np.uint8) * 255

    # Margin from edge
    margin_px = int((1.5 / 25.4) * dpi)  # 1.5 inch margin

    print(f"📄 Page size: {width_px} × {height_px} pixels (8.5\" × 11\")")
    print(f"📏 Marker size: {marker_size_px} pixels ({marker_size_mm}mm)")

    # Marker positions: ID 0=top-left, 1=top-right, 2=bottom-right, 3=bottom-left
    positions = {
        0: (margin_px, margin_px),  # Top-left
        1: (width_px - margin_px - marker_size_px, margin_px),  # Top-right
        2: (width_px - margin_px - marker_size_px, height_px - margin_px - marker_size_px),  # Bottom-right
        3: (margin_px, height_px - margin_px - marker_size_px)  # Bottom-left
    }

    # Place markers
    for marker_id, (x, y) in positions.items():
        print(f"   Placing marker ID {marker_id} at ({x}, {y})")
        marker = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_px)
        page[y:y+marker_size_px, x:x+marker_size_px] = marker

    # Add title at top center
    font = cv2.FONT_HERSHEY_SIMPLEX
    title = f"ArUco Calibration Card - {marker_size_mm}mm markers"
    title_size = cv2.getTextSize(title, font, 1.5, 3)[0]
    title_x = (width_px - title_size[0]) // 2
    cv2.putText(page, title, (title_x, 100), font, 1.5, (0, 0, 0), 3)

    # Add instructions
    instructions = [
        "PRINT AT 100% SCALE (ACTUAL SIZE) - DO NOT SCALE TO FIT",
        f"Each marker should measure exactly {marker_size_mm}mm × {marker_size_mm}mm",
        "Verify size with a ruler before using"
    ]

    y_offset = 160
    for instruction in instructions:
        text_size = cv2.getTextSize(instruction, font, 0.7, 2)[0]
        text_x = (width_px - text_size[0]) // 2
        cv2.putText(page, instruction, (text_x, y_offset), font, 0.7, (0, 0, 0), 2)
        y_offset += 40

    # Add measurement guides (corner to corner distance)
    # Distance between marker centers (useful for validation)
    center_distance_x = width_px - 2 * margin_px - marker_size_px
    center_distance_y = height_px - 2 * margin_px - marker_size_px
    center_distance_x_mm = (center_distance_x / dpi) * 25.4
    center_distance_y_mm = (center_distance_y / dpi) * 25.4

    # Add dimension info at bottom
    dim_y = height_px - 80
    dim_text = f"Marker spacing: {center_distance_x_mm:.1f}mm × {center_distance_y_mm:.1f}mm (center to center)"
    dim_size = cv2.getTextSize(dim_text, font, 0.6, 2)[0]
    dim_x = (width_px - dim_size[0]) // 2
    cv2.putText(page, dim_text, (dim_x, dim_y), font, 0.6, (100, 100, 100), 2)

    # Save
    filename = f"calibration_card_{marker_size_mm}mm_letter.png"
    cv2.imwrite(filename, page)

    print(f"\n✅ Created: {filename}")
    print(f"   Page: 8.5\" × 11\" (Letter size)")
    print(f"   Markers: {marker_size_mm}mm × {marker_size_mm}mm")
    print(f"   IDs: 0 (top-left), 1 (top-right), 2 (bottom-right), 3 (bottom-left)")
    print(f"   Marker spacing: {center_distance_x_mm:.1f}mm × {center_distance_y_mm:.1f}mm")

    return page

if __name__ == "__main__":
    print("ArUco Marker Generator")
    print("=" * 70)
    print("\nGenerating calibration cards with different marker sizes...\n")

    # Generate multiple sizes for testing
    sizes = [10, 15, 20]  # mm

    for size in sizes:
        print(f"\n{'─' * 70}")
        print(f"Generating {size}mm markers...")
        print(f"{'─' * 70}")
        generate_calibration_card_letter(marker_size_mm=size)

    print("\n" + "=" * 70)
    print("✅ ALL CARDS GENERATED!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  📄 calibration_card_10mm_letter.png - Smallest (1cm markers)")
    print("  📄 calibration_card_15mm_letter.png - Medium (1.5cm markers)")
    print("  📄 calibration_card_20mm_letter.png - Largest (2cm markers)")

    print("\n📝 PRINTING INSTRUCTIONS:")
    print("=" * 70)
    print("1. Choose ONE card size to print (start with 15mm or 20mm)")
    print("2. Print settings:")
    print("   - Paper size: Letter (8.5\" × 11\")")
    print("   - Scale: 100% (ACTUAL SIZE - do NOT scale to fit)")
    print("   - Quality: Best/High")
    print("3. After printing, verify with a ruler:")
    print("   - Markers should measure exactly as specified")
    print("4. If size is wrong, check printer settings")

    print("\n📸 TESTING RECOMMENDATIONS:")
    print("=" * 70)
    print("• Start with 20mm markers (easiest to detect)")
    print("• If 20mm works well, try 15mm")
    print("• Only use 10mm if larger sizes are too big for your hoop")
    print("\n• 20mm markers: Easier detection, 20-50cm distance")
    print("• 15mm markers: Good balance, 15-40cm distance")
    print("• 10mm markers: Smallest, needs 15-30cm distance, sharp focus")

    print("\n🧪 Test with: python 2_test_detection.py <photo_path>")
    print("=" * 70)
