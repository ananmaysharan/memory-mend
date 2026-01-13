# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Memory Mend is a full-stack application for documenting textile repairs with unique pattern generation and optional ML-based damage detection. Users capture garment images, attach memories (text/photos), and generate a unique 7×7 stitch pattern derived from the memory hash.

## Commands

### Frontend (SvelteKit)
```bash
npm install          # Install dependencies
npm run dev          # Start dev server (HTTPS on localhost:5173)
npm run build        # Production build
npm run check        # Type checking
npm run check:watch  # Type checking in watch mode
```

### Backend (FastAPI)
```bash
cd python-backend
source venv/bin/activate        # Activate venv (macOS/Linux)
pip install -r requirements.txt # Install dependencies
uvicorn main:app --reload --port 5001  # Run server
# API docs: http://localhost:5001/docs
```

## Architecture

### Tech Stack
- **Frontend**: SvelteKit 5 + TypeScript + Tailwind CSS 4 + Supabase
- **Backend**: FastAPI with YOLOv8 (ultralytics) for damage detection
- **Database**: Supabase PostgreSQL for shared mends

### Route Groups
- `src/routes/(app)/` - Main app navigation (home, history, profile)
- `src/routes/(flows)/` - Mend creation workflow (capture → memory → pattern → preview)

### State Management
Svelte 5 runes-based stores in `src/lib/stores/`:
- `mendStore.svelte.ts` - Current workflow state (image, memory, pattern)
- `historyStore.svelte.ts` - All saved mends (localStorage + Supabase)
- `scanStore.svelte.ts` - Pattern scanning state

### Core Data Flow
1. **Capture** - User photographs garment + enters details
2. **Memory** - User adds text/photos of the associated memory
3. **Pattern** - Memory hash → 6-char base36 ID → 7×7 boolean grid
4. **Preview** - Review and save (localStorage + optional Supabase)

### Pattern Generation Pipeline
Memory content → `simpleHash()` → 6-char base36 ID → 42-bit binary → 7×7 grid with corner fiducials

### Key Interfaces (`src/lib/types/mend.ts`)
- `Mend` - Complete mend record with image, memory, pattern, detection
- `Memory` - User memory (id, title, text, images)
- `PatternData` - 7×7 boolean grid with config
- `Detection` - YOLOv8 bounding box results

### Backend Endpoints (port 5001)
- `POST /detect` - YOLOv8 damage detection (base64 image → bounding boxes)
- `POST /detect-pattern` - Pattern extraction from photo (ArUco fiducials + 7×7 grid)

## Environment Variables

Copy `.env.example` to `.env`:
```env
VITE_API_URL=http://localhost:5001
VITE_PUBLIC_SUPABASE_URL=<your-supabase-url>
VITE_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-key>
```

## Notes

- The YOLOv8 model file (`best.pt`) is not in git (>100MB). Must be added to `python-backend/` separately.
- HTTPS dev server requires `cert.crt` and `cert.key` files (see `vite.config.ts`).
- MCP servers configured in `.mcp.json`: Svelte docs + Supabase integration.
