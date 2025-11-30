# ArUco Marker Testing

Simple testing setup for ArUco marker detection before integrating into Memory Mend.

## Setup

1. **Install dependencies:**
   ```bash
   pip install opencv-contrib-python numpy
   ```

2. **Generate markers:**
   ```bash
   python 1_generate_markers.py
   ```
   This creates THREE calibration cards:
   - `calibration_card_10mm_letter.png` - 1cm markers (smallest)
   - `calibration_card_15mm_letter.png` - 1.5cm markers (recommended)
   - `calibration_card_20mm_letter.png` - 2cm markers (easiest to detect)

3. **Print a calibration card:**
   - **Recommended:** Start with `calibration_card_15mm_letter.png` or `calibration_card_20mm_letter.png`
   - Print at **100% scale / Actual Size** (DO NOT scale to fit!)
   - Paper: Letter (8.5" × 11")
   - Verify with a ruler that markers measure exactly as specified
   - Optional: laminate for durability

   💡 **Tip:** Try 20mm first (easiest), then 15mm, then 10mm only if needed

## Testing

### Option 1: Test with a photo

1. Place printed calibration card in/on your embroidery hoop
2. Take a photo with your phone/camera
3. Transfer photo to computer
4. Run:
   ```bash
   python 2_test_detection.py path/to/your/photo.jpg
   ```

### Option 2: Test with webcam

```bash
python 2_test_detection.py webcam
```

Live controls:
- Press `c` to capture and analyze
- Press `s` to save current frame
- Press `q` to quit

## What to Test

- **Marker sizes:** Test 20mm, 15mm, then 10mm (in that order)
- **Distance:**
  - 20mm markers: 20-50cm from camera
  - 15mm markers: 15-40cm from camera
  - 10mm markers: 15-30cm from camera
- **Angle:** Perpendicular, 30°, 45° downward
- **Lighting:** Different lighting conditions (bright, dim, with/without shadows)
- **Focus:** Ensure camera focuses sharply (especially for smaller markers)
- **Placement:** Card inside hoop vs markers cut out and attached to hoop frame

## Success Criteria

✅ All 4 markers (IDs 0, 1, 2, 3) should be detected
✅ Detection should work at various distances (depends on marker size)
✅ Detection should work at downward angles (30-45°)
✅ Chosen marker size fits well on your hoop and detects reliably

💡 **Choose the smallest marker size that still detects reliably** - smaller is better for less intrusive appearance, but must be detectable

## Next Steps

Once detection is working reliably:
1. Choose marker placement method (card vs frame)
2. Test homography transformation (see aruco_plan.md)
3. Validate measurement accuracy with known-size objects
4. Integrate into Memory Mend backend
