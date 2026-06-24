Render deployment checklist
==========================

Quick checklist to deploy the Streamlit attendance app to Render.

- Ensure your repo is pushed to GitHub (branch: `main`).
- Confirm these files exist in the repo root: `start.sh`, `render.yaml`, `runtime.txt`, `requirements.txt`.
- Confirm `start.sh` is executable and launches Streamlit with `$PORT`:

  ```bash
  PORT=${PORT:-8501}
  exec streamlit run app.py --server.port "$PORT" --server.headless true
  ```

- Render settings (if not auto-detected):
  - Environment: `Python`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `bash start.sh`

- Important runtime notes:
  - `tensorflow==2.20.0` requires Python 3.13; `runtime.txt` requests `python-3.13.12`.
  - Local `data/` and `faces/` folders are ephemeral on Render. Use external storage (S3 / object storage) for persistence.

- Post-deploy checks:
  - Open the assigned Render URL and verify the UI loads.
  - Check Render service logs for build or startup errors.

- Optional improvements (recommended):
  - Add a small health-check route or a lightweight `/health` page in the app to confirm readiness.
  - Add a GitHub Action or Render webhook to auto-deploy on `main` push.
  - Move `data/` to S3 or a managed DB and update app I/O accordingly.

Quick commands
--------------

Push changes and trigger Render deploy:

```bash
git add .
git commit -m "Add Render deployment checklist"
git push origin main
```

View Render logs (Render UI) or use the Render dashboard to inspect build logs.

If you want, I can add a `/.github/workflows/deploy-to-render.yml` GitHub Action or a simple health-check endpoint next.
