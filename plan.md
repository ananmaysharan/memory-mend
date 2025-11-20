# Memory Mend - Project Plan & Progress

## Recent Changes (2025-11-19) - Phase 2: YOLOv8 Integration

**DAMAGE DETECTION SYSTEM - YOLOV8 INTEGRATION:**
- **Created FastAPI backend** - Python-based API service for YOLOv8 damage detection on port 5001
- **Implemented /detect endpoint** - Accepts base64 images, returns bounding box coordinates with confidence scores
- **New detection workflow step** - Added /detection page between capture and memory steps
- **Interactive bounding box editor** - Draggable corner vertices for manual adjustment (like Apple Notes document scanning)
- **Scanning animation** - Visual feedback during API processing with animated scanning line
- **Manual box addition** - Users can add detection box manually if none detected by AI
- **Updated navigation flow** - capture → detection → memory → pattern → preview
- **Environment configuration** - Added .env.example for API URL configuration (dev vs production)
- **Railway deployment ready** - Dockerfile and railway.json for one-click deployment

**Files created:**
- `python-backend/main.py` - FastAPI server with YOLOv8 model integration
- `python-backend/requirements.txt` - Python dependencies (fastapi, ultralytics, opencv, torch)
- `python-backend/Dockerfile` - Container configuration for Railway deployment
- `python-backend/railway.json` - Railway deployment configuration
- `python-backend/README.md` - Setup and deployment instructions
- `python-backend/.gitignore` - Ignore model file, venv, etc.
- `python-backend/.env.example` - Environment variables template
- `src/routes/detection/+page.svelte` - Detection page with editing UI
- `src/lib/components/detection/ScanningAnimation.svelte` - Loading animation overlay
- `src/lib/components/detection/BoundingBoxEditor.svelte` - Interactive box editor with draggable vertices
- `.env.example` - Frontend environment configuration (API URL)

**Files updated:**
- `src/lib/services/imageProcessing.ts` - Replaced mock detectDamage() with real FastAPI call
- `src/lib/stores/mendStore.svelte.ts` - Added detection field, setDetection() method, updated workflow steps
- `src/routes/capture/+page.svelte` - Navigate to /detection instead of /memory after capture

**How it works:**
1. User captures image on /capture page
2. Redirected to /detection page, which automatically calls FastAPI /detect endpoint
3. YOLOv8 model analyzes image and returns bounding box coordinates
4. User sees annotated image with draggable corner vertices
5. User can adjust box by dragging vertices, or add box manually if none detected
6. Detection data stored in mendStore, proceeds to memory step

**Development setup:**
```bash
# Terminal 1: SvelteKit frontend
npm run dev  # https://localhost:5173

# Terminal 2: FastAPI backend
cd python-backend
pip install -r requirements.txt
uvicorn main:app --reload --port 5001  # http://localhost:5001
```

**Deployment:**
- Frontend: Vercel (existing setup with adapter-auto)
- Backend: Railway.app (auto-deploys from GitHub, uses Dockerfile)
- API URL configured via VITE_API_URL environment variable

**Reason:** Phase 2 integration brings AI-powered damage detection to Memory Mend. Users get intelligent assistance in identifying repair areas, with the flexibility to manually adjust or override AI suggestions. This sets the foundation for future features like size estimation and pattern scaling.

---

## Previous Changes (2025-11-19)

**UX HARMONIZATION - CONSISTENT NAVIGATION:**
- **Created reusable navigation components** - TopBar and BackButton components for consistent UI across all pages
- **Implemented unified top bar structure** - all pages now have consistent header with title and optional back button
- **Standardized page layouts** - all pages use same flex layout pattern (full-height, scrollable content area)
- **Context-aware back navigation** - Mend Detail page uses custom handler for smart navigation based on `?from` parameter
- **Kept bottom back buttons on workflow pages** - Memory, Pattern, and Preview pages keep bottom back buttons for better form UX
- **Files created:**
  - src/lib/components/navigation/TopBar.svelte - reusable top bar with title and optional back button
  - src/lib/components/navigation/BackButton.svelte - transparent back button matching original capture page style
- **Files updated:**
  - All 7 +page.svelte files - added TopBar, standardized layout from `.page` class to flex layout
  - Removed custom header from capture page, replaced with TopBar component
  - History and Mend Detail pages - fixed layout to use consistent pattern
- **Reason:** Consistent navigation improves UX - users always know where to find the back button. Standardized layouts make the app feel more cohesive. Reusable components reduce code duplication and make future updates easier.

## Previous Changes (2025-11-15)

**KEY IMPROVEMENTS:**
- **Mobile-first camera capture** - back camera default, fixed upload button, full-screen on mobile, HEIC support
- **Pattern system simplified** - 6-character IDs (base36), 8x8 grids with corner markers (TL: X, TR: ||, BL: O, BR: solid), read-only patterns
- **Smart navigation** - context-aware back buttons using query parameters (?from=home or ?from=library), clickable mend cards
- **Consistent styling** - Tailwind CSS throughout, clean light theme, standardized layouts
- **Library organization** - home shows 6 recent mends, full library at /history, detail pages accessible from both
- **Removed G-code generation** - simplified codebase to focus on core pattern functionality

---

## Project Overview

**Memory Mend** is a web application that transforms personal memories into unique embroidery patterns for repairing damaged textiles. Each repair becomes a meaningful story, with memories literally woven into the fabric.

**Core Concept:**
1. User photographs a repair area
2. User inputs a memory (text/image)
3. Memory is hashed into a unique 6-character ID
4. ID is converted to binary, with each bit representing a stitch
5. Pattern is generated (read-only, deterministic) with corner markers for orientation
6. Pattern is sent to Raspberry Pi connected to embroidery machine (future)

---

## Technology Stack

**Frontend:**
- SvelteKit 5 (file-based routing)
- Svelte 5 (with runes for reactivity)
- Tailwind CSS 4.1
- TypeScript (type safety)
- Vite 7 (build tool)

**Future Backend:**
- SvelteKit server routes OR FastAPI (Python)
- PostgreSQL/MongoDB (database)
- YOLOv8 (damage detection)
- OpenCV (ArUco marker detection)

**Hardware:**
- Raspberry Pi (G-code server)
- Embroidery machine

**Deployment:**
- Vercel (web app hosting)
- PWA support for offline use

---

## [COMPLETED] MVP Prototype (Phase 1)

### Architecture & Foundation

**Folder Structure:**
```
src/
├── lib/
│   ├── components/
│   │   ├── camera/
│   │   │   └── CameraCapture.svelte          [DONE] Camera with capture/upload
│   │   ├── memory/
│   │   │   └── MemoryInput.svelte            [DONE] Text/image memory input
│   │   ├── pattern/
│   │   │   └── PatternEditor.svelte          [DONE] Interactive grid editor
│   │   └── ui/
│   │       ├── Button.svelte                 [DONE] Reusable button
│   │       ├── Card.svelte                   [DONE] Card container
│   │       └── LoadingSpinner.svelte         [DONE] Loading indicator
│   ├── services/
│   │   ├── imageProcessing.ts                [DONE] Image preprocessing
│   │   ├── patternGenerator.ts               [DONE] Memory to pattern conversion
│   │   └── gcodeGenerator.ts                 [DONE] Pattern to G-code conversion
│   ├── stores/
│   │   ├── mendStore.svelte.ts               [DONE] Current mend state (Svelte 5 runes)
│   │   └── historyStore.svelte.ts            [DONE] Saved mends management
│   ├── utils/
│   │   ├── hashUtils.ts                      [DONE] Memory hashing & binary conversion
│   │   ├── imageUtils.ts                     [DONE] Image manipulation helpers
│   │   └── storage.ts                        [DONE] LocalStorage abstraction
│   └── types/
│       ├── mend.ts                           [DONE] Type definitions for mends
│       └── gcode.ts                          [DONE] G-code configuration types
├── routes/
│   ├── +page.svelte                          [DONE] Home page
│   ├── capture/+page.svelte                  [DONE] Image capture
│   ├── memory/+page.svelte                   [DONE] Memory input
│   ├── pattern/+page.svelte                  [DONE] Pattern editing
│   ├── preview/+page.svelte                  [DONE] G-code preview
│   └── history/
│       ├── +page.svelte                      [DONE] All mends
│       └── [id]/+page.svelte                 [DONE] Individual mend details
```

### Key Features Implemented

#### 1. Image Capture System
**File:** src/lib/components/camera/CameraCapture.svelte

Features:
- [DONE] Device camera access via WebRTC
- [DONE] Front/back camera toggle
- [DONE] Photo capture with preview
- [DONE] File upload fallback
- [DONE] Retake functionality
- [DONE] Error handling for permission issues

#### 2. Memory Encoding System
**Files:**
- src/lib/components/memory/MemoryInput.svelte
- src/lib/utils/hashUtils.ts

**How it works:**
- [DONE] Accepts text and/or image memory
- [DONE] Uses Web Crypto API (SHA-256) for hashing
- [DONE] Converts hash to binary representation
- [DONE] Maps binary to 16x16 grid (256 bits)
- [DONE] Deterministic: same memory = same pattern always

**Example Flow:**
```
Memory text: "My grandmother's garden"
    |
    v
SHA-256 Hash: "a7b3c2d1..."
    |
    v
Binary: "10101011001111010010..."
    |
    v
16x16 Grid: [
  [true, false, true, ...],
  [false, true, true, ...],
  ...
]
```

#### 3. Pattern Generation & Editing
**File:** src/lib/components/pattern/PatternEditor.svelte

Features:
- [DONE] Interactive 16x16 stitch grid
- [DONE] Click individual cells to toggle
- [DONE] Click and drag to paint
- [DONE] Invert entire pattern
- [DONE] Clear entire pattern
- [DONE] Live stitch count & percentage
- [DONE] Visual indication of edited patterns
- [DONE] Readonly mode for viewing

#### 4. Pattern Preview & Send
**File:** src/routes/preview/+page.svelte

Features:
- [DONE] Preview final pattern
- [DONE] Save mend to history
- [PLACEHOLDER] Non-functional "Send to Pi" button (future implementation)

#### 5. State Management (Svelte 5 Runes)
**Files:**
- src/lib/stores/mendStore.svelte.ts
- src/lib/stores/historyStore.svelte.ts

**mendStore:**
- [DONE] Tracks current workflow state
- [DONE] Manages step progression (capture -> memory -> pattern -> preview)
- [DONE] Stores image, memory, pattern, G-code
- [DONE] Auto-saves to localStorage
- [DONE] Can resume interrupted workflows

**historyStore:**
- [DONE] Manages all saved mends
- [DONE] CRUD operations
- [DONE] Search and filter
- [DONE] Status tracking (draft, ready, sent, completed)
- [DONE] Statistics aggregation

#### 6. Complete User Flow
1. **Home (/)** - Landing page with "Start New Mend" button and grid of 6 most recent mends (clickable cards)
   - If > 6 mends exist, shows "View Full Mend Library" button
   - Clicking mend card navigates to detail with ?from=home parameter
2. **Capture (/capture)** - Take/upload photo
3. **Memory (/memory)** - Input memory and generate pattern
4. **Pattern (/pattern)** - Review/edit pattern
5. **Preview (/preview)** - Preview final pattern and send to Pi (placeholder)
6. **Mend Library (/history)** - Full library view of all mends (clickable cards)
   - Clicking mend card navigates to detail with ?from=library parameter
7. **Mend Detail (/history/[id])** - View individual mend details, delete mend
   - Smart back button returns to origin (home or library) based on ?from parameter

#### 7. Data Persistence
**File:** src/lib/utils/storage.ts

Features:
- [DONE] LocalStorage abstraction layer
- [DONE] Saves mends with all data
- [DONE] Saves work-in-progress
- [DONE] Easy to swap for API calls later
- [DONE] Error handling

### What Works Right Now

**Working Features:**
- End-to-End Flow: Capture -> Memory -> Pattern -> Preview & Save
- Local Persistence: All mends saved in browser localStorage
- Pattern Generation: Read-only, deterministic 8x8 grids with corner markers and 6-character IDs
- Memory Encoding: Simple hash function for short, readable IDs
- Recent Mends Grid: 6 most recent mends displayed on home page as clickable cards
- Mend Library: Full library view at /history showing all mends as clickable cards
- Unified Navigation: Consistent TopBar on all pages with context-aware back buttons
- Mend Details: View individual mend details, delete mends
- Clean UI: Tailwind CSS throughout, consistent layouts, mobile-first camera
- Camera Access: Back camera by default, file upload with HEIC support

### Testing Checklist

- [x] Camera capture works (mobile-first, back camera default)
- [x] File upload works (HEIC/HEIF support)
- [x] Memory text hashing works (6-character IDs)
- [x] Pattern generation is deterministic (read-only 8x8 grids)
- [x] LocalStorage persistence works
- [x] Navigation between pages works (unified TopBar)
- [x] Context-aware back navigation works (query parameters)
- [x] History page shows saved mends
- [x] Individual mend details page works
- [x] Delete mend works
- [x] Workflow state is preserved
- [x] Preview page shows final pattern
- [x] Save & Finish works

---

## [TODO] Next Development Phases

### Phase 2: Image Processing & Detection (Week 2) - [COMPLETED]

#### YOLOv8 Integration ✅ COMPLETED
**Priority:** High | **Complexity:** Medium-High | **Status:** DONE

**Completed Tasks:**
- [x] ~~Set up YOLOv8 model training environment~~ (User provided pre-trained model)
- [x] ~~Collect/create dataset of damaged textiles~~ (User provided pre-trained model)
- [x] Use fine-tuned YOLOv8 model on damage detection
- [x] Create Python API endpoint for inference (FastAPI `/detect`)
- [x] Deploy YOLOv8 service (FastAPI backend, Railway-ready)
- [x] Integrate detection into capture flow (new `/detection` page)
- [x] Display bounding boxes on image (BoundingBoxEditor component)
- [x] Allow manual adjustment of detection area (draggable corner vertices)

**✅ Implementation Summary:**
- **FastAPI Backend:** Created in `python-backend/` directory
  - `/detect` endpoint accepts base64 images, returns JSON with bounding box coordinates
  - CORS configured for dev (localhost:5173) and production
  - Health check endpoint at `/health`
  - Swagger UI docs at `/docs`

- **Frontend Integration:**
  - New `/detection` route between capture and memory steps
  - `BoundingBoxEditor` component with Apple Notes-style draggable vertices
  - `ScanningAnimation` component for visual feedback during API call
  - Detection data stored in mendStore
  - Retry detection functionality
  - Manual box addition if no AI detection found

- **Deployment Ready:**
  - Dockerfile for containerized deployment
  - railway.json for Railway.app one-click deploy
  - Environment-based configuration via `.env` files
  - Backend runs on port 5001, frontend calls via VITE_API_URL

**Files Created:**
```
python-backend/
  ├── main.py                          (FastAPI server with YOLOv8)
  ├── requirements.txt                 (Python dependencies)
  ├── Dockerfile                       (Railway deployment)
  ├── railway.json                     (Railway config)
  ├── README.md                        (Setup instructions)
  └── best.pt                          (YOLOv8 model - user provided)

src/routes/detection/+page.svelte      (Detection page)
src/lib/components/detection/
  ├── BoundingBoxEditor.svelte         (Interactive box editor)
  └── ScanningAnimation.svelte         (Loading animation)
```

**Files Updated:**
```
src/lib/services/imageProcessing.ts    (Real API integration)
src/lib/stores/mendStore.svelte.ts     (Detection field added)
src/routes/capture/+page.svelte        (Navigate to /detection)
```

#### ArUco Marker Detection
**Priority:** Medium | **Complexity:** Medium | **Status:** [PLANNED - Future Enhancement]

**Purpose:** Real-world size estimation and automatic pattern scaling

**Why Deferred:**
Focus was on core damage detection first. ArUco markers will enable advanced features:
- **Size Calibration:** Measure damage area in real-world units (mm/cm)
- **Automatic Scaling:** Scale embroidery pattern based on hole size
- **Machine Positioning:** Precise calibration for embroidery machine coordinates
- **Quality Assurance:** Validate repair coverage

**Planned Tasks:**
- [ ] Implement ArUco marker detection using OpenCV backend (extend FastAPI)
- [ ] Create printable ArUco marker templates (calibration cards with known sizes)
- [ ] Detect markers alongside damage detection in same API call
- [ ] Calculate pixels-to-mm ratio from marker distances
- [ ] Transform detected damage area to real-world dimensions (mm)
- [ ] Scale pattern size based on damage measurements
- [ ] Add optional calibration step to detection workflow
- [ ] Create UI guidance for marker placement in camera view
- [ ] Store calibration data in detection object

**Proposed Implementation:**

**Backend (FastAPI):**
```python
# Add to python-backend/main.py
import cv2
from cv2 import aruco

@app.post("/detect-with-calibration")
async def detect_with_markers(request: DetectionRequest):
    # Detect both damage (YOLOv8) AND ArUco markers (OpenCV)
    damage_boxes = yolo_detection(image)
    markers = aruco_detection(image)

    # Calculate calibration if markers found
    if markers:
        pixels_per_mm = calculate_scale(markers)
        real_size_mm = bbox_to_mm(damage_boxes[0], pixels_per_mm)

    return {
        "damage": damage_boxes,
        "markers": markers,
        "calibration": { "pixels_per_mm": pixels_per_mm },
        "real_size_mm": real_size_mm
    }
```

**Frontend Component:**
```svelte
<!-- src/lib/components/detection/ArucoCalibration.svelte -->
- Visual guide: "Place calibration card in frame"
- Live marker detection feedback (green borders when detected)
- Calibration success indicators
- Skip calibration option (proceed with pixel-based sizing)
- Display real-world measurements when calibrated
```

**Integration Point:**
- Optional "Calibrate Size" button on detection page
- If markers detected, show real measurements: "Hole size: 25mm × 30mm"
- Store calibration data alongside detection in mendStore
- Use measurements for automatic pattern scaling in future phases

#### Manual Detection Adjustment ✅ COMPLETED
**Priority:** High | **Complexity:** Low | **Status:** DONE

**Completed Tasks:**
- [x] Create draggable bounding box overlay (SVG-based interactive component)
- [x] Allow resize via draggable corner vertices (4 draggable circles)
- [x] Save adjusted coordinates to mendStore
- [x] Manual box addition if no AI detection found
- [x] Visual confidence indicators and feedback

**Implementation:**
- **Component:** `src/lib/components/detection/BoundingBoxEditor.svelte`
- **Features:**
  - Interactive SVG overlay with 4 draggable corner vertices (TL, TR, BL, BR)
  - Real-time bounding box updates during drag
  - Vertex positions constrained to image bounds
  - Minimum box size validation (20px × 20px)
  - Confidence badge (AI percentage vs "Manual selection")
  - "Add Detection Box" button when no AI detection
  - "Remove Box" button to clear and start over
  - Image auto-scaling to fit container

**User Experience:**
- Apple Notes-style document scanning interaction
- Smooth drag-and-drop with visual feedback
- Works on both desktop (mouse) and mobile (touch)
- Clear instructions: "Drag the corner circles to adjust the detection area"
- Blue dashed animated border for visibility

**Data Flow:**
1. User adjusts vertices by dragging corner circles
2. Component updates local bounding box state
3. Calls `onChange()` callback with new Detection object
4. Detection page stores updated data in mendStore
5. Detection persists through navigation and localStorage

---

#### What's Next for Phase 2? (Future Enhancements)

**Short-term Improvements:**
- [ ] Multiple detection support - detect and mark multiple holes in a single image
- [ ] Detection confidence threshold slider - let users adjust sensitivity in UI
- [ ] Save annotated image - store image with bounding box drawn for reference
- [ ] Detection history - show recent detections on detection page
- [ ] Damage severity classification - categorize as small/medium/large based on size

**Medium-term Additions:**
- [ ] ArUco marker integration - add size calibration capabilities (see section above)
- [ ] Automatic pattern scaling - scale stitch pattern based on detected hole size
- [ ] Fabric type detection - identify fabric material to adjust stitch density
- [ ] Damage shape analysis - classify as circular, linear, tear, irregular
- [ ] Detection analytics - track detection accuracy and user adjustments

**Long-term Vision:**
- [ ] Real-time detection preview - show detection overlay during camera capture
- [ ] Multi-camera/multi-angle - combine images from different angles
- [ ] 3D depth estimation - use multiple photos to estimate hole depth
- [ ] AI-suggested repair techniques - recommend repair approach based on damage
- [ ] Fabric condition assessment - detect worn areas around damage
- [ ] Detection model improvement - fine-tune model based on user corrections

**Technical Improvements:**
- [ ] Offline detection - run lightweight model in browser via ONNX.js
- [ ] Detection caching - avoid re-running detection on same image
- [ ] Batch detection - process multiple images at once
- [ ] Detection export - save detection data as JSON for external tools
- [ ] API rate limiting - prevent abuse of detection endpoint
- [ ] Model versioning - support multiple YOLOv8 model versions

---

### Phase 3: Backend & Database (Week 3)

#### Backend Architecture Decision
**Options:**
1. **SvelteKit Server Routes** (recommended for MVP+)
   - Pros: Single codebase, easy deployment
   - Cons: Less suitable for heavy ML workloads

2. **Separate FastAPI Backend**
   - Pros: Better for Python ML models, async support
   - Cons: Need to manage two services

**Recommended:** Hybrid approach
- SvelteKit server routes for CRUD operations
- Separate FastAPI for ML inference (YOLOv8, image processing)

#### Database Setup
**Priority:** High | **Complexity:** Medium

**Recommended:** PostgreSQL with Prisma ORM

**Tasks:**
- [ ] Choose database (PostgreSQL vs MongoDB)
- [ ] Set up Prisma ORM
- [ ] Design database schema
- [ ] Create migration files
- [ ] Implement API routes
- [ ] Update storage.ts to use API instead of localStorage
- [ ] Add database indexes for performance

**Schema Design:**
```prisma
// prisma/schema.prisma

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  mends     Mend[]
  createdAt DateTime @default(now())
}

model Mend {
  id          String   @id @default(cuid())
  userId      String
  user        User     @relation(fields: [userId], references: [id])
  name        String?
  image       String   // URL to stored image
  memoryText  String?
  memoryImage String?  // URL to stored image
  memoryId    String
  pattern     Json     // PatternData as JSON
  gcode       String?
  detection   Json?    // Detection data
  status      MendStatus
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}

enum MendStatus {
  DRAFT
  READY
  SENT
  COMPLETED
}
```

**API Routes to Implement:**
```
POST   /api/mends              Create new mend
GET    /api/mends              List all mends (paginated)
GET    /api/mends/:id          Get specific mend
PATCH  /api/mends/:id          Update mend
DELETE /api/mends/:id          Delete mend
POST   /api/mends/:id/gcode    Generate G-code
```

#### Image Storage
**Priority:** High | **Complexity:** Low-Medium

**Options:**
1. **Cloud Storage:** AWS S3, Cloudflare R2, Vercel Blob
2. **Database:** Store as base64 (not recommended for production)

**Recommended:** Vercel Blob (easy Vercel integration)

**Tasks:**
- [ ] Set up Vercel Blob storage
- [ ] Create upload endpoint
- [ ] Update image capture to upload to blob storage
- [ ] Store blob URLs in database instead of base64
- [ ] Implement image optimization pipeline

---

### Phase 4: Authentication & User Management (Week 3-4)

#### Authentication Implementation
**Priority:** Medium-High | **Complexity:** Medium

**Recommended:** Lucia Auth (modern, type-safe)

**Tasks:**
- [ ] Install Lucia Auth
- [ ] Set up session management
- [ ] Create login/signup pages
- [ ] Implement password hashing (Argon2)
- [ ] Add email verification (optional for MVP)
- [ ] Implement OAuth providers (Google, GitHub - optional)
- [ ] Add protected routes
- [ ] Create user profile page

**New Routes:**
```
src/routes/
  ├── login/+page.svelte
  ├── signup/+page.svelte
  ├── profile/+page.svelte
  └── (protected)/              # Layout for protected routes
      ├── +layout.server.ts     # Check auth
      ├── capture/
      ├── memory/
      └── ...
```

**Auth Hooks:**
```typescript
// src/hooks.server.ts
import { lucia } from '$lib/server/auth';

export async function handle({ event, resolve }) {
  const sessionId = event.cookies.get(lucia.sessionCookieName);
  // Validate session...
  return resolve(event);
}
```

#### User Features
- [ ] User dashboard
- [ ] Mend ownership (only see your own mends)
- [ ] Profile settings
- [ ] Account deletion
- [ ] Export all data (GDPR compliance)

---

### Phase 5: Raspberry Pi Integration (Week 4)

#### Python Server on Raspberry Pi
**Priority:** High | **Complexity:** Medium

**Tasks:**
- [ ] Set up Raspberry Pi with Raspberry Pi OS
- [ ] Install Python 3.10+
- [ ] Create Flask/FastAPI G-code receiver
- [ ] Implement G-code parser
- [ ] Connect to embroidery machine serial port
- [ ] Create G-code execution queue
- [ ] Add status reporting (WebSocket)
- [ ] Implement emergency stop
- [ ] Add machine calibration endpoint

**Raspberry Pi Server Structure:**
```python
# pi-server/main.py
from fastapi import FastAPI, WebSocket
import serial

app = FastAPI()

@app.post("/gcode")
async def receive_gcode(gcode: str):
    # Validate G-code
    # Add to queue
    # Return job ID
    pass

@app.websocket("/status")
async def status_websocket(websocket: WebSocket):
    # Send real-time status updates
    pass

@app.post("/execute/{job_id}")
async def execute_job(job_id: str):
    # Execute G-code from queue
    # Send commands to serial port
    pass

@app.post("/stop")
async def emergency_stop():
    # Immediately halt machine
    pass
```

#### Web App Integration
**Priority:** High | **Complexity:** Medium

**Tasks:**
- [ ] Create Pi connection settings page
- [ ] Implement WebSocket client
- [ ] Add "Send to Pi" functionality
- [ ] Show real-time execution status
- [ ] Display queue status
- [ ] Add execution history
- [ ] Implement error handling and retry logic

**New Component:**
```svelte
<!-- src/lib/components/pi/PiConnection.svelte -->
- Connection status indicator
- Manual connect/disconnect
- Show Pi IP address
- Test connection button
```

**New Store:**
```typescript
// src/lib/stores/piStore.svelte.ts
class PiStore {
  connected = $state(false);
  status = $state('idle');
  currentJob = $state(null);
  queue = $state([]);

  async connect(ipAddress: string) { ... }
  async sendGcode(gcode: string) { ... }
  async getStatus() { ... }
}
```

#### Network Configuration
**Options:**
1. **Local Network:** Pi and web app on same WiFi
2. **Cloud Proxy:** Expose Pi via ngrok/Cloudflare Tunnel
3. **VPN:** Secure remote access

**Recommended for MVP:** Local network with mDNS discovery

---

### Phase 6: PWA & Offline Support (Week 5)

#### Progressive Web App Setup
**Priority:** Medium | **Complexity:** Low-Medium

**Tasks:**
- [ ] Create web app manifest
- [ ] Design app icons (multiple sizes)
- [ ] Implement service worker
- [ ] Add offline fallback page
- [ ] Cache static assets
- [ ] Implement offline queue for G-code
- [ ] Add "Add to Home Screen" prompt
- [ ] Test install flow on mobile

**Manifest:**
```json
// static/manifest.json
{
  "name": "Memory Mend",
  "short_name": "MemoryMend",
  "description": "Transform memories into repair patterns",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

**Service Worker:**
```typescript
// src/service-worker.ts
import { build, files, version } from '$service-worker';

const CACHE = `cache-${version}`;
const ASSETS = [...build, ...files];

// Install and cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS))
  );
});

// Serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Cache-first strategy
});
```

#### Offline Features
- [ ] View cached mends offline
- [ ] Edit patterns offline
- [ ] Queue G-code sends for when online
- [ ] Sync when connection restored
- [ ] Show offline indicator

---

### Phase 7: Advanced Features (Week 6+)

#### Pattern Library
**Priority:** Low | **Complexity:** Low

- [ ] Preset pattern templates (hearts, flowers, geometric)
- [ ] Community shared patterns
- [ ] Pattern categories/tags
- [ ] Search patterns
- [ ] Like/favorite patterns

#### Advanced Pattern Generation
**Priority:** Medium | **Complexity:** High

- [ ] Multiple pattern sizes (8x8, 16x16, 32x32)
- [ ] Color/thread selection
- [ ] Multi-color patterns
- [ ] Pattern symmetry options
- [ ] Style transfer (apply artistic styles to patterns)
- [ ] AI-generated patterns based on memory sentiment

#### Collaboration Features
**Priority:** Low | **Complexity:** Medium

- [ ] Share mends with others
- [ ] Collaborative pattern editing
- [ ] Comments on mends
- [ ] Mend collections/albums
- [ ] Social feed of community mends

#### Analytics & Insights
**Priority:** Low | **Complexity:** Low

- [ ] Total stitches across all mends
- [ ] Most common memory themes
- [ ] Pattern complexity metrics
- [ ] Time spent mending
- [ ] Environmental impact calculator (items saved from landfill)

#### Machine Learning Enhancements
**Priority:** Medium | **Complexity:** High

- [ ] Automatic repair technique suggestion
- [ ] Pattern quality scoring
- [ ] Predict execution time
- [ ] Optimize stitch path for efficiency
- [ ] Fabric type detection
- [ ] Damage severity assessment

---

## Technical Debt & Improvements

### Code Quality
- [ ] Add unit tests (Vitest)
- [ ] Add component tests (Playwright)
- [ ] Add E2E tests
- [ ] Improve error handling throughout app
- [ ] Add loading states everywhere
- [ ] Implement proper error boundaries
- [ ] Add TypeScript strict mode compliance
- [ ] Add JSDoc comments to all functions
- [ ] Set up ESLint and Prettier
- [ ] Add pre-commit hooks (Husky)

### Performance
- [ ] Implement image lazy loading
- [ ] Add virtual scrolling for history page
- [ ] Optimize pattern rendering for larger grids
- [ ] Add debouncing to pattern editor
- [ ] Implement request caching
- [ ] Add service worker caching strategy
- [ ] Optimize bundle size (code splitting)
- [ ] Add performance monitoring (Sentry, LogRocket)

### Accessibility
- [ ] Add ARIA labels to all interactive elements
- [ ] Ensure keyboard navigation works everywhere
- [ ] Test with screen readers
- [ ] Add focus indicators
- [ ] Ensure color contrast meets WCAG AA
- [ ] Add alt text to all images
- [ ] Support reduced motion preferences
- [ ] Add skip links

### Security
- [ ] Implement rate limiting
- [ ] Add CSRF protection
- [ ] Sanitize user inputs
- [ ] Implement content security policy (CSP)
- [ ] Add helmet middleware
- [ ] Encrypt sensitive data in database
- [ ] Implement secure session management
- [ ] Add XSS protection
- [ ] Regular dependency updates (Dependabot)

### UX Improvements
- [ ] Add onboarding tutorial
- [ ] Add tooltips and help text
- [ ] Improve mobile responsiveness
- [ ] Add confirmation dialogs for destructive actions
- [ ] Add undo/redo for pattern editing
- [ ] Add keyboard shortcuts
- [ ] Add dark mode
- [ ] Improve loading states and skeletons
- [ ] Add success/error toast notifications
- [ ] Add image cropping tool

---

## Deployment Strategy

### Development Environment
- **Current:** Local development server (http://localhost:5173/)
- **Database:** None yet (using localStorage)
- **Image Storage:** Base64 in localStorage

### Staging Environment
**Recommended:** Vercel Preview Deployments

- [ ] Connect GitHub repo to Vercel
- [ ] Set up preview deployments for PRs
- [ ] Configure environment variables
- [ ] Set up staging database
- [ ] Set up staging blob storage

### Production Environment
**Recommended:** Vercel + PostgreSQL + Vercel Blob

- [ ] Deploy to Vercel
- [ ] Set up production database (Vercel Postgres or Supabase)
- [ ] Configure production blob storage
- [ ] Set up custom domain
- [ ] Configure DNS
- [ ] Enable HTTPS
- [ ] Set up monitoring (Vercel Analytics)
- [ ] Set up error tracking (Sentry)
- [ ] Configure backups
- [ ] Set up CI/CD pipeline

### Raspberry Pi Deployment
- [ ] Create deployment script
- [ ] Set up systemd service for auto-start
- [ ] Configure firewall rules
- [ ] Set up logging
- [ ] Implement auto-updates
- [ ] Add monitoring and alerts

---

## Project Timeline

### Week 1 - [COMPLETED]
- Set up SvelteKit project
- Build core MVP flow
- Implement pattern generation
- Add G-code generation
- Create all pages and components
- **Status:** MVP prototype working!

### Week 2 - [COMPLETED]
- ✅ YOLOv8 integration (FastAPI backend with /detect endpoint)
- ✅ Manual detection adjustment (draggable bounding box editor)
- ✅ Image processing pipeline (base64 → API → detection results)
- ⏭️ ArUco marker detection (deferred to future phase)
- **Status:** Damage detection system fully integrated!

### Week 3
- Backend setup (SvelteKit + FastAPI)
- Database schema and migrations
- Authentication system
- Image storage solution
- API implementation

### Week 4
- Raspberry Pi server setup
- Machine communication protocol
- WebSocket status updates
- Queue management
- Error handling and recovery

### Week 5
- PWA implementation
- Offline support
- Service worker
- Performance optimization
- Mobile testing

### Week 6+
- Advanced features
- Community features
- Analytics
- Polish and refinement

---

## Resources & Documentation

### Key Libraries
- [SvelteKit Docs](https://svelte.dev/docs/kit)
- [Svelte 5 Runes](https://svelte.dev/docs/svelte/reactivity)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Prisma ORM](https://www.prisma.io/docs)
- [Lucia Auth](https://lucia-auth.com/)
- [YOLOv8](https://docs.ultralytics.com/)
- [OpenCV.js](https://docs.opencv.org/4.x/d5/d10/tutorial_js_root.html)

### Embroidery & G-code
- [G-code Reference](https://reprap.org/wiki/G-code)
- [Embroidery File Formats](https://inkstitch.org/docs/formats/)
- [RepRap G-code Guide](https://reprap.org/wiki/G-code)

### Design Inspiration
- [Visible Mending](https://www.instagram.com/explore/tags/visiblemending/)
- [Sashiko Stitching](https://en.wikipedia.org/wiki/Sashiko)
- [Boro Textiles](https://en.wikipedia.org/wiki/Boro_(textile))

---

## Current Status Summary

**[WORKING]**
- Complete end-to-end flow (Capture → Detection → Memory → Pattern → Save)
- Mobile-first camera capture with back camera default
- **YOLOv8 damage detection** - FastAPI backend with real-time detection
- **Interactive bounding box editor** - Draggable vertices for manual adjustment
- **Scanning animation** - Visual feedback during detection
- Memory hashing with 6-character IDs (base36)
- Read-only pattern generation (8x8 grids with corner markers)
- Local data persistence (localStorage)
- Unified navigation with consistent TopBar on all pages
- Context-aware back navigation using query parameters
- History management (recent mends on home, full library page)
- Clean, consistent UI with Tailwind CSS

**[INFRASTRUCTURE]**
- FastAPI backend (python-backend/) - YOLOv8 detection service
- Railway deployment ready - Dockerfile and config files
- Environment-based API URL configuration
- CORS configured for dev and production

**[REMOVED]**
- G-code generation (simplified for now)
- Pattern editing features (now read-only, deterministic)

**[PLACEHOLDER]**
- "Send to Pi" button (non-functional, for future implementation)

**[PLANNED]**
- ArUco marker detection (for size estimation)
- Raspberry Pi integration
- G-code generation (to be re-implemented when needed)
- Backend infrastructure (database, auth)
- Database integration
- User authentication
- Cloud storage
- PWA features
- Advanced ML features
- Community features

---

## Notes & Decisions

### Architecture Decisions
1. **Svelte 5 Runes over Stores:** Using new reactivity system for cleaner code
2. **localStorage for MVP:** Quick iteration, easy to swap later
3. **8x8 Grid with Corner Markers:** Compact patterns with orientation indicators
4. **Simple Hash Function:** Generates short 6-character IDs (base36) instead of SHA-256
5. **Tailwind CSS:** Rapid prototyping, consistent design
6. **Reusable Components:** TopBar and BackButton for consistent navigation
7. **FastAPI for ML Backend:** Separate Python service for YOLOv8, keeps frontend lightweight
8. **Monorepo Structure:** Python backend in same repo for easier development

### Design Decisions
1. **No Auth for MVP:** Faster testing and iteration
2. **Single User Initially:** Simplifies data model
3. **Camera-first Flow:** Mobile-optimized experience with back camera default
4. **Read-only Patterns:** Deterministic, non-editable patterns for consistency
5. **G-code Removed:** Simplified codebase to focus on core pattern generation
6. **Unified Top Bar:** Consistent header on all pages improves UX
7. **Smart Navigation with Query Params:** Context-aware back button improves UX
8. **Recent Mends on Home:** Shows 6 most recent mends, full library accessible via button
9. **Clickable Cards:** Entire mend card is clickable for better mobile UX
10. **Detection Step Optional:** Users can proceed even if no damage detected (manual override)
11. **Interactive Detection Editing:** Apple Notes-style draggable vertices for intuitive adjustment
12. **Automatic Detection on Page Load:** Immediate feedback, scanning animation during processing

### Future Considerations
1. **Multi-user Support:** Need solid auth and data isolation
2. **Scalability:** Consider CDN for images, caching strategies
3. **Internationalization:** Support multiple languages
4. **Accessibility:** Must work with screen readers
5. **Mobile Performance:** Optimize for slower devices

---

## Getting Started (For New Developers)

### Prerequisites
- Node.js 18+ installed
- npm or pnpm
- Git
- Modern browser (Chrome, Firefox, Safari, Edge)

### Initial Setup
```bash
# Clone repository
git clone https://github.com/yourusername/memory-mend.git
cd memory-mend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Development Workflow
1. Make changes to files
2. Browser auto-reloads (Vite HMR)
3. Test in browser
4. Commit changes

### Running Tests (Coming Soon)
```bash
npm run test          # Unit tests
npm run test:e2e      # End-to-end tests
npm run lint          # Check code quality
npm run format        # Format code
```

### Build for Production
```bash
npm run build
npm run preview       # Preview production build
```

---

## Contact & Support

**Project Lead:** [Your Name]
**Repository:** https://github.com/yourusername/memory-mend
**Issues:** https://github.com/yourusername/memory-mend/issues

---

**Last Updated:** 2025-11-19
**Version:** 0.1.0 (MVP Prototype)
