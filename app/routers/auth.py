"""LINE Login flow handlers."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import urllib.parse

import requests
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.config import Settings, get_settings

AUTHORIZE_ENDPOINT = "https://access.line.me/oauth2/v2.1/authorize"
TOKEN_ENDPOINT = "https://api.line.me/oauth2/v2.1/token"
PROFILE_ENDPOINT = "https://api.line.me/v2/profile"

router = APIRouter(tags=["line-login"])
logger = logging.getLogger(__name__)


def _assert_login_enabled(settings: Settings) -> None:
    if not (
        settings.line_login_channel_id
        and settings.line_login_channel_secret
        and settings.line_login_redirect_uri
    ):
        raise HTTPException(status_code=503, detail="LINE Login 尚未設定")


def _sign_state(token: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()


@router.get("/login-line")
async def login_line(
    request: Request,
    return_to: str = "/coupons-room",
    settings: Settings = Depends(get_settings),
):
    """Redirect users to LINE Login authorization page."""

    _assert_login_enabled(settings)
    state_token = secrets.token_urlsafe(16)
    encoded_path = urllib.parse.quote(return_to, safe="")
    signature = _sign_state(state_token, settings.line_login_channel_secret)
    combined_state = f"{state_token}|{signature}|{encoded_path}"
    params = {
        "response_type": "code",
        "client_id": settings.line_login_channel_id,
        "redirect_uri": settings.line_login_redirect_uri,
        "state": combined_state,
        "scope": "profile openid",
        "nonce": secrets.token_urlsafe(8),
    }
    authorize_url = f"{AUTHORIZE_ENDPOINT}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(authorize_url, status_code=302)


@router.get("/line-login/callback")
async def line_login_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    settings: Settings = Depends(get_settings),
):
    """Handle LINE Login callback, store LINE user id in cookie, then redirect."""

    _assert_login_enabled(settings)
    redirect_target = "/coupons-room"
    if error:
        raise HTTPException(status_code=400, detail=error_description or error)
    if not code or not state:
        raise HTTPException(status_code=400, detail="LINE Login 參數錯誤")

    decoded_state = urllib.parse.unquote(state)
    state_token, _, remainder = decoded_state.partition("|")
    if not remainder:
        raise HTTPException(status_code=400, detail="LINE Login 驗證失敗 (state 格式錯誤)")
    provided_signature, _, encoded_path = remainder.partition("|")
    expected_signature = _sign_state(state_token, settings.line_login_channel_secret)
    if not hmac.compare_digest(provided_signature, expected_signature):
        logger.warning("LINE Login state signature mismatch")
        raise HTTPException(status_code=400, detail="LINE Login 驗證失敗 (state 不符)")
    if encoded_path:
        redirect_target = urllib.parse.unquote(encoded_path)

    token_payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.line_login_redirect_uri,
        "client_id": settings.line_login_channel_id,
        "client_secret": settings.line_login_channel_secret,
    }
    token_response = requests.post(
        TOKEN_ENDPOINT,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=token_payload,
        timeout=15,
    )
    if not token_response.ok:
        raise HTTPException(status_code=400, detail="LINE Login 交換 token 失敗")
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="LINE Login 缺少 access token")

    profile_response = requests.get(
        PROFILE_ENDPOINT,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    if not profile_response.ok:
        raise HTTPException(status_code=400, detail="LINE Login 取得使用者資訊失敗")
    profile = profile_response.json()
    line_user_id = profile.get("userId")
    if not line_user_id:
        raise HTTPException(status_code=400, detail="LINE Login 缺少 userId")

    response = RedirectResponse(redirect_target, status_code=302)
    response.set_cookie(
        "cony_user_id",
        line_user_id,
        max_age=60 * 60 * 24 * 30,
        httponly=False,
        secure=True,
        samesite="lax",
    )
    return response
