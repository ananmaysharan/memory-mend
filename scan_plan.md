# Scan & Decode Mend Feature - Implementation Plan

## Overview

Build a feature that allows users to scan embroidered mends and decode the hidden memories. Two methods: (1) camera photo detection, (2) manual pattern input. Mends stored locally but also shared globally via Supabase (opt-in).

## Key Discovery

 **Decoding functions already exist!** `gridToBinary()` and `binaryToId()` are in `hashUtils.ts` (lines 147-166, 79-91). This significantly simplifies implementation.

## Phased Implementation Strategy

### PHASE 1: Manual Pattern Input + Local Decode (2-3 hours)
**Goal**: Build working decode system with manual 7×7 grid input, looking up mends from localStorage only.

**Why start here**: No external dependencies, tests core decode logic, foundation for all other features.

#### Files to Create

1. **`/src/routes/scan/+page.svelte`** - Main scan page
   - Manual pattern input mode
   - Decode logic: `grid ’ gridToBinary() ’ binaryToId() ’ lookup`
   - Display results (found/not found states)
   - Success: Show memory title/text with "View Full Mend" button
   - Error: "Pattern not found in your library"

2. **`/src/lib/components/scan/ManualPatternInput.svelte`** - Interactive 7×7 grid
   - 7×7 tappable cells (36px each)
   - Corner markers pre-filled and locked:
     - TL (0,0): X pattern (two crossing diagonals)
     - TR (0,6): || pattern (two vertical lines)
     - BL (6,0): O pattern (circle outline)
     - BR (6,6):   pattern (solid square)
   - Non-corner cells: Toggle black (stitch) / white (no stitch) on tap
   - Auto-trigger decode via `$effect()` on grid changes
   - Props: `onComplete(grid: boolean[][])`

#### Files to Modify

3. **`/src/lib/stores/historyStore.svelte.ts`** - Add lookup method (line ~141)
   ```typescript
   /**
    * Find a mend by its pattern ID
    */
   findMendByPatternId(patternId: string): Mend | undefined {
     return this.mends.find((m) => m.pattern.id === patternId);
   }
   ```

4. **`/src/routes/+page.svelte`** - Wire scan button (line 29)
   ```svelte
   <Button onclick={() => goto('/scan')}>
     <Scan size={18} weight="bold" />Scan Mend
   </Button>
   ```

#### Testing Phase 1
1. Create new mend ’ note pattern ID
2. Navigate to `/scan`
3. Recreate pattern manually
4. Verify mend found and displays correctly
5. Test "not found" with random pattern

---

### PHASE 2: Database Integration - Supabase (3-4 hours)
**Goal**: Enable global mend sharing with privacy controls.

#### Supabase Setup

1. **Create Supabase project** at [supabase.com](https://supabase.com)
2. **Run SQL schema** in SQL Editor:
   ```sql
   CREATE TABLE public.mends (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     pattern_id TEXT NOT NULL UNIQUE,
     title TEXT,
     text TEXT,
     images JSONB,  -- Array of base64 images
     garment_type TEXT,
     material TEXT,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   CREATE INDEX idx_mends_pattern_id ON public.mends(pattern_id);

   ALTER TABLE public.mends ENABLE ROW LEVEL SECURITY;

   -- Anyone can read
   CREATE POLICY "Public mends viewable by everyone"
     ON public.mends FOR SELECT USING (true);

   -- Anyone can insert (anonymous sharing)
   CREATE POLICY "Anyone can create mends"
     ON public.mends FOR INSERT WITH CHECK (true);
   ```

3. **Environment variables** - Add to `.env.local`:
   ```bash
   PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
   ```

4. **Install package**:
   ```bash
   npm install @supabase/supabase-js
   ```

#### Files to Create

1. **`/src/lib/services/supabase.ts`** - Supabase client and functions
   - `getSupabaseClient()` - Initialize client with env vars
   - `uploadMendToSupabase(mend: Mend)` - Upload to database (upsert on pattern_id)
   - `findMendByPatternId(patternId: string)` - Lookup by pattern ID
   - `isSupabaseAvailable()` - Check if configured
   - Reconstruct full Mend from database row (regenerate pattern grid from ID)
   - Warn if images > 5MB

#### Files to Modify

2. **`/src/lib/types/mend.ts`** - Add privacy field (line ~51)
   ```typescript
   export interface Mend {
     // ... existing fields ...
     isPublic?: boolean;  // NEW: Privacy flag for Supabase sharing
   }
   ```

3. **`/src/routes/preview/+page.svelte`** - Add privacy controls
   - State: `let sharePublicly = $state(true)` (default checked)
   - Checkbox before action buttons:
     ```svelte
     <label class="flex items-start gap-3">
       <input type="checkbox" bind:checked={sharePublicly} />
       <div>
         <p class="font-medium">Share publicly</p>
         <p class="text-sm text-gray-600">
           Allow others to discover this memory by scanning the pattern.
         </p>
       </div>
     </label>
     ```
   - In `handleSaveAndFinish()`:
     - Add `isPublic: sharePublicly` to mend
     - If `sharePublicly && isSupabaseAvailable()`, call `uploadMendToSupabase()`
     - Show upload status/errors (non-blocking)

4. **`/src/routes/scan/+page.svelte`** - Add Supabase fallback
   ```typescript
   import { findMendByPatternId as findInSupabase } from '$lib/services/supabase';

   async function decodePattern() {
     // 1. Try local lookup first
     let mend = historyStore.findMendByPatternId(patternId);

     // 2. If not found locally, try Supabase
     if (!mend) {
       mend = await findInSupabase(patternId);
     }

     // Display result or "not found" error
   }
   ```

#### Testing Phase 2
1. Create mend with "Share publicly" ON ’ verify in Supabase dashboard
2. Create mend with checkbox OFF ’ verify NOT in Supabase
3. Scan shared mend from different device ’ found in Supabase
4. Test with Supabase disabled ’ works locally

---

### PHASE 3: Camera Detection with OpenCV (6-8 hours)
**Goal**: Automatic pattern detection from photos.

#### Backend: FastAPI Pattern Detection

**Modify `/python-backend/main.py`** - Add endpoint after `/detect` (line ~202)

```python
from typing import Optional

class PatternDetectionRequest(BaseModel):
    image: str  # base64
    debug: Optional[bool] = False

class PatternDetectionResponse(BaseModel):
    grid: List[List[bool]]  # 7x7 grid
    confidence: float  # 0-1
    corner_markers_found: int  # Should be 4
    debug_image: Optional[str] = None

def detect_corner_markers(image_gray: np.ndarray) -> dict:
    """Find 4 corner markers (X, ||, O,  ) using contour detection."""
    # Apply binary threshold
    # Find contours
    # Divide into quadrants (TL, TR, BL, BR)
    # Find largest contour in each quadrant
    # Return pixel coordinates

def extract_grid_from_corners(image_gray: np.ndarray, corners: dict) -> List[List[bool]]:
    """Extract 7x7 grid using perspective transform."""
    # Perspective transform to square
    # Sample each cell (7x7)
    # Threshold: dark = stitch, light = no stitch
    # Return boolean grid

@app.post("/detect-pattern")
async def detect_pattern(request: PatternDetectionRequest):
    # Decode image
    # Detect corners
    # Extract grid
    # Return grid + confidence
```

**OpenCV already installed** - `opencv-python-headless==4.10.0.84` in requirements.txt

#### Frontend: Camera Mode

**Modify `/src/routes/scan/+page.svelte`** - Add camera mode

1. **Import camera component**:
   ```typescript
   import CameraCapture from '$lib/components/camera/CameraCapture.svelte';
   ```

2. **Add mode state**:
   ```typescript
   let mode = $state<'manual' | 'camera'>('camera');  // Default camera
   let isScanning = $state(false);
   let capturedImage = $state<string | null>(null);
   ```

3. **Camera capture handler**:
   ```typescript
   async function handleCameraCapture(imageData: string) {
     capturedImage = imageData;
     isScanning = true;

     // Call backend
     const response = await fetch(`${API_URL}/detect-pattern`, {
       method: 'POST',
       body: JSON.stringify({ image: imageData })
     });

     const result = await response.json();

     // Check confidence
     if (result.confidence < 0.8) {
       error = 'Low confidence. Try manual input.';
       mode = 'manual';
       return;
     }

     // Use detected grid
     grid = result.grid;
     await decodePattern();
   }
   ```

4. **Add mode selector UI**:
   ```svelte
   <div class="flex gap-2 mb-6">
     <Button onclick={() => switchMode('camera')}>Camera Scan</Button>
     <Button onclick={() => switchMode('manual')}>Manual Input</Button>
   </div>

   {#if mode === 'camera'}
     {#if !capturedImage && !isScanning}
       <CameraCapture onCapture={handleCameraCapture} />
     {:else if isScanning}
       <!-- Reuse scanning animation from /scanning/+page.svelte -->
       <div class="relative">
         <img src={capturedImage} />
         <div class="scanning-bar"></div>
       </div>
     {/if}
   {:else}
     <ManualPatternInput onComplete={handleGridComplete} />
   {/if}
   ```

5. **Add scanning animation styles** (copy from `/src/routes/scanning/+page.svelte` lines 96-115):
   ```css
   .scanning-bar {
     position: absolute;
     left: 0; right: 0;
     height: 4px;
     background: var(--color-blue);
     animation: scan 2s ease-in-out infinite;
   }

   @keyframes scan {
     0%, 100% { top: 0; }
     50% { top: calc(100% - 4px); }
   }
   ```

#### Testing Phase 3
1. Print a pattern on paper
2. Photograph with camera
3. Verify corners detected (all 4)
4. Verify grid extracted correctly
5. Test various lighting/angles
6. Test fallback to manual on low confidence

---

## Implementation Order & Dependencies

```
Phase 1 (Manual + Local)
  “
Phase 2 (Database)    Phase 3 (Camera)
  “                        “
        Both complete     
```

- **Phase 1** is foundation - no dependencies
- **Phase 2** and **Phase 3** can be built in parallel after Phase 1
- **MVP**: Phase 1 only
- **Recommended**: Phase 1 ’ Phase 2 ’ Phase 3

## Critical Files Summary

### Phase 1 (Core Decode)
- `/src/routes/scan/+page.svelte` - NEW
- `/src/lib/components/scan/ManualPatternInput.svelte` - NEW
- `/src/lib/stores/historyStore.svelte.ts` - MODIFY (add `findMendByPatternId`)
- `/src/routes/+page.svelte` - MODIFY (wire scan button)
- `/src/lib/utils/hashUtils.ts` - NO CHANGES (already has `gridToBinary`, `binaryToId`)

### Phase 2 (Database)
- `/src/lib/services/supabase.ts` - NEW
- `/src/lib/types/mend.ts` - MODIFY (add `isPublic` field)
- `/src/routes/preview/+page.svelte` - MODIFY (add checkbox + upload)
- `/src/routes/scan/+page.svelte` - MODIFY (add Supabase fallback)

### Phase 3 (Camera)
- `/python-backend/main.py` - MODIFY (add `/detect-pattern` endpoint)
- `/src/routes/scan/+page.svelte` - MODIFY (add camera mode)

## Edge Cases & Error Handling

### Phase 1
- Empty grid ’ "Please fill in the pattern"
- Invalid binary ’ Catch and show friendly message
- Pattern not found ’ "Not found in your library"

### Phase 2
- Supabase unavailable ’ Degrade to local-only
- Upload fails ’ Save locally, show warning (non-blocking)
- Large images (>5MB) ’ Warn user
- Network timeout ’ Set reasonable timeout (10s)

### Phase 3
- < 4 corners detected ’ Show error, switch to manual
- Low confidence (<80%) ’ Warn and offer manual
- Backend offline ’ Fall back to manual
- Camera permission denied ’ Show manual mode
- Blurry image ’ Suggest retake

## Environment Setup

1. **Supabase credentials** (Phase 2):
   - Add to `.env.local` (create if needed)
   - Add `.env.local` to `.gitignore`

2. **Backend URL** (Phase 3):
   - Update fetch calls to use Railway backend URL
   - Or use `import.meta.env.VITE_API_URL`

3. **Dependencies**:
   - `@supabase/supabase-js` (Phase 2)
   - OpenCV already installed in backend

## Success Criteria

 **Phase 1 Complete When**:
- User can manually recreate 7×7 pattern
- Pattern decodes to correct 6-character ID
- Mend found in local history and displays
- "Not found" message for unknown patterns

 **Phase 2 Complete When**:
- Checkbox on preview page works
- Checked mends upload to Supabase
- Unchecked mends stay local
- Scan finds mends from Supabase
- Graceful degradation when offline

 **Phase 3 Complete When**:
- Camera captures photo
- Backend detects 4 corners
- Grid extracted correctly (>80% confidence)
- Auto-decode works
- Manual fallback available
- Scanning animation plays

---

**Total Estimated Time**: 11-15 hours (2-3 + 3-4 + 6-8)

**MVP Time**: 2-3 hours (Phase 1 only)
