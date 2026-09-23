# AI Clothing Size Assistant

This project measures clothing dimensions such as length, chest, shoulder, waist, and sleeve using image processing and OpenCV.

## Project structure

- `app.py` - original local CLI app
- `web_app.py` - local Flask app for browser testing
- `backend/` - deployable backend API for the measurement service
- `frontend/` - Vercel-ready frontend UI

## Run the backend locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then use the frontend with a configured `API_URL` or set `window.__API_URL__`.

## Run the frontend locally

Open `frontend/index.html` in a browser or serve it with any static server.

## Environment variables

Copy `.env.example` and fill in the required values.

## Deployment idea

- Frontend: deploy on Vercel from the `frontend/` folder
- Backend: deploy on Render, Railway, Fly.io, or another Python service
