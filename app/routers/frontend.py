"""Frontend routes serving the Cony UI."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
AVATAR_SRC = "/static/assets/cony-avatar.png"
PANEL_SRC = "/static/assets/cony-story.png"

router = APIRouter(tags=["frontend"])


def _render_page(
    request: Request,
    template: str,
    page_id: str,
    title: str,
    extra_context: dict | None = None,
) -> HTMLResponse:
    context = {
        "request": request,
        "title": title,
        "page_id": page_id,
        "avatar_src": AVATAR_SRC,
    }
    if extra_context:
        context.update(extra_context)
    return templates.TemplateResponse(template, context)


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request) -> HTMLResponse:
    """Top-level page explaining available LINE menu actions."""

    return _render_page(request, "index.html", page_id="home", title="Cony Playland")


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request) -> HTMLResponse:
    """Dedicated Cony introduction page."""

    return _render_page(
        request,
        "about.html",
        page_id="about",
        title="About Cony",
        extra_context={"panel_src": PANEL_SRC},
    )


@router.get("/play", response_class=HTMLResponse)
async def play_page(request: Request) -> HTMLResponse:
    """Dedicated Cony game page."""

    return _render_page(request, "play.html", page_id="play", title="Play with Cony")


@router.get("/coupons-room", response_class=HTMLResponse)
async def coupons_page(request: Request) -> HTMLResponse:
    """Dedicated coupon viewing page."""

    return _render_page(request, "coupons.html", page_id="coupons", title="Cony Coupon Room")
