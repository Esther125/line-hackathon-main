# Cony LINE Hackathon Bot

FastAPI backend + pink‑themed frontend that lets users chat with Cony, play a guessing game, and manage coupons. Coupons are persisted in PostgreSQL, chat replies come from OpenAI, and LINE Login identifies each user.

## Tech Stack

-   **FastAPI + Uvicorn** – API server and LINE webhook handler
-   **PostgreSQL + SQLAlchemy** – `app_user` / `coupon` tables for catalog & rewarded coupons
-   **OpenAI API** – persona replies driven by `prompts/prompt.txt`
-   **LINE Messaging API** – `/callback` endpoint replies to LINE users
-   **LINE Login** – `/login-line` + `/line-login/callback` issue `cony_user_id` cookie
-   **Frontend** – Jinja templates + vanilla JS in `frontend/static/js/app.js`

## Project Layout

```
app/
├── config.py              # Settings loaded from .env
├── dependencies.py        # DB session + service factories + user resolver
├── main.py                # FastAPI entrypoint (mounts routers/static)
├── routers/
│   ├── auth.py            # LINE Login flow
│   ├── frontend.py        # Web pages
│   ├── info.py            # REST APIs (chat/game/coupons)
│   └── line.py            # LINE Messaging webhook
└── services/
    ├── chat_service.py    # requests -> OpenAI
    ├── coupon_service.py  # Postgres CRUD (seed user, consume coupon)
    └── game_service.py    # Guessing game + reward logic
frontend/
├── templates/             # index/about/play/coupons (Jinja)
└── static/                # css/style.css, js/app.js, assets
prompts/web_prompt.txt     # Casual chat persona (網站)
prompts/line_prompt.txt    # LINE 官方帳號/客服 persona
data/coupons.json          # Optional seed data (manual import)
database/                  # SQLAlchemy models + session helper
```

## Environment Setup

1. Install deps:
    ```bash
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    ```
2. Copy an env template and fill required variables:
    ```bash
    cp .env.example .env
    ```
3. Run:
    ```bash
    uvicorn app.main:app --reload
    ```
4. Configure LINE Messaging API webhook → `https://<domain>/callback`.
5. Configure LINE Login callback → `https://<domain>/line-login/callback`. Hitting `/login-line?return_to=/coupons-room` starts OAuth; on success the LINE `userId` is stored in `cony_user_id` cookie and used for subsequent coupon/game operations.

## Key Endpoints

### Main Pages

-   `GET /` – landing page
-   `GET /about` – intro + chat demo (`POST /chat-with-cony`)
-   `GET /play` – guessing game (`POST /play-with-cony`)
-   `GET /coupons-room` – coupon gallery (shows LINE Login button when anonymous)

### Other Endpoints

-   `GET /coupons` – JSON coupons for current user
-   `POST /use-coupon` – delete coupon by `coupon_code`
-   `GET /login-line`, `GET /line-login/callback` – LINE Login flow
-   `POST /callback` – LINE Messaging webhook
-   `GET /health` – readiness probe

## Docker

```
docker compose up --build
# or
docker build -t cony-bot .
docker run --env-file .env -p 8000:8000 cony-bot
```

`Dockerfile` exposes port 8000 and runs `uvicorn app.main:app`.

## Notes

-   Coupons are stored per user (`DEFAULT_USER_ID` when no login, LINE userId otherwise).
-   `data/coupons.json` is optional seed data; insert it into Postgres manually if you want default catalog coupons.
-   Web chat uses `prompts/web_prompt.txt` (休閒語氣)，LINE webhook uses `prompts/line_prompt.txt`（客服/促銷，辨識 `@客戶服務`、`@促銷活動`）。
-   Chat replies remain in Traditional Chinese; adjust the prompt files if you need different tone.
