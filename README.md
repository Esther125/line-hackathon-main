# Cony LINE Hackathon Bot

This project implements a FastAPI backend plus a lightweight pink-themed frontend that connects to the LINE Messaging API and ChatGPT to let users chat with Cony (the LINE FRIENDS bunny), learn about her personality, view game coupons, and play a small guessing game to earn rewards.

## Features
- **LINE Webhook (`/callback`)** – verifies the signature, forwards user text to OpenAI with a Cony persona prompt, and replies automatically.
- **Pink Web App (`GET /`)** – Landing page describing each LINE menu action with quick links.
- **Dedicated Views**
  - `GET /about` – Cony introduction page with chat demo (calls `POST /chat-with-cony`).
  - `GET /play` – guessing mini-game, winning mints new coupons.
  - `GET /coupons-room` – pink coupon gallery for sharing through LINE menus.
- **Frontend APIs**
  - `GET /about-cony` supplies the persona section used in the page.
  - `GET /coupons` lists all unlocked coupons.
  - `POST /chat-with-cony` lets the web UI call the Cony persona directly.
  - `POST /play-with-cony` is the guessing mini-game; winning now mints an extra 9折 coupon in addition to the catalog.
- **Health Check (`GET /health`)** – minimal readiness endpoint for deployments.

## Project Structure
```
app/
├── config.py          # Centralized settings using Pydantic BaseSettings
├── dependencies.py    # FastAPI dependency factories
├── main.py            # FastAPI app entrypoint
├── routers/
│   ├── __init__.py
│   ├── frontend.py    # Serves the pink landing page
│   ├── info.py        # About, coupon, chat, and play endpoints
│   └── line.py        # LINE webhook endpoint
└── services/
    ├── chat_service.py    # Wraps OpenAI calls with Cony's persona
    ├── coupon_service.py  # Manages demo coupons
    └── game_service.py    # Contains mini-game logic and reward handling
static/
├── css/style.css          # Pink LINE FRIENDS styling
└── js/app.js              # Frontend interactions
templates/
├── base.html              # Shared layout + nav links
├── index.html             # Landing page with quick actions
├── about.html             # Cony introduction + chat demo (with persona bullets and image slot)
├── play.html              # Game-only page
└── coupons.html           # Coupon gallery page
static/assets/
├── cony-avatar.png        # Circle avatar shown in hero sections
└── cony-story.png         # Square panel used in the About page
frontend/
├── static/                # CSS/JS/assets served by FastAPI
└── templates/             # Jinja2 templates
data/
└── coupons.json           # Seed coupons for initial insertion into Postgres
prompts/
└── prompt.txt             # Cony persona prompt consumed by chat + LINE webhook
```

## Getting Started
1. Install dependencies:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure environment variables by copying the appropriate template:
   ```bash
   cp .env.dev .env   # local/external DB (Render external host)
   # or
   cp .env.prod .env  # in-cluster/internal DB (Render internal host)
   ```
   `DEFAULT_USER_ID` controls which `app_user.user_id` receives coupons. If you're just demoing,
   leave it as `demo-user`; when integrating with real LINE IDs, set it to the actual user identifier.
3. Run the FastAPI app:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Configure the LINE Messaging API webhook URL to point to your `/callback` endpoint.
5. Visit `http://localhost:8000/` for the landing page, or jump straight to:
   - `http://localhost:8000/about` – Cony introduction + chat demo
   - `http://localhost:8000/play` – mini-game
   - `http://localhost:8000/coupons-room` – coupon gallery
6. APIs remain available directly if you want to integrate elsewhere:
   - `GET /about-cony`
   - `GET /coupons`
   - `POST /chat-with-cony` with `{ "message": "想吃什麼?" }`
   - `POST /play-with-cony` with `{ "player_choice": "carrot" }`

### Docker quick start
```
docker compose up --build
# or plain Docker
docker build -t cony-bot .
docker run --env-file .env -p 8000:8000 cony-bot
```
Remember to set `OPENAI_API_KEY`, `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_CHANNEL_SECRET`, and `DATABASE_URL` in `.env` before building. For Render deployments, use the internal connection string (`postgresql://...@dpg-d4i6f895pdvs739knqp0-a/cony_db`) so traffic stays on the private network. The app expects the PostgreSQL schema described in `/database/models.py` (tables `app_user` and `coupon`).

### Customizing Cony images
- Hero avatar: place `cony-avatar.png` (or update `AVATAR_SRC` in `app/routers/frontend.py`).
- About page panel: place `cony-story.png` (or update `PANEL_SRC`) to fill the square illustration on the persona card.

## Notes
- The chat replies are generated in Traditional Chinese to match the character.
- The coupon and game data is in-memory for demonstration; plug in your data store if needed.
