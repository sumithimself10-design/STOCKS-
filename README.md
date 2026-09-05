# FinAI Pro India — backend

## Structure

```
core/
  config.py         Settings (env-driven), QGLP pillar weights
  auth.py            Shared-secret write protection for the simulator
db/
  database.py        Async SQLAlchemy engine/session
  models.py           Stock, PriceBar, QuarterlyFinancial, PERatioSnapshot,
                       QGLPScoreSnapshot, SimulatedTrade
schemas/schemas.py     Pydantic response/request models
services/
  data_fetcher.py      Only file that talks to yfinance/nsepython — everything
                        external is isolated here so upstream breakage is a
                        one-file fix, not a scattered one
  financial_mapper.py  Maps yfinance's raw column labels into QuarterlyRecord —
                        field names verified against yfinance's own source
                          (camel2title with EBIT/EBITDA/EPS/NI preserved as
                          acronyms), shared by the QGLP router, fundamentals
                          router, and refresh_data.py
    price_repository.py  DB-first reads with live-fetch fallback — routers
                          prefer what refresh_data.py already ingested over
                          hitting yfinance on every request
    cache.py              Redis get/set helpers
  engines/                 Pure business logic — no I/O, unit-testable in isolation
    qglp_engine.py          Quality / Growth / Longevity / Price scoring,
                             including compute_roce() (EBIT / Invested Capital,
                             falling back to EBIT / (Total Assets − Current
                             Liabilities))
    technical_engine.py     200-DMA + volume signal, RSI as secondary context
    fundamentals_engine.py  PE, D/E, interest coverage, quarterly series
  routers/                 FastAPI endpoints — thin, just orchestrate
                           fetcher/DB -> engine -> response
    stocks.py    /api/v1/stocks/search
    qglp.py      /api/v1/qglp/{ticker}
    technical.py /api/v1/technical/{ticker}
    fundamentals.py /api/v1/fundamentals/{ticker}
    simulator.py /api/v1/simulator/trades  (POST is API-key protected)
    news.py      /api/v1/news/{company_name}
  scripts/
    seed_stocks.py    populates the Stock table from data/nse_universe.py
    refresh_data.py   the ingestion pipeline — prices, quarterly financials,
                       and a daily PE snapshot (feeds the Price pillar's
                       5-year median over time), rate-limit-paced
  main.py                  App wiring, CORS, startup table creation
```

## Why this layout

- **Engines never import `yfinance`, `nsepython`, or SQLAlchemy.** They take
  plain dataclasses/DataFrames in, return plain dataclasses out. You can
  `pytest` the QGLP scoring math with fabricated numbers and never touch a
  network call or a database.
- **`data_fetcher.py` is the single point of contact with flaky Indian data
  sources.** When NSE/yfinance changes something, this is the only file
  that needs to change.
- **Routers read from Postgres first, live yfinance second.** Once
  `refresh_data.py` has run for a ticker, page views hit the DB — live
  calls only happen for tickers the cron hasn't reached yet, which keeps
  the app from re-triggering IP throttling under real traffic.
- **The Price pillar's 5-year median PE is now real, not a stand-in.**
  `refresh_data.py` writes one `PERatioSnapshot` row per stock per day it
  runs; `get_pe_median()` reads the accumulated history back. Early on
  (first weeks of running the cron) the median will just reflect whatever
  has accumulated so far — the API surfaces that as a note rather than
  pretending it's a true 5-year figure.

## Running locally

```bash
pip install -r requirements.txt --break-system-packages
cp .env.example .env
# SQLite is the default DATABASE_URL for local dev — no Postgres needed
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive OpenAPI UI.

## UI theme

The frontend uses a dark, glowing green-on-black "digital dashboard" theme —
monospace type, scanline overlay, glowing borders on hover, red only for
bearish signals/errors. All colors live in `frontend/tailwind.config.js`
(`matrix`, `matrixDim`, `matrixFaint`, `bg`, `panel`, `bearish`) so retheming
later is a palette swap, not a rewrite. No external fonts are loaded — the
monospace stack is all system fonts, so it works in restricted build
environments without extra config.

## Known gaps to close before this is fully production-ready

1. ~~yfinance column names were placeholders~~ — **fixed**, verified against
   yfinance's own source, consolidated in `financial_mapper.py`.
2. ~~`roce_pct` wasn't computed~~ — **fixed**, `compute_roce()` in
   `qglp_engine.py`.
3. ~~Price pillar used current PE as a fake "median"~~ — **fixed**,
   `PERatioSnapshot` + `get_pe_median()` accumulate real history via the
   daily cron. Needs the cron to actually run for a while before the
   median is meaningful — that's inherent to the approach, not a bug.
4. ~~Routers hit yfinance live on every request~~ — **fixed** for the
   technical signal (DB-first via `price_repository.py`). QGLP and
   fundamentals still make one live call each for EPS/current-PE (Yahoo's
   `.info` endpoint) — cheap, but could be cached similarly if it becomes
   a bottleneck.
5. ~~No auth on the simulator~~ — **partially fixed**: `POST
   /simulator/trades` now requires an `X-API-Key` header matching
   `SIMULATOR_API_KEY`. This is a shared secret, not per-user auth — fine
   for a personal/capstone deployment, not fine if you open the simulator
   to other people without building real accounts.
6. `promoter_holding_pct` and `dividend_payout_pct` aren't available from
   yfinance at all — need a separate NSE corporate-actions source if you
   want the Quality/Longevity pillars to score them.
7. `refresh_data.py`'s price-date mapping is an approximation of the
   trading calendar, not the real one (see the code comment in
   `_date_range_for`) — worth fixing before trusting exact dates.
