# Memory Mend - Python Backend (FastAPI)

This is the YOLOv8 damage detection API for Memory Mend. It receives images from the SvelteKit frontend and returns bounding box coordinates for detected fabric damage.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Your fine-tuned YOLOv8 model file (`best.pt`)

## Setup Instructions

### 1. Install Dependencies

```bash
cd python-backend
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
cd python-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Add Your Model File

Place your fine-tuned YOLOv8 model in this directory:

```
python-backend/
└── best.pt  # Your YOLOv8 model file
```

**Note:** If your model file is large (>100MB), it won't be committed to Git (see `.gitignore`). You'll need to download it separately or use Git LFS.

### 3. Configure Environment (Optional)

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if needed:

```env
MODEL_PATH=best.pt
PORT=5001
```

### 4. Run the Server

```bash
# Make sure you're in the python-backend directory
uvicorn main:app --reload --port 5001
```

The API will be available at:
- **API**: http://localhost:5001
- **Docs**: http://localhost:5001/docs (interactive Swagger UI)
- **Health Check**: http://localhost:5001/health

## API Endpoints

### `GET /`
Health check endpoint.

**Response:**
```json
{
  "service": "Memory Mend Detection API",
  "status": "running",
  "model_loaded": true
}
```

### `GET /health`
Detailed health check.

**Response:**
```json
{
  "status": "healthy",
  "model_path": "best.pt",
  "model_loaded": true
}
```

### `POST /detect`
Detect fabric damage in an image.

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "confidence_threshold": 0.3
}
```

**Response:**
```json
{
  "detections": [
    {
      "bbox": {
        "x": 120,
        "y": 80,
        "width": 200,
        "height": 150
      },
      "confidence": 0.87,
      "class_name": "damage"
    }
  ],
  "image_width": 640,
  "image_height": 480
}
```

## Development Workflow

### Running Both Servers Locally

You need two terminal windows:

**Terminal 1 - SvelteKit Frontend:**
```bash
# In project root
npm run dev
# Runs at https://localhost:5173
```

**Terminal 2 - FastAPI Backend:**
```bash
# In python-backend directory
uvicorn main:app --reload --port 5001
# Runs at http://localhost:5001
```

### Testing the API

#### Using Swagger UI (Easiest)
1. Go to http://localhost:5001/docs
2. Click on `POST /detect`
3. Click "Try it out"
4. Paste a base64 image string
5. Click "Execute"

#### Using curl
```bash
curl -X POST http://localhost:5001/detect \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,YOUR_BASE64_STRING",
    "confidence_threshold": 0.3
  }'
```

## Deployment

### Railway.app (Recommended)

1. Push code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select this repository
5. Railway will auto-detect the Dockerfile
6. Add environment variables:
   - `MODEL_PATH=best.pt`
7. Upload `best.pt` to Railway or use external storage

### Other Options
- **Render.com**: Similar to Railway, auto-deploys from Git
- **Heroku**: Use Procfile: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- **AWS EC2**: Run with systemd service
- **Docker**: Use the included Dockerfile

## Troubleshooting

### Model Not Loading
- Check that `best.pt` exists in the `python-backend/` directory
- Verify file is a valid YOLOv8 model
- Check server logs for specific error messages

### CORS Errors
- Make sure your frontend origin is listed in `main.py` under `allow_origins`
- For development: `http://localhost:5173` and `https://localhost:5173`
- For production: Add your Vercel domain

### Port Already in Use
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Or use a different port
uvicorn main:app --reload --port 5002
```

### Import Errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Model Information

Your YOLOv8 model should be fine-tuned for fabric damage detection. The model expects:
- **Input**: RGB images (any size, will be auto-resized)
- **Output**: Bounding boxes with class "damage" (or your custom class name)
- **Confidence threshold**: Default 0.3 (adjustable in request)

## File Structure

```
python-backend/
├── main.py              # FastAPI server
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .env                 # Your local config (not committed)
├── .gitignore           # Ignore patterns
├── Dockerfile           # For Railway/Docker deployment
├── README.md            # This file
├── best.pt              # Your YOLOv8 model (not committed if >100MB)
└── venv/                # Virtual environment (not committed)
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Add your `best.pt` model file
3. ✅ Run the server
4. ✅ Test with Swagger UI
5. ⏭️  Integrate with SvelteKit frontend
6. ⏭️  Deploy to Railway when ready

## Support

For issues or questions:
- Check the main [Memory Mend README](../README.md)
- Review FastAPI docs: https://fastapi.tiangolo.com
- Review Ultralytics YOLOv8 docs: https://docs.ultralytics.com
