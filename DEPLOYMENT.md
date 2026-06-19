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

4. Visit `http://localhost:5000`.

### Notes

- The app uses local disks for `faces/`, `attendance_*.csv`, and pickle files. Use mounted volumes on production hosts.
- `video_feed` currently accesses a server-side webcam (`cv2.VideoCapture(0)`). For cloud deployment, this feature will only work if the host has a connected camera.
- If you need browser-based camera capture, the app should be updated to send frames from the client to `/api/camera/frame`.

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
