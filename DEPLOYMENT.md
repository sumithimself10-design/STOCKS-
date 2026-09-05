# Deployment guide

Two services deploy separately: the FastAPI backend (Railway or Render) and
the Next.js frontend (Vercel). Postgres and Redis are managed add-ons, not
things you run yourself.

## 0. Unzip and push to GitHub

```bash
unzip fin_ai_pro_v2_backend.zip
cd fin_ai_pro_v2
git init
git add .
git commit -m "Initial backend + frontend scaffold"
```

Create a new empty repo on GitHub (don't initialize it with a README), then:

```bash
git remote add origin https://github.com/<your-username>/finai-pro-india.git
git branch -M main
git push -u origin main
```

The zip contains both `app/` (backend) and `frontend/` (frontend) in one
repo — Railway/Render and Vercel each let you point at a subfolder, so one
repo is fine, you don't need to split it.

## 1. Provision Postgres + Redis

Easiest path: do this inside Railway (step 2) — it can provision both with
one click in the same project. If you'd rather use free-tier specialists
instead: Neon for Postgres, Upstash for Redis. Either way you end up with
a `DATABASE_URL` and a `REDIS_URL` — that's all that matters for the next step.

## 2. Deploy the backend (Railway)

1. Go to railway.app, sign in with GitHub, **New Project → Deploy from GitHub repo** → select your repo.
2. Railway will try to build the whole repo — set the service's **Root Directory** to `/` (backend files live at the repo root) in the service Settings.
3. In the same Railway project, click **+ New → Database → PostgreSQL**, and **+ New → Database → Redis**. Railway auto-injects `DATABASE_URL`-style variables — copy the actual connection string it generates into your backend service's variables as `DATABASE_URL` (make sure it's the `postgresql+asyncpg://` form, Railway's default string usually needs `+asyncpg` added after `postgresql`) and `REDIS_URL`.
4. Under the backend service → **Variables**, add:
   - `DATABASE_URL` (from step 3, with `+asyncpg` in the scheme)
   - `REDIS_URL` (from step 3)
   - `FRONTEND_ORIGIN` — leave as `http://localhost:3000` for now, you'll update it after step 4 gives you the Vercel URL
   - `NEWS_API_KEY` — from newsapi.org (free tier is enough to start)
   - `GEMINI_API_KEY` — if you're using Gemini for anything on the backend
5. Under **Settings → Deploy**, set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Deploy. Once it's live, open the generated `*.up.railway.app` URL + `/health` — you should see `{"status": "ok", ...}`.
7. Seed the stock universe once, using Railway's one-off command runner (Service → the three-dot menu → **Run a command**, or `railway run` via the CLI):
   ```bash
   python -m app.scripts.seed_stocks
   python -m app.scripts.refresh_data
   ```
   `refresh_data` takes a few minutes for 30 tickers (it deliberately paces itself to avoid throttling) — that's expected.

## 3. Deploy the frontend (Vercel)

1. Go to vercel.com, **Add New → Project**, import the same GitHub repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset should auto-detect as Next.js — leave build/output settings default.
4. Under **Environment Variables**, add `NEXT_PUBLIC_API_URL` = your Railway backend URL from step 2.6 (e.g. `https://finai-backend-production.up.railway.app`).
5. Deploy. Vercel gives you a `*.vercel.app` URL.

## 4. Close the loop on CORS

Go back to Railway → backend service → Variables → set `FRONTEND_ORIGIN` to your actual Vercel URL (e.g. `https://finai-pro-india.vercel.app`), then redeploy the backend so the CORS middleware picks it up. Until you do this, the frontend's API calls will be blocked by the browser.

## 5. Schedule ongoing data refresh

`refresh_data.py` needs to run daily (after NSE market close is enough).
On Railway: **+ New → Cron Job** in the same project, pointed at the same
repo/root, with:
- Command: `python -m app.scripts.refresh_data`
- Schedule: `30 11 * * 1-5` (11:30 UTC = 5:00 PM IST, weekdays)

This runs as a separate one-off container, not inside your always-on API
process — keeps the API responsive instead of blocking on a 30-ticker fetch.

## 6. Verify end to end

- Visit the Vercel URL — the screener should list the 30 seeded stocks.
- Click into one — QGLP, technical, and fundamentals cards should populate
  (first load per ticker will be slower since nothing's cached yet).
- Log a trade in the simulator and confirm it shows up with a live return.

## 7. Optional polish

- Custom domain: add it in both the Railway service and the Vercel project settings.
- HTTPS is automatic on both platforms — nothing to configure.
- If Railway's free tier sleeps/limits you, Render is a drop-in alternative for the backend with the same Dockerfile-free deploy flow.
