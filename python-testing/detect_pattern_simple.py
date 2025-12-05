"""
Simple Pattern Detection for Embroidered 7x7 Grid

Approach:
1. Find TL (top-left) X fiducial
2. Calculate cell size from fiducial size (cell ≈ fiducial × 1.30)
3. Grid starts at bottom-right of fiducial + offset
4. Classify each cell by dark pixel ratio (>15% = filled)

Usage:
    python detect_pattern_simple.py image.jpg [--debug]
"""

import cv2
import numpy as np
import sys
import os
from pathlib import Path


def find_tl_fiducial(binary, image_shape):
    """
    Find the top-left X fiducial.
    Returns (x, y, width, height) of bounding box.
    """
    h, w = image_shape[:2]
    
    # Search in top-left corner (12% of image)
    margin = int(min(h, w) * 0.12)
    tl_region = binary[0:margin, 0:margin]
    
    # Find contours
    contours, _ = cv2.findContours(tl_region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        raise ValueError("No contours found in TL corner")
    
    # Take the largest contour (should be the X fiducial)
    best = max(contours, key=cv2.contourArea)
    x, y, fw, fh = cv2.boundingRect(best)
    
    return x, y, fw, fh


def detect_grid(image_path, debug=False):
    """
    Detect the 7x7 grid pattern in an embroidered image.
    
    Returns:
        grid: 7x7 numpy array of booleans (True = X present)
        scores: 7x7 numpy array of dark pixel ratios
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    
    # Binary threshold (dark embroidery on light fabric)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find TL fiducial
    fx, fy, fw, fh = find_tl_fiducial(binary, image.shape)
    
    # Calculate cell size from fiducial
    # The fiducial is approximately 75-80% of cell size
    fiducial_size = (fw + fh) // 2
    cell_size = int(fiducial_size * 1.30)
    
    # Grid starts at bottom-right of fiducial + small offset
    offset = int(fiducial_size * 0.1)
    grid_start_x = fx + fw + offset
    grid_start_y = fy + fh + offset
    
    # Classify each cell
    grid = np.zeros((7, 7), dtype=bool)
    scores = np.zeros((7, 7))
    
    for row in range(7):
        for col in range(7):
            x1 = grid_start_x + col * cell_size
            y1 = grid_start_y + row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            
            # Clip to image bounds
            x1, x2 = max(0, x1), min(w, x2)
            y1, y2 = max(0, y1), min(h, y2)
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            # Calculate dark pixel ratio
            cell = binary[y1:y2, x1:x2]
            dark_ratio = np.sum(cell > 0) / cell.size if cell.size > 0 else 0
            scores[row, col] = dark_ratio
            
            # Threshold: >15% dark pixels means X is present
            grid[row, col] = dark_ratio > 0.15
    
    # Save debug visualization if requested
    if debug:
        debug_dir = Path("debug_output")
        debug_dir.mkdir(exist_ok=True)
        
        viz = image.copy()
        
        # Draw fiducial box
        cv2.rectangle(viz, (fx, fy), (fx + fw, fy + fh), (0, 0, 255), 3)
        
        # Draw grid
        for row in range(7):
            for col in range(7):
                x1 = grid_start_x + col * cell_size
                y1 = grid_start_y + row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                color = (0, 255, 0) if grid[row, col] else (128, 128, 128)
                cv2.rectangle(viz, (x1, y1), (x2, y2), color, 2)
        
        cv2.imwrite(str(debug_dir / "detection_result.png"), viz)
        print(f"Debug image saved to {debug_dir}/detection_result.png")
    
    return grid, scores


def print_grid(grid):
    """Print grid as ASCII art"""
    print("\n" + "=" * 25)
    print("DETECTED GRID (7x7)")
    print("=" * 25)
    print("   " + " ".join(str(c) for c in range(7)))
    for row in range(7):
        symbols = ["█" if grid[row, col] else "·" for col in range(7)]
        print(f"{row}  " + " ".join(symbols))
    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    image_path = sys.argv[1]
    debug = "--debug" in sys.argv
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)
    
    try:
        grid, scores = detect_grid(image_path, debug=debug)
        print_grid(grid)
        
        # Print statistics
        filled = np.sum(grid)
        print(f"Filled cells: {filled}/49")
        print(f"Score range: {scores.min():.3f} - {scores.max():.3f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()