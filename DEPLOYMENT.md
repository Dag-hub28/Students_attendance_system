# Deployment Guide

This repository supports Docker deployment and simple cloud hosting.

## Docker Deployment

1. Copy `.env.example` to `.env` and configure values:
   - `SECRET_KEY`
   - `DEFAULT_ADMIN_USERNAME`
   - `DEFAULT_ADMIN_EMAIL`
   - `DEFAULT_ADMIN_PASSWORD`
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `SMTP_SENDER_EMAIL`
   - `SMTP_SENDER_PASSWORD`

2. Start Docker Desktop or the Docker daemon.

3. Build and start the container:

```bash
docker compose up --build -d
```

4. Visit `http://localhost:8501`.

### Notes

- The app uses local disks for `faces/`, `attendance_*.csv`, and pickle files. Use mounted volumes on production hosts.
- `video_feed` currently accesses a server-side webcam (`cv2.VideoCapture(0)`). For cloud deployment, this feature will only work if the host has a connected camera.
- If you need browser-based camera capture, the app should be updated to send frames from the client to `/api/camera/frame`.

## Railway (Quick Deploy)

1. Push your changes to GitHub.
2. Sign in to https://railway.app and create a new project.
3. Choose "Deploy from GitHub" and connect the repository.
4. Set the branch to `main` (or your preferred branch).
5. Set the following commands in Railway service settings:

```
Build Command: pip install -r requirements.txt
Start Command: bash start.sh
```

Railway will provide a `PORT` environment variable; `start.sh` uses it automatically.

## Render (Quick Deploy)

1. Push your changes to GitHub.
2. On Render (https://render.com) create a new Web Service and connect your GitHub repo.
3. Choose `Python` as the environment and set the branch to `main`.
4. Use these commands in the Render service settings:

```
Build Command: pip install -r requirements.txt
Start Command: bash start.sh
```

Render will inject `PORT` automatically into the environment; `start.sh` will expand it.

### Important runtime note

This project uses `tensorflow==2.20.0`, which requires a Python 3.13 runtime (or 3.11/3.12 depending on build). To ensure compatibility, `runtime.txt` has been added to request Python 3.13 on platforms that honour that file (Heroku, some buildpacks).

## Heroku / PaaS

This app includes a `Procfile` for Heroku.

1. Ensure `requirements.txt` lists all required dependencies.
2. Deploy the repo to Heroku.
3. Set environment variables in the Heroku dashboard or CLI.

> Note: Heroku has an ephemeral filesystem, so attendance CSV and face data are not persistent unless you add external storage.

## Windows CMD / PowerShell

Run these commands from the repo root:

```cmd
copy .env.example .env
docker compose up --build -d
```

Or in PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```
