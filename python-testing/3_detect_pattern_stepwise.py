"""
Pattern Detection Script
Detects embroidered patterns with corner fiducials:
- TL = X (cross), TR = || (parallel lines)
- BL = O (circle), BR = □ (square)

Grid detection uses TL fiducial size to calculate cell size,
then classifies cells by dark pixel ratio.

Usage:
    python 3_detect_pattern_stepwise.py path/to/image.jpg
"""

import cv2
import numpy as np
import sys
import os
from pathlib import Path

DEBUG_DIR = "debug_output"


def save_debug(name, img):
    """Save debug image"""
    Path(DEBUG_DIR).mkdir(exist_ok=True)
    cv2.imwrite(os.path.join(DEBUG_DIR, name), img)
    print(f"  -> {name}")


def order_points(pts):
    """
    Order points in consistent order: top-left, top-right, bottom-right, bottom-left.
    This is essential for perspective transform.
    """
    rect = np.zeros((4, 2), dtype="float32")
    
    # Sum of coordinates: smallest = top-left, largest = bottom-right
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    
    # Difference of coordinates: smallest = top-right, largest = bottom-left
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    
    return rect


def four_point_transform(image, pts):
    """
    Apply perspective transform to crop and straighten the region defined by 4 points.
    """
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    # Calculate width of new image (max of top and bottom widths)
    width_top = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    width_bottom = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    max_width = max(int(width_top), int(width_bottom))
    
    # Calculate height of new image (max of left and right heights)
    height_left = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    height_right = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    max_height = max(int(height_left), int(height_right))
    
    # Destination points for the transform
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")
    
    # Compute perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))
    
    return warped


def find_pattern_region(image):
    """
    Find the pattern region in an image where the pattern may not fill the entire frame.
    Uses edge detection and contour finding to locate the largest rectangular region.
    
    Returns:
        - Cropped image if pattern region found
        - Original image if no clear pattern region detected
        - pts: The 4 corner points of the detected region (or None)
    """
    print("\n[STEP 0] Finding pattern region...")
    
    h, w = image.shape[:2]
    print(f"  Image size: {w}x{h}")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    pattern_pts = None
    debug_img = image.copy()
    
    # Method 1: Inverted binary threshold + morphological closing
    # This works well for dark patterns on light backgrounds
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Close gaps to merge pattern elements into a single region
    kernel_size = max(15, int(min(h, w) * 0.03))
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    save_debug("0a_binary_closed.png", closed)
    
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        for contour in contours[:10]:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # Look for 4-sided polygons
            if len(approx) == 4:
                area = cv2.contourArea(approx)
                # Must be at least 5% of image area
                if area < (h * w * 0.05):
                    continue
                
                x, y, cw, ch = cv2.boundingRect(approx)
                aspect = max(cw, ch) / min(cw, ch) if min(cw, ch) > 0 else 999
                
                # Pattern should be roughly square (aspect < 1.5)
                if aspect > 1.5:
                    continue
                
                pattern_pts = approx.reshape(4, 2)
                cv2.drawContours(debug_img, [approx], -1, (0, 255, 0), 3)
                print(f"  Found pattern region: {cw}x{ch}, aspect {aspect:.2f}, area {area}")
                break
    
    # Method 2: Canny edge detection (fallback)
    if pattern_pts is None:
        edges = cv2.Canny(blurred, 50, 150)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        save_debug("0a_edges.png", edges)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            for contour in contours[:10]:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                if len(approx) == 4:
                    area = cv2.contourArea(approx)
                    if area < (h * w * 0.05):
                        continue
                    
                    x, y, cw, ch = cv2.boundingRect(approx)
                    aspect = max(cw, ch) / min(cw, ch) if min(cw, ch) > 0 else 999
                    
                    if aspect > 1.5:
                        continue
                    
                    pattern_pts = approx.reshape(4, 2)
                    cv2.drawContours(debug_img, [approx], -1, (0, 255, 0), 3)
                    print(f"  Found pattern region (edges): {cw}x{ch}, aspect {aspect:.2f}")
                    break
    
    save_debug("0b_pattern_region.png", debug_img)
    
    if pattern_pts is None:
        print("  No clear pattern region found, using full image")
        return image, None
    
    # Apply perspective transform to crop and straighten
    cropped = four_point_transform(image, pattern_pts.astype("float32"))
    save_debug("0c_cropped.png", cropped)
    
    ch, cw = cropped.shape[:2]
    print(f"  Cropped to: {cw}x{ch}")
    
    return cropped, pattern_pts


def find_fiducials(image):
    """
    Find the 4 corner fiducials by position.
    Searches each corner region separately for the largest shape.
    Returns dict with {tl, tr, bl, br} containing bounding box info.
    """
    print("\n[STEP 1] Finding fiducials...")
    
    h, w = image.shape[:2]
    print(f"  Image size: {w}x{h}")
    
    # Use Otsu threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    save_debug("1_binary.png", binary)

    # Apply morphological closing only for larger images (photos with texture)
    # Smaller/cleaner images don't need it
    if min(h, w) > 800:
        kernel_size = max(3, int(min(h, w) * 0.008))
        if kernel_size % 2 == 0:
            kernel_size += 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        save_debug("1b_binary_closed.png", binary)
        print(f"  Applied morphological closing with kernel size: {kernel_size}px")
    else:
        print(f"  Skipping morphological closing for small image")

    # Corner margin - use 18% to ensure we capture full fiducials
    margin = int(min(h, w) * 0.18)
    
    # Define corner regions as (y1, y2, x1, x2) for slicing
    corners = {
        'tl': (0, margin, 0, margin),
        'tr': (0, margin, w - margin, w),
        'bl': (h - margin, h, 0, margin),
        'br': (h - margin, h, w - margin, w)
    }
    
    fiducials = {}
    debug_img = image.copy()
    
    for corner, (y1, y2, x1, x2) in corners.items():
        # Extract corner region from binary image
        region = binary[y1:y2, x1:x2]
        
        # Find contours in this region
        contours, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print(f"  {corner.upper()}: Not found (no contours)")
            continue

        # Merge nearby contours if multiple exist
        if len(contours) > 1:
            # Sort by area and take top 3
            contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:3]
            # Merge all top contours into single bounding box
            all_points = np.vstack(contours_sorted)
            bx, by, bw, bh = cv2.boundingRect(all_points)
        else:
            best = max(contours, key=cv2.contourArea)
            bx, by, bw, bh = cv2.boundingRect(best)
        
        # Adjust coordinates back to full image
        bx += x1
        by += y1
        
        fiducials[corner] = {'bbox': (bx, by, bw, bh)}
        aspect_ratio = max(bw, bh) / min(bw, bh) if min(bw, bh) > 0 else 999
        print(f"  {corner.upper()}: Found at ({bx}, {by}), size {bw}x{bh}, aspect {aspect_ratio:.2f}")
    
    # Normalize fiducial sizes based on the most square ones
    # This fixes cases where one fiducial has artifacts making it non-square
    if len(fiducials) >= 2:
        fiducials = normalize_fiducial_sizes(fiducials)
    
    # Draw on debug image
    for corner, fid in fiducials.items():
        bx, by, bw, bh = fid['bbox']
        cv2.rectangle(debug_img, (bx, by), (bx+bw, by+bh), (0, 255, 0), 3)
        cv2.putText(debug_img, corner.upper(), (bx, by-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    save_debug("2_fiducials.png", debug_img)
    return fiducials


def normalize_fiducial_sizes(fiducials):
    """
    Normalize fiducial bounding boxes to be square, using the most reliable fiducials
    as reference. This fixes cases where one fiducial picks up extra artifacts.
    """
    # Calculate aspect ratio and size for each fiducial
    fid_info = []
    for corner, fid in fiducials.items():
        bx, by, bw, bh = fid['bbox']
        aspect = max(bw, bh) / min(bw, bh) if min(bw, bh) > 0 else 999
        size = (bw + bh) / 2
        fid_info.append((corner, aspect, size, bw, bh))
    
    # Find fiducials with good (square-ish) aspect ratios (< 1.3)
    square_fids = [(c, a, s, w, h) for c, a, s, w, h in fid_info if a < 1.3]
    
    if not square_fids:
        # No square fiducials, use the one with best aspect ratio
        square_fids = sorted(fid_info, key=lambda x: x[1])[:1]
    
    # Calculate target size from the square fiducials
    target_size = int(sum(s for _, _, s, _, _ in square_fids) / len(square_fids))
    
    print(f"  Normalizing to target size: {target_size}px (from {len(square_fids)} square fiducials)")
    
    # Adjust non-square fiducials to use target size, keeping center position
    normalized = {}
    for corner, fid in fiducials.items():
        bx, by, bw, bh = fid['bbox']
        aspect = max(bw, bh) / min(bw, bh) if min(bw, bh) > 0 else 999
        
        if aspect > 1.3:
            # This fiducial is non-square, normalize it
            # Keep the center, adjust to target size
            cx, cy = bx + bw // 2, by + bh // 2
            new_bx = cx - target_size // 2
            new_by = cy - target_size // 2
            normalized[corner] = {'bbox': (new_bx, new_by, target_size, target_size)}
            print(f"    {corner.upper()}: Normalized from {bw}x{bh} to {target_size}x{target_size}")
        else:
            # Keep as-is but make it square using its own average size
            own_size = (bw + bh) // 2
            cx, cy = bx + bw // 2, by + bh // 2
            new_bx = cx - own_size // 2
            new_by = cy - own_size // 2
            normalized[corner] = {'bbox': (new_bx, new_by, own_size, own_size)}
    
    return normalized


def decode_grid(image, fiducials):
    """
    Decode 7x7 grid using fiducials to determine grid bounds.
    Uses all available fiducials for more robust calculation.
    """
    print("\n[STEP 2] Decoding grid...")
    
    if 'tl' not in fiducials:
        raise ValueError("TL fiducial not found - cannot decode grid")
    
    h, w = image.shape[:2]
    
    # Get TL fiducial - always needed
    tl_x, tl_y, tl_w, tl_h = fiducials['tl']['bbox']
    
    # Calculate grid bounds using all available fiducials
    # Grid starts after TL fiducial and ends before BR fiducial
    
    if all(k in fiducials for k in ['tl', 'tr', 'bl', 'br']):
        # Best case: all 4 fiducials found - use them to define grid bounds
        tr_x, tr_y, tr_w, tr_h = fiducials['tr']['bbox']
        bl_x, bl_y, bl_w, bl_h = fiducials['bl']['bbox']
        br_x, br_y, br_w, br_h = fiducials['br']['bbox']
        
        # Grid boundaries (inside the fiducials)
        grid_left = max(tl_x + tl_w, bl_x + bl_w)  # Right edge of left fiducials
        grid_right = min(tr_x, br_x)                # Left edge of right fiducials
        grid_top = max(tl_y + tl_h, tr_y + tr_h)   # Bottom edge of top fiducials
        grid_bottom = min(bl_y, br_y)               # Top edge of bottom fiducials
        
        # Calculate cell size from grid span
        grid_width = grid_right - grid_left
        grid_height = grid_bottom - grid_top
        cell_size = int((grid_width + grid_height) / 14)  # Average of both dimensions / 7 cells
        
        print(f"  Using all 4 fiducials for grid bounds")
        print(f"  Grid span: {grid_width}x{grid_height}px")
    else:
        # Fallback: use TL fiducial size to estimate
        fiducial_size = (tl_w + tl_h) // 2
        cell_size = int(fiducial_size * 1.30)
        grid_left = tl_x + tl_w + int(fiducial_size * 0.1)
        grid_top = tl_y + tl_h + int(fiducial_size * 0.1)
        print(f"  Using TL fiducial only (size: {fiducial_size}px)")
    
    print(f"  Cell size: {cell_size}px")
    print(f"  Grid starts at: ({grid_left}, {grid_top})")
    
    # Get binary image for classification
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    save_debug("3_binary_grid.png", binary)
    
    grid = np.zeros((7, 7), dtype=bool)
    scores = np.zeros((7, 7))
    debug_img = image.copy()
    
    # Draw fiducial references
    for corner, fid in fiducials.items():
        fx, fy, fw, fh = fid['bbox']
        cv2.rectangle(debug_img, (fx, fy), (fx+fw, fy+fh), (0, 0, 255), 2)
    
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
            
            # Calculate dark pixel ratio
            cell = binary[y1c:y2c, x1c:x2c]
            dark_ratio = np.sum(cell > 0) / cell.size if cell.size > 0 else 0
            scores[row, col] = dark_ratio
    
    # Adaptive threshold: find natural gap in scores
    all_scores = sorted(scores.flatten())
    # Find largest gap in sorted scores to determine threshold
    best_gap = 0
    threshold = 0.15  # Default fallback
    for i in range(len(all_scores) - 1):
        gap = all_scores[i + 1] - all_scores[i]
        if gap > best_gap:
            best_gap = gap
            threshold = (all_scores[i] + all_scores[i + 1]) / 2
    
    # Ensure threshold is reasonable (between 10% and 50%)
    threshold = max(0.10, min(0.50, threshold))
    print(f"  Adaptive threshold: {threshold:.3f}")
    
    for row in range(7):
        for col in range(7):
            x1 = grid_left + col * cell_size
            y1 = grid_top + row * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            
            grid[row, col] = scores[row, col] > threshold
            
            # Draw cell
            color = (0, 255, 0) if grid[row, col] else (100, 100, 100)
            cv2.rectangle(debug_img, (x1, y1), (x2, y2), color, 2)
    
    save_debug("4_grid_result.png", debug_img)
    
    print(f"  Score range: {scores.min():.3f} - {scores.max():.3f}")
    print(f"  Filled cells: {np.sum(grid)}/49")
    
    return grid, scores


def print_grid(grid):
    """Print grid as ASCII"""
    print("\n" + "=" * 25)
    print("DETECTED GRID (7x7)")
    print("=" * 25)
    print("   " + " ".join(str(c) for c in range(7)))
    for row in range(7):
        symbols = ["█" if grid[row, col] else "·" for col in range(7)]
        print(f"{row}  " + " ".join(symbols))
    print()


def print_grid_binary(grid):
    """Print grid as binary rows (1=filled, 0=empty)"""
    print("BINARY ROWS:")
    for row in range(7):
        binary_row = "".join(["1" if grid[row, col] else "0" for col in range(7)])
        print(f"  Row {row}: {binary_row}")
    print()


def grid_to_binary(grid):
    """
    Convert grid to binary string, skipping corner cells.
    Reads row-by-row, left-to-right.
    """
    binary = ""
    grid_size = len(grid)
    
    for row in range(grid_size):
        for col in range(grid_size):
            # Skip corner cells
            is_corner = (
                (row == 0 and col == 0) or
                (row == 0 and col == grid_size - 1) or
                (row == grid_size - 1 and col == 0) or
                (row == grid_size - 1 and col == grid_size - 1)
            )
            
            if not is_corner:
                binary += "1" if grid[row, col] else "0"
    
    return binary


def binary_to_id(binary, id_length=6):
    """
    Convert binary string to ID.
    Each 7 bits → one ASCII character.
    """
    chars = []
    
    for i in range(0, id_length * 7, 7):
        chunk = binary[i:i+7]
        # Pad with zeros if needed
        padded_chunk = chunk.ljust(7, '0')
        ascii_code = int(padded_chunk, 2)
        if ascii_code > 0:  # Only add printable characters
            chars.append(chr(ascii_code))
    
    return "".join(chars)


def decode_id(grid):
    """Full decode: Grid → Binary → ID"""
    binary = grid_to_binary(grid)
    id_str = binary_to_id(binary)
    
    print("ID DECODING:")
    print(f"  Binary (45 bits, no corners): {binary}")
    print(f"  Chunks (7 bits each):")
    for i in range(6):
        chunk = binary[i*7:(i+1)*7]
        ascii_code = int(chunk.ljust(7, '0'), 2)
        char = chr(ascii_code) if 32 <= ascii_code < 127 else '?'
        print(f"    Bits {i*7+1}-{(i+1)*7}: {chunk} → {ascii_code:3d} → '{char}'")
    
    # Last 3 bits (unused)
    remaining = binary[42:45]
    print(f"    Bits 43-45: {remaining} (unused)")
    
    print(f"\n  DECODED ID: {id_str}")
    return id_str


def main():
    if len(sys.argv) < 2:
        print("Usage: python 3_detect_pattern_stepwise.py path/to/image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)
    
    print(f"\nProcessing: {image_path}")
    print(f"Debug output: {DEBUG_DIR}/\n")
    
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load image")
        sys.exit(1)
    
    save_debug("0_original.png", image)
    
    try:
        # Step 0: Try to find and crop pattern region
        # This handles images where the pattern is not at the edges
        cropped_image, pattern_pts = find_pattern_region(image)
        
        # Use the cropped image for further processing
        working_image = cropped_image
        
        # Step 1: Find all 4 fiducials
        fiducials = find_fiducials(working_image)
        
        found = list(fiducials.keys())
        missing = [k for k in ['tl', 'tr', 'bl', 'br'] if k not in fiducials]
        
        if 'tl' not in fiducials:
            print("\n❌ FAILED: TL fiducial not found (required for grid)")
            sys.exit(1)
        
        if missing:
            print(f"\n⚠️  Missing fiducials: {missing} (continuing with TL)")
        else:
            print(f"\n✓ Found all 4 fiducials")
        
        # Step 2: Decode grid using fiducials
        grid, scores = decode_grid(working_image, fiducials)
        
        # Print results
        print_grid(grid)
        print_grid_binary(grid)
        decode_id(grid)
        
        print(f"\n✓ Done! Check '{DEBUG_DIR}/' for debug images.")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
