import json
import os
import platform
import re
import time
from datetime import datetime
from pathlib import Path

import psutil
from flask import Flask, jsonify, render_template, request, send_from_directory
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

app = Flask(__name__, template_folder="templates", static_folder="static")

START_TIME = time.time()
ENV_FILE = Path(__file__).parent.parent / ".env"
BOT_INFO_FILE = Path(__file__).parent.parent / "bot_info.json"


def read_bot_info() -> dict:
    try:
        if BOT_INFO_FILE.exists():
            import json
            return json.loads(BOT_INFO_FILE.read_text())
    except Exception:
        pass
    return {}

SENSITIVE_KEYS = {
    "API_HASH", "BOT_TOKEN", "MONGO_DB_URI",
    "STRING_SESSION", "STRING_SESSION2", "STRING_SESSION3",
    "STRING_SESSION4", "STRING_SESSION5",
    "GIT_TOKEN", "HEROKU_API_KEY", "SPOTIFY_CLIENT_SECRET",
}

ALL_KEYS = [
    {"key": "API_ID",              "label": "API ID",              "hint": "From my.telegram.org/apps",   "section": "identity", "sensitive": False},
    {"key": "API_HASH",            "label": "API Hash",            "hint": "From my.telegram.org/apps",   "section": "identity", "sensitive": True},
    {"key": "BOT_TOKEN",           "label": "Bot Token",           "hint": "From @BotFather",             "section": "identity", "sensitive": True},
    {"key": "MONGO_DB_URI",        "label": "MongoDB URI",         "hint": "From cloud.mongodb.com",      "section": "database", "sensitive": True},
    {"key": "LOGGER_ID",           "label": "Logger Chat ID",      "hint": "Group/channel ID for logs",   "section": "settings", "sensitive": False},
    {"key": "OWNER_ID",            "label": "Owner Telegram ID",   "hint": "Your numeric Telegram ID",    "section": "settings", "sensitive": False},
    {"key": "SUPPORT_CHANNEL",     "label": "Support Channel URL", "hint": "e.g. https://t.me/exucodex", "section": "settings", "sensitive": False},
    {"key": "SUPPORT_CHAT",        "label": "Support Chat URL",    "hint": "e.g. https://t.me/exucodex", "section": "settings", "sensitive": False},
    {"key": "DURATION_LIMIT",      "label": "Duration Limit (min)","hint": "Max song length in minutes", "section": "settings", "sensitive": False},
    {"key": "START_IMG_URL",       "label": "Startup Image URL",   "hint": "Shown on /start command",    "section": "images",   "sensitive": False},
    {"key": "PING_IMG_URL",        "label": "Ping Image URL",      "hint": "Shown on /ping command",     "section": "images",   "sensitive": False},
    {"key": "STRING_SESSION",      "label": "String Session 1",    "hint": "Primary assistant account",  "section": "sessions", "sensitive": True},
    {"key": "STRING_SESSION2",     "label": "String Session 2",    "hint": "Second assistant (optional)","section": "sessions", "sensitive": True},
    {"key": "STRING_SESSION3",     "label": "String Session 3",    "hint": "Third assistant (optional)", "section": "sessions", "sensitive": True},
    {"key": "SPOTIFY_CLIENT_ID",   "label": "Spotify Client ID",   "hint": "developer.spotify.com",      "section": "optional", "sensitive": False},
    {"key": "SPOTIFY_CLIENT_SECRET","label":"Spotify Client Secret","hint":"developer.spotify.com",       "section": "optional", "sensitive": True},
    {"key": "UPSTREAM_REPO",       "label": "Upstream Repo URL",   "hint": "GitHub repo for updates",    "section": "optional", "sensitive": False},
]


# ── .env helpers ───────────────────────────────────────────────────────────
def read_env_file():
    data = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                data[k.strip()] = v.strip()
    return data


SESSION_KEYS = {
    "STRING_SESSION", "STRING_SESSION2", "STRING_SESSION3",
    "STRING_SESSION4", "STRING_SESSION5",
}
SESSION_FILE = Path(__file__).parent.parent / ".sessions.json"


def read_session_store() -> dict:
    try:
        if SESSION_FILE.exists():
            import json
            return json.loads(SESSION_FILE.read_text())
    except Exception:
        pass
    return {}


def write_session_store(updates: dict):
    import json
    store = read_session_store()
    store.update(updates)
    SESSION_FILE.write_text(json.dumps(store))


def write_env_file(updates: dict):
    session_updates = {k: v for k, v in updates.items() if k in SESSION_KEYS}
    other_updates   = {k: v for k, v in updates.items() if k not in SESSION_KEYS}
    if session_updates:
        write_session_store(session_updates)
    if other_updates:
        existing = read_env_file()
        existing.update(other_updates)
        lines = [f"{k}={v}" for k, v in existing.items()]
        ENV_FILE.write_text("\n".join(lines) + "\n")
    for k, v in updates.items():
        os.environ[k] = v


def mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "•" * len(value)
    return value[:4] + "•" * (len(value) - 8) + value[-4:]


def get_uptime():
    seconds = int(time.time() - START_TIME)
    days, r   = divmod(seconds, 86400)
    hours, r  = divmod(r, 3600)
    minutes, s = divmod(r, 60)
    parts = []
    if days:    parts.append(f"{days}d")
    if hours:   parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    parts.append(f"{s}s")
    return " ".join(parts)


# ── Routes ─────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def stats():
    cpu  = psutil.cpu_percent(interval=0.5)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    env  = read_env_file()
    bi   = read_bot_info()
    return jsonify({
        "bot_name":           bi.get("bot_name")     or "EXU Music",
        "bot_username":       bi.get("bot_username")  or "",
        "bot_id":             bi.get("bot_id")        or "",
        "owner_id":           bi.get("owner_id")      or env.get("OWNER_ID", os.getenv("OWNER_ID", "—")),
        "owner_name":         bi.get("owner_name")    or "",
        "owner_username":     bi.get("owner_username") or env.get("OWNER_ID", os.getenv("OWNER_ID", "—")),
        "assistant_name":     bi.get("assistant_name")     or "",
        "assistant_username": bi.get("assistant_username") or "",
        "status":       "online",
        "uptime":       get_uptime(),
        "cpu":          round(cpu, 1),
        "ram_used":     round(ram.used  / (1024**3), 2),
        "ram_total":    round(ram.total / (1024**3), 2),
        "ram_percent":  ram.percent,
        "disk_used":    round(disk.used  / (1024**3), 2),
        "disk_total":   round(disk.total / (1024**3), 2),
        "disk_percent": disk.percent,
        "platform":     platform.system(),
        "python":       platform.python_version(),
        "timestamp":    datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "support":      env.get("SUPPORT_CHANNEL", "https://t.me/exucodex"),
    })


@app.route("/api/env", methods=["GET"])
def get_env():
    env = read_env_file()
    sessions = read_session_store()
    result = []
    for meta in ALL_KEYS:
        k = meta["key"]
        if k in SESSION_KEYS:
            raw = sessions.get(k) or env.get(k, os.getenv(k, ""))
        else:
            raw = env.get(k, os.getenv(k, ""))
        result.append({**meta, "value": mask(raw) if meta["sensitive"] else raw, "is_set": bool(raw)})
    return jsonify(result)


@app.route("/api/env", methods=["POST"])
def post_env():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"ok": False, "message": "Invalid payload"}), 400
    updates, errors = {}, []
    for k, v in data.items():
        v = str(v).strip()
        if not v or set(v) <= {"•"}:
            continue
        if k in ("SUPPORT_CHANNEL", "SUPPORT_CHAT", "START_IMG_URL",
                  "PING_IMG_URL", "UPSTREAM_REPO") and v:
            if not re.match(r"https?://", v):
                errors.append(f"{k} must start with https://")
                continue
        updates[k] = v
    if errors:
        return jsonify({"ok": False, "message": "; ".join(errors)}), 400
    if updates:
        write_env_file(updates)
    return jsonify({"ok": True, "message": f"Saved {len(updates)} value(s). Restart bot to apply."})


@app.route("/api/login/start", methods=["POST"])
def login_start():
    data = request.get_json(silent=True) or {}
    phone = str(data.get("phone", "")).strip()
    if not phone:
        return jsonify({"ok": False, "message": "Phone number is required"}), 400
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    if not api_id or not api_hash:
        return jsonify({"ok": False, "message": "API_ID and API_HASH are required"}), 400

    import asyncio

    async def _send():
        client = Client("session_gen", api_id=int(api_id), api_hash=api_hash, in_memory=True, no_updates=True)
        await client.connect()
        sent = await client.send_code(phone)
        await client.disconnect()
        return sent.phone_code_hash

    phone_code_hash = asyncio.run(_send())
    app.config["LOGIN_PHONE"] = phone
    app.config["LOGIN_HASH"] = phone_code_hash
    return jsonify({"ok": True, "message": "OTP sent. Enter the code now."})


@app.route("/api/login/finish", methods=["POST"])
def login_finish():
    data = request.get_json(silent=True) or {}
    phone = app.config.get("LOGIN_PHONE") or str(data.get("phone", "")).strip()
    phone_code_hash = app.config.get("LOGIN_HASH")
    otp = str(data.get("otp", "")).strip()
    password = str(data.get("password", "")).strip()
    if not phone or not otp:
        return jsonify({"ok": False, "message": "Phone and OTP are required"}), 400
    async def _run():
        client = Client("session_gen", api_id=int(os.getenv("API_ID")), api_hash=os.getenv("API_HASH"), in_memory=True, no_updates=True)
        await client.connect()
        try:
            await client.sign_in(phone, phone_code_hash, otp)
        except SessionPasswordNeeded:
            if not password:
                await client.disconnect()
                return None, "2FA password required"
            await client.check_password(password)
        session = await client.export_session_string()
        await client.disconnect()
        return session, None
    import asyncio
    session, error = asyncio.run(_run())
    if error:
        return jsonify({"ok": False, "message": error}), 400
    write_env_file({"STRING_SESSION": session})
    return jsonify({"ok": True, "message": "Login complete. Session saved."})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "bot": "EXU Music"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
