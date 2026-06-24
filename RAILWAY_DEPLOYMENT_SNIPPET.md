Railway deployment checklist
===========================

Quick checklist to deploy the Streamlit attendance app to Railway.

- Ensure your repo is pushed to GitHub (branch: `main`).
- Confirm these files exist in the repo root: `start.sh`, `render.yaml` (optional), `runtime.txt`, `requirements.txt`.
- Confirm `start.sh` is executable and launches Streamlit with `$PORT`:

  ```bash
  PORT=${PORT:-8501}
  exec streamlit run app.py --server.port "$PORT" --server.headless true
  ```

- Railway setup (quick):
  1. Sign in to https://railway.app and create a new project.
  2. Choose "Deploy from GitHub" and connect the repository.
  3. Select branch `main`.
  4. In the service settings, use these commands if Railway doesn't auto-detect:

     - Build Command: `pip install -r requirements.txt`
     - Start Command: `bash start.sh`

- Important notes:
  - Railway provides a `PORT` env var; `start.sh` expands it.
  - `tensorflow==2.20.0` requires Python 3.13; `runtime.txt` requests `python-3.13.12`.
  - Local `data/` and `faces/` are ephemeral in Railway environments. Use S3 or a managed DB for persistence.

- Post-deploy checks:
  - Open the Railway-assigned URL and verify the app loads.
  - Inspect Railway build logs for dependency or startup errors (TensorFlow builds are large).

- Optional improvements:
  - Add a `/health` endpoint or a lightweight Streamlit page that returns OK for health checks.
  - Use Railway variables to set `DEFAULT_ADMIN_PASSWORD` and other secrets.
  - Add a GitHub Action or Railway CLI step to trigger redeploys automatically.

Quick push commands
------------------

```bash
git add RAILWAY_DEPLOYMENT_SNIPPET.md
git commit -m "Add Railway deployment checklist"
git push origin main
```

If you want, I can add a GitHub Action to notify Railway via the CLI or prepare a small health-check route next.
