import json
import os
import random
import shutil
import sqlite3
import threading
import time
import base64
import secrets
from typing import Optional
from http import cookies
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, unquote
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import core
import anomaly_effects
import dictionary as effect_dictionary

ROOT = Path(__file__).resolve().parent


def debug_mode_enabled():
    """Read the developer switch without requiring a server restart."""
    try:
        for raw_line in (ROOT / "debug.txt").read_text(encoding="utf-8-sig").splitlines():
            key, separator, value = raw_line.partition("=")
            if separator and key.strip().lower() == "debug":
                return value.strip() == "1"
    except (OSError, UnicodeError):
        pass
    return False


def _configured_path(value, fallback):
    candidate = Path(str(value or fallback)).expanduser()
    return candidate if candidate.is_absolute() else ROOT / candidate


DB_PATH = _configured_path(os.getenv("WEB_GAME_DB_PATH"), ROOT / "WEB_GAME.db")
HOST = os.getenv("HOST", "0.0.0.0")
try:
    PORT = int(os.getenv("PORT", "8080"))
except (TypeError, ValueError):
    PORT = 8080
MAX_LOBBY_PLAYERS = 4
DISCORD_CLIENT_ID = os.getenv("CLIENT_ID", "").strip()
DISCORD_CLIENT_SECRET = os.getenv("CLIENT_SECRET", "").strip()
DISCORD_REDIRECT_URI = os.getenv("REDIRECT_URI", "http://127.0.0.1:8080/auth/discord/callback").strip()
DISCORD_SCOPE = "identify"
SESSION_COOKIE = "weblob_session"
DISCORD_AUTH_URL = "https://discord.com/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_ME_URL = "https://discord.com/api/users/@me"
HTTP_USER_AGENT = os.getenv("HTTP_USER_AGENT", "weblob/1.0").strip() or "weblob/1.0"
TOTAL_GAME_DAYS = 15
DISABLED_ANOMALY_IDS = {4, 13, 33}
DISABLED_ANOMALY_MESSAGE = "Аномалии №4, №13 и №33 сейчас отключены и оставлены только для дальнейшей проработки."
CLASS_DAYS = {
    1: [1, 1, 1, 1, 1],
    2: [1, 1, 1, 2, 2],
    3: [1, 2, 2, 2, (1, 2)],
    4: [2, 2, 2, 2, 2],
    5: [2, 2, 2, 3, 3],
    6: [2, 3, 3, 3, (2, 3)],
    7: [3, 3, 3, 3, 3],
    8: [3, 3, 3, 4, 4],
    9: [3, 4, 4, 4, (3, 4)],
    10: [4, 4, 4, 4, 4],
    11: [4, 4, 4, 4, 5],
    12: [4, 4, 4, 5, (4, 5)],
    13: [4, 4, 4, 5, 5],
    14: [4, 4, 4, 5, 5],
    15: [5, 5, 5, 5, 5],
}

state_lock = threading.RLock()
train_timer_lock = threading.RLock()
# Serialize state-changing HTTP requests. The server is threaded, and without
# this guard a double click can pass the same turn check twice.
gameplay_action_lock = threading.RLock()
runtime_players = {}
runtime_taken_anomalies = set()
moon_eye_game_sessions = {}
emoji_glasses_game_sessions = {}
sea_monster_game_sessions = {}
tenna_game_sessions = {}
po3_sessions = {}
camera_view_states = {}
game_action_log = []
softlock_vote_state = {}
sessions = {}
oauth_states = {}


def _player_display_name(user_id):
    with db_connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(NAME, '') AS NAME FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
    return str(row["NAME"] or f"Игрок {int(user_id)}").strip() if row else f"Игрок {int(user_id)}"


def _append_game_action_log(kind, text, user_id=0):
    entry = {
        "id": int(time.time() * 1000000),
        "kind": str(kind or "event"),
        "user_id": int(user_id or 0),
        "text": str(text or "").strip(),
        "at": time.time(),
    }
    if not entry["text"]:
        return
    with state_lock:
        game_action_log.append(entry)
        del game_action_log[:-10]


def _queue_target_notice(target_id, title, message, source_id=0):
    """Persist a targeted-action notice until the target's next own turn."""
    target_id = int(target_id)
    key = f"TARGET_NOTICES_{target_id}"
    notices = _safe_global_value(key, []) or []
    if not isinstance(notices, list):
        notices = []
    notices.append({
        "id": int(time.time() * 1000000),
        "title": str(title or "Воздействие другого игрока"),
        "message": str(message or ""),
        "source_id": int(source_id or 0),
    })
    core.set_global_value(DB_PATH, key, notices[-10:])


def _target_notice_payload(user_id, core_state=None):
    user_id = int(user_id)
    state = core_state or core.get_game_state(DB_PATH)
    if state.get("status") != "started" or int(state.get("current_turn_user_id") or 0) != user_id:
        return None
    notices = _safe_global_value(f"TARGET_NOTICES_{user_id}", []) or []
    if not isinstance(notices, list) or not notices:
        return None
    notice = notices[0] if isinstance(notices[0], dict) else {}
    return {"pending": True, **notice}


def consume_target_notice(user_id, notice_id):
    user_id = int(user_id)
    key = f"TARGET_NOTICES_{user_id}"
    notices = _safe_global_value(key, []) or []
    if not isinstance(notices, list):
        notices = []
    remaining = [
        notice for notice in notices
        if not isinstance(notice, dict) or int(notice.get("id") or 0) != int(notice_id or 0)
    ]
    core.set_global_value(DB_PATH, key, remaining)
    return {"ok": True, "target_notice": _target_notice_payload(user_id)}


def _log_player_effect(user_id, effect_result, fallback_name="", hint_text=""):
    if not isinstance(effect_result, dict):
        return
    modal = effect_result.get("modal") if isinstance(effect_result.get("modal"), dict) else {}
    effect_name = str(
        effect_result.get("title") or modal.get("intro")
        or effect_result.get("effect_name") or fallback_name or "Неизвестный эффект"
    ).strip()
    effect_text = str(
        modal.get("effect") or effect_result.get("description")
        or effect_result.get("message") or ""
    ).strip()
    technical_markers = (
        "глобальн", "флаг ", "флаг установлен", "установлен в", "runtime",
        "событие зарегистрировано", "event registered", "очередь событий",
    )
    is_hidden_technical = (
        str(effect_result.get("effect_key") or "") == "PisosCurse"
        or (not modal and any(marker in effect_text.casefold() for marker in technical_markers))
    )
    event_type = str(((effect_result.get("event") or {}) if isinstance(effect_result.get("event"), dict) else {}).get("type") or "")
    if event_type == "kill_contract_offer":
        _append_game_action_log(
            "effect",
            f"{_player_display_name(user_id)}: Игрок выбрал кого-то целью для убийства. Если тот не откупится, то не проживет слишком долго.",
            user_id,
        )
        return
    if is_hidden_technical:
        if not str(hint_text or "").strip():
            return
        effect_name = "Эффект подсказки"
        effect_text = str(hint_text).strip()
    if effect_text:
        _append_game_action_log(
            "effect",
            f'{_player_display_name(user_id)} получил эффект ({effect_name}) — "{effect_text}"',
            user_id,
        )


def _default_lobby_messages():
    return [
        {
            "author": "Система",
            "text": "Лобби готово. Выбери артефакт и отмечайся.",
            "timestamp": int(time.time()),
        }
    ]


lobby_state = {
    "created": False,
    "players": [],
    "messages": _default_lobby_messages(),
    "status": "idle",
    "countdown_started_at": None,
    "game_started_at": None,
    "game_assignments": {},
}
runtime_game = {
    "started": False,
    "current_day": 0,
    "total_days": TOTAL_GAME_DAYS,
    "day_started_at": None,
    "winner_id": None,
    "final_player_ids": [],
    "final_results": {"exists": False, "winner_id": None, "winner_name": "", "standings": []},
}


def db_connect():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


def db_connect_write():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=rwc", uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def ensure_web_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        return
    # A new Railway Volume must be initialized from the current web-game
    # database, not from the obsolete GAME.db left from the original bot.
    # WEB_GAME.seed.db is committed as an immutable deployment template;
    # local launches continue to use WEB_GAME.db directly.
    for source in (ROOT / "WEB_GAME.seed.db", ROOT / "WEB_GAME.db"):
        if source.exists() and source.resolve() != DB_PATH.resolve():
            shutil.copy2(str(source), str(DB_PATH))
            return
    raise RuntimeError(f"Не найдена исходная база для создания {DB_PATH}")


def ensure_runtime_tables():
    core.init_core_schema(DB_PATH)
    with db_connect_write() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS LAPLACE67_SNAPSHOT (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                active INTEGER NOT NULL DEFAULT 0,
                armed INTEGER NOT NULL DEFAULT 0,
                owner_user_id INTEGER,
                day_number INTEGER NOT NULL DEFAULT 0,
                loop_count INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT,
                created_at REAL NOT NULL DEFAULT 0
            )
            """
        )
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(PLAYERS)").fetchall()]
        if "AVATAR_URL" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN AVATAR_URL TEXT")
        if "IlvetalPendingStat" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN IlvetalPendingStat TEXT")
        if "IlvetalPendingOld" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN IlvetalPendingOld INTEGER NOT NULL DEFAULT 0")
        if "IlvetalPendingNew" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN IlvetalPendingNew INTEGER NOT NULL DEFAULT 0")
        if "CheapTrickPendingNotice" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN CheapTrickPendingNotice INTEGER NOT NULL DEFAULT 0")
        if "PisosCurseRevealed" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN PisosCurseRevealed INTEGER NOT NULL DEFAULT 0")
        if "FleeIsDeathRevealed" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN FleeIsDeathRevealed INTEGER NOT NULL DEFAULT 0")
        if "FleeIsDeathHidden" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN FleeIsDeathHidden INTEGER NOT NULL DEFAULT 0")
        flee_effect_columns = " OR ".join(f"COALESCE({column}, '') = 'FleeIsDeath'" for column in core.EFFECT_COLUMNS)
        conn.execute(
            f"""
            UPDATE PLAYERS
            SET FleeIsDeathHidden = 1,
                FleeIsDeathRevealed = CASE
                    WHEN EXISTS (
                        SELECT 1 FROM WORK
                        WHERE WORK.user_id = PLAYERS.ID
                          AND WORK.anomaly_id = 6
                          AND COALESCE(WORK.hintcount, 0) > 0
                          AND COALESCE(WORK.hintunlocked, 0) >= COALESCE(WORK.hintcount, 0)
                    ) THEN 1 ELSE 0 END
            WHERE ({flee_effect_columns})
              AND EXISTS (
                  SELECT 1 FROM WORK
                  WHERE WORK.user_id = PLAYERS.ID AND WORK.anomaly_id = 6
              )
            """
        )
        pisos_columns = " OR ".join(f"COALESCE({column}, '') = 'PisosCurse'" for column in core.EFFECT_COLUMNS)
        conn.execute(
            f"""
            UPDATE PLAYERS
            SET PisosCurseRevealed = 1
            WHERE PisosCurseRevealed = 0
              AND ({pisos_columns})
              AND EXISTS (
                  SELECT 1 FROM WORK
                  WHERE WORK.user_id = PLAYERS.ID
                    AND WORK.anomaly_id = 6
                    AND COALESCE(WORK.hintunlocked, 0) >= 3
              )
            """
        )
        anomaly_columns = [row["name"] for row in conn.execute("PRAGMA table_info(ANOMALY)").fetchall()]
        if "MODEL" not in anomaly_columns:
            conn.execute("ALTER TABLE ANOMALY ADD COLUMN MODEL TEXT")
        if "codename" not in anomaly_columns:
            conn.execute("ALTER TABLE ANOMALY ADD COLUMN codename TEXT")
        work_columns = {row["name"] for row in conn.execute("PRAGMA table_info(WORK)").fetchall()}
        if "RewardClaimed" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN RewardClaimed INTEGER NOT NULL DEFAULT 0")
        if "HiddenHintUnlocked" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN HiddenHintUnlocked INTEGER NOT NULL DEFAULT 0")
        if "ResetUsed" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN ResetUsed INTEGER NOT NULL DEFAULT 0")
        if "PendingCompanionOffer" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN PendingCompanionOffer INTEGER NOT NULL DEFAULT 0")
        if "PendingCompanionHint" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN PendingCompanionHint INTEGER NOT NULL DEFAULT 0")
        if "PendingCompanionId" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN PendingCompanionId INTEGER NOT NULL DEFAULT 0")
        if "PendingCompanionEffect" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN PendingCompanionEffect TEXT")
        if "CompanionOfferDeclined" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN CompanionOfferDeclined INTEGER NOT NULL DEFAULT 0")
        if "WorkCount" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN WorkCount INTEGER NOT NULL DEFAULT 0")
        if "BerserkGateFailed" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN BerserkGateFailed INTEGER NOT NULL DEFAULT 0")
        if "SiphPunishment" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN SiphPunishment INTEGER NOT NULL DEFAULT 0")
        if "ChooseBonusDamage" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN ChooseBonusDamage INTEGER NOT NULL DEFAULT 5")
        if "PendingChooseBonus" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN PendingChooseBonus INTEGER NOT NULL DEFAULT 0")
        if "AlastorDealRefusals" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN AlastorDealRefusals INTEGER NOT NULL DEFAULT 0")
        if "AlastorDealAccepted" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN AlastorDealAccepted INTEGER NOT NULL DEFAULT 0")
        if "AlastorDealStarted" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN AlastorDealStarted INTEGER NOT NULL DEFAULT 0")
        if "PredatorVnResolved" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN PredatorVnResolved INTEGER NOT NULL DEFAULT 0")
        if "ContractOfferPending" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN ContractOfferPending INTEGER NOT NULL DEFAULT 0")
        if "StatConversionPending" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN StatConversionPending INTEGER NOT NULL DEFAULT 0")
        if "DeathShieldOfferPending" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN DeathShieldOfferPending INTEGER NOT NULL DEFAULT 0")
        if "AltarOfferingPending" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN AltarOfferingPending INTEGER NOT NULL DEFAULT 0")
        if "DevilDealPending" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN DevilDealPending INTEGER NOT NULL DEFAULT 0")
        if "FreeStatPending" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN FreeStatPending INTEGER NOT NULL DEFAULT 0")
        if "Curse137Pending" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN Curse137Pending INTEGER NOT NULL DEFAULT 0")
        if "Curse137Trigger" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN Curse137Trigger TEXT")
        if "LangustTracking" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN LangustTracking INTEGER NOT NULL DEFAULT 0")
        if "LangustAffection" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN LangustAffection INTEGER NOT NULL DEFAULT 0")
        if "SnapshotHP" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN SnapshotHP INTEGER")
        if "SnapshotMaxHP" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN SnapshotMaxHP INTEGER")
        if "SnapshotSP" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN SnapshotSP INTEGER")
        if "SnapshotMaxSP" not in work_columns:
            conn.execute("ALTER TABLE WORK ADD COLUMN SnapshotMaxSP INTEGER")
        tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if "DISCORD_PROFILES" in tables:
            rows = conn.execute("SELECT USER_ID, AVATAR_URL FROM DISCORD_PROFILES").fetchall()
            for row in rows:
                conn.execute(
                    "UPDATE PLAYERS SET AVATAR_URL = ? WHERE ID = ?",
                    (row["AVATAR_URL"], row["USER_ID"]),
                )
            conn.execute("DROP TABLE DISCORD_PROFILES")
        rows = conn.execute(
            "SELECT ID, TYPE, CLASS_ID, COALESCE(item_id, 0) AS item_id, COALESCE(HINTHIDDEN, '') AS HINTHIDDEN FROM ANOMALY"
        ).fetchall()
        type_map = {1: "NA", 2: "DA", 3: "CO", 4: "AB", 5: "HU"}
        class_map = {1: "Z", 2: "T", 3: "H", 4: "W", 5: "A"}
        for row in rows:
            prefix = "IA" if int(row["item_id"] or 0) > 0 else ("SH" if str(row["HINTHIDDEN"] or "").strip() else "SC")
            codename = f"{prefix}-{type_map.get(int(row['TYPE'] or 0), 'UN')}-{class_map.get(int(row['CLASS_ID'] or 0), 'U')}-{int(row['ID'])}"
            conn.execute("UPDATE ANOMALY SET codename = ? WHERE ID = ?", (codename, int(row["ID"])))
        conn.commit()


def row_to_dict(row):
    return {key: row[key] for key in row.keys()}


def get_arts():
    with db_connect() as conn:
        return [row_to_dict(row) for row in conn.execute("SELECT ID, NAME, DESCRIPTION FROM ARTS ORDER BY ID")]


def get_leaderboard():
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT l.USER_ID, l.NAME, l.CP, p.AVATAR_URL
            FROM LEADERBOARD l
            LEFT JOIN PLAYERS p ON p.ID = l.USER_ID
            WHERE NOT (l.USER_ID BETWEEN 8000000000000000 AND 8999999999999999)
            ORDER BY l.CP DESC, l.USER_ID ASC
            """
        ).fetchall()
    return [row_to_dict(row) for row in rows]


def get_leaderboard_page(page=1, per_page=10):
    entries = get_leaderboard()
    total_count = len(entries)
    page = max(1, page)
    per_page = max(1, per_page)
    start = (page - 1) * per_page
    paged = entries[start:start + per_page]
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    return {
        "entries": paged,
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
        "total_pages": total_pages,
    }


def _is_guest_user(user_id):
    user_id = int(user_id)
    if 8_000_000_000_000_000 <= user_id <= 8_999_999_999_999_999:
        return True
    return any(int(profile.get("id") or 0) == user_id and bool(profile.get("is_guest")) for profile in sessions.values())


def sync_leaderboard_entry(user_id, name=None, cp=None, conn=None):
    if _is_guest_user(user_id):
        return
    own_conn = conn is None
    if own_conn:
        conn = db_connect_write()
    try:
        player_row = conn.execute(
            "SELECT NAME, COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
        resolved_name = name
        resolved_cp = cp
        if player_row:
            if resolved_name is None:
                resolved_name = player_row["NAME"]
            if resolved_cp is None:
                resolved_cp = int(player_row["CP"] or 0)
        if resolved_name is None:
            resolved_name = f"Player-{int(user_id)}"
        if resolved_cp is None:
            resolved_cp = 0

        leaderboard_row = conn.execute(
            "SELECT COALESCE(CP, 0) AS CP FROM LEADERBOARD WHERE USER_ID = ?",
            (int(user_id),),
        ).fetchone()
        if not leaderboard_row:
            conn.execute(
                "INSERT INTO LEADERBOARD (USER_ID, NAME, CP) VALUES (?, ?, ?)",
                (int(user_id), resolved_name, int(resolved_cp)),
            )
        else:
            saved_cp = int(leaderboard_row["CP"] or 0)
            if int(resolved_cp) > saved_cp:
                conn.execute(
                    "UPDATE LEADERBOARD SET NAME = ?, CP = ? WHERE USER_ID = ?",
                    (resolved_name, int(resolved_cp), int(user_id)),
                )
            else:
                conn.execute(
                    "UPDATE LEADERBOARD SET NAME = ? WHERE USER_ID = ?",
                    (resolved_name, int(user_id)),
                )
        if own_conn:
            conn.commit()
    finally:
        if own_conn:
            conn.close()


def ensure_player(user_id=None, username=None, avatar_url=None):
    if user_id is not None and user_id in runtime_players:
        profile = runtime_players[user_id].copy()
        if username:
            profile["name"] = username
        if avatar_url is not None:
            profile["avatar_url"] = avatar_url
        runtime_players[user_id] = profile
        return profile

    with db_connect() as conn:
        cur = conn.cursor()
        if user_id is not None:
            row = cur.execute("SELECT ID, NAME, ART, AVATAR_URL FROM PLAYERS WHERE ID = ?", (user_id,)).fetchone()
            if row:
                profile = {
                    "id": row["ID"],
                    "name": username or row["NAME"],
                    "avatar_url": avatar_url or row["AVATAR_URL"],
                    "art_id": row["ART"] or 0,
                }
                runtime_players[profile["id"]] = profile
                return profile

        existing = cur.execute("SELECT ID, NAME, ART, AVATAR_URL FROM PLAYERS ORDER BY ID LIMIT 1").fetchone()
        if existing and user_id is None and username is None:
            profile = {
                "id": existing["ID"],
                "name": existing["NAME"],
                "avatar_url": avatar_url or existing["AVATAR_URL"],
                "art_id": existing["ART"] or 0,
            }
            runtime_players[profile["id"]] = profile
            return profile

    generated_id = user_id if user_id is not None else int(time.time() * 1000) + random.randint(100, 999)
    profile = {"id": generated_id, "name": username or f"Agent-{str(generated_id)[-4:]}", "avatar_url": avatar_url, "art_id": 0}
    runtime_players[generated_id] = profile
    return profile


def ensure_player_registered(user_id, username=None, avatar_url=None):
    profile = ensure_player(user_id=user_id, username=username, avatar_url=avatar_url)
    with db_connect() as conn:
        existing = conn.execute(
            "SELECT ID FROM PLAYERS WHERE ID = ?",
            (int(profile["id"]),),
        ).fetchone()
    if existing:
        return profile
    try:
        with db_connect_write() as conn:
            conn.execute(
                """
                INSERT INTO PLAYERS
                (ID, NAME, HP, MAXHP, SP, MAXSP, INVSLOT1, SLOT1AMOUNT, INVSLOT2, SLOT2AMOUNT, COMPSLOT, RP, CP, RT, ART, STAT1, STAT2, STAT3, STAT4, PENALTY, KLIPOTA, BONUS, AVATAR_URL)
                VALUES (?, ?, 100, 100, 200, 200, 0, 0, 0, 0, 0, 0, 0, 0, ?, 1, 1, 1, 1, 0, 0, 0, ?)
                """,
                (
                    int(profile["id"]),
                    profile["name"],
                    int(profile.get("art_id") or 0),
                    profile.get("avatar_url"),
                ),
            )
            conn.commit()
    except sqlite3.OperationalError:
        # If another request is touching SQLite right now, avoid crashing the room open.
        pass
    return profile


def update_player_art(player_id, art_id):
    profile = runtime_players.get(player_id)
    if profile:
        profile["art_id"] = art_id
        runtime_players[player_id] = profile
    try:
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE PLAYERS SET ART = ? WHERE ID = ?",
                (int(art_id or 0), int(player_id)),
            )
            conn.commit()
    except sqlite3.OperationalError:
        pass


def get_art_by_id(art_id):
    with db_connect() as conn:
        row = conn.execute("SELECT ID, NAME, DESCRIPTION FROM ARTS WHERE ID = ?", (art_id,)).fetchone()
        return row_to_dict(row) if row else None


def normalize_lobby_player(entry):
    art = get_art_by_id(entry.get("art_id") or 0)
    return {
        "id": entry["id"],
        "name": entry["name"],
        "avatar_url": entry.get("avatar_url"),
        "art_id": entry.get("art_id") or 0,
        "art_name": art["NAME"] if art else "Не выбран",
        "art_description": art["DESCRIPTION"] if art else "Выберите артефакт перед стартом.",
        "ready": bool(entry.get("ready")),
        "agent_character": int(entry.get("agent_character") or 0),
    }


def add_system_message(text):
    lobby_state["messages"].append({"author": "РЎРёСЃС‚РµРјР°", "text": text, "timestamp": int(time.time())})


def _reset_lobby_state():
    with state_lock:
        lobby_state["created"] = False
        lobby_state["players"] = []
        lobby_state["messages"] = _default_lobby_messages()
        lobby_state["status"] = "idle"
        lobby_state["countdown_started_at"] = None
        lobby_state["game_started_at"] = None
        lobby_state["game_assignments"] = {}


def _finalize_finished_game(player_ids):
    _sync_death_action_log(player_ids)
    runtime_game["started"] = False
    runtime_game["day_started_at"] = None
    runtime_game["final_player_ids"] = [int(pid) for pid in (player_ids or [])]
    runtime_game["final_results"] = get_final_results_payload(runtime_game["final_player_ids"])
    _reset_lobby_state()


def reset_runtime_game():
    runtime_game["started"] = False
    runtime_game["current_day"] = 0
    runtime_game["day_started_at"] = None
    runtime_game["winner_id"] = None
    runtime_game["final_player_ids"] = []
    runtime_game["final_results"] = {"exists": False, "winner_id": None, "winner_name": "", "standings": []}
    with db_connect_write() as conn:
        conn.execute(
            """
            UPDATE CORE_GAME_STATE
            SET status = 'idle',
                current_day = 0,
                turn_index = 0,
                current_turn_user_id = NULL,
                turn_order_json = '[]',
                started_at = NULL,
                finished_at = NULL,
                winner_user_id = NULL,
                last_event_at = ?
            WHERE id = 1
            """,
            (time.time(),),
        )
        conn.execute("DELETE FROM CORE_TURN_EVENTS")
        # Глобальный тайник аномалии 135 существует между отдельными играми.
        conn.execute("DELETE FROM GAME_GLOBALS WHERE key <> 'RIFT_STASH_ITEM_ID'")
        conn.commit()


def determine_winner_by_cp(player_ids):
    if not player_ids:
        return None
    placeholders = ",".join("?" for _ in player_ids)
    with db_connect() as conn:
        row = conn.execute(
            f"SELECT ID, COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID IN ({placeholders}) ORDER BY CP DESC, ID ASC LIMIT 1",
            tuple(int(pid) for pid in player_ids),
        ).fetchone()
    return int(row["ID"]) if row else None


def get_final_results_payload(player_ids=None):
    with state_lock:
        lobby_players = [dict(player) for player in lobby_state["players"]]
    if player_ids is None:
        player_ids = [int(player["id"]) for player in lobby_players]
    player_ids = [int(pid) for pid in player_ids]
    if not player_ids:
        return {"exists": False, "winner_id": None, "winner_name": "", "standings": []}
    placeholders = ",".join("?" for _ in player_ids)
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT ID, NAME, COALESCE(CP, 0) AS CP, COALESCE(IsDead, 0) AS IsDead,
                   COALESCE(AVATAR_URL, '') AS AVATAR_URL, COALESCE(DEATHREASON, '') AS DEATHREASON
            FROM PLAYERS
            WHERE ID IN ({placeholders})
            ORDER BY CP DESC, ID ASC
            """,
            tuple(player_ids),
        ).fetchall()
    standings = []
    for row in rows:
        lobby_player = next((player for player in lobby_players if int(player["id"]) == int(row["ID"])), None)
        standings.append(
            {
                "id": int(row["ID"]),
                "name": row["NAME"] or (lobby_player or {}).get("name") or f"Игрок {row['ID']}",
                "cp": int(row["CP"] or 0),
                "is_dead": int(row["IsDead"] or 0) == 1,
                "avatar_url": row["AVATAR_URL"] or (lobby_player or {}).get("avatar_url"),
                "death_reason": _normalize_death_reason(row["DEATHREASON"]),
            }
        )
    winner_id = runtime_game["winner_id"] or (standings[0]["id"] if standings else None)
    winner = next((entry for entry in standings if entry["id"] == winner_id), standings[0] if standings else None)
    return {
        "exists": bool(standings),
        "winner_id": winner_id,
        "winner_name": winner["name"] if winner else "",
        "standings": standings,
    }


def day_classes(day):
    classes = CLASS_DAYS.get(int(day))
    if not classes:
        classes = CLASS_DAYS[TOTAL_GAME_DAYS]
    # Resolve the random fifth slot when the day's pool is generated. This
    # avoids choosing at import and then accidentally randomising it again.
    return [random.choice(value) if isinstance(value, tuple) else int(value) for value in classes]


WORK_TYPES = {
    "intuition": {"label": "Интуиция", "stat": "STAT1"},
    "insight": {"label": "Понимание", "stat": "STAT2"},
    "affection": {"label": "Привязанность", "stat": "STAT3"},
    "suppression": {"label": "Подавление", "stat": "STAT4"},
}

COMPANION_OFFER_EFFECTS = {
    "bulbasaur": 1,
    "ilvetal": 2,
    "kurem": 3,
    "cheaptrick": 4,
    "genesect": 5,
    "hanged_cat": 6,
    "stupidreptile": 7,
    "stonefox": 8,
    "xqc": 9,
    "sprigatito": 10,
    "fairy": 11,
    "shnublik": 12,
    "lil_zema": 13,
    "salamander": 14,
}
# These temporary companions may be replaced by a later offer. Lava Salamander
# (14), including its enhanced form, is permanent once accepted.
COMPANION_REPLACEABLE_SLOTS = {11, 13}
XQC_LINES = [
    "CHAT IS THIS REAL? HE CHOSE THIS???",
    "No shot, NO SHOT. He picks the worst one again, man.",
    "Hello? Mods? This is actually rigged. I can't, bro.",
    "Dude… what is this decision, man? I'm molding.",
    "Chat, my brain is offline, this is TOS of decision-making.",
]

RISK_META = {
    1: {"label": "ZAYIN", "icon": "/photo/work_room/Risk_Zayin.png"},
    2: {"label": "TETH", "icon": "/photo/work_room/Risk_Teth.png"},
    3: {"label": "HE", "icon": "/photo/work_room/Risk_He.png"},
    4: {"label": "WAW", "icon": "/photo/work_room/Risk_Waw.png"},
    5: {"label": "ALEPH", "icon": "/photo/work_room/Risk_Aleph.png"},
}
ANOMALY_TYPE_LABELS = {1: "Природный", 2: "Темный", 3: "Конструкт", 4: "Абстракт", 5: "Гуманоид"}
BLACK_HOLE_ITEM_ID = -1001

DETAIL_RISK_COLORS = {
    1: "#2CD92B",
    2: "#0008FF",
    3: "#F7EB05",
    4: "#7103A1",
    5: "#EB1010",
}

DAMAGE_BY_CLASS = {1: 2, 2: 4, 3: 8, 4: 16, 5: 25}
GOOD_RESULT_MIN = {1: 4, 2: 5, 3: 6, 4: 7, 5: 8}
BASE_RESEARCH_COST = 15
DESCRIPTION_COST = 10
BASE_CP_REWARD = {1: 100, 2: 250, 3: 1000, 4: 2500, 5: 5000}
CURSED_ITEM_IDS = {26, 29, 30, 31, 32, 33, 35}
HEART_ATTACK_DEATH_REASON = "Причина смерти: передозировка анксиолитиком и остановка сердца"
PSYCHOSIS_1008_DEATH_REASON = "Сотрудник не пережил последствия психоза «Мазохизм»"
STAT_UPGRADE_META = {
    "fortitude": {
        "column": "STAT1",
        "label": "Выносливость",
        "icon": "/photo/stats/FortitudeIcon.png",
        "effect": "+50 к максимальному и текущему здоровью",
    },
    "prudence": {
        "column": "STAT2",
        "label": "Удача",
        "icon": "/photo/stats/PrudenceIcon.png",
        "effect": "Двойное количество очков прокачки за аномалию класса, равного уровню атрибута",
    },
    "temperance": {
        "column": "STAT3",
        "label": "Гибкость Ума",
        "icon": "/photo/stats/TemperanceIcon.png",
        "effect": "+5% к шансу удачной работы за уровень",
    },
    "justice": {
        "column": "STAT4",
        "label": "Адаптивность",
        "icon": "/photo/stats/JusticeIcon.png",
        "effect": "+0.5 множитель соревновательных очков при полном исследовании за уровень",
    },
}
DMG_TYPE_LABELS = {1: "RED", 2: "BLACK", 3: "MIXED"}
PSYCHOSIS_EFFECTS = {
    1001: {"name": "Никтофобия", "desc": "Получает +10 урона от темных"},
    1002: {"name": "Биофобия", "desc": "Получает +10 урона от природных"},
    1003: {"name": "Теофобия", "desc": "Получает +10 урона от абстрактных"},
    1004: {"name": "Антропофобия", "desc": "Получает +10 урона от гуманоидов"},
    1005: {"name": "Технофобия", "desc": "Получает +10 урона от конструктов"},
    1006: {"name": "Ничего", "desc": "Абсолютно ничего не произошло"},
    1007: {"name": "Прозрение", "desc": "Единоразово снижает текущий стресс на 50"},
    1008: {"name": "Мазохизм", "desc": "Единоразово получает 20 красного урона"},
    1009: {"name": "Паника", "desc": "Невозможно провести работу на Привязанность"},
    1010: {"name": "Ярость", "desc": "Невозможно провести работу на Понимание"},
}
PSYCHOSIS_PHOBIA_TYPES = {1001: 2, 1002: 1, 1003: 4, 1004: 5, 1005: 3}
BLOCKED_WORK_BY_PSYCHOSIS = {1009: "affection", 1010: "insight"}
SKIBIDI_TEXT_LINES = (
    "СКИБИДИ ЙЕС ЙЕС ЙЕС",
    "СКИБИДИ ВА-БА-ДА, ОП ОП ОП!",
    "СКИБИДИ ДОП ДОП ДОП ДА ДА",
    "СКИБИДИ ВА-ПА-ПА-ПАМ!",
    "YES YES SKIBIDI, БРАТИШКА",
    "СКИБИДИ БУМ-БУМ — ВЫБИРАЙ ЧТО-НИБУДЬ",
    "SKIBIDI TO THE MOON",
)
TEMP_EFFECTS_TO_CLEAN = [
    "FleeIsDeath",
    "BlockedPhoto",
    "BlockedDescription",
    "BlockedHint",
    "LovecraftHotDog",
    "UnderCurse2",
    "UnderCurse3",
]

X125_TOTAL = 12
X125_ACTION_REASONS = {
    "damage": "получения урона",
    "item_gained": "получения предмета",
    "companion_gained": "получения компаньона",
    "day10": "наступления 10-го дня",
    "curse": "получения проклятия",
    "flee": "побега сотрудника",
    "item_used": "использования предмета",
    "psychosis": "получения психоза",
    "stat5": "достижения 5-го уровня характеристики",
    "rabbits": "вызова кроликов",
    "aleph": "полного исследования аномалии ALEPH",
    "death": "смерти игрока",
}

KLIPOTA_LOSS_PERCENT = 25
X125_ATTACK_DURATIONS = (8.25, 8.0, 11.0, 30.0, 12.0, 90.0, 15.0, 17.75, 15.0, 90.0)
X125_ATTACK_GAP = 0.8


def _x125_attack_timeline(elapsed):
    elapsed = max(0.0, float(elapsed or 0))
    cursor = 0.0
    for index, duration in enumerate(X125_ATTACK_DURATIONS, start=1):
        gap = X125_ATTACK_GAP if index < len(X125_ATTACK_DURATIONS) else 0
        if elapsed < cursor + duration + gap:
            return index, max(0.0, elapsed - cursor), elapsed < cursor + duration
        cursor += duration + gap
    return len(X125_ATTACK_DURATIONS), X125_ATTACK_DURATIONS[-1], False


X125_BATTLE_TOTAL_SECONDS = sum(X125_ATTACK_DURATIONS) + X125_ATTACK_GAP * max(0, len(X125_ATTACK_DURATIONS) - 1)


def _x125_mark_unlocked(action_key, reason=None):
    action_key = str(action_key or "").strip()
    if action_key not in X125_ACTION_REASONS:
        return None
    if int(_safe_global_value("X125_ACTIVE", 0) or 0) != 1:
        return None
    raw_done = str(_safe_global_value("X125_DONE", "") or "")
    done = {value for value in raw_done.split(",") if value}
    if action_key in done:
        return None
    done.add(action_key)
    remaining = max(0, X125_TOTAL - len(done))
    event_id = int(_safe_global_value("X125_EVENT_ID", 0) or 0) + 1
    run_token = int(_safe_global_value("X125_RUN_TOKEN", 0) or 0)
    if run_token <= 0:
        run_token = int(time.time() * 1000)
        core.set_global_value(DB_PATH, "X125_RUN_TOKEN", run_token)
    reason_text = str(reason or X125_ACTION_REASONS[action_key])
    event = {
        "id": event_id,
        "run_id": int(_safe_global_value("X125_RUN_ID", 1) or 1),
        "run_token": run_token,
        "action": action_key,
        "remaining": remaining,
        "reason": reason_text,
        "text": f"Счетчик аномалии Х-125 достиг значения {remaining} из-за {reason_text}.",
        "at": time.time(),
    }
    events = _safe_global_value("X125_EVENTS", [])
    if not isinstance(events, list):
        events = []
    events = (events + [event])[-X125_TOTAL:]
    core.set_global_value(DB_PATH, "X125_DONE", ",".join(sorted(done)))
    core.set_global_value(DB_PATH, "X125_EVENT_ID", event_id)
    core.set_global_value(DB_PATH, "X125_EVENTS", events)
    if remaining <= 0:
        core.set_global_value(DB_PATH, "X125_EVENT_FIRED", 1)
        current_day = max(1, int(_current_day_number() or 1))
        core.set_global_value(DB_PATH, "X125_SPECIAL_EVENT_DAY", current_day + 1)
        core.set_global_value(DB_PATH, "X125_SPECIAL_EVENT_ID", run_token)
    return event


def _x125_mark(action_key, reason=None):
    with state_lock:
        return _x125_mark_unlocked(action_key, reason)


def _x125_events_payload():
    if int(_safe_global_value("X125_ACTIVE", 0) or 0) != 1:
        return []
    events = _safe_global_value("X125_EVENTS", [])
    return events if isinstance(events, list) else []


def _x125_special_event_payload():
    if int(_safe_global_value("X125_EVENT_FIRED", 0) or 0) != 1:
        return None
    target_day = int(_safe_global_value("X125_SPECIAL_EVENT_DAY", 0) or 0)
    current_day = int(_current_day_number() or 0)
    if target_day <= 0 or current_day < target_day:
        return None
    battle = _ensure_x125_battle()
    player_name = "Сотрудник"
    if battle and int(battle.get("owner_id") or 0) > 0:
        with db_connect_write() as conn:
            player_row = conn.execute(
                "SELECT COALESCE(NAME, '') AS NAME FROM PLAYERS WHERE ID = ?",
                (int(battle["owner_id"]),),
            ).fetchone()
        if player_row and str(player_row["NAME"] or "").strip():
            player_name = str(player_row["NAME"]).strip()
    return {
        "id": int(_safe_global_value("X125_SPECIAL_EVENT_ID", 0) or 0),
        "day": current_day,
        "title": "Х-125",
        "text": "Особое событие Х-125 сработало. Здесь позднее появится полноценная сцена события.",
        "player_name": player_name,
        "battle": battle,
    }


def _ensure_x125_battle():
    battle = _safe_global_value("X125_BATTLE", {})
    if isinstance(battle, dict) and battle.get("status") in {"active", "completed", "dead", "owner_dead_intro", "owner_dead_done"}:
        return battle
    owner_id = int(_safe_global_value("X125_OWNER_ID", 0) or 0)
    if owner_id <= 0:
        return None
    with db_connect_write() as conn:
        row = conn.execute(
            "SELECT COALESCE(HP, 0) AS HP, COALESCE(MAXHP, 100) AS MAXHP, COALESCE(IsDead, 0) AS IsDead, COALESCE(NAME, 'Сотрудник') AS NAME FROM PLAYERS WHERE ID = ?",
            (owner_id,),
        ).fetchone()
        if row and int(row["IsDead"] or 0) == 1:
            battle = {
                "id": int(_safe_global_value("X125_SPECIAL_EVENT_ID", 0) or 0),
                "owner_id": owner_id,
                "owner_name": str(row["NAME"] or "Сотрудник"),
                "status": "owner_dead_intro",
                "updated_at": time.time(),
            }
            core.set_global_value(DB_PATH, "X125_BATTLE", battle)
            return battle
        if row:
            restored_hp = max(1, int(row["MAXHP"] or 100))
            conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (restored_hp, owner_id))
            conn.commit()
    if not row:
        return None
    battle = {
        "id": int(_safe_global_value("X125_SPECIAL_EVENT_ID", 0) or 0),
        "owner_id": owner_id,
        "status": "active",
        # The client first plays Eram's introduction.  The owner resets attack 1
        # when that scene ends; this future value keeps observers from skipping
        # ahead while the introduction is still on screen.
        "started_at": time.time() + 30.0,
        "x": 0.5,
        "y": 0.5,
        "facing": "up",
        "shots": [],
        "destroyed": [],
        "destroyed_at": {},
        "destroyed_attack": 1,
        "hp": restored_hp,
        "max_hp": max(1, int(row["MAXHP"] or 100)),
        "attack": 1,
        "updated_at": time.time(),
    }
    core.set_global_value(DB_PATH, "X125_BATTLE", battle)
    return battle


def finish_x125_dead_owner_event():
    battle = _safe_global_value("X125_BATTLE", {})
    if not isinstance(battle, dict) or battle.get("status") not in {"owner_dead_intro", "owner_dead_done"}:
        raise ValueError("Особый монолог Х-125 сейчас не активен.")
    if battle.get("status") != "owner_dead_done":
        state = core.get_game_state(DB_PATH)
        player_ids = [int(pid) for pid in state.get("turn_order", [])]
        for player_id in player_ids:
            if not _is_player_dead(player_id):
                core.set_player_dead(DB_PATH, player_id, reason="Эрам развлёкся в комплексе после пробуждения")
        battle["status"] = "owner_dead_done"
        battle["completed_at"] = time.time()
        core.set_global_value(DB_PATH, "X125_BATTLE", battle)
        finished_state = core.finish_game(DB_PATH, winner_user_id=None, reason="x125_owner_dead")
        runtime_game["started"] = False
        runtime_game["current_day"] = int(finished_state.get("current_day") or runtime_game.get("current_day") or 0)
        _sync_death_action_log(player_ids)
        _finalize_finished_game(player_ids)
    return {"ok": True, "battle": battle, "game_state": get_game_state(0), "final_results": runtime_game.get("final_results")}


def update_x125_battle(user_id, state):
    with state_lock:
        battle = _ensure_x125_battle()
        if not battle or int(battle.get("owner_id") or 0) != int(user_id):
            raise ValueError("Управлять этим боем может только владелец Х-125.")
        if battle.get("status") != "active":
            return {"ok": True, "battle": battle}
        state = state if isinstance(state, dict) else {}
        restart_attack = int(state.get("restart_attack") or 0)
        if restart_attack in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}:
            offset = 0.0
            for index, duration in enumerate(X125_ATTACK_DURATIONS, start=1):
                if index >= restart_attack:
                    break
                offset += duration + X125_ATTACK_GAP
            battle["status"] = "active"
            battle["started_at"] = time.time() + 0.35 - offset
            battle["attack"] = restart_attack
            battle["shots"] = []
            battle["destroyed"] = []
            battle["destroyed_at"] = {}
            battle["destroyed_attack"] = restart_attack
            battle["updated_at"] = time.time()
            core.set_global_value(DB_PATH, "X125_BATTLE", battle)
            return {"ok": True, "battle": battle}
        for key in ("x", "y"):
            if key in state:
                battle[key] = max(0.0, min(1.0, float(state[key])))
        if str(state.get("facing") or "") in {"up", "down", "left", "right"}:
            battle["facing"] = str(state["facing"])
        elapsed = max(0.0, time.time() - float(battle.get("started_at") or time.time()))
        battle["attack"], _, _ = _x125_attack_timeline(elapsed)
        shots = state.get("shots")
        if isinstance(shots, list):
            sanitized = []
            for shot in shots[-24:]:
                if not isinstance(shot, dict):
                    continue
                try:
                    sanitized.append({
                        # Yellow-soul projectiles are allowed to leave the local arena
                        # and continue through the full 640x480 battle screen.
                        "x": max(-4.0, min(4.0, float(shot.get("x", 0)))),
                        "y": max(-4.0, min(4.0, float(shot.get("y", 0)))),
                        "vx": max(-600.0, min(600.0, float(shot.get("vx", 0)))),
                        "vy": max(-600.0, min(600.0, float(shot.get("vy", 0)))),
                    })
                except (TypeError, ValueError):
                    continue
            battle["shots"] = sanitized
        destroyed = state.get("destroyed")
        if isinstance(destroyed, list):
            sanitized_destroyed = []
            for hazard_id in destroyed[-256:]:
                hazard_id = str(hazard_id or "")[:96]
                if hazard_id and hazard_id not in sanitized_destroyed:
                    sanitized_destroyed.append(hazard_id)
            battle["destroyed"] = sanitized_destroyed
            destroyed_at = state.get("destroyed_at")
            sanitized_destroyed_at = {}
            if isinstance(destroyed_at, dict):
                for hazard_id in sanitized_destroyed:
                    try:
                        sanitized_destroyed_at[hazard_id] = max(0.0, min(180.0, float(destroyed_at.get(hazard_id, 0))))
                    except (TypeError, ValueError):
                        continue
            battle["destroyed_at"] = sanitized_destroyed_at
            try:
                reported_attack = int(state.get("attack") or battle.get("attack") or 1)
            except (TypeError, ValueError):
                reported_attack = int(battle.get("attack") or 1)
            battle["destroyed_attack"] = max(1, min(10, reported_attack))
        battle["updated_at"] = time.time()
        early_final_clear = bool(state.get("complete_early")) and int(battle.get("attack") or 0) in {6, 10}
        if bool(state.get("completed")) and (elapsed >= X125_BATTLE_TOTAL_SECONDS - 1.0 or early_final_clear):
            battle["status"] = "completed"
            battle["completed_at"] = time.time()
            if not battle.get("reward_granted"):
                with db_connect_write() as conn:
                    reward_row = conn.execute(
                        "SELECT COALESCE(STAT4, 1) AS STAT4 FROM PLAYERS WHERE ID = ?",
                        (int(user_id),),
                    ).fetchone()
                    stat4 = int(reward_row["STAT4"] or 1) if reward_row else 1
                    reward_cp = int(5000 * _get_stat4_multiplier(stat4))
                    conn.execute(
                        "UPDATE PLAYERS SET CP = COALESCE(CP, 0) + ? WHERE ID = ?",
                        (reward_cp, int(user_id)),
                    )
                    conn.commit()
                battle["reward_cp"] = reward_cp
                battle["reward_granted"] = True
        core.set_global_value(DB_PATH, "X125_BATTLE", battle)
        return {"ok": True, "battle": battle}


def damage_x125_battle(user_id, amount=7):
    with state_lock:
        battle = _ensure_x125_battle()
        if not battle or int(battle.get("owner_id") or 0) != int(user_id):
            raise ValueError("Урон боя относится к другому игроку.")
        if battle.get("status") != "active":
            return {"ok": True, "battle": battle}
        now = time.time()
        if now - float(battle.get("last_hit_at") or 0) < 0.75:
            return {"ok": True, "battle": battle, "ignored": True}
        battle["last_hit_at"] = now
        with db_connect_write() as conn:
            player_row = conn.execute(
                "SELECT COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?",
                (int(user_id),),
            ).fetchone()
            current_hp = int(player_row["HP"] or 0) if player_row else 0
            hit_amount = max(1, int(amount))
            # During X-125 a lethal hit first invokes mercy and leaves 1 HP.
            # Once the player is already at 1 HP, the next hit is genuinely fatal.
            if current_hp > 1 and current_hp - hit_amount <= 0:
                conn.execute("UPDATE PLAYERS SET HP = 1 WHERE ID = ?", (int(user_id),))
                conn.commit()
                damage = {"hp": 1, "is_dead": False, "hp_damage": current_hp - 1}
            else:
                damage = None
        if damage is None:
            damage = core.apply_damage(DB_PATH, int(user_id), hp_damage=hit_amount, reason="Погиб во время события Х-125")
        battle["hp"] = int((damage or {}).get("hp", battle.get("hp") or 0))
        if bool((damage or {}).get("is_dead")):
            battle["status"] = "dead"
            battle["completed_at"] = time.time()
        battle["updated_at"] = time.time()
        core.set_global_value(DB_PATH, "X125_BATTLE", battle)
    payload = {"ok": True, "battle": battle, "damage": damage}
    if battle.get("status") == "dead":
        payload["game_state"] = _advance_after_nonwork_death(int(user_id), "x125_battle_death")
    return payload


def _klipota_event_payload(user_id):
    events = _safe_global_value("KLIPOTA_EVENTS", [])
    if not isinstance(events, list):
        return None
    for event in reversed(events):
        if int(event.get("user_id") or 0) == int(user_id):
            return event
    return None


def _apply_klipota_on_anomaly_taken(user_id, anomaly_id):
    """Apply the original bot's Qliphoth counter when an anomaly is taken."""
    with state_lock:
        current_day = max(1, int(_current_day_number() or 1))
        applied_key = f"KlipotaApplied_{current_day}_{int(user_id)}_{int(anomaly_id)}"
        if int(_safe_global_value(applied_key, 0) or 0) == 1:
            return None
        with db_connect_write() as conn:
            anomaly = conn.execute(
                "SELECT COALESCE(KLIPOTA, 0) AS KLIPOTA FROM ANOMALY WHERE ID = ?",
                (int(anomaly_id),),
            ).fetchone()
            player = conn.execute(
                "SELECT COALESCE(KLIPOTA, 0) AS KLIPOTA, COALESCE(CP, 0) AS CP, "
                "COALESCE(ART, 0) AS ART FROM PLAYERS WHERE ID = ?",
                (int(user_id),),
            ).fetchone()
            if not anomaly or not player:
                return None
            added = max(0, int(anomaly["KLIPOTA"] or 0))
            current = max(0, int(player["KLIPOTA"] or 0))
            threshold = 13 if int(player["ART"] or 0) == 4 else 10
            total = current + added
            if total < threshold:
                conn.execute("UPDATE PLAYERS SET KLIPOTA = ? WHERE ID = ?", (total, int(user_id)))
                conn.commit()
                core.set_global_value(DB_PATH, applied_key, 1)
                return None

            cp_before = max(0, int(player["CP"] or 0))
            lost_cp = int(cp_before * KLIPOTA_LOSS_PERCENT / 100)
            cp_after = max(0, cp_before - lost_cp)
            conn.execute(
                "UPDATE PLAYERS SET KLIPOTA = 0, CP = ? WHERE ID = ?",
                (cp_after, int(user_id)),
            )
            conn.commit()

        core.set_global_value(DB_PATH, applied_key, 1)

        event_id = int(_safe_global_value("KLIPOTA_EVENT_ID", 0) or 0) + 1
        event = {
            "id": event_id,
            "user_id": int(user_id),
            "anomaly_id": int(anomaly_id),
            "percent": KLIPOTA_LOSS_PERCENT,
            "lost_cp": lost_cp,
            "cp_after": cp_after,
            "text": (
                "Перегрев клипота\n"
                f"Для устранения перегрева клипота была привлечена команда кроликов. "
                f"За их услуги было снято {KLIPOTA_LOSS_PERCENT}% СО, "
                f"Текущий остаток СО - {cp_after}."
            ),
            "at": time.time(),
        }
        events = _safe_global_value("KLIPOTA_EVENTS", [])
        if not isinstance(events, list):
            events = []
        core.set_global_value(DB_PATH, "KLIPOTA_EVENT_ID", event_id)
        core.set_global_value(DB_PATH, "KLIPOTA_EVENTS", (events + [event])[-20:])
        _x125_mark_unlocked("rabbits")
        return event


def _x125_mark_effect_result(effect_result, anomaly_id=0, effect_name=""):
    if not isinstance(effect_result, dict):
        return
    nested_results = effect_result.get("effects")
    if isinstance(nested_results, list):
        for nested in nested_results:
            _x125_mark_effect_result(nested, anomaly_id, effect_name)
    if int(effect_result.get("item_id") or 0) > 1 and int(effect_result.get("amount") or 0) > 0:
        _x125_mark("item_gained")
    if int(effect_result.get("companion_id") or 0) > 0:
        _x125_mark("companion_gained")
    if str(effect_result.get("effect_kind") or "") == "curse":
        _x125_mark("curse")
    if int(anomaly_id or 0) == 70 and str(effect_name or "") == "memetic_rabbit_scene":
        _x125_mark("rabbits")


def _skibidi_text(*seed_parts):
    seed = ":".join(str(part) for part in seed_parts)
    return random.Random(seed).choice(SKIBIDI_TEXT_LINES)


def _brainrot_music_payload(user_id):
    user_id = int(user_id)
    day = max(1, int(_current_day_number() or 1))
    if not _player_has_effect(user_id, "skibidi"):
        return {"active": False, "day": day, "tracks": []}
    activated_day = int(_safe_global_value(f"SkibidiActivatedDay_{user_id}", 0) or 0)
    if activated_day <= 0:
        core.set_global_value(DB_PATH, f"SkibidiActivatedDay_{user_id}", day)
        return {"active": False, "day": day, "tracks": []}
    if day <= activated_day:
        return {"active": False, "day": day, "tracks": []}
    key = f"BrainrotMusic_{user_id}_{day}"
    stored = _safe_global_value(key, None)
    if stored is None:
        stored = 1 if random.randint(1, 100) <= 25 else 0
        core.set_global_value(DB_PATH, key, stored)
    tracks = []
    folder = ROOT / "sound" / "brainrot"
    if folder.exists():
        tracks = [f"/sound/brainrot/{path.name}" for path in sorted(folder.iterdir()) if path.suffix.lower() in (".mp3", ".wav", ".ogg", ".m4a")]
    return {"active": int(stored or 0) == 1 and bool(tracks), "day": day, "tracks": tracks}


def _anomaly105_work_chances(user_id, create=False, reroll=False):
    key = f"A105WorkChances_{int(user_id)}"
    work_types = ("intuition", "insight", "affection", "suppression")
    allowed = sorted((25, 50, 65, 80))
    stored = _safe_global_value(key, {})
    valid = (
        isinstance(stored, dict)
        and set(stored.keys()) == set(work_types)
        and sorted(int(value) for value in stored.values()) == allowed
    )
    if valid and not reroll:
        return {work: int(stored[work]) for work in work_types}
    if not create and not reroll:
        return {}
    previous = {work: int(stored[work]) for work in work_types} if valid else None
    values = list(allowed)
    for _ in range(12):
        random.shuffle(values)
        result = dict(zip(work_types, values))
        if result != previous:
            break
    core.set_global_value(DB_PATH, key, result)
    return result


def _room_model_url(model_ref):
    fallback = "/photo/work_room/404.png"
    if not model_ref:
        return fallback
    model_ref = str(model_ref).strip().replace("\\", "/")
    if not model_ref:
        return fallback
    path = ROOT / "photo" / "models" / model_ref
    if path.exists():
        return f"/photo/models/{model_ref}"
    if "." not in model_ref:
        png_path = ROOT / "photo" / "models" / f"{model_ref}.png"
        if png_path.exists():
            return f"/photo/models/{model_ref}.png"
    return fallback


def _room_model_for_anomaly(anomaly_id):
    """Resolve a containment-room model by anomaly id and its size folder."""
    anomaly_id = int(anomaly_id or 0)
    stems = (f"{anomaly_id:03d}", str(anomaly_id))
    for size in ("tiny", "small", "normal", "large"):
        folder = ROOT / "photo" / "models" / size
        for stem in stems:
            for extension in (".png", ".webp", ".jpg", ".jpeg"):
                path = folder / f"{stem}{extension}"
                if path.exists():
                    return {
                        "url": f"/photo/models/{size}/{path.name}",
                        "size": size,
                        "placeholder": False,
                    }
    return {"url": "/photo/work_room/404.png", "size": "placeholder", "placeholder": True}


def _get_companion_debug(companion_id, player_id=None):
    companion_id = int(companion_id or 0)
    if companion_id <= 0:
        return None
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(ID, 0) AS ID,
                   COALESCE(NAME, '') AS NAME,
                   COALESCE(DESC, '') AS DESC,
                   COALESCE(DESCFULL, '') AS DESCFULL,
                   COALESCE(DAYS, 0) AS DAYS
            FROM COMPANIONS
            WHERE ID = ?
            """,
            (companion_id,),
        ).fetchone()
    if not row:
        return {"id": companion_id, "name": f"Компаньон {companion_id}", "description": "Описание компаньона пока не найдено."}
    short_desc = str(row["DESC"] or "").strip()
    full_desc = str(row["DESCFULL"] or "").strip()
    days = int(row["DAYS"] or 0)
    description = full_desc if days >= 3 and (full_desc or short_desc) else (short_desc or "—")
    result = {
        "id": int(row["ID"] or companion_id),
        "name": str(row["NAME"] or f"Компаньон {companion_id}"),
        "description": description,
        "days": days,
    }
    if companion_id == 11 and player_id is not None:
        with db_connect() as conn:
            player_row = conn.execute(
                f"SELECT {', '.join(core.EFFECT_COLUMNS)} FROM PLAYERS WHERE ID = ?",
                (int(player_id),),
            ).fetchone()
        if player_row:
            for column in core.EFFECT_COLUMNS:
                raw = str(player_row[column] or "").strip()
                if _effect_base_key(raw).lower() != core.COMP11_TOK.lower():
                    continue
                try:
                    result["hp"] = max(0, int(raw.split("=", 1)[1]))
                except (IndexError, TypeError, ValueError):
                    pass
                break
    return result


ILVETAL_STAT_LABELS = {
    "STAT1": "Выносливость",
    "STAT2": "Удача",
    "STAT3": "Гибкость Ума",
    "STAT4": "Адаптивность",
}


def _get_ilvetal_notice(user_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(NAME, 'Сотрудник') AS NAME,
                   COALESCE(IlvetalPendingStat, '') AS IlvetalPendingStat,
                   COALESCE(IlvetalPendingOld, 0) AS IlvetalPendingOld,
                   COALESCE(IlvetalPendingNew, 0) AS IlvetalPendingNew
            FROM PLAYERS
            WHERE ID = ?
            """,
            (int(user_id),),
        ).fetchone()
    if not row:
        return {"pending": False}
    stat_key = str(row["IlvetalPendingStat"] or "").strip().upper()
    if not stat_key:
        return {"pending": False}
    old_value = int(row["IlvetalPendingOld"] or 0)
    new_value = int(row["IlvetalPendingNew"] or 0)
    player_name = str(row["NAME"] or "Сотрудник").strip() or "Сотрудник"
    stat_label = ILVETAL_STAT_LABELS.get(stat_key, stat_key)
    return {
        "pending": True,
        "stat_key": stat_key,
        "stat_label": stat_label,
        "old_value": old_value,
        "new_value": new_value,
        "player_name": player_name,
        "modal": {
            "intro": "Эффект компаньона",
            "effect": (
                f"Сотрудник \"{player_name}\" потерял часть своих характеристик "
                f"(атрибут {stat_label} был снижен с {old_value} до {new_value}) из-за эффекта аномалии."
            ),
            "icon": "/photo/work_room/badresult.png",
            "iconAlt": "Эффект компаньона",
        },
    }


def _get_cheaptrick_notice(user_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(CheapTrickPendingNotice, 0) AS CheapTrickPendingNotice
            FROM PLAYERS
            WHERE ID = ?
            """,
            (int(user_id),),
        ).fetchone()
    pending = bool(row and int(row["CheapTrickPendingNotice"] or 0) == 1)
    return {
        "pending": pending,
        "modal": {
            "intro": "Поздравляем!",
            "effect": "Вы стали новым владельцем компаньона Чиптрик!",
            "icon": "/photo/work_room/badresult.png",
            "iconAlt": "Чиптрик",
        },
    } if pending else {"pending": False}


def _clear_ilvetal_notice(user_id):
    with db_connect_write() as conn:
        conn.execute(
            """
            UPDATE PLAYERS
            SET IlvetalPendingStat = NULL,
                IlvetalPendingOld = 0,
                IlvetalPendingNew = 0
            WHERE ID = ?
            """,
            (int(user_id),),
        )
        conn.commit()
def _clear_cheaptrick_notice(user_id):
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE PLAYERS SET CheapTrickPendingNotice = 0 WHERE ID = ?",
            (int(user_id),),
        )
        conn.commit()


def _work_progress(user_id, anomaly_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(photounlocked, 0) AS photounlocked,
                   COALESCE(descriptionunlocked, 0) AS descriptionunlocked,
                   COALESCE(hintunlocked, 0) AS hintunlocked,
                   COALESCE(hintcount, 0) AS hintcount,
                   COALESCE(IsCompleted, 0) AS IsCompleted,
                   COALESCE(RewardClaimed, 0) AS RewardClaimed,
                   COALESCE(HiddenHintUnlocked, 0) AS HiddenHintUnlocked,
                   COALESCE(ResetUsed, 0) AS ResetUsed,
                   COALESCE(PendingCompanionOffer, 0) AS PendingCompanionOffer,
                   COALESCE(PendingCompanionHint, 0) AS PendingCompanionHint,
                   COALESCE(PendingCompanionId, 0) AS PendingCompanionId,
                   COALESCE(PendingCompanionEffect, '') AS PendingCompanionEffect,
                   COALESCE(CompanionOfferDeclined, 0) AS CompanionOfferDeclined,
                   COALESCE(WorkCount, 0) AS WorkCount,
                   COALESCE(BerserkGateFailed, 0) AS BerserkGateFailed,
                   COALESCE(SiphPunishment, 0) AS SiphPunishment,
                   COALESCE(ChooseBonusDamage, 5) AS ChooseBonusDamage,
                   COALESCE(PendingChooseBonus, 0) AS PendingChooseBonus,
                   COALESCE(AlastorDealRefusals, 0) AS AlastorDealRefusals,
                   COALESCE(AlastorDealAccepted, 0) AS AlastorDealAccepted,
                   COALESCE(AlastorDealStarted, 0) AS AlastorDealStarted,
                   COALESCE(PredatorVnResolved, 0) AS PredatorVnResolved,
                   COALESCE(ContractOfferPending, 0) AS ContractOfferPending,
                   COALESCE(StatConversionPending, 0) AS StatConversionPending,
                   COALESCE(DeathShieldOfferPending, 0) AS DeathShieldOfferPending,
                   COALESCE(AltarOfferingPending, 0) AS AltarOfferingPending,
                   COALESCE(DevilDealPending, 0) AS DevilDealPending
                   , COALESCE(FreeStatPending, 0) AS FreeStatPending
                   , COALESCE(Curse137Pending, 0) AS Curse137Pending
                   , COALESCE(Curse137Trigger, '') AS Curse137Trigger
            FROM WORK
            WHERE user_id = ? AND anomaly_id = ?
            """,
            (int(user_id), int(anomaly_id)),
        ).fetchone()
    if not row:
        return {
            "photounlocked": 0,
            "descriptionunlocked": 0,
            "hintunlocked": 0,
            "hintcount": 0,
            "IsCompleted": 0,
            "RewardClaimed": 0,
            "HiddenHintUnlocked": 0,
            "ResetUsed": 0,
            "PendingCompanionOffer": 0,
            "PendingCompanionHint": 0,
            "PendingCompanionId": 0,
            "PendingCompanionEffect": "",
            "CompanionOfferDeclined": 0,
            "WorkCount": 0,
            "BerserkGateFailed": 0,
            "SiphPunishment": 0,
            "ChooseBonusDamage": 5,
            "PendingChooseBonus": 0,
            "AlastorDealRefusals": 0,
            "AlastorDealAccepted": 0,
            "AlastorDealStarted": 0,
            "PredatorVnResolved": 0,
            "ContractOfferPending": 0,
            "StatConversionPending": 0,
            "DeathShieldOfferPending": 0,
            "AltarOfferingPending": 0,
            "DevilDealPending": 0,
            "FreeStatPending": 0,
            "Curse137Pending": 0,
            "Curse137Trigger": "",
        }
    return row_to_dict(row)


def _get_anomaly_row(anomaly_id):
    with db_connect() as conn:
        columns = {str(col["name"]).strip().upper() for col in conn.execute("PRAGMA table_info(ANOMALY)").fetchall()}
        base_columns = [
            "ID", "NAME", "CLASS_ID", "TYPE", "DMGTYPE", "PHOTO", "HINTHIDDEN", "HINT", "DESCRIPTION",
            "PDESCRIPTION", "IsDone", "KLIPOTA", "MODEL", "codename", "INITIALEFFECT", "item_id"
        ]
        hint_columns = [f"HINT{i}" for i in range(1, 13)]
        hint_effect_columns = [f"HINT{i}EFFECT" for i in range(1, 13)]
        select_columns = [column for column in base_columns + hint_columns + hint_effect_columns if column.upper() in columns]
        row = conn.execute(
            f"SELECT {', '.join(select_columns)} FROM ANOMALY WHERE ID = ?",
            (int(anomaly_id),),
        ).fetchone()
    return row_to_dict(row) if row else None


def _anomaly_codename(anomaly_or_id):
    anomaly = anomaly_or_id if isinstance(anomaly_or_id, dict) else _get_anomaly_row(anomaly_or_id)
    if not anomaly:
        return "SC-UN-U-0"
    anomaly_id = int(anomaly.get("ID") or 0)
    return str(anomaly.get("codename") or f"SC-UN-U-{anomaly_id}")


def _work_death_reason(anomaly_id):
    anomaly = _get_anomaly_row(anomaly_id)
    codename = _anomaly_codename(anomaly)
    if int(anomaly_id) == 69:
        return "Затерялся во времени"
    if int(anomaly_id) == 8:
        return f"Напор аномалии {codename} оказался сильнее сотрудника"
    return f"Сотрудник был найден мертвым в камере содержания аномалии {codename}"


def _normalize_death_reason(reason_text):
    reason = str(reason_text or "").strip()
    if not reason:
        return ""
    if reason == "heart_attack":
        return HEART_ATTACK_DEATH_REASON
    if reason == "psychosis_1008":
        return PSYCHOSIS_1008_DEATH_REASON
    if reason.startswith("bad_work:") and ":anomaly_" in reason:
        try:
            return _work_death_reason(int(reason.rsplit("anomaly_", 1)[1]))
        except (TypeError, ValueError):
            return reason
    return reason


def _get_hint_effect_name(anomaly: Optional[dict], hint_slot: int) -> str:
    if not anomaly:
        return ""
    slot = int(hint_slot or 0)
    if slot <= 0:
        return ""
    # Anomaly 7 checks the recorded first work exactly once, on hint 1.
    # Older databases still store check_cat_reward in hint2effect, which
    # caused a second (usually failed) result modal on the next hint.
    if int(anomaly.get("ID") or 0) == 7:
        return "check_cat_reward" if slot == 1 else ""
    if int(anomaly.get("ID") or 0) == 25:
        return "langustwasmet" if slot == 1 else ("langustartifact" if slot == 2 else "")
    if int(anomaly.get("ID") or 0) == 39:
        return "moon_game" if slot == 1 else ""
    # The original rabbit scene belongs to the first hint. Some database
    # versions still contain the legacy binding in hint4effect.
    if int(anomaly.get("ID") or 0) == 70:
        return "memetic_rabbit_scene" if slot == 1 else ""
    if int(anomaly.get("ID") or 0) == 104 and slot == 1:
        return ""
    db_key = f"hint{slot}effect"
    db_effect = str(anomaly.get(db_key) or anomaly.get(db_key.upper()) or "").strip()
    if db_effect:
        return db_effect
    return str(
        (anomaly_effects.HINT_EFFECTS_BY_ANOMALY.get(int(anomaly.get("ID") or 0), {}) or {}).get(f"hint{slot}effect", "")
    ).strip()


def _get_initial_effect_name(anomaly: Optional[dict]) -> str:
    if not anomaly:
        return ""
    if int(anomaly.get("ID") or 0) == 104:
        return "start_tenna_game"
    return str(anomaly.get("initialeffect") or anomaly.get("INITIALEFFECT") or "").strip()


def _anomaly_hint_list(anomaly_row):
    hints = []
    for index in range(1, 13):
        value = anomaly_row.get(f"HINT{index}")
        if value is not None and str(value).strip():
            hints.append(str(value).strip())
    fallback_count = int(anomaly_row.get("HINT") or 0)
    if not hints and fallback_count > 0:
        hints = [f"Подсказка {index}" for index in range(1, fallback_count + 1)]
    return hints


def _pending_companion_offer(progress):
    if not progress:
        return None
    if int(progress.get("PendingCompanionOffer") or 0) != 1:
        return None
    return {
        "pending": True,
        "hint_index": int(progress.get("PendingCompanionHint") or 0),
        "companion_id": int(progress.get("PendingCompanionId") or 0),
        "effect_name": str(progress.get("PendingCompanionEffect") or "").strip(),
    }


def _companion_offer_is_blocking(progress):
    return bool(
        int(progress.get("CompanionOfferDeclined") or 0) == 1
        or int(progress.get("PendingCompanionOffer") or 0) == 1
    )


def _companion_offer_block_reason(progress):
    if int(progress.get("PendingCompanionOffer") or 0) == 1:
        return "Сначала ответьте на предложение компаньона."
    if int(progress.get("CompanionOfferDeclined") or 0) == 1:
        return "После отказа от компаньона дальнейшее исследование невозможно."
    return ""


def _berserk_gate_failed(progress):
    return bool(int((progress or {}).get("BerserkGateFailed") or 0) == 1)


def _berserk_gate_codename():
    anomaly = _get_anomaly_row(2)
    return _anomaly_codename(anomaly)


def _research_is_locked(progress):
    return _companion_offer_is_blocking(progress) or _berserk_gate_failed(progress)


def _research_lock_reason(progress):
    companion_reason = _companion_offer_block_reason(progress)
    if companion_reason:
        return companion_reason
    if _berserk_gate_failed(progress):
        return f"Без активного сигнала от {_berserk_gate_codename()} дальнейшее исследование невозможно."
    return ""


def _cleanup_companion_on_replace(user_id, current_companion_id):
    current_companion_id = int(current_companion_id or 0)
    if current_companion_id == 11:
        for effect_name in list(core.list_player_effects(DB_PATH, int(user_id))):
            if str(effect_name).startswith(core.COMP11_TOK):
                core.remove_player_effect(DB_PATH, int(user_id), str(effect_name))
    elif current_companion_id == 13:
        effects = core.list_player_effects(DB_PATH, int(user_id))
        if "Comp13Applied" in effects:
            core.remove_player_effect(DB_PATH, int(user_id), "Comp13Applied")
            with db_connect_write() as conn:
                conn.execute("UPDATE PLAYERS SET BONUS = MAX(0, COALESCE(BONUS, 0) - 5) WHERE ID = ?", (int(user_id),))
                conn.commit()
    elif current_companion_id == 14:
        for effect_name in list(core.list_player_effects(DB_PATH, int(user_id))):
            text = str(effect_name)
            if text.startswith("SALA_MULT") or text.startswith("SALA_SHIELD_CUR"):
                core.remove_player_effect(DB_PATH, int(user_id), text)


def _transfer_companion_to_next_player(companion_id, from_user_id):
    companion_id = int(companion_id or 0)
    from_user_id = int(from_user_id)
    if companion_id <= 0:
        return None
    try:
        core_state = core.get_game_state(DB_PATH)
        turn_order = [int(pid) for pid in core_state.get("turn_order", [])]
    except sqlite3.OperationalError:
        turn_order = []
    with state_lock:
        lobby_order = [int(player["id"]) for player in lobby_state.get("players", [])]
    candidate_order = turn_order or lobby_order
    if not candidate_order:
        return None
    rows_map = _player_rows_map(candidate_order)
    recipient_id = None
    if from_user_id in candidate_order:
        start_index = candidate_order.index(from_user_id)
        for offset in range(1, len(candidate_order)):
            candidate_id = int(candidate_order[(start_index + offset) % len(candidate_order)])
            if candidate_id == from_user_id:
                continue
            row = rows_map.get(candidate_id)
            if not row or int(row.get("IsDead") or 0) == 1:
                continue
            recipient_id = candidate_id
            break
    else:
        for candidate_id in candidate_order:
            candidate_id = int(candidate_id)
            if candidate_id == from_user_id:
                continue
            row = rows_map.get(candidate_id)
            if not row or int(row.get("IsDead") or 0) == 1:
                continue
            recipient_id = candidate_id
            break
    if recipient_id is None:
        return None
    recipient_row = rows_map.get(int(recipient_id)) or {}
    current_companion_id = int(recipient_row.get("COMPSLOT") or 0)
    if current_companion_id not in (0, companion_id):
        _cleanup_companion_on_replace(int(recipient_id), current_companion_id)
    with db_connect_write() as conn:
        conn.execute("UPDATE PLAYERS SET COMPSLOT = 0 WHERE ID = ?", (int(from_user_id),))
        conn.execute("UPDATE PLAYERS SET COMPSLOT = ? WHERE ID = ?", (int(companion_id), int(recipient_id)))
        if int(companion_id) == 4:
            conn.execute("UPDATE PLAYERS SET CheapTrickPendingNotice = 1 WHERE ID = ?", (int(recipient_id),))
        conn.commit()
    return int(recipient_id)


def _can_accept_companion_offer(user_id, new_companion_id):
    with db_connect() as conn:
        row = conn.execute("SELECT COALESCE(COMPSLOT, 0) AS COMPSLOT FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    current_companion_id = int(row["COMPSLOT"] or 0) if row else 0
    if current_companion_id in (0, int(new_companion_id or 0)):
        return {"allowed": True, "current_companion_id": current_companion_id, "reason": ""}
    if int(new_companion_id or 0) == 14:
        return {"allowed": True, "current_companion_id": current_companion_id, "reason": ""}
    if current_companion_id in COMPANION_REPLACEABLE_SLOTS:
        return {"allowed": True, "current_companion_id": current_companion_id, "reason": ""}
    if current_companion_id == 14:
        return {
            "allowed": False,
            "current_companion_id": current_companion_id,
            "reason": "Лава-саламандру нельзя заменить другим компаньоном",
        }
    return {
        "allowed": False,
        "current_companion_id": current_companion_id,
        "reason": "нельзя сменить имеющегося компаньона",
    }


def _queue_companion_offer(user_id, anomaly_id, hint_slot, effect_name, companion_id):
    with db_connect_write() as conn:
        conn.execute(
            """
            UPDATE WORK
            SET PendingCompanionOffer = 1,
                PendingCompanionHint = ?,
                PendingCompanionId = ?,
                PendingCompanionEffect = ?,
                CompanionOfferDeclined = 0
            WHERE user_id = ? AND anomaly_id = ?
            """,
            (int(hint_slot), int(companion_id), str(effect_name or "").strip(), int(user_id), int(anomaly_id)),
        )
        conn.commit()


def _clear_companion_offer_state(user_id, anomaly_id, declined=False):
    with db_connect_write() as conn:
        conn.execute(
            """
            UPDATE WORK
            SET PendingCompanionOffer = 0,
                PendingCompanionHint = 0,
                PendingCompanionId = 0,
                PendingCompanionEffect = '',
                CompanionOfferDeclined = ?
            WHERE user_id = ? AND anomaly_id = ?
            """,
            (1 if declined else 0, int(user_id), int(anomaly_id)),
        )
        conn.commit()


def _build_companion_offer_payload(user_id, anomaly_id, progress=None):
    progress = progress or _work_progress(user_id, anomaly_id)
    pending = _pending_companion_offer(progress)
    if not pending:
        return None
    anomaly = _get_anomaly_row(anomaly_id)
    display_name = str(anomaly.get("NAME") or "Неизвестно") if int(progress.get("photounlocked") or 0) == 1 else _anomaly_codename(anomaly)
    acceptance = _can_accept_companion_offer(user_id, pending["companion_id"])
    return {
        "pending": True,
        "hint_index": pending["hint_index"],
        "companion_id": pending["companion_id"],
        "effect_name": pending["effect_name"],
        "display_name": display_name,
        "can_accept": bool(acceptance["allowed"]),
        "blocked_reason": acceptance["reason"],
        "current_companion_id": int(acceptance["current_companion_id"] or 0),
        "modal": {
            "intro": "Новый компаньон",
            "effect": (
                f"Вам предложена аномалия {display_name} в качестве компаньона. "
                "В случае отказа - дальнейшее исследование невозможно."
            ),
            "icon": "/photo/work_room/goodresult.png",
            "iconAlt": "Новый компаньон",
        },
    }


def _run_companion_accept_side_effect(effect_name, user_id, previous_companion_id=0):
    effect_name = str(effect_name or "").strip()
    if effect_name == "cheaptrick":
        _remove_effect_exact(int(user_id), "BlockedPhoto")
        _remove_effect_exact(int(user_id), "BlockedDescription")
    elif effect_name == "stupidreptile":
        core.set_global_value(DB_PATH, "bitecount", 3)
    elif effect_name == "xqc":
        current_day = int(_current_day_number() or 0)
        anomaly_effects.apply_player_effect(f"comp9_next={current_day + 2}", player_id=int(user_id), db_path=DB_PATH)
    elif effect_name == "fairy":
        anomaly_effects.apply_player_effect(f"{core.COMP11_TOK}=5", player_id=int(user_id), db_path=DB_PATH)
    elif effect_name == "lil_zema":
        effects = set(core.list_player_effects(DB_PATH, int(user_id)))
        if core.COMP13_TOKEN not in effects:
            with db_connect_write() as conn:
                conn.execute("UPDATE PLAYERS SET BONUS = COALESCE(BONUS, 0) + 5 WHERE ID = ?", (int(user_id),))
                conn.commit()
            anomaly_effects.apply_player_effect(core.COMP13_TOKEN, player_id=int(user_id), db_path=DB_PATH)
    elif effect_name == "salamander":
        mult = 2 if int(previous_companion_id or 0) not in (0, 14) else 1
        # The normal form uses the implicit default multiplier of 1. Persist a
        # token only for a genuinely enhanced salamander; otherwise the status
        # panel would incorrectly label SALA_MULT=1 as the enhanced form.
        with db_connect_write() as conn:
            effects = core.list_player_effects(DB_PATH, int(user_id))
            if mult >= 2:
                core._effect_token_write(effects, core.SALA_MULT_TOK, mult)
            else:
                core._effect_remove_prefix(effects, core.SALA_MULT_TOK)
            core._save_effects(conn, int(user_id), effects)
            conn.commit()
    elif effect_name == "ilvetal":
        with db_connect_write() as conn:
            before_row = conn.execute(
                """
                SELECT COALESCE(STAT1, 1) AS STAT1,
                       COALESCE(MAXHP, 100) AS MAXHP,
                       COALESCE(HP, 0) AS HP
                FROM PLAYERS
                WHERE ID = ?
                """,
                (int(user_id),),
            ).fetchone()
            conn.execute(
                """
                UPDATE PLAYERS
                SET STAT1 = MIN(5, COALESCE(STAT1, 1) + 1),
                    STAT2 = MIN(5, COALESCE(STAT2, 1) + 1),
                    STAT3 = MIN(5, COALESCE(STAT3, 1) + 1),
                    STAT4 = MIN(5, COALESCE(STAT4, 1) + 1)
                WHERE ID = ?
                """,
                (int(user_id),),
            )
            if before_row:
                old_stat1 = int(before_row["STAT1"] or 1)
                new_stat1 = min(5, old_stat1 + 1)
                stat1_gain = max(0, new_stat1 - old_stat1)
                if stat1_gain > 0:
                    hp_gain = 50 * stat1_gain
                    conn.execute(
                        """
                        UPDATE PLAYERS
                        SET MAXHP = MIN(COALESCE(MAXHP, 100) + ?, 300),
                            HP = MIN(COALESCE(HP, 0) + ?, MIN(COALESCE(MAXHP, 100) + ?, 300))
                        WHERE ID = ?
                        """,
                        (hp_gain, hp_gain, hp_gain, int(user_id)),
                    )
            conn.commit()
        anomaly_effects.apply_player_effect("IlvitalWeakening", player_id=int(user_id), db_path=DB_PATH)
        if int(_safe_global_value("AlephWasStudied", 0) or 0) == 1:
            _apply_ilvetal_aleph_trigger([int(user_id)])


def _apply_ilvetal_aleph_trigger(player_ids):
    targets = [int(pid) for pid in (player_ids or [])]
    if not targets:
        return []
    triggered = []
    for player_id in targets:
        effects = set(core.list_player_effects(DB_PATH, int(player_id)))
        if "IlvitalWeakening" not in effects:
            continue
        stat_choice = random.choice(["STAT2", "STAT3", "STAT4"])
        with db_connect_write() as conn:
            row = conn.execute(
                f"SELECT COALESCE({stat_choice}, 1) AS stat_value FROM PLAYERS WHERE ID = ?",
                (int(player_id),),
            ).fetchone()
            if not row:
                continue
            current_value = int(row["stat_value"] or 1)
            new_value = max(1, current_value - 3)
            conn.execute(
                f"""
                UPDATE PLAYERS
                SET {stat_choice} = ?,
                    IlvetalPendingStat = ?,
                    IlvetalPendingOld = ?,
                    IlvetalPendingNew = ?
                WHERE ID = ?
                """,
                (int(new_value), stat_choice, int(current_value), int(new_value), int(player_id)),
            )
            conn.commit()
        core.remove_player_effect(DB_PATH, int(player_id), "IlvitalWeakening")
        triggered.append(
            {
                "player_id": int(player_id),
                "stat": stat_choice,
                "old_value": current_value,
                "new_value": new_value,
            }
        )
    return triggered


def _get_hidden_companion_rp_bonus(user_id, anomaly):
    if not anomaly:
        return 0
    if int(anomaly.get("TYPE") or 0) != 1:
        return 0
    with db_connect() as conn:
        row = conn.execute("SELECT COALESCE(COMPSLOT, 0) AS COMPSLOT FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    if not row:
        return 0
    return 2 if int(row["COMPSLOT"] or 0) == 1 else 0


def _apply_siph_research_penalty(anomaly_id, work_type):
    if int(anomaly_id or 0) != 20:
        return 0
    if str(work_type or "").strip().lower() != "suppression":
        return 0
    current_penalty = int(_safe_global_value("SiphPunishment", 0) or 0)
    next_penalty = min(5, max(1, current_penalty + 1))
    try:
        core.set_global_value(DB_PATH, "SiphIsSad", 1)
        core.set_global_value(DB_PATH, "SiphPunishment", next_penalty)
    except sqlite3.OperationalError:
        pass
    return next_penalty


def _ensure_work_entry(user_id, anomaly_id):
    if int(anomaly_id or 0) in DISABLED_ANOMALY_IDS:
        raise ValueError(DISABLED_ANOMALY_MESSAGE)
    anomaly = _get_anomaly_row(anomaly_id)
    if not anomaly:
        raise ValueError("Аномалия не найдена.")
    hintcount = len(_anomaly_hint_list(anomaly))
    with db_connect_write() as conn:
        row = conn.execute(
            "SELECT anomaly_id FROM WORK WHERE user_id = ?",
            (int(user_id),),
        ).fetchone()
        if not row:
            conn.execute(
                """
                INSERT INTO WORK (
                    user_id, anomaly_id, photounlocked, descriptionunlocked, hintunlocked, hintcount,
                    IsCompleted, RewardClaimed, HiddenHintUnlocked, ResetUsed,
                    PendingCompanionOffer, PendingCompanionHint, PendingCompanionId, PendingCompanionEffect, CompanionOfferDeclined,
                    WorkCount, BerserkGateFailed, ChooseBonusDamage, PendingChooseBonus, AlastorDealRefusals, AlastorDealAccepted, AlastorDealStarted
                )
                VALUES (?, ?, 0, 0, 0, ?, 0, 0, 0, 0, 0, 0, 0, '', 0, 0, 0, 5, 0, 0, 0, 0)
                """,
                (int(user_id), int(anomaly_id), int(hintcount)),
            )
            conn.execute("UPDATE PLAYERS SET RP = 0 WHERE ID = ?", (int(user_id),))
        elif int(row["anomaly_id"] or 0) != int(anomaly_id):
            conn.execute(
                """
                UPDATE WORK
                SET anomaly_id = ?, photounlocked = 0, descriptionunlocked = 0, hintunlocked = 0, hintcount = ?, IsCompleted = 0,
                    RewardClaimed = 0, HiddenHintUnlocked = 0, ResetUsed = 0,
                    PendingCompanionOffer = 0, PendingCompanionHint = 0, PendingCompanionId = 0, PendingCompanionEffect = '', CompanionOfferDeclined = 0,
                    WorkCount = 0, BerserkGateFailed = 0, ChooseBonusDamage = 5, PendingChooseBonus = 0,
                    AlastorDealRefusals = 0, AlastorDealAccepted = 0, AlastorDealStarted = 0, PredatorVnResolved = 0,
                    ContractOfferPending = 0, StatConversionPending = 0, DeathShieldOfferPending = 0,
                    AltarOfferingPending = 0, DevilDealPending = 0, FreeStatPending = 0,
                    Curse137Pending = 0, Curse137Trigger = ''
                WHERE user_id = ?
                """,
                (int(anomaly_id), int(hintcount), int(user_id)),
            )
            conn.execute("UPDATE PLAYERS SET RP = 0 WHERE ID = ?", (int(user_id),))
        elif hintcount:
            conn.execute(
                "UPDATE WORK SET hintcount = ? WHERE user_id = ? AND anomaly_id = ?",
                (int(hintcount), int(user_id), int(anomaly_id)),
            )
        conn.commit()


def _capture_work_status_snapshot(user_id, anomaly_id):
    """Freeze visible HP/SP before initial anomaly effects are applied."""
    _ensure_work_entry(int(user_id), int(anomaly_id))
    with db_connect_write() as conn:
        conn.execute(
            """
            UPDATE WORK
            SET SnapshotHP = (SELECT COALESCE(HP, 0) FROM PLAYERS WHERE ID = ?),
                SnapshotMaxHP = (SELECT COALESCE(MAXHP, 100) FROM PLAYERS WHERE ID = ?),
                SnapshotSP = (SELECT COALESCE(SP, 0) FROM PLAYERS WHERE ID = ?),
                SnapshotMaxSP = (SELECT COALESCE(MAXSP, 200) FROM PLAYERS WHERE ID = ?)
            WHERE user_id = ? AND anomaly_id = ?
            """,
            (int(user_id), int(user_id), int(user_id), int(user_id), int(user_id), int(anomaly_id)),
        )
        conn.commit()


def _reset_work_state_for_new_game(player_ids):
    player_ids = [int(player_id) for player_id in (player_ids or [])]
    if not player_ids:
        return
    placeholders = ",".join("?" for _ in player_ids)
    with db_connect_write() as conn:
        conn.execute(f"DELETE FROM WORK WHERE user_id IN ({placeholders})", tuple(player_ids))
        conn.commit()
    for key, value in (
        ("AlastorPrey", 0),
        ("AlastorMood", 0),
        ("AlastorTask", 0),
        ("AlastorAcceptedDay", 0),
        ("AlastorTaskDay", 0),
        ("AlastorTaskShownDay", 0),
        ("AlastorSuccessCount", 0),
        ("AlastorFledPlayer", 0),
        ("AlastorPendingSuccessText", ""),
        ("AlastorUsedTasks_M1", ""),
        ("AlastorUsedTasks_M2", ""),
        ("AlastorUsedTasks_M3", ""),
        ("DebugForcedAlastorTask", 0),
        ("DebugForcedAlastorTaskDay", 0),
        ("currentgoal", 0),
        ("check_work", 0),
        ("ChosenAnomalyNumber", 0),
        ("first_work_type", ""),
        ("first_work_class", 0),
        ("first_work_anomalytype", 0),
        ("NonAnomalyClass", 0),
        ("NonAnomalyType", 0),
        ("WormActive", 0),
        ("WormStartDay", 0),
        ("WormVictim", 0),
        ("WormLastTickDay", 0),
        ("CompanionDoomActive", 0),
        ("CompanionDoomStartDay", 0),
        ("CompanionDoomVictim", 0),
        ("CompanionDoomLastTickDay", 0),
    ):
        try:
            core.set_global_value(DB_PATH, key, value)
        except sqlite3.OperationalError:
            continue
    try:
        for key in core.list_globals(DB_PATH):
            if (
                str(key).startswith("CrimsonBite_")
                or str(key).startswith("CrimsonInfectedDay_")
                or str(key).startswith("TARGET_NOTICES_")
            ):
                core.set_global_value(DB_PATH, str(key), 0)
    except sqlite3.OperationalError:
        pass


def _update_work_completion(user_id, anomaly_id):
    progress = _work_progress(user_id, anomaly_id)
    is_completed = int(progress["photounlocked"] or 0) == 1 and int(progress["descriptionunlocked"] or 0) == 1
    is_completed = is_completed and int(progress["hintunlocked"] or 0) >= int(progress["hintcount"] or 0)
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET IsCompleted = ? WHERE user_id = ? AND anomaly_id = ?",
            (1 if is_completed else 0, int(user_id), int(anomaly_id)),
        )
        conn.commit()
    progress["IsCompleted"] = 1 if is_completed else 0
    return progress


def _hint_unlock_cost(hint_unlocked):
    return 6 + (2 * int(hint_unlocked or 0))


def _get_damage_display(class_id, dmg_type):
    base = int(DAMAGE_BY_CLASS.get(int(class_id or 1), 2))
    dmg_type = int(dmg_type or 0)
    if dmg_type == 1:
        return {"label": "RED", "amount": str(base)}
    if dmg_type == 2:
        return {"label": "BLACK", "amount": str(base)}
    if dmg_type == 3:
        hp_split = [1, 2, 4, 8, 15][max(0, min(4, int(class_id or 1) - 1))]
        sp_split = max(0, base - hp_split)
        return {"label": "MIXED", "amount": f"{hp_split}/{sp_split}"}
    return {"label": "UNKNOWN", "amount": "-"}


def _clear_psychosis_effects(user_id):
    for effect_id in PSYCHOSIS_EFFECTS:
        core.remove_player_effect(DB_PATH, int(user_id), str(effect_id))


def _current_psychosis_id(user_id):
    effects = {str(item) for item in _safe_player_effects(user_id)}
    for effect_id in PSYCHOSIS_EFFECTS:
        if str(effect_id) in effects:
            return effect_id
    return None


def _current_psychosis_info(user_id):
    psychosis_id = _current_psychosis_id(user_id)
    if not psychosis_id:
        return None
    info = PSYCHOSIS_EFFECTS.get(int(psychosis_id))
    return {"id": int(psychosis_id), "name": info["name"], "desc": info["desc"]} if info else None


def _roll_psychosis(user_id, *, force=False):
    effects = {str(item) for item in _safe_player_effects(user_id)}
    if not force and _current_psychosis_id(user_id) is not None:
        return None
    if force:
        _clear_psychosis_effects(user_id)
        effects = {str(item) for item in _safe_player_effects(user_id)}
    choices = list(PSYCHOSIS_EFFECTS.keys())
    if "witness_curse" in effects or "WitnessCurse" in effects:
        choices = [effect_id for effect_id in choices if effect_id not in (1006, 1007)]
    effect_id = random.choice(choices)
    info = PSYCHOSIS_EFFECTS[effect_id]
    if effect_id not in (1006, 1007):
        _x125_mark("psychosis")
    if effect_id == 1007:
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE PLAYERS SET SP = MIN(COALESCE(MAXSP, 200), COALESCE(SP, 0) + 50) WHERE ID = ?",
                (int(user_id),),
            )
            conn.commit()
        return {"id": effect_id, "name": info["name"], "desc": info["desc"], "message": f"Психоз: {info['name']}. SP увеличен на 50."}
    if effect_id == 1008:
        damage_result = core.apply_damage(DB_PATH, int(user_id), hp_damage=20, sp_damage=0, reason=PSYCHOSIS_1008_DEATH_REASON)
        anomaly_effects.apply_player_effect(str(effect_id), player_id=int(user_id), db_path=DB_PATH)
        return {
            "id": effect_id,
            "name": info["name"],
            "desc": info["desc"],
            "message": f"Психоз: {info['name']}. Игрок получил 20 красного урона.",
            "damage": damage_result,
            "heart_attack": {
                "triggered": bool((damage_result or {}).get("heart_attack_triggered")),
                "dead": bool((damage_result or {}).get("heart_attack_dead")),
                "message": "Сердечный приступ!" if bool((damage_result or {}).get("heart_attack_triggered")) else "",
            } if damage_result else None,
        }
    anomaly_effects.apply_player_effect(str(effect_id), player_id=int(user_id), db_path=DB_PATH)
    return {"id": effect_id, "name": info["name"], "desc": info["desc"], "message": f"Психоз: {info['name']}. {info['desc']}"}


def _post_stress_damage_psychosis(db_path, user_id, damage_result):
    if int((damage_result or {}).get("hp_damage_final") or 0) > 0 or int((damage_result or {}).get("sp_damage_final") or 0) > 0:
        _x125_mark("damage")
    if bool((damage_result or {}).get("is_dead")):
        _x125_mark("death")
    if bool((damage_result or {}).get("is_dead")):
        return None
    if int((damage_result or {}).get("sp_damage_final") or 0) <= 0:
        return None
    if int((damage_result or {}).get("sp") or 999999) > 100:
        return None
    if _current_psychosis_id(int(user_id)) is not None:
        return None
    return _roll_psychosis(int(user_id))


core.set_post_damage_hook(_post_stress_damage_psychosis)


def _laplace67_snapshot_row():
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM LAPLACE67_SNAPSHOT WHERE id = 1").fetchone()
    return dict(row) if row else None


def _laplace67_clear():
    with db_connect_write() as conn:
        conn.execute("DELETE FROM LAPLACE67_SNAPSHOT WHERE id = 1")
        conn.commit()


def _laplace67_rows(conn, table_name, where_sql="", params=()):
    query = f"SELECT * FROM {table_name}"
    if where_sql:
        query += f" WHERE {where_sql}"
    return [dict(row) for row in conn.execute(query, tuple(params)).fetchall()]


def _laplace67_capture(assignments):
    pool = next(iter((assignments or {}).values()), [])
    if not any(int(item.get("id") or 0) == 67 for item in pool):
        return False
    current = _laplace67_snapshot_row()
    if current and int(current.get("active") or 0) == 1:
        return False
    with state_lock:
        lobby_player_ids = [int(player["id"]) for player in lobby_state.get("players", [])]
        assignments_copy = json.loads(json.dumps(assignments or {}, ensure_ascii=False))
    if not lobby_player_ids:
        return False
    placeholders = ",".join("?" for _ in lobby_player_ids)
    with db_connect() as conn:
        alive_rows = conn.execute(
            f"SELECT ID FROM PLAYERS WHERE ID IN ({placeholders}) AND COALESCE(IsDead, 0) = 0",
            tuple(lobby_player_ids),
        ).fetchall()
        alive_ids = [int(row["ID"]) for row in alive_rows]
        if not alive_ids:
            return False
        alive_placeholders = ",".join("?" for _ in alive_ids)
        payload = {
            "player_ids": alive_ids,
            "players": _laplace67_rows(conn, "PLAYERS", f"ID IN ({alive_placeholders})", alive_ids),
            "work": _laplace67_rows(conn, "WORK", f"user_id IN ({alive_placeholders})", alive_ids),
            "player_items": _laplace67_rows(conn, "PLAYER_ITEMS", f"player_id IN ({alive_placeholders})", alive_ids),
            "studied": _laplace67_rows(conn, "PLAYER_STUDIED_ANOMALIES", f"user_id IN ({alive_placeholders})", alive_ids),
            "sue_snapshots": _laplace67_rows(conn, "SUE_SNAPSHOTS", f"user_id IN ({alive_placeholders})", alive_ids),
            "globals": _laplace67_rows(conn, "GAME_GLOBALS"),
            "core_state": _laplace67_rows(conn, "CORE_GAME_STATE", "id = 1"),
            "anomaly_progress": _laplace67_rows(conn, "ANOMALY"),
            "assignments": assignments_copy,
            "runtime_taken_anomalies": sorted(int(value) for value in runtime_taken_anomalies),
            "runtime_game": {
                "started": bool(runtime_game.get("started")),
                "current_day": int(runtime_game.get("current_day") or 1),
                "winner_id": runtime_game.get("winner_id"),
            },
        }
    day_number = int((payload.get("core_state") or [{}])[0].get("current_day") or runtime_game.get("current_day") or 1)
    with db_connect_write() as conn:
        conn.execute(
            """
            INSERT INTO LAPLACE67_SNAPSHOT
                (id, active, armed, owner_user_id, day_number, loop_count, payload_json, created_at)
            VALUES (1, 1, 0, NULL, ?, 0, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                active = 1, armed = 0, owner_user_id = NULL, day_number = excluded.day_number,
                loop_count = 0, payload_json = excluded.payload_json, created_at = excluded.created_at
            """,
            (day_number, json.dumps(payload, ensure_ascii=False), time.time()),
        )
        conn.commit()
    return True


def _laplace67_arm(owner_user_id):
    with db_connect_write() as conn:
        cursor = conn.execute(
            "UPDATE LAPLACE67_SNAPSHOT SET armed = 1, owner_user_id = ? WHERE id = 1 AND active = 1",
            (int(owner_user_id),),
        )
        conn.commit()
    return bool(cursor.rowcount)


def _laplace67_insert_rows(conn, table_name, rows):
    for row in rows or []:
        columns = list(row.keys())
        if not columns:
            continue
        quoted = ", ".join(f'"{column}"' for column in columns)
        placeholders = ", ".join("?" for _ in columns)
        conn.execute(
            f"INSERT OR REPLACE INTO {table_name} ({quoted}) VALUES ({placeholders})",
            tuple(row[column] for column in columns),
        )


def _laplace67_day_transition(db_path, previous_day, requested_day):
    snapshot = _laplace67_snapshot_row()
    if not snapshot or int(snapshot.get("active") or 0) != 1 or int(snapshot.get("armed") or 0) != 1:
        return None
    if int(snapshot.get("day_number") or 0) != int(previous_day):
        return None
    try:
        payload = json.loads(snapshot.get("payload_json") or "{}")
    except (TypeError, ValueError):
        return None
    player_ids = [int(value) for value in payload.get("player_ids") or []]
    if not player_ids:
        return None
    placeholders = ",".join("?" for _ in player_ids)
    with db_connect_write() as conn:
        conn.execute(f"DELETE FROM PLAYERS WHERE ID IN ({placeholders})", tuple(player_ids))
        _laplace67_insert_rows(conn, "PLAYERS", payload.get("players"))
        for table_name, key, rows_key in (
            ("WORK", "user_id", "work"),
            ("PLAYER_ITEMS", "player_id", "player_items"),
            ("PLAYER_STUDIED_ANOMALIES", "user_id", "studied"),
            ("SUE_SNAPSHOTS", "user_id", "sue_snapshots"),
        ):
            conn.execute(f"DELETE FROM {table_name} WHERE {key} IN ({placeholders})", tuple(player_ids))
            _laplace67_insert_rows(conn, table_name, payload.get(rows_key))
        conn.execute("DELETE FROM GAME_GLOBALS")
        _laplace67_insert_rows(conn, "GAME_GLOBALS", payload.get("globals"))
        _laplace67_insert_rows(conn, "CORE_GAME_STATE", payload.get("core_state"))
        for anomaly_row in payload.get("anomaly_progress") or []:
            conn.execute(
                "UPDATE ANOMALY SET IsDone = ? WHERE ID = ?",
                (anomaly_row.get("IsDone"), anomaly_row.get("ID")),
            )
        conn.execute(
            "UPDATE LAPLACE67_SNAPSHOT SET loop_count = COALESCE(loop_count, 0) + 1 WHERE id = 1"
        )
        conn.commit()
    restored_assignments = {
        int(key): value for key, value in (payload.get("assignments") or {}).items()
    }
    with state_lock:
        lobby_state["game_assignments"] = restored_assignments
    runtime_taken_anomalies.clear()
    runtime_taken_anomalies.update(int(value) for value in payload.get("runtime_taken_anomalies") or [])
    loop_deaths = []
    for player_id in player_ids:
        if _is_player_dead(int(player_id)):
            continue
        core.set_global_value(DB_PATH, "LAPLACE_FORCE_MAD_DEATH", int(player_id))
        damage = core.apply_damage(
            DB_PATH,
            int(player_id),
            sp_damage=25,
            reason="выведен из временной линии",
            bypass_death_shield=True,
        )
        if damage.get("is_dead"):
            loop_deaths.append(int(player_id))
    core.set_global_value(DB_PATH, "LAPLACE_FORCE_MAD_DEATH", 0)
    # The world returns to the same snapshot, but the price of each completed
    # loop must accumulate; otherwise SP could never reach zero.
    with db_connect() as conn:
        accumulated_players = _laplace67_rows(
            conn,
            "PLAYERS",
            f"ID IN ({placeholders})",
            player_ids,
        )
    payload["players"] = accumulated_players
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE LAPLACE67_SNAPSHOT SET payload_json = ? WHERE id = 1",
            (json.dumps(payload, ensure_ascii=False),),
        )
        conn.commit()
    state = core.get_game_state(DB_PATH)
    alive_ids = [player_id for player_id in state.get("turn_order", []) if not _is_player_dead(int(player_id))]
    if alive_ids:
        first_alive = int(alive_ids[0])
        turn_order = [int(value) for value in state.get("turn_order", [])]
        turn_index = turn_order.index(first_alive)
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE CORE_GAME_STATE SET status = 'started', current_day = ?, turn_index = ?, current_turn_user_id = ?, winner_user_id = NULL, finished_at = NULL, last_event_at = ? WHERE id = 1",
                (int(previous_day), int(turn_index), first_alive, time.time()),
            )
            conn.commit()
        core.set_global_value(DB_PATH, "CurrentDay", int(previous_day))
        core.set_global_value(DB_PATH, "ActiveWorker", first_alive)
    else:
        core.finish_game(DB_PATH, reason="laplace_time_loop")
    runtime_game["started"] = bool(alive_ids)
    runtime_game["current_day"] = int(previous_day)
    runtime_game["day_started_at"] = time.time()
    runtime_game["winner_id"] = None
    final_state = core.get_game_state(DB_PATH)
    return {
        "state": final_state,
        "event": {
            "day": int(previous_day),
            "stress_damage": 25,
            "dead_player_ids": loop_deaths,
            "message": "Проклятье Лапласа вернуло день к началу.",
        },
    }


core.set_day_transition_hook(_laplace67_day_transition)


def _apply_heart_attack_if_needed(user_id):
    with db_connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(HP, 0) AS HP, COALESCE(SP, 0) AS SP FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
    if not row:
        return None
    hp = int(row["HP"] or 0)
    sp = int(row["SP"] or 0)
    if sp > 0:
        return None
    if hp > 1:
        with db_connect_write() as conn:
            conn.execute("UPDATE PLAYERS SET HP = 1, SP = 50 WHERE ID = ?", (int(user_id),))
            conn.commit()
        return {"triggered": True, "dead": False, "message": "Сердечный приступ! HP -> 1, SP -> 50."}
    core.set_player_dead(DB_PATH, int(user_id), reason=HEART_ATTACK_DEATH_REASON)
    with db_connect_write() as conn:
        conn.execute("UPDATE PLAYERS SET SP = 0 WHERE ID = ?", (int(user_id),))
        conn.commit()
    return {"triggered": True, "dead": True, "message": "Сердечный приступ оказался смертельным."}


def _damage_values(class_id, dmg_type):
    base = int(DAMAGE_BY_CLASS.get(int(class_id or 1), 2))
    dmg_type = int(dmg_type or 0)
    if dmg_type == 1:
        return {"hp": base, "sp": 0, "label": "RED"}
    if dmg_type == 2:
        return {"hp": 0, "sp": base, "label": "BLACK"}
    if dmg_type == 3:
        hp_split = [1, 2, 4, 8, 15][max(0, min(4, int(class_id or 1) - 1))]
        sp_split = max(0, base - hp_split)
        return {"hp": hp_split, "sp": sp_split, "label": "MIXED"}
    return {"hp": 0, "sp": 0, "label": "UNKNOWN"}


def _apply_anomaly_work_damage_passives(anomaly_id, user_id, damage_payload):
    anomaly_id = int(anomaly_id or 0)
    adjusted = {
        "hp": int((damage_payload or {}).get("hp") or 0),
        "sp": int((damage_payload or {}).get("sp") or 0),
        "label": (damage_payload or {}).get("label") or "UNKNOWN",
    }
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(p.HP, 0) AS HP,
                   COALESCE(p.MAXHP, 100) AS MAXHP,
                   COALESCE(p.COMPSLOT, 0) AS COMPSLOT,
                   COALESCE(a.CLASS_ID, 1) AS CLASS_ID
            FROM PLAYERS p
            JOIN ANOMALY a ON a.ID = ?
            WHERE p.ID = ?
            """,
            (int(anomaly_id), int(user_id)),
        ).fetchone()
    if not row:
        return adjusted
    if anomaly_id == 5:
        hp = int(row["HP"] or 0)
        max_hp = max(1, int(row["MAXHP"] or 100))
        if hp <= max_hp / 2:
            adjusted["hp"] *= 2
            adjusted["sp"] *= 2
    if int(row["COMPSLOT"] or 0) == 5:
        current_class = max(1, int(row["CLASS_ID"] or 1))
        downgraded_class = max(1, current_class - 1)
        current_total = int(adjusted["hp"] or 0) + int(adjusted["sp"] or 0)
        if current_total > 0 and downgraded_class != current_class:
            lowered = _damage_values(downgraded_class, 1 if adjusted["sp"] == 0 else (2 if adjusted["hp"] == 0 else 3))
            adjusted["hp"] = int(lowered["hp"] or 0)
            adjusted["sp"] = int(lowered["sp"] or 0)
    return adjusted


def _result_thresholds(class_id):
    good_min = int(GOOD_RESULT_MIN.get(int(class_id or 1), 4))
    bad_max = max(0, good_min - 1)
    return {"good": f"{good_min}-10", "bad": f"0-{bad_max}"}


def _progress_percent(progress):
    total = 2 + int(progress["hintcount"] or 0)
    opened = int(progress["photounlocked"] or 0) + int(progress["descriptionunlocked"] or 0) + int(progress["hintunlocked"] or 0)
    return round((opened / total) * 100) if total > 0 else 0


def _player_has_hidden_hint_artifact(user_id):
    with db_connect() as conn:
        row = conn.execute("SELECT COALESCE(ART, 0) AS ART FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    return bool(row and int(row["ART"] or 0) == 3)


def _black_hole_uses(user_id):
    return max(0, min(3, int(_safe_global_value(f"ART1COUNT_{int(user_id)}", 0) or 0)))


def use_black_hole(user_id):
    user_id = int(user_id)
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Сейчас не ваш ход.")
    used = _black_hole_uses(user_id)
    if used >= 3:
        raise ValueError("Лимит Чёрной дыры исчерпан: 3/3.")
    with db_connect_write() as conn:
        row = conn.execute("SELECT COALESCE(ART, 0) AS ART FROM PLAYERS WHERE ID = ?", (user_id,)).fetchone()
        if not row or int(row["ART"] or 0) != 1:
            raise ValueError("Чёрная дыра вам не принадлежит.")
        conn.execute(
            "UPDATE PLAYERS SET INVSLOT1 = 1, SLOT1AMOUNT = 0, INVSLOT2 = 1, SLOT2AMOUNT = 0 WHERE ID = ?",
            (user_id,),
        )
        conn.commit()
    if int(_safe_global_value("ClayHolder", 0) or 0) == user_id:
        core.set_global_value(DB_PATH, "ClayHolder", 0)
        core.set_global_value(DB_PATH, "CLAY_ABSORB", 0)
    used += 1
    core.set_global_value(DB_PATH, f"ART1COUNT_{user_id}", used)
    return {
        "ok": True,
        "message": f"Чёрная дыра полностью очистила инвентарь, включая специальный слот Глиняной статуи. Использовано: {used}/3.",
        "inventory": get_inventory_payload(user_id),
    }


def _protocol_x_payload(user_id):
    user_id = int(user_id)
    current_day = max(1, int(_current_day_number() or 1))
    with db_connect() as conn:
        owner = conn.execute("SELECT COALESCE(ART, 0) AS ART FROM PLAYERS WHERE ID = ?", (user_id,)).fetchone()
    if not owner or int(owner["ART"] or 0) != 2:
        return {"owned": False, "available": False, "used_today": False, "targets": []}
    state = core.get_game_state(DB_PATH)
    is_turn = state.get("status") == "started" and int(state.get("current_turn_user_id") or 0) == user_id
    used_today = int(_safe_global_value(f"SABOTAGE_USED_DAY_{user_id}", 0) or 0) == current_day
    with state_lock:
        lobby_players = [dict(player) for player in lobby_state.get("players", [])]
    targets = []
    with db_connect() as conn:
        for player in lobby_players:
            target_id = int(player.get("id") or 0)
            if target_id == user_id:
                continue
            row = conn.execute("SELECT COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID = ?", (target_id,)).fetchone()
            if row and int(row["IsDead"] or 0) == 0:
                targets.append({"id": target_id, "name": player.get("name") or f"Игрок {target_id}"})
    return {
        "owned": True,
        "available": bool(is_turn and not used_today and targets),
        "used_today": used_today,
        "is_turn": is_turn,
        "targets": targets,
    }


def use_protocol_x(user_id, target_id):
    user_id, target_id = int(user_id), int(target_id)
    protocol = _protocol_x_payload(user_id)
    if protocol.get("used_today"):
        raise ValueError("Протокол X уже использован сегодня.")
    if not protocol.get("is_turn"):
        raise ValueError("Сейчас не ваш ход.")
    if target_id not in {int(target["id"]) for target in protocol.get("targets", [])}:
        raise ValueError("Недопустимая цель для саботажа.")
    effect = random.choice(("steal_rt", "destroy_item", "klipota_9"))
    with db_connect_write() as conn:
        target = conn.execute(
            "SELECT COALESCE(NAME, '') AS NAME, COALESCE(RT, 0) AS RT, COALESCE(KLIPOTA, 0) AS KLIPOTA, "
            "COALESCE(INVSLOT1, 1) AS INVSLOT1, COALESCE(SLOT1AMOUNT, 0) AS SLOT1AMOUNT, "
            "COALESCE(INVSLOT2, 1) AS INVSLOT2, COALESCE(SLOT2AMOUNT, 0) AS SLOT2AMOUNT FROM PLAYERS WHERE ID = ?",
            (target_id,),
        ).fetchone()
        if not target:
            raise ValueError("Цель не найдена.")
        target_name = str(target["NAME"] or f"Игрок {target_id}")
        if effect == "steal_rt":
            amount = min(int(target["RT"] or 0), random.randint(1, 3))
            if amount:
                conn.execute("UPDATE PLAYERS SET RT = RT - ? WHERE ID = ?", (amount, target_id))
                conn.execute("UPDATE PLAYERS SET RT = RT + ? WHERE ID = ?", (amount, user_id))
                message = f"У {target_name} украдено {amount} RT."
            else:
                message = f"У {target_name} не оказалось RT для кражи."
        elif effect == "destroy_item":
            slots = []
            for slot in (1, 2):
                item_id, amount = int(target[f"INVSLOT{slot}"] or 1), int(target[f"SLOT{slot}AMOUNT"] or 0)
                if item_id not in (0, 1) and amount > 0:
                    slots.append((slot, item_id, amount))
            if slots:
                slot, item_id, amount = random.choice(slots)
                item = conn.execute("SELECT COALESCE(NAME, ?) AS NAME FROM ITEMS WHERE ID = ?", (f"Предмет {item_id}", item_id)).fetchone()
                if amount > 1:
                    conn.execute(f"UPDATE PLAYERS SET SLOT{slot}AMOUNT = SLOT{slot}AMOUNT - 1 WHERE ID = ?", (target_id,))
                else:
                    conn.execute(f"UPDATE PLAYERS SET INVSLOT{slot} = 1, SLOT{slot}AMOUNT = 0 WHERE ID = ?", (target_id,))
                message = f"У {target_name} уничтожен предмет «{item['NAME'] if item else item_id}»."
            else:
                message = f"У {target_name} не оказалось предметов для уничтожения."
        else:
            before = int(target["KLIPOTA"] or 0)
            after = max(before, 9)
            conn.execute("UPDATE PLAYERS SET KLIPOTA = ? WHERE ID = ?", (after, target_id))
            message = f"Клипота {target_name} повышена до {after}."
        conn.commit()
    day = max(1, int(_current_day_number() or 1))
    core.set_global_value(DB_PATH, f"SABOTAGE_USED_DAY_{user_id}", day)
    # Этот флаг использует эффект аномалии 46.
    core.set_global_value(DB_PATH, "xprotocol", 1)
    actor_name = _player_display_name(user_id)
    log_text = f"{actor_name} применил Протокол X. Цель — {target_name}. {message}"
    _append_game_action_log("effect", log_text, user_id)
    _queue_target_notice(
        target_id,
        "Протокол X",
        f"Игрок {actor_name} выбрал вас целью Протокола X. {message}",
        source_id=user_id,
    )
    return {
        "ok": True,
        "effect": effect,
        "message": f"Протокол X: {message}",
        "protocol_x": _protocol_x_payload(user_id),
        "game_state": get_game_state(user_id),
    }


def _get_stat4_multiplier(stat4_level):
    return {1: 1, 2: 1.5, 3: 2, 4: 2.5, 5: 3}.get(int(stat4_level or 1), 1)


def _get_player_penalty(user_id):
    with db_connect() as conn:
        row = conn.execute("SELECT COALESCE(PENALTY, 0) AS PENALTY FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    return int(row["PENALTY"] or 0) if row else 0


def _set_player_penalty(user_id, value):
    with db_connect_write() as conn:
        conn.execute("UPDATE PLAYERS SET PENALTY = ? WHERE ID = ?", (int(value or 0), int(user_id)))
        conn.commit()


def _player_has_effect(user_id, effect_name):
    target = str(effect_name or "").strip()
    if not target:
        return False
    return any(str(item).strip() == target for item in _safe_player_effects(user_id))


def _increment_global_int(key, amount=1):
    current = int(core.get_global_value(DB_PATH, key, 0) or 0)
    new_value = current + int(amount or 0)
    core.set_global_value(DB_PATH, key, new_value)
    return new_value


def _pisos_curse_floor(user_id):
    if not _player_has_effect(user_id, "PisosCurse"):
        return 0
    count = int(core.get_global_value(DB_PATH, "PisosCurseCount", 0) or 0)
    return min(30, max(0, count * 5))


def _reset_player_penalty(user_id):
    pisos_floor = _pisos_curse_floor(user_id)
    with db_connect_write() as conn:
        conn.execute("UPDATE PLAYERS SET PENALTY = ? WHERE ID = ?", (int(pisos_floor), int(user_id)))
        conn.commit()


def _increase_player_penalty(user_id, anomaly_class):
    anomaly_class = int(anomaly_class or 0)
    increment_map = {4: 8, 5: 10}
    cap_map = {4: 32, 5: 30}
    increment = increment_map.get(anomaly_class)
    cap = cap_map.get(anomaly_class)
    if increment is None or cap is None:
        return _get_player_penalty(user_id)
    pisos_floor = _pisos_curse_floor(user_id)
    with db_connect_write() as conn:
        row = conn.execute("SELECT COALESCE(PENALTY, 0) AS PENALTY FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        current = int(row["PENALTY"] or 0) if row else 0
        new_penalty = min(cap, max(current + increment, pisos_floor))
        conn.execute("UPDATE PLAYERS SET PENALTY = ? WHERE ID = ?", (new_penalty, int(user_id)))
        conn.commit()
    return new_penalty


def _effective_penalty_for_work(player_id, anomaly_class, stored_penalty, work_count):
    anomaly_class = int(anomaly_class or 0)
    if anomaly_class not in (4, 5):
        return 0
    work_count = int(work_count or 0)
    if work_count <= 0:
        return _pisos_curse_floor(player_id)
    return int(stored_penalty or 0)


def _should_apply_progress_penalty(user_id, anomaly_id, anomaly_class):
    anomaly_class = int(anomaly_class or 0)
    return anomaly_class in (4, 5)


def _player_opened_any_anomaly_info(user_id, anomaly_id):
    progress = _work_progress(user_id, anomaly_id)
    return bool(
        int(progress.get("photounlocked") or 0) > 0
        or int(progress.get("descriptionunlocked") or 0) > 0
        or int(progress.get("hintunlocked") or 0) > 0
    )


def _track_first_work_after_cat(work_type):
    if int(_safe_global_value("CatOnStoveEncountered", 0) or 0) != 1:
        return False
    normalized_work = str(work_type or "").strip().lower()
    core.set_global_value(DB_PATH, "CatOnStoveEncountered", 0)
    core.set_global_value(DB_PATH, "CatFirstWorkType", normalized_work)
    core.set_global_value(DB_PATH, "CatGiveReward", 1 if normalized_work == "intuition" else 0)
    return True


def _track_langust_work(user_id, work_type):
    """Remember the first work selected after anomaly 25's first hint."""
    with db_connect_write() as conn:
        row = conn.execute(
            """SELECT COALESCE(LangustTracking, 0) AS tracking
               FROM WORK WHERE user_id = ? AND anomaly_id = 25""",
            (int(user_id),),
        ).fetchone()
        if not row or int(row["tracking"] or 0) != 1:
            return False
        conn.execute(
            """UPDATE WORK
               SET LangustTracking = 0, LangustAffection = ?
               WHERE user_id = ? AND anomaly_id = 25""",
            (1 if str(work_type or "").strip().lower() == "affection" else 0, int(user_id)),
        )
        conn.commit()
    return True


def _apply_under_curse2_work_penalty(user_id, anomaly_id, work_type):
    if int(_safe_global_value("UnderCurse2", 0) or 0) != 1:
        return {"applied": False, "dead": False}
    if str(work_type or "").strip().lower() == "suppression":
        return {"applied": False, "dead": False}

    with db_connect_write() as conn:
        row = conn.execute(
            "SELECT COALESCE(HP, 0) AS HP, COALESCE(MAXHP, 100) AS MAXHP FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
        if not row:
            return {"applied": False, "dead": False}
        current_hp = int(row["HP"] or 0)
        current_max_hp = max(0, int(row["MAXHP"] or 0))
        new_hp = max(0, current_hp - 5)
        new_max_hp = max(0, current_max_hp - 5)
        conn.execute(
            "UPDATE PLAYERS SET HP = ?, MAXHP = ? WHERE ID = ?",
            (int(new_hp), int(new_max_hp), int(user_id)),
        )
        conn.commit()

    if new_hp <= 0:
        core.set_player_dead(DB_PATH, int(user_id), reason=_work_death_reason(int(anomaly_id)))
        return {"applied": True, "dead": True, "hp": new_hp, "maxhp": new_max_hp}
    return {"applied": True, "dead": False, "hp": new_hp, "maxhp": new_max_hp}


def _stat_upgrade_cost(level):
    level = int(level or 1)
    if level >= 5:
        return None
    return level


def _is_sparing_curse_upgrade_blocked(user_id, level):
    effects = {str(item) for item in _safe_player_effects(user_id)}
    if "SparingCurse" not in effects:
        return False
    if int(_safe_global_value("AlephWasStudied", 0) or 0) == 1:
        return False
    return int(level or 1) >= 3


def get_upgrade_payload(user_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(RT, 0) AS RT,
                   COALESCE(STAT1, 1) AS STAT1,
                   COALESCE(STAT2, 1) AS STAT2,
                   COALESCE(STAT3, 1) AS STAT3,
                   COALESCE(STAT4, 1) AS STAT4
            FROM PLAYERS
            WHERE ID = ?
            """,
            (int(user_id),),
        ).fetchone()
    if not row:
        raise ValueError("Игрок не найден.")

    stats = []
    available = int(row["RT"] or 0)
    for key, meta in STAT_UPGRADE_META.items():
        level = int(row[meta["column"]] or 1)
        cost = _stat_upgrade_cost(level)
        blocked_by_sparing = _is_sparing_curse_upgrade_blocked(user_id, level)
        stats.append(
            {
                "key": key,
                "label": meta["label"],
                "icon": meta["icon"],
                "effect": meta["effect"],
                "level": level,
                "cost": cost,
                "can_upgrade": cost is not None and available >= int(cost) and not blocked_by_sparing,
                "maxed": cost is None,
                "blocked_by_sparing": blocked_by_sparing,
                "blocked_reason": "Проклятье Спаринга блокирует прокачку выше 3, пока кто-то не изучит ALEPH." if blocked_by_sparing else "",
            }
        )

    return {
        "points_available": available,
        "stats": stats,
    }


def _is_cursed_item(item_id):
    try:
        return int(item_id or 0) in CURSED_ITEM_IDS
    except Exception:
        return False


def _get_anomaly_item_id(anomaly_id):
    try:
        anomaly = _get_anomaly_row(anomaly_id)
        return int((anomaly or {}).get("item_id") or (anomaly or {}).get("ITEM_ID") or 0)
    except Exception:
        return 0


def _get_item_reward_value(item_id):
    with db_connect() as conn:
        row = conn.execute("SELECT REWARD FROM ITEMS WHERE ID = ?", (int(item_id),)).fetchone()
    if not row or row["REWARD"] is None:
        return None
    try:
        return int(row["REWARD"])
    except (TypeError, ValueError):
        return None


def _should_award_cp_on_item_use(anomaly_id):
    item_id = _get_anomaly_item_id(anomaly_id)
    if item_id in (0, 1) or _is_cursed_item(item_id):
        return False
    reward = _get_item_reward_value(item_id)
    return reward is not None and reward != -1


def _grant_item_use_reward(player_id, item_id):
    if _is_cursed_item(item_id):
        return 0
    reward = _get_item_reward_value(item_id)
    if reward is None or reward == -1:
        return 0
    with db_connect_write() as conn:
        row = conn.execute(
            "SELECT COALESCE(STAT4, 1) AS STAT4, COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID = ?",
            (int(player_id),),
        ).fetchone()
        if not row:
            return 0
        delta = int(int(reward) * _get_stat4_multiplier(int(row["STAT4"] or 1)))
        if delta <= 0:
            return 0
        conn.execute("UPDATE PLAYERS SET CP = COALESCE(CP, 0) + ? WHERE ID = ?", (delta, int(player_id)))
    return delta


def _build_item_modal(title, effect_text, icon="/photo/work_room/success.png", icon_alt="Предмет"):
    return {
        "status": "implemented",
        "title": title,
        "description": effect_text,
        "modal": {
            "intro": title,
            "effect": effect_text,
            "icon": icon,
            "iconAlt": icon_alt,
        },
    }


def _clay_transfer_candidates(user_id):
    with state_lock:
        player_ids = [
            int(player["id"])
            for player in lobby_state.get("players", [])
            if int(player["id"]) != int(user_id)
        ]
    if not player_ids:
        return []
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT ID, COALESCE(NAME, 'Сотрудник') AS NAME, COALESCE(IsDead, 0) AS IsDead
            FROM PLAYERS
            WHERE ID IN ({','.join('?' for _ in player_ids)})
            """,
            tuple(player_ids),
        ).fetchall()
    candidates = []
    for row in rows:
        if int(row["IsDead"] or 0) == 1:
            continue
        candidates.append({"id": int(row["ID"]), "name": str(row["NAME"])})
    return candidates


def transfer_clay_statue(user_id, target_id):
    user_id = int(user_id)
    target_id = int(target_id)
    candidates = {int(item["id"]): item for item in _clay_transfer_candidates(user_id)}
    if target_id not in candidates:
        raise ValueError("Получатель недоступен или у него нет свободного слота.")
    with db_connect_write() as conn:
        holder_id = int(_safe_global_value("ClayHolder", 0) or 0)
        owns_in_inventory = _player_has_inventory_item(conn, user_id, core.CLAY_ITEM_ID)
        if holder_id != user_id and not owns_in_inventory:
            raise ValueError("У вас больше нет Глиняной статуи.")
        target = _player_row_for_inventory(conn, target_id)
        if not target or int(target["IsDead"] or 0) == 1:
            raise ValueError("Получатель недоступен.")
        if owns_in_inventory:
            _consume_inventory_item(conn, user_id, core.CLAY_ITEM_ID)
    current_day = int(core.get_game_state(DB_PATH).get("current_day") or 1)
    core.set_global_value(DB_PATH, "ClayHolder", target_id)
    core.set_global_value(DB_PATH, "ClayLastTransferDay", current_day)
    core.set_global_value(DB_PATH, "CLAY_LAST_TRANSFER_DAY", current_day)
    popup_id = int(_safe_global_value("ClayPopupId", 0) or 0) + 1
    core.set_global_value(DB_PATH, "ClayPopupId", popup_id)
    core.set_global_value(DB_PATH, f"ClayPopup_{target_id}", {
        "id": popup_id,
        "title": "Глиняная статуя",
        "text": f"Игрок {_player_display_name(user_id)} передал вам Глиняную статую.",
        "acknowledged": False,
    })
    _mark_item_used(core.CLAY_ITEM_ID)
    gained_cp = _grant_item_use_reward(user_id, core.CLAY_ITEM_ID)
    target_name = candidates[target_id]["name"]
    text = f"Глиняная статуя передана игроку {target_name}."
    if gained_cp > 0:
        text += f" Получено {gained_cp} CP за использование."
    return {
        "ok": True,
        "inventory": get_inventory_payload(user_id),
        "item_result": _build_item_modal("Глиняная статуя", text),
        "target_id": target_id,
        "gained_cp": gained_cp,
    }


def _current_work_anomaly_id(user_id):
    with db_connect() as conn:
        row = conn.execute("SELECT anomaly_id FROM WORK WHERE user_id = ?", (int(user_id),)).fetchone()
    return int(row["anomaly_id"] or 0) if row else 0


def _clear_anomaly69_runtime(user_id):
    core.remove_player_effect(DB_PATH, int(user_id), "TimeDebt69")
    core.set_global_value(DB_PATH, "A69_HP", 0)
    core.set_global_value(DB_PATH, "A69_SP", 0)
    core.set_global_value(DB_PATH, "A69_CNT", 0)


def _get_reset_targets(user_id):
    with state_lock:
        candidate_ids = [int(player["id"]) for player in lobby_state.get("players", [])]
    if not candidate_ids:
        candidate_ids = [int(user_id)]
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT ID, COALESCE(NAME, 'Сотрудник') AS NAME, COALESCE(IsDead, 0) AS IsDead
            FROM PLAYERS
            WHERE ID IN ({','.join('?' for _ in candidate_ids)})
            ORDER BY ID
            """,
            tuple(candidate_ids),
        ).fetchall()
    targets = []
    for row in rows:
        if int(row["IsDead"] or 0) == 1:
            continue
        targets.append({"id": int(row["ID"]), "label": str(row["NAME"] or f"Игрок {row['ID']}")})
    return targets


def _current_day_number():
    try:
        core_state = core.get_game_state(DB_PATH)
        day = int(core_state.get("current_day") or 0)
        if day > 0:
            return day
    except sqlite3.OperationalError:
        pass
    return int(runtime_game.get("current_day") or _safe_global_value("CurrentDay", 0) or 0)


def _contract_state():
    try:
        pending = int(_safe_global_value("HIT_PENDING", 0) or 0)
        bidder_id = int(_safe_global_value("HIT_BIDDER", 0) or 0)
        target_id = int(_safe_global_value("HIT_TARGET", 0) or 0)
        exec_day = int(_safe_global_value("HIT_EXEC_DAY", 0) or 0)
        payers = [int(value) for value in (_safe_global_value("HIT_PAYERS", []) or [])]
        responded = [int(value) for value in (_safe_global_value("HIT_RESPONDED", []) or [])]
        summary = _safe_global_value("HIT_SUMMARY", None)
        summary_seen = [int(value) for value in (_safe_global_value("HIT_SUMMARY_SEEN", []) or [])]
    except Exception:
        pending = 0
        bidder_id = 0
        target_id = 0
        exec_day = 0
        payers = []
        responded = []
        summary = None
        summary_seen = []
    return {
        "pending": pending == 1,
        "bidder_id": bidder_id,
        "target_id": target_id,
        "exec_day": exec_day,
        "payers": payers,
        "responded": responded,
        "summary": summary if isinstance(summary, dict) else None,
        "summary_seen": summary_seen,
    }


def _set_contract_state(*, pending=None, bidder_id=None, target_id=None, exec_day=None, payers=None, responded=None, summary=None, summary_seen=None):
    updates = []
    if pending is not None:
        updates.append(("HIT_PENDING", int(1 if pending else 0)))
    if bidder_id is not None:
        updates.append(("HIT_BIDDER", int(bidder_id or 0)))
    if target_id is not None:
        updates.append(("HIT_TARGET", int(target_id or 0)))
    if exec_day is not None:
        updates.append(("HIT_EXEC_DAY", int(exec_day or 0)))
    if payers is not None:
        updates.append(("HIT_PAYERS", [int(value) for value in payers]))
    if responded is not None:
        updates.append(("HIT_RESPONDED", [int(value) for value in responded]))
    if summary is not None:
        updates.append(("HIT_SUMMARY", summary))
    if summary_seen is not None:
        updates.append(("HIT_SUMMARY_SEEN", [int(value) for value in summary_seen]))
    for key, value in updates:
        try:
            core.set_global_value(DB_PATH, key, value)
        except sqlite3.OperationalError:
            continue


def _player_rows_map(player_ids):
    player_ids = [int(pid) for pid in (player_ids or [])]
    if not player_ids:
        return {}
    placeholders = ",".join("?" for _ in player_ids)
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT ID,
                   COALESCE(NAME, 'Сотрудник') AS NAME,
                   COALESCE(CP, 0) AS CP,
                   COALESCE(IsDead, 0) AS IsDead
            FROM PLAYERS
            WHERE ID IN ({placeholders})
            """,
            tuple(player_ids),
        ).fetchall()
    return {int(row["ID"]): row_to_dict(row) for row in rows}


def _living_contract_candidates(exclude_user_id=None):
    with state_lock:
        player_ids = [int(player["id"]) for player in lobby_state.get("players", [])]
    rows_map = _player_rows_map(player_ids)
    result = []
    for player_id in player_ids:
        row = rows_map.get(int(player_id))
        if not row or int(row["IsDead"] or 0) == 1:
            continue
        if exclude_user_id is not None and int(player_id) == int(exclude_user_id):
            continue
        result.append(
            {
                "id": int(player_id),
                "name": str(row["NAME"] or f"Игрок {player_id}"),
                "cp": int(row["CP"] or 0),
            }
        )
    return result


def _contract_bidder_name(contract_state):
    bidder_id = int(contract_state.get("bidder_id") or 0)
    if bidder_id <= 0:
        return "Сотрудник"
    row = _player_rows_map([bidder_id]).get(bidder_id)
    return str((row or {}).get("NAME") or "Сотрудник")


def _resolve_contract_if_due():
    state = _contract_state()
    if not state.get("pending"):
        return state
    current_day = _current_day_number()
    exec_day = int(state.get("exec_day") or 0)
    if exec_day <= 0 or current_day < exec_day:
        return state

    bidder_id = int(state.get("bidder_id") or 0)
    target_id = int(state.get("target_id") or 0)
    payers = [int(value) for value in (state.get("payers") or [])]
    rows_map = _player_rows_map([bidder_id, target_id] + payers)
    target_name = str((rows_map.get(target_id) or {}).get("NAME") or f"Игрок {target_id}") if target_id else ""
    bidder_name = str((rows_map.get(bidder_id) or {}).get("NAME") or "Сотрудник")
    payer_names = [
        str((rows_map.get(player_id) or {}).get("NAME") or f"Игрок {player_id}")
        for player_id in payers
        if int(player_id) != int(bidder_id)
    ]
    outcome = "Никто не устранен."
    killed_id = 0
    death_reason = ""
    if target_id and target_id not in payers:
        death_reason = f"Был устранен по заказу сотрудника {bidder_name}"
        try:
            core.set_player_dead(DB_PATH, int(target_id), reason=death_reason)
        except sqlite3.OperationalError:
            pass
        killed_id = int(target_id)
        outcome = f"{target_name} был убит."
    summary = {
        "bidder_id": bidder_id,
        "target_id": target_id,
        "target_name": target_name,
        "payer_ids": payers,
        "payer_names": payer_names,
        "killed_id": killed_id,
        "death_reason": death_reason,
        "outcome": outcome,
        "resolved_day": current_day,
    }
    _set_contract_state(
        pending=False,
        bidder_id=0,
        target_id=0,
        exec_day=0,
        payers=[],
        responded=[],
        summary=summary,
        summary_seen=[],
    )
    return _contract_state()


def _build_contract_warning_payload(user_id):
    state = _resolve_contract_if_due()
    if state.get("summary"):
        return None
    if not state.get("pending"):
        return None
    current_user = int(user_id)
    bidder_id = int(state.get("bidder_id") or 0)
    if current_user == bidder_id:
        return None
    if current_user in {int(value) for value in (state.get("responded") or [])}:
        return None
    rows_map = _player_rows_map([current_user, bidder_id])
    user_row = rows_map.get(current_user)
    if not user_row or int(user_row.get("IsDead") or 0) == 1:
        return None
    bidder_name = str((rows_map.get(bidder_id) or {}).get("NAME") or "Сотрудник")
    current_cp = int(user_row.get("CP") or 0)
    return {
        "pending": True,
        "intro": "Предупреждение!",
        "effect": f"Сотрудник {bidder_name} выбрал целью одного из сотрудников. Если цель не откупится, то будет устранена спустя определенное время. Откупиться?",
        "can_pay": current_cp >= 500,
        "pay_cost": 500,
        "icon": "/photo/work_room/badresult.png",
        "iconAlt": "Предупреждение",
    }


def _build_contract_summary_payload(user_id):
    state = _resolve_contract_if_due()
    summary = state.get("summary") or {}
    if not summary:
        return None
    current_user = int(user_id)
    seen = {int(value) for value in (state.get("summary_seen") or [])}
    if current_user in seen:
        return None
    payer_names = [str(name) for name in (summary.get("payer_names") or []) if str(name).strip()]
    paid_text = ", ".join(payer_names) if payer_names else "никто"
    target_name = str(summary.get("target_name") or "")
    chosen_text = f"Целью был выбран {target_name}." if target_name else "Цели выбрано не было."
    effect = f"{chosen_text} Откупились: {paid_text}. Итог: {summary.get('outcome') or 'Никто не устранен.'}"
    return {
        "pending": True,
        "intro": "Исход",
        "effect": effect,
        "icon": "/photo/work_room/badresult.png",
        "iconAlt": "Исход",
        "current_user_killed": int(summary.get("killed_id") or 0) == current_user,
        "death_reason": str(summary.get("death_reason") or "Был устранен по заказу убийцы."),
    }


def get_contract_offer_preview(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id))
    if anomaly_id != 19:
        raise ValueError("Особый эффект доступен только для аномалии 19.")
    state = _contract_state()
    if state.get("pending"):
        raise ValueError("Убийца уже ожидает исполнения другого заказа.")
    targets = _living_contract_candidates(exclude_user_id=int(user_id))
    if not targets:
        return {
            "action": {
                "intro": "Предложение убийцы",
                "effect": "Вы можете заказать устранение другого сотрудника за 1000 СО. Что скажете?",
                "targets": [],
            }
        }
    with db_connect() as conn:
        player_row = conn.execute(
            "SELECT COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
    if not player_row:
        raise ValueError("Игрок не найден.")
    if int(player_row["CP"] or 0) < 1000:
        raise ValueError("Недостаточно СО (нужно 1000).")
    return {
        "action": {
            "intro": "Предложение убийцы",
            "effect": "Вы можете заказать устранение другого сотрудника за 1000 СО. Что скажете?",
            "targets": [{"id": int(target["id"]), "label": str(target["name"])} for target in targets],
        }
    }


STAT_CONVERSION_OPTIONS = [
    {"key": "STAT2", "label": "Удача"},
    {"key": "STAT3", "label": "Гибкость ума"},
    {"key": "STAT4", "label": "Адаптация"},
]

CHOOSE_BONUS_STAT4_MULTIPLIERS = {1: 1, 2: 1.5, 3: 2, 4: 2.5, 5: 3}


def get_stat_conversion_preview(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id))
    if anomaly_id != 21:
        raise ValueError("Особый эффект доступен только для аномалии 21.")
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(STAT1, 1) AS STAT1,
                   COALESCE(STAT2, 1) AS STAT2,
                   COALESCE(STAT3, 1) AS STAT3,
                   COALESCE(STAT4, 1) AS STAT4
            FROM PLAYERS
            WHERE ID = ?
            """,
            (int(user_id),),
        ).fetchone()
    if not row:
        raise ValueError("Игрок не найден.")
    stat1 = int(row["STAT1"] or 1)
    endurance_maxed = stat1 >= 5
    options = []
    for item in STAT_CONVERSION_OPTIONS:
        current_value = int(row[item["key"]] or 1)
        disabled = endurance_maxed or current_value <= 1
        blocked_reason = ""
        if endurance_maxed:
            blocked_reason = "Выносливость уже максимальна."
        elif current_value <= 1:
            blocked_reason = "Нельзя снизить атрибут ниже 1."
        options.append(
            {
                "key": item["key"],
                "label": item["label"],
                "current_value": current_value,
                "disabled": disabled,
                "blocked_reason": blocked_reason,
            }
        )
    return {
        "action": {
            "intro": "Обмен",
            "effect": "Вы можете обменять 1 очко Удачи, Гибкости ума или Адаптации на +1 к Выносливости. Согласиться?",
            "options": options,
            "endurance_maxed": endurance_maxed,
        }
    }


def apply_stat_conversion(user_id, stat_key):
    anomaly_id = _current_work_anomaly_id(user_id)
    if int(anomaly_id) != 21:
        raise ValueError("Особый эффект доступен только для аномалии 21.")
    stat_key = str(stat_key or "").strip().upper()
    if stat_key not in {"STAT2", "STAT3", "STAT4"}:
        raise ValueError("Недопустимый атрибут для обмена.")
    with db_connect_write() as conn:
        row = conn.execute(
            f"""
            SELECT COALESCE(STAT1, 1) AS STAT1,
                   COALESCE({stat_key}, 1) AS source_stat,
                   COALESCE(HP, 0) AS HP,
                   COALESCE(MAXHP, 100) AS MAXHP
            FROM PLAYERS
            WHERE ID = ?
            """,
            (int(user_id),),
        ).fetchone()
        if not row:
            raise ValueError("Игрок не найден.")
        stat1 = int(row["STAT1"] or 1)
        source_value = int(row["source_stat"] or 1)
        if stat1 >= 5:
            raise ValueError("Выносливость уже максимальна.")
        if source_value <= 1:
            raise ValueError("Нельзя снизить атрибут ниже 1.")
        new_stat1 = min(5, stat1 + 1)
        new_source = max(1, source_value - 1)
        hp_gain = 50 * max(0, new_stat1 - stat1)
        conn.execute(
            f"""
            UPDATE PLAYERS
            SET STAT1 = ?,
                {stat_key} = ?,
                MAXHP = MIN(COALESCE(MAXHP, 100) + ?, 300),
                HP = MIN(COALESCE(HP, 0) + ?, MIN(COALESCE(MAXHP, 100) + ?, 300))
            WHERE ID = ?
            """,
            (int(new_stat1), int(new_source), int(hp_gain), int(hp_gain), int(hp_gain), int(user_id)),
        )
        conn.execute(
            "UPDATE WORK SET StatConversionPending = 0 WHERE user_id = ? AND anomaly_id = 21",
            (int(user_id),),
        )
        conn.commit()
    _remove_utilizer_if_fortitude_too_high(int(user_id))
    return {
        "ok": True,
        "room": get_work_room_payload(int(user_id), int(anomaly_id)),
        "details": get_details_payload(int(user_id), int(anomaly_id)),
        "upgrade": get_upgrade_payload(int(user_id)),
    }


def decline_stat_conversion(user_id):
    anomaly_id = _current_work_anomaly_id(user_id)
    if int(anomaly_id) != 21:
        raise ValueError("Особый эффект доступен только для аномалии 21.")
    with db_connect_write() as conn:
        row = conn.execute(
            "SELECT COALESCE(StatConversionPending, 0) AS pending FROM WORK WHERE user_id = ? AND anomaly_id = 21",
            (int(user_id),),
        ).fetchone()
        if not row or int(row["pending"] or 0) != 1:
            raise ValueError("Ожидающего решения по обмену нет.")
        conn.execute(
            "UPDATE WORK SET StatConversionPending = 0 WHERE user_id = ? AND anomaly_id = 21",
            (int(user_id),),
        )
        conn.commit()
    return {
        "ok": True,
        "room": get_work_room_payload(int(user_id), 21),
        "details": get_details_payload(int(user_id), 21),
        "message": "Обмен характеристик отклонён.",
    }


def get_death_shield_offer_preview(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id))
    if anomaly_id != 35:
        raise ValueError("Особый эффект доступен только для аномалии 35.")
    active_effects = set(core.list_player_effects(DB_PATH, int(user_id)))
    has_shield = "death_shield" in active_effects
    return {
        "action": {
            "intro": "Сделка",
            "effect": "Аномалия готова защитить вас от смерти, но будет забирать часть СО. Согласиться?",
            "icon": "/photo/work_room/neutralresult.png",
            "iconAlt": "Сделка",
            "can_accept": not has_shield,
            "blocked_reason": "Щит уже активен." if has_shield else "",
        }
    }


def apply_death_shield_offer(user_id):
    anomaly_id = int(_current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 35:
        raise ValueError("Особый эффект доступен только для аномалии 35.")
    result = anomaly_effects.apply_player_effect("death_shield", player_id=int(user_id), anomaly_id=anomaly_id, db_path=DB_PATH)
    if result.get("status") == "blocked":
        raise ValueError("Не удалось применить эффект защиты.")
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET DeathShieldOfferPending = 0 WHERE user_id = ? AND anomaly_id = 35",
            (int(user_id),),
        )
        conn.commit()
    return {
        "ok": True,
        "room": get_work_room_payload(int(user_id), int(anomaly_id)),
        "details": get_details_payload(int(user_id), int(anomaly_id)),
    }


def decline_death_shield_offer(user_id):
    anomaly_id = int(_current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 35:
        raise ValueError("Особый эффект доступен только для аномалии 35.")
    with db_connect_write() as conn:
        row = conn.execute(
            "SELECT COALESCE(DeathShieldOfferPending, 0) AS pending FROM WORK WHERE user_id = ? AND anomaly_id = 35",
            (int(user_id),),
        ).fetchone()
        if not row or int(row["pending"] or 0) != 1:
            raise ValueError("Ожидающего предложения защиты нет.")
        conn.execute(
            "UPDATE WORK SET DeathShieldOfferPending = 0 WHERE user_id = ? AND anomaly_id = 35",
            (int(user_id),),
        )
        conn.commit()
    return {
        "ok": True,
        "room": get_work_room_payload(int(user_id), 35),
        "details": get_details_payload(int(user_id), 35),
        "message": "Предложение защиты отклонено.",
    }


def get_altar_offering_preview(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 37:
        raise ValueError("Подношение доступно только для аномалии 37.")
    progress = _work_progress(user_id, anomaly_id)
    if int(progress.get("AltarOfferingPending") or 0) != 1:
        raise ValueError("Предложение подношения сейчас не активно.")
    with db_connect() as conn:
        row = conn.execute("SELECT COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    hp = int(row["HP"] or 0) if row else 0
    return {
        "action": {
            "intro": "Подношение Алтарю угля",
            "effect": "Хотите сделать подношение в виде крови? Без этого продолжить исследование не получится.",
            "can_accept": hp >= 10,
            "blocked_reason": "Недостаточно HP для подношения (нужно 10)." if hp < 10 else "",
            "icon": "/photo/work_room/neutralresult.png",
            "iconAlt": "Алтарь угля",
        }
    }


def apply_altar_offering(user_id):
    anomaly_id = int(_current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 37:
        raise ValueError("Подношение доступно только для аномалии 37.")
    progress = _work_progress(user_id, anomaly_id)
    if int(progress.get("AltarOfferingPending") or 0) != 1:
        raise ValueError("Предложение подношения сейчас не активно.")
    with db_connect() as conn:
        row = conn.execute("SELECT COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    if not row or int(row["HP"] or 0) < 10:
        raise ValueError("Недостаточно HP для подношения (нужно 10).")
    damage = core.apply_damage(DB_PATH, int(user_id), hp_damage=10, reason="Подношение Алтарю угля")
    player_dead = bool((damage or {}).get("is_dead"))
    if player_dead:
        game_state = _advance_after_nonwork_death(int(user_id), "altar_offering_death")
        return {
            "ok": True,
            "player_dead": True,
            "death_reason": "Отдал Алтарю угля слишком много крови",
            "damage": damage,
            "game_state": game_state,
            "final_results": game_state.get("final_results"),
        }
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET AltarOfferingPending = 0 WHERE user_id = ? AND anomaly_id = 37",
            (int(user_id),),
        )
        conn.commit()
    core.set_global_value(DB_PATH, "altarismet", 1)
    return {
        "ok": True,
        "player_dead": False,
        "damage": damage,
        "room": get_work_room_payload(int(user_id), 37),
        "details": get_details_payload(int(user_id), 37),
        "message": "Подношение принято. Потеряно 10 HP.",
    }


def get_devil_deal_preview(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 41:
        raise ValueError("Сделка доступна только для аномалии 41.")
    if int(_work_progress(user_id, 41).get("DevilDealPending") or 0) != 1:
        raise ValueError("Предложение сделки сейчас не активно.")
    return {
        "action": {
            "intro": "Сделка",
            "effect": "Душа в обмен на знания.",
            "icon": "/photo/anomaly/041_devil.png",
            "iconAlt": "Дьявол",
        }
    }


def resolve_devil_deal(user_id, accept):
    anomaly_id = int(_current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 41:
        raise ValueError("Сделка доступна только для аномалии 41.")
    if int(_work_progress(user_id, 41).get("DevilDealPending") or 0) != 1:
        raise ValueError("Предложение сделки сейчас не активно.")
    if bool(accept):
        anomaly_effects.apply_player_effect("DevilsDeal", player_id=int(user_id), anomaly_id=41, db_path=DB_PATH)
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE PLAYERS SET HP = 1, MAXHP = 1, STAT1 = 5 WHERE ID = ?",
                (int(user_id),),
            )
            conn.execute(
                "UPDATE WORK SET DevilDealPending = 0 WHERE user_id = ? AND anomaly_id = 41",
                (int(user_id),),
            )
            conn.commit()
        return {
            "ok": True,
            "accepted": True,
            "player_dead": False,
            "details": get_details_payload(int(user_id), 41),
            "room": get_work_room_payload(int(user_id), 41),
        }
    damage = core.apply_damage(DB_PATH, int(user_id), hp_damage=666, reason="Сгинул в преисподней")
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET DevilDealPending = 0 WHERE user_id = ? AND anomaly_id = 41",
            (int(user_id),),
        )
        conn.commit()
    player_dead = bool((damage or {}).get("is_dead"))
    if player_dead:
        game_state = _advance_after_nonwork_death(int(user_id), "devil_deal_refused")
        return {
            "ok": True,
            "accepted": False,
            "player_dead": True,
            "death_reason": "Сгинул в преисподней",
            "damage": damage,
            "game_state": game_state,
            "final_results": game_state.get("final_results"),
        }
    return {
        "ok": True,
        "accepted": False,
        "player_dead": False,
        "damage": damage,
        "details": get_details_payload(int(user_id), 41),
        "room": get_work_room_payload(int(user_id), 41),
    }


FREE_STAT_OPTIONS = {
    "STAT1": "Выносливость",
    "STAT2": "Удача",
    "STAT3": "Гибкость ума",
    "STAT4": "Адаптация",
}


def get_free_stat_preview(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 49:
        raise ValueError("Дар характеристики доступен только для аномалии 49.")
    if int(_work_progress(user_id, 49).get("FreeStatPending") or 0) != 1:
        raise ValueError("Дар характеристики сейчас не ожидает выбора.")
    with db_connect() as conn:
        row = conn.execute(
            """SELECT COALESCE(STAT1, 1) AS STAT1, COALESCE(STAT2, 1) AS STAT2,
                      COALESCE(STAT3, 1) AS STAT3, COALESCE(STAT4, 1) AS STAT4
               FROM PLAYERS WHERE ID = ?""",
            (int(user_id),),
        ).fetchone()
    if not row:
        raise ValueError("Игрок не найден.")
    return {
        "action": {
            "intro": "Дар характеристики",
            "effect": "Выберите характеристику, которую хотите повысить на 1.",
            "options": [
                {"key": key, "label": label, "level": int(row[key] or 1), "can_choose": int(row[key] or 1) < 5}
                for key, label in FREE_STAT_OPTIONS.items()
            ],
            "icon": "/photo/anomaly/049_toiletgod.png",
            "iconAlt": "Дар характеристики",
        }
    }


def apply_free_stat_choice(user_id, stat_key):
    anomaly_id = int(_current_work_anomaly_id(user_id) or 0)
    stat_key = str(stat_key or "").strip().upper()
    if anomaly_id != 49:
        raise ValueError("Дар характеристики доступен только для аномалии 49.")
    if stat_key not in FREE_STAT_OPTIONS:
        raise ValueError("Неизвестная характеристика.")
    if int(_work_progress(user_id, 49).get("FreeStatPending") or 0) != 1:
        raise ValueError("Дар характеристики уже использован.")
    with db_connect_write() as conn:
        row = conn.execute(
            f"SELECT COALESCE({stat_key}, 1) AS level, COALESCE(HP, 0) AS HP, COALESCE(MAXHP, 100) AS MAXHP FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
        if not row:
            raise ValueError("Игрок не найден.")
        level = int(row["level"] or 1)
        if level >= 5:
            raise ValueError(f"{FREE_STAT_OPTIONS[stat_key]} уже достигла максимума.")
        if stat_key == "STAT1":
            new_max_hp = min(300, int(row["MAXHP"] or 100) + 50)
            new_hp = min(new_max_hp, int(row["HP"] or 0) + 50)
            conn.execute(
                "UPDATE PLAYERS SET STAT1 = STAT1 + 1, HP = ?, MAXHP = ? WHERE ID = ?",
                (new_hp, new_max_hp, int(user_id)),
            )
        else:
            conn.execute(f"UPDATE PLAYERS SET {stat_key} = {stat_key} + 1 WHERE ID = ?", (int(user_id),))
        conn.execute("UPDATE WORK SET FreeStatPending = 0 WHERE user_id = ? AND anomaly_id = 49", (int(user_id),))
        conn.commit()
    if stat_key == "STAT1":
        _remove_utilizer_if_fortitude_too_high(int(user_id))
    return {
        "ok": True,
        "stat_key": stat_key,
        "stat_name": FREE_STAT_OPTIONS[stat_key],
        "new_level": level + 1,
        "details": get_details_payload(int(user_id), 49),
        "room": get_work_room_payload(int(user_id), 49),
    }


def start_moon_eye_game(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 39:
        raise ValueError("Игра глаз доступна только для аномалии 39.")
    if int(_work_progress(user_id, anomaly_id).get("hintunlocked") or 0) < 1:
        raise ValueError("Сначала откройте первую подсказку.")
    colors = ("red", "yellow", "purple")
    labels = {"red": "красного", "yellow": "жёлтого", "purple": "фиолетового"}
    first_target = random.choice(colors)
    other_colors = tuple(color for color in colors if color != first_target)
    first_eyes = [random.choice(other_colors) for _ in range(5)]
    first_eyes.extend(random.choice(colors) for _ in range(7))
    if first_target not in first_eyes[5:]:
        first_eyes[random.randint(5, 11)] = first_target
    second_eyes = [random.choice(colors) for _ in range(12)]
    third_eyes = [random.choice(colors) for _ in range(25)]
    targets = [first_target, random.choice(colors), random.choice(colors)]
    challenge_id = secrets.token_urlsafe(18)
    expected = [targets[0], second_eyes.count(targets[1]), third_eyes.count(targets[2])]
    moon_eye_game_sessions[int(user_id)] = {
        "challenge_id": challenge_id,
        "expected": expected,
        "rounds": [first_eyes, second_eyes, third_eyes],
        "current_round": 0,
        "errors": 0,
        "score": 0,
        "created_at": time.time(),
    }
    return {
        "challenge_id": challenge_id,
        "rounds": [
            {"type": "reaction", "instruction": f"Нажми СТОП, когда увидишь глаз {labels[targets[0]]} цвета", "target": targets[0], "eyes": first_eyes},
            {"type": "fall", "instruction": f"Подсчитай глаза {labels[targets[1]]} цвета", "question": f"Сколько глаз {labels[targets[1]]} цвета упало?", "eyes": second_eyes},
            {"type": "rings", "instruction": f"Сколько {labels[targets[2]]} цвета глаз ты увидел?", "question": f"Сколько глаз {labels[targets[2]]} цвета ты увидел?", "eyes": third_eyes},
        ],
    }


def start_emoji_glasses_game(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 44:
        raise ValueError("Игра с очками доступна только для аномалии 44.")
    if int(_work_progress(user_id, 44).get("hintunlocked") or 0) < 1:
        raise ValueError("Сначала откройте первую подсказку.")
    challenge_id = secrets.token_urlsafe(18)
    emoji_glasses_game_sessions[int(user_id)] = {
        "challenge_id": challenge_id,
        "created_at": time.time(),
    }
    return {"challenge_id": challenge_id, "duration": 10}


def resolve_emoji_glasses_game(user_id, challenge_id, success):
    session = emoji_glasses_game_sessions.get(int(user_id))
    if not session or str(session.get("challenge_id")) != str(challenge_id or ""):
        raise ValueError("Сессия игры устарела.")
    elapsed = time.time() - float(session.get("created_at") or 0)
    emoji_glasses_game_sessions.pop(int(user_id), None)
    succeeded = bool(success) and elapsed <= 12
    if succeeded:
        return {
            "ok": True,
            "success": True,
            "player_dead": False,
            "message": "Очки надеты вовремя!",
            "details": get_details_payload(int(user_id), 44),
            "room": get_work_room_payload(int(user_id), 44),
        }
    damage = core.apply_damage(DB_PATH, int(user_id), hp_damage=10, reason="Не успел надеть очки во время затмения")
    player_dead = bool((damage or {}).get("is_dead"))
    if player_dead:
        game_state = _advance_after_nonwork_death(int(user_id), "emoji_glasses_game_death")
        return {
            "ok": True,
            "success": False,
            "player_dead": True,
            "damage": damage,
            "death_reason": "Не успел надеть очки во время затмения",
            "game_state": game_state,
            "final_results": game_state.get("final_results"),
        }
    return {
        "ok": True,
        "success": False,
        "player_dead": False,
        "damage": damage,
        "message": "Время вышло. Получено 10 урона.",
        "details": get_details_payload(int(user_id), 44),
        "room": get_work_room_payload(int(user_id), 44),
    }


def start_sea_monster_game(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 61:
        raise ValueError("Бой с Морским дьяволом доступен только для аномалии 61.")
    existing = sea_monster_game_sessions.get(int(user_id))
    if existing and time.time() - float(existing.get("created_at") or 0) <= 900:
        return {"challenge_id": existing["challenge_id"], "round": int(existing.get("round") or 1), "target_rounds": 5}
    challenge_id = secrets.token_urlsafe(18)
    sea_monster_game_sessions[int(user_id)] = {
        "challenge_id": challenge_id,
        "round": 1,
        "created_at": time.time(),
    }
    return {"challenge_id": challenge_id, "round": 1, "target_rounds": 5}


def resolve_sea_monster_round(user_id, challenge_id, success):
    session = sea_monster_game_sessions.get(int(user_id))
    if not session or str(session.get("challenge_id")) != str(challenge_id or ""):
        raise ValueError("Сессия боя устарела.")
    if time.time() - float(session.get("created_at") or 0) > 900:
        sea_monster_game_sessions.pop(int(user_id), None)
        raise ValueError("Время боя истекло.")
    current_round = int(session.get("round") or 1)
    if bool(success):
        next_round = current_round + 1
        finished = next_round > 5
        if finished:
            sea_monster_game_sessions.pop(int(user_id), None)
            _ensure_work_entry(int(user_id), 61)
            with db_connect_write() as conn:
                conn.execute(
                    """
                    UPDATE WORK
                    SET photounlocked = 1,
                        descriptionunlocked = 1,
                        hintunlocked = hintcount,
                        IsCompleted = 1
                    WHERE user_id = ? AND anomaly_id = 61
                    """,
                    (int(user_id),),
                )
                conn.commit()
        else:
            session["round"] = next_round
        return {
            "ok": True,
            "success": True,
            "finished": finished,
            "round": min(next_round, 5),
            "player_dead": False,
            "message": "Атака отражена!" if not finished else "Все пять атак Морского дьявола отражены.",
            "details": get_details_payload(int(user_id), 61) if finished else None,
            "room": get_work_room_payload(int(user_id), 61),
        }

    damage = core.apply_damage(DB_PATH, int(user_id), hp_damage=75, reason="Не смог отразить атаку Морского дьявола")
    player_dead = bool(damage.get("is_dead"))
    if player_dead:
        sea_monster_game_sessions.pop(int(user_id), None)
        game_state = _advance_after_nonwork_death(int(user_id), "sea_monster_game_death")
        return {
            "ok": True,
            "success": False,
            "finished": True,
            "round": current_round,
            "damage": damage,
            "player_dead": True,
            "death_reason": "Не смог отразить атаку Морского дьявола",
            "game_state": game_state,
            "final_results": game_state.get("final_results"),
        }
    return {
        "ok": True,
        "success": False,
        "finished": False,
        "round": current_round,
        "damage": damage,
        "player_dead": False,
        "message": "Щит не успел закрыть атаку. Получено 75 урона.",
        "room": get_work_room_payload(int(user_id), 61),
    }


def resolve_moon_eye_game(user_id, challenge_id, round_index, answer):
    session = moon_eye_game_sessions.get(int(user_id))
    if not session or str(session.get("challenge_id")) != str(challenge_id or ""):
        raise ValueError("Сессия игры устарела. Запустите игру заново.")
    if time.time() - float(session.get("created_at") or 0) > 900:
        moon_eye_game_sessions.pop(int(user_id), None)
        raise ValueError("Время игры истекло.")
    round_index = int(round_index)
    if round_index != int(session.get("current_round") or 0) or round_index not in (0, 1, 2):
        raise ValueError("Этот раунд уже завершён или ещё не начался.")
    if round_index == 0:
        try:
            stop_index = int(answer)
        except (TypeError, ValueError):
            stop_index = -1
        reaction_timeout = stop_index < 0
        correct = 0 <= stop_index < len(session["rounds"][0]) and session["rounds"][0][stop_index] == session["expected"][0]
    else:
        reaction_timeout = False
        try:
            correct = int(answer) == int(session["expected"][round_index])
        except (TypeError, ValueError):
            correct = False
    if correct:
        session["score"] = int(session.get("score") or 0) + 1
    else:
        session["errors"] = int(session.get("errors") or 0) + 1
    error_number = int(session.get("errors") or 0)
    damage = None
    if not correct:
        with db_connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(HP, 0) AS HP, COALESCE(MAXHP, 100) AS MAXHP FROM PLAYERS WHERE ID = ?",
                (int(user_id),),
            ).fetchone()
        current_hp = max(0, int(row["HP"] or 0) if row else 0)
        max_hp = max(1, int(row["MAXHP"] or 100) if row else 100)
        if error_number >= 3:
            # The third failure is explicitly fatal even through effects that
            # can reduce or redirect ordinary damage.
            hp_damage = max(current_hp, max_hp) + 9999
        else:
            hp_damage = max(1, int((max_hp * 33 + 99) // 100))
        damage = core.apply_damage(
            DB_PATH,
            int(user_id),
            hp_damage=hp_damage,
            reason="Несовершенен",
            bypass_death_shield=error_number >= 3,
        )
        if error_number >= 3 and not bool((damage or {}).get("is_dead")):
            core.set_player_dead(DB_PATH, int(user_id), reason="Несовершенен")
            damage = {**(damage or {}), "is_dead": True, "hp": 0, "fatal_forced": True}
    player_dead = bool((damage or {}).get("is_dead"))
    if player_dead:
        moon_eye_game_sessions.pop(int(user_id), None)
        game_state = _advance_after_nonwork_death(int(user_id), "moon_eye_game_death")
        return {
            "ok": True, "correct": False, "score": int(session.get("score") or 0),
            "errors": error_number, "damage": damage, "player_dead": True,
            "death_reason": "Несовершенен",
            "game_state": game_state, "final_results": game_state.get("final_results"),
        }
    session["current_round"] = round_index + 1
    finished = session["current_round"] >= 3
    result = {
        "ok": True,
        "correct": bool(correct),
        "score": int(session.get("score") or 0),
        "errors": error_number,
        "damage": damage,
        "player_dead": False,
        "finished": finished,
        "reaction_timeout": reaction_timeout,
    }
    if finished:
        moon_eye_game_sessions.pop(int(user_id), None)
        _ensure_work_entry(int(user_id), 39)
        with db_connect_write() as conn:
            conn.execute(
                """UPDATE WORK
                   SET photounlocked = 1,
                       descriptionunlocked = 1,
                       hintunlocked = hintcount,
                       IsCompleted = 1
                   WHERE user_id = ? AND anomaly_id = 39""",
                (int(user_id),),
            )
            conn.commit()
        result["details"] = get_details_payload(int(user_id), 39)
        result["room"] = get_work_room_payload(int(user_id), 39)
    return result


def _advance_after_nonwork_death(user_id, reason):
    previous_day = int(runtime_game.get("current_day") or _current_day_number() or 1)
    with state_lock:
        player_ids_before = [int(player["id"]) for player in lobby_state["players"]]
        lobby_state["game_assignments"][int(user_id)] = []
    advance_payload = core.advance_turn(DB_PATH, reason=str(reason or "nonwork_death"))
    core_state = advance_payload.get("state", {})
    runtime_game["started"] = core_state.get("status") == "started"
    runtime_game["current_day"] = int(core_state.get("current_day") or 0)
    runtime_game["winner_id"] = core_state.get("winner_user_id")
    if core_state.get("status") == "started" and int(core_state.get("current_day") or 0) > previous_day:
        runtime_game["day_started_at"] = time.time()
        _cleanup_new_day_effects(player_ids_before)
        _apply_new_day_companion_effects(player_ids_before)
        _prepare_alastor_new_day_task()
        with state_lock:
            lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
    elif core_state.get("status") == "finished":
        _finalize_finished_game(player_ids_before)
    return get_game_state(int(user_id))


def _recover_dead_current_turn(requester_id=None):
    """Advance a game left on a dead current player after an interrupted action."""
    state = core.get_game_state(DB_PATH)
    if state.get("status") != "started":
        return None
    current_id = int(state.get("current_turn_user_id") or 0)
    if current_id <= 0 or not _is_player_dead(current_id):
        return None
    _advance_after_nonwork_death(current_id, "recover_dead_current_turn")
    return get_game_state(int(requester_id) if requester_id is not None else current_id)


ALASTOR_TASKS = {
    1: "Выбери аномалию {anomaly_name}",
    2: "Твоё здоровье должно остаться на прежнем уровне после изучения аномалии.",
    3: "Твоя первая работа должна быть {work}.",
    4: "Выживи и не сбегай",
    5: "Закончи день, имея психоз",
    6: "Выбери аномалию самого высокого класса на текущий день",
    7: "Кто-то должен умереть сегодня",
    8: "Потеряй не менее 50% здоровья и закончи исследование",
    9: "В инвентаре не должно быть предметов, доступных для использования",
    10: "ПОРА УМИРАТЬ",
}

ALASTOR_TASK_POOLS = {
    1: [1, 2, 3],
    2: [4, 5, 6],
    3: [7, 8, 9],
}

ALASTOR_WORKS = {
    "intuition": "Интуиция",
    "insight": "Понимание",
    "affection": "Привязанность",
    "suppression": "Подавление",
}

HIGHEST_CLASS_BY_DAY = {
    1: 1, 2: 2, 3: 2, 4: 2, 5: 3,
    6: 3, 7: 3, 8: 4, 9: 4, 10: 4,
    11: 5, 12: 5, 13: 5, 14: 5, 15: 5,
}


def _alastor_pool_key(mood):
    return f"AlastorUsedTasks_M{int(mood)}"


def _alastor_accepted_day():
    return int(_safe_global_value("AlastorAcceptedDay", 0) or 0)


def _alastor_task_day():
    return int(_safe_global_value("AlastorTaskDay", 0) or 0)


def _alastor_task_shown_day():
    return int(_safe_global_value("AlastorTaskShownDay", 0) or 0)


def _clear_alastor_task_runtime():
    core.set_global_value(DB_PATH, "AlastorTask", 0)
    core.set_global_value(DB_PATH, "AlastorTaskDay", 0)
    core.set_global_value(DB_PATH, "AlastorTaskShownDay", 0)
    core.set_global_value(DB_PATH, "currentgoal", 0)
    core.set_global_value(DB_PATH, "check_work", 0)
    core.set_global_value(DB_PATH, "ChosenAnomalyNumber", 0)
    core.set_global_value(DB_PATH, "first_work_type", "")
    core.set_global_value(DB_PATH, "first_work_class", 0)
    core.set_global_value(DB_PATH, "first_work_anomalytype", 0)
    core.set_global_value(DB_PATH, "AlastorFledPlayer", 0)


def _alastor_get_pact_state(user_id):
    global_prey = int(_safe_global_value("AlastorPrey", 0) or 0)
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(AlastorDealAccepted, 0) AS accepted,
                   COALESCE(AlastorDealStarted, 0) AS started,
                   COALESCE(AlastorDealRefusals, 0) AS refusals
            FROM WORK
            WHERE user_id = ? AND anomaly_id = 63
            """,
            (int(user_id),),
        ).fetchone()
    if not row:
        accepted = global_prey == int(user_id)
        return {"accepted": accepted, "started": accepted, "refusals": 0}
    accepted = int(row["accepted"] or 0) == 1 or global_prey == int(user_id)
    return {
        "accepted": accepted,
        "started": int(row["started"] or 0) == 1 or accepted,
        "refusals": int(row["refusals"] or 0),
    }


def _alastor_pick_task_for_mood(mood):
    pool = list(ALASTOR_TASK_POOLS.get(int(mood), []))
    if not pool:
        return 10
    # Tasks are a progression, not a random deck. The success counter is the
    # completed position inside the current mood (0 -> first, 1 -> second...).
    progress = max(0, min(len(pool) - 1, int(_safe_global_value("AlastorSuccessCount", 0) or 0)))
    picked = int(pool[progress])
    key = _alastor_pool_key(mood)
    core.set_global_value(DB_PATH, key, ",".join(str(task_id) for task_id in pool[:progress + 1]))
    return picked


def _build_alastor_task_text(task_id, user_id):
    text_tpl = ALASTOR_TASKS.get(int(task_id), "Задание неизвестно")
    if int(task_id) == 1:
        with state_lock:
            pool = list(lobby_state.get("game_assignments", {}).get(int(user_id), []))
        goal_anomaly_id = int(_safe_global_value("currentgoal", 0) or 0)
        if goal_anomaly_id > 0:
            chosen = next(
                (item for item in pool if int(item.get("id") or 0) == goal_anomaly_id),
                {"id": goal_anomaly_id},
            )
        elif pool:
            chosen = random.choice(pool)
            goal_anomaly_id = int(chosen.get("id") or 0)
            core.set_global_value(DB_PATH, "currentgoal", goal_anomaly_id)
        else:
            # The pool is normally ready by the time the task window is shown.
            # Keep the task pending instead of inventing an anomaly outside it.
            return "Выбери указанную мной аномалию из доступного пула."
        anomaly = _get_anomaly_row(goal_anomaly_id) or {}
        is_studied = int(anomaly.get("IsDone") or 0) == 1
        anomaly_name = (
            str(anomaly.get("NAME") or chosen.get("real_name") or goal_anomaly_id)
            if is_studied
            else str(anomaly.get("codename") or chosen.get("codename") or f"SC-UN-U-{goal_anomaly_id}")
        )
        return text_tpl.format(anomaly_name=anomaly_name)
    if int(task_id) == 2:
        with db_connect() as conn:
            row = conn.execute("SELECT COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        core.set_global_value(DB_PATH, "currentgoal", int(row["HP"] or 0) if row else 0)
        return text_tpl
    if int(task_id) == 3:
        work_key = random.choice(list(ALASTOR_WORKS.keys()))
        core.set_global_value(DB_PATH, "currentgoal", work_key)
        core.set_global_value(DB_PATH, "check_work", 1)
        return text_tpl.format(work=ALASTOR_WORKS.get(work_key, work_key))
    if int(task_id) == 6:
        day = int(runtime_game.get("current_day") or _current_day_number() or 1)
        goal_class = int(HIGHEST_CLASS_BY_DAY.get(day, 5))
        core.set_global_value(DB_PATH, "currentgoal", goal_class)
        return text_tpl
    if int(task_id) == 8:
        with db_connect() as conn:
            row = conn.execute("SELECT COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        core.set_global_value(DB_PATH, "currentgoal", int(row["HP"] or 0) if row else 0)
        return text_tpl
    return text_tpl


def _grant_alastor_success_reward(user_id):
    reward_type = random.choice(["rt", "klipota", "heal_hp", "restore_sp"])
    with db_connect_write() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(HP, 0) AS HP,
                   COALESCE(MAXHP, 100) AS MAXHP,
                   COALESCE(SP, 0) AS SP,
                   COALESCE(MAXSP, 200) AS MAXSP,
                   COALESCE(RT, 0) AS RT,
                   COALESCE(KLIPOTA, 0) AS KLIPOTA
            FROM PLAYERS
            WHERE ID = ?
            """,
            (int(user_id),),
        ).fetchone()
        if not row:
            return "Награда не получена."
        hp = int(row["HP"] or 0)
        max_hp = max(0, int(row["MAXHP"] or 100))
        sp = int(row["SP"] or 0)
        max_sp = max(0, int(row["MAXSP"] or 200))
        rt_value = int(row["RT"] or 0)
        klipota = int(row["KLIPOTA"] or 0)

        if reward_type == "rt":
            delta = random.randint(1, 5)
            new_rt = rt_value + delta
            conn.execute("UPDATE PLAYERS SET RT = ? WHERE ID = ?", (int(new_rt), int(user_id)))
            conn.commit()
            return f"Исследовательские очки прокачки: +{delta} (теперь {new_rt})"

        if reward_type == "klipota":
            if klipota != 0:
                conn.execute("UPDATE PLAYERS SET KLIPOTA = 0 WHERE ID = ?", (int(user_id),))
                conn.commit()
            return "Клипота -> 0"

        if reward_type == "heal_hp":
            delta = random.choice([10, 20, 30])
            new_hp = min(max_hp, hp + delta)
            conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (int(new_hp), int(user_id)))
            conn.commit()
            return f"Лечение: +{delta} HP (теперь {new_hp}/{max_hp})"

        delta = random.choice([10, 20, 30])
        new_sp = min(max_sp, sp + delta)
        conn.execute("UPDATE PLAYERS SET SP = ? WHERE ID = ?", (int(new_sp), int(user_id)))
        conn.commit()
        return f"Восстановление: +{delta} SP (теперь {new_sp}/{max_sp})"


def _alastor_task_visual(mood):
    mood = max(1, min(4, int(mood or 1)))
    return {
        1: {"portrait": "/photo/VN/alastor1.png", "background": "/photo/VN/VN_anomalyinteraction.png"},
        2: {"portrait": "/photo/VN/alastor2.png", "background": "/photo/VN/VN_anomalyinteraction2.png"},
        3: {"portrait": "/photo/VN/alastor3.png", "background": "/photo/VN/VN_anomalyinteraction3.png"},
        4: {"portrait": "/photo/VN/alastor4.png", "background": None},
    }[mood]


def _build_alastor_resolution_payload(success, mood, reward_text):
    visual = _alastor_task_visual(mood)
    if success:
        text = f"Аластор выглядит удовлетворенным.\nПолучена награда: {reward_text}"
    else:
        text = "Аластор выглядит раздраженным"
    return {
        "pending": True,
        "success": bool(success),
        "nameplate": "Аластор",
        "portrait": visual["portrait"],
        "background": visual["background"],
        "text": text,
    }


def _alastor_build_daily_task_text(task_id, user_id):
    base = _build_alastor_task_text(task_id, user_id)
    if int(task_id) == 10:
        return "ПОРА УМИРАТЬ"
    return f"Сегодня ты должен сделать следующее: {base}"


def _assign_alastor_task_for_current_day(user_id):
    current_day = int(_current_day_number() or 0)
    accepted_day = _alastor_accepted_day()
    if current_day <= 0 or current_day <= accepted_day:
        return 0
    if _alastor_task_shown_day() == current_day and int(_safe_global_value("AlastorTask", 0) or 0) <= 0:
        return 0
    task_day = _alastor_task_day()
    current_task = int(_safe_global_value("AlastorTask", 0) or 0)
    if task_day == current_day and current_task > 0:
        return current_task
    mood = int(_safe_global_value("AlastorMood", 0) or 0)
    if mood <= 0:
        mood = 1
        core.set_global_value(DB_PATH, "AlastorMood", 1)
    forced_task = int(_safe_global_value("DebugForcedAlastorTask", 0) or 0)
    forced_day = int(_safe_global_value("DebugForcedAlastorTaskDay", 0) or 0)
    if forced_task in ALASTOR_TASKS and forced_day == current_day:
        forced_mood = 4 if forced_task == 10 else ((forced_task - 1) // 3) + 1
        forced_progress = 0 if forced_task == 10 else (forced_task - 1) % 3
        if mood != forced_mood:
            mood = forced_mood
            core.set_global_value(DB_PATH, "AlastorMood", mood)
        core.set_global_value(DB_PATH, "AlastorSuccessCount", forced_progress)
        if forced_mood in ALASTOR_TASK_POOLS:
            forced_pool = ALASTOR_TASK_POOLS[forced_mood]
            core.set_global_value(
                DB_PATH,
                _alastor_pool_key(forced_mood),
                ",".join(str(value) for value in forced_pool[:forced_progress + 1]),
            )
        task_id = forced_task
        core.set_global_value(DB_PATH, "DebugForcedAlastorTask", 0)
        core.set_global_value(DB_PATH, "DebugForcedAlastorTaskDay", 0)
    else:
        if forced_day > 0 and forced_day < current_day:
            core.set_global_value(DB_PATH, "DebugForcedAlastorTask", 0)
            core.set_global_value(DB_PATH, "DebugForcedAlastorTaskDay", 0)
        task_id = 10 if mood == 4 else _alastor_pick_task_for_mood(mood)
    _clear_alastor_task_runtime()
    core.set_global_value(DB_PATH, "AlastorTask", int(task_id))
    core.set_global_value(DB_PATH, "AlastorTaskDay", int(current_day))
    core.set_global_value(DB_PATH, "AlastorTaskShownDay", 0)
    if int(task_id) == 7:
        with state_lock:
            active_ids = [int(player["id"]) for player in lobby_state.get("players", [])]
        if not active_ids:
            try:
                active_ids = [int(pid) for pid in core.get_game_state(DB_PATH).get("turn_order", [])]
            except sqlite3.OperationalError:
                active_ids = []
        if active_ids:
            placeholders = ",".join("?" for _ in active_ids)
            with db_connect() as conn:
                row = conn.execute(
                    f"SELECT COUNT(*) AS cnt FROM PLAYERS WHERE ID IN ({placeholders}) AND COALESCE(IsDead, 0) = 0",
                    tuple(active_ids),
                ).fetchone()
            core.set_global_value(DB_PATH, "currentgoal", int(row["cnt"] or 0) if row else 0)
        else:
            core.set_global_value(DB_PATH, "currentgoal", 0)
    return int(task_id)


def _build_alastor_task_prompt(user_id):
    pact = _alastor_get_pact_state(user_id)
    if not pact["accepted"]:
        return None
    prey_id = int(_safe_global_value("AlastorPrey", 0) or 0)
    if int(prey_id) != int(user_id):
        return None
    current_day = int(_current_day_number() or 0)
    if current_day <= _alastor_accepted_day():
        return None
    if _alastor_task_shown_day() == current_day and int(_safe_global_value("AlastorTask", 0) or 0) <= 0:
        return None
    task_id = _assign_alastor_task_for_current_day(user_id)
    if task_id <= 0:
        return None
    # At mood 4 the final command is deliberately hidden until the player
    # finishes the anomaly or chooses to flee.
    if int(task_id) == 10:
        return None
    if _alastor_task_shown_day() == current_day:
        return None
    mood = int(_safe_global_value("AlastorMood", 1) or 1)
    text = _alastor_build_daily_task_text(task_id, user_id)
    previous_success = str(_safe_global_value("AlastorPendingSuccessText", "") or "").strip()
    if previous_success:
        text = f"{previous_success}\n\n{text}"
    visual = _alastor_task_visual(mood)
    return {
        "pending": True,
        "task_id": int(task_id),
        "mood": int(mood),
        "nameplate": "Аластор",
        "portrait": visual["portrait"],
        "background": visual["background"],
        "text": text,
        "confirm_only": True,
        "confirm_label": "Умереть" if int(task_id) == 10 else "ОК",
    }


def resolve_alastor_task_prompt(user_id, anomaly_id=None):
    prompt = _build_alastor_task_prompt(user_id)
    if not prompt:
        payload = {"ok": True}
        if anomaly_id is not None and int(anomaly_id) > 0:
            payload["room"] = get_work_room_payload(int(user_id), int(anomaly_id))
        else:
            payload["game_state"] = get_game_state(int(user_id))
        return payload
    current_day = int(_current_day_number() or 0)
    if int(prompt.get("task_id") or 0) != 10:
        core.set_global_value(DB_PATH, "AlastorTaskShownDay", current_day)
        core.set_global_value(DB_PATH, "AlastorPendingSuccessText", "")
        payload = {"ok": True}
        if anomaly_id is not None and int(anomaly_id) > 0:
            payload["room"] = get_work_room_payload(int(user_id), int(anomaly_id))
        else:
            payload["game_state"] = get_game_state(int(user_id))
        return payload
    death_reason = "Бездушная оболочка сотрудника осталась в камере..."
    core.set_player_dead(DB_PATH, int(user_id), reason=death_reason)
    core.set_global_value(DB_PATH, "AlastorTaskShownDay", current_day)
    game_state = _advance_after_nonwork_death(int(user_id), "alastor_final_mood")
    return {
        "ok": True,
        "player_dead": True,
        "death_reason": death_reason,
        "game_state": game_state,
        "final_results": game_state.get("final_results"),
    }


def get_alastor_deal_preview(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id))
    if anomaly_id != 63:
        raise ValueError("Сделка Аластора доступна только для аномалии 63.")
    _ensure_work_entry(user_id, anomaly_id)
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET AlastorDealStarted = 1 WHERE user_id = ? AND anomaly_id = ?",
            (int(user_id), int(anomaly_id)),
        )
        conn.commit()
    progress = _work_progress(user_id, anomaly_id)
    accepted = int(progress.get("AlastorDealAccepted") or 0) == 1
    refusals = int(progress.get("AlastorDealRefusals") or 0)
    return {
        "action": {
            "intro": "Сделка",
            "nameplate": "Аластор",
            "speaker": "Аластор",
            "portrait": "/photo/VN/alastor1.png",
            "text": (
                "Отлично. Тогда приступай"
                if accepted
                else "Твоя глупость будет стоить тебе руки (*Потеряно 50 хп*). А теперь подумай ещё раз."
                if refusals >= 1
                else "Как насчёт небольшой сделки?\n"
                     "Я буду давать тебе простые задания, а взамен ты будешь зарабатывать ценные награды."
            ),
            "accepted": accepted,
            "refusals": refusals,
        }
    }


def apply_alastor_deal_choice(user_id, choice):
    anomaly_id = int(_current_work_anomaly_id(user_id))
    if anomaly_id != 63:
        raise ValueError("Сделка Аластора недоступна.")
    _ensure_work_entry(user_id, anomaly_id)
    progress = _work_progress(user_id, anomaly_id)
    refusals = int(progress.get("AlastorDealRefusals") or 0)
    choice = str(choice or "").strip().lower()
    if choice not in {"accept", "refuse"}:
        raise ValueError("Неизвестный выбор сделки.")

    if choice == "accept":
        with db_connect_write() as conn:
            conn.execute(
                """
                UPDATE WORK
                SET AlastorDealAccepted = 1,
                    AlastorDealStarted = 1,
                    photounlocked = 1,
                    descriptionunlocked = 1,
                    hintunlocked = hintcount,
                    IsCompleted = 1
                WHERE user_id = ? AND anomaly_id = ?
                """,
                (int(user_id), int(anomaly_id)),
            )
            conn.commit()
        core.set_global_value(DB_PATH, "AlastorPrey", int(user_id))
        if int(_safe_global_value("AlastorMood", 0) or 0) == 0:
            core.set_global_value(DB_PATH, "AlastorMood", 1)
        core.set_global_value(DB_PATH, "AlastorAcceptedDay", int(_current_day_number() or 0))
        core.set_global_value(DB_PATH, "AlastorSuccessCount", int(_safe_global_value("AlastorSuccessCount", 0) or 0))
        _clear_alastor_task_runtime()
        return {
            "ok": True,
            "result": "accepted",
            "action": {
                "intro": "Сделка",
                "nameplate": "Аластор",
                "speaker": "Аластор",
                "portrait": "/photo/VN/alastor1.png",
                "text": "Отлично. Тогда приступай",
            },
            "room": get_work_room_payload(int(user_id), int(anomaly_id)),
        }

    if refusals >= 1:
        death_reason = "Ты думал, что можешь отказаться?"
        core.set_player_dead(DB_PATH, int(user_id), reason=death_reason)
        game_state = _advance_after_nonwork_death(int(user_id), "alastor_second_refusal")
        return {
            "ok": True,
            "result": "killed",
            "death_reason": death_reason,
            "player_dead": True,
            "game_state": game_state,
            "final_results": game_state.get("final_results"),
        }

    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET AlastorDealRefusals = 1 WHERE user_id = ? AND anomaly_id = ?",
            (int(user_id), int(anomaly_id)),
        )
        conn.commit()
    damage = core.apply_damage(
        DB_PATH,
        int(user_id),
        hp_damage=50,
        sp_damage=0,
        reason="Ты думал, что можешь отказаться?",
    )
    game_state = None
    final_results = {"exists": False, "winner_id": None, "winner_name": "", "standings": []}
    if bool(damage.get("is_dead")):
        game_state = _advance_after_nonwork_death(int(user_id), "alastor_first_refusal_damage")
        final_results = game_state.get("final_results") or final_results
    room = get_work_room_payload(int(user_id), int(anomaly_id))
    return {
        "ok": True,
        "result": "refused_once",
        "damage": damage,
        "player_dead": bool(damage.get("is_dead")),
        "death_reason": "Ты думал, что можешь отказаться?" if bool(damage.get("is_dead")) else "",
        "action": {
            "intro": "Сделка",
            "nameplate": "Аластор",
            "speaker": "Аластор",
            "portrait": "/photo/VN/alastor1.png",
            "text": "Твоя глупость будет стоить тебе руки (*Потеряно 50 хп*). А теперь подумай ещё раз.",
        },
        "room": room,
        "game_state": game_state,
        "final_results": final_results,
    }


def _alastor_current_task_state(user_id):
    pact = _alastor_get_pact_state(user_id)
    if not pact["accepted"]:
        return None
    prey_id = int(_safe_global_value("AlastorPrey", 0) or 0)
    if int(prey_id) != int(user_id):
        return None
    task_id = int(_safe_global_value("AlastorTask", 0) or 0)
    task_day = _alastor_task_day()
    current_day = int(_current_day_number() or 0)
    if task_id <= 0 or task_day <= 0 or task_day != current_day:
        return None
    mood = int(_safe_global_value("AlastorMood", 1) or 1)
    return {
        "task_id": task_id,
        "mood": mood,
        "day": current_day,
    }


def _alastor_task_completed(user_id, anomaly_id, task_id):
    task_id = int(task_id or 0)
    if task_id == 1:
        goal_anomaly_id = int(_safe_global_value("currentgoal", 0) or 0)
        return goal_anomaly_id > 0 and int(anomaly_id or 0) == goal_anomaly_id
    if task_id == 2:
        goal_hp = int(_safe_global_value("currentgoal", -1) or -1)
        with db_connect() as conn:
            row = conn.execute("SELECT COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        current_hp = int(row["HP"] or -1) if row else -1
        return goal_hp >= 0 and current_hp == goal_hp
    if task_id == 3:
        goal_key = str(_safe_global_value("currentgoal", "") or "").strip().lower()
        first_work_type = str(_safe_global_value("first_work_type", "") or "").strip().lower()
        return bool(goal_key) and goal_key == first_work_type
    if task_id == 4:
        return int(_safe_global_value("AlastorFledPlayer", 0) or 0) != int(user_id)
    if task_id == 5:
        return _current_psychosis_id(user_id) is not None
    if task_id == 6:
        goal_class = int(_safe_global_value("currentgoal", 0) or 0)
        anomaly = _get_anomaly_row(anomaly_id)
        chosen_class = int((anomaly or {}).get("CLASS_ID") or 0)
        return goal_class > 0 and chosen_class == goal_class
    if task_id == 7:
        alive_at_assignment = int(_safe_global_value("currentgoal", 0) or 0)
        with state_lock:
            active_ids = [int(player["id"]) for player in lobby_state.get("players", [])]
        if not active_ids:
            try:
                active_ids = [int(pid) for pid in core.get_game_state(DB_PATH).get("turn_order", [])]
            except sqlite3.OperationalError:
                active_ids = []
        if not active_ids or alive_at_assignment <= 0:
            return False
        placeholders = ",".join("?" for _ in active_ids)
        with db_connect() as conn:
            row = conn.execute(
                f"SELECT COUNT(*) AS cnt FROM PLAYERS WHERE ID IN ({placeholders}) AND COALESCE(IsDead, 0) = 0",
                tuple(active_ids),
            ).fetchone()
        alive_now = int(row["cnt"] or 0) if row else 0
        return alive_now < alive_at_assignment
    if task_id == 8:
        base_hp = int(_safe_global_value("currentgoal", -1) or -1)
        with db_connect() as conn:
            row = conn.execute("SELECT COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        current_hp = int(row["HP"] or -1) if row else -1
        return current_hp == 1 or (base_hp > 0 and current_hp <= max(1, base_hp // 2))
    if task_id == 9:
        with db_connect() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(INVSLOT1, 0) AS INVSLOT1,
                       COALESCE(INVSLOT2, 0) AS INVSLOT2,
                       COALESCE(SLOT1AMOUNT, 0) AS SLOT1AMOUNT,
                       COALESCE(SLOT2AMOUNT, 0) AS SLOT2AMOUNT
                FROM PLAYERS
                WHERE ID = ?
                """,
                (int(user_id),),
            ).fetchone()
        if not row:
            return True
        usable = []
        for item_id, amount in (
            (int(row["INVSLOT1"] or 0), int(row["SLOT1AMOUNT"] or 0)),
            (int(row["INVSLOT2"] or 0), int(row["SLOT2AMOUNT"] or 0)),
        ):
            if amount <= 0 or item_id in (0, 1):
                continue
            with db_connect() as conn:
                item = conn.execute("SELECT COALESCE(IsPassive, 0) AS IsPassive FROM ITEMS WHERE ID = ?", (int(item_id),)).fetchone()
            if not item or int(item["IsPassive"] or 0) != 1:
                usable.append(item_id)
        return not usable
    return False


def _resolve_alastor_task_result(user_id, anomaly_id, *, forced_failure=False):
    state = _alastor_current_task_state(user_id)
    if not state:
        return None
    task_id = int(state["task_id"])
    # Task 7 covers the entire day. Resolve it only after the last turn, when
    # the game advances to the following day.
    if task_id == 7:
        return None
    mood = int(state["mood"])
    current_day = int(state["day"])
    success = False if forced_failure else _alastor_task_completed(user_id, anomaly_id, task_id)
    reward_text = "Награды нет"
    if success:
        if task_id in (7, 8, 9):
            reward_text = "Сегодня ты не умрешь."
        else:
            reward_text = _grant_alastor_success_reward(user_id)
        success_count = int(_safe_global_value("AlastorSuccessCount", 0) or 0) + 1
        core.set_global_value(DB_PATH, "AlastorSuccessCount", success_count)
        if success_count >= 3:
            mood = min(4, mood + 1)
            core.set_global_value(DB_PATH, "AlastorMood", mood)
            core.set_global_value(DB_PATH, "AlastorSuccessCount", 0)
    else:
        mood = min(4, mood + 1)
        core.set_global_value(DB_PATH, "AlastorMood", mood)
        # Successes belong to the current mood level. A failure moves Alastor
        # to the next mood immediately, so the old level's streak must not
        # carry over.
        core.set_global_value(DB_PATH, "AlastorSuccessCount", 0)
    _clear_alastor_task_runtime()
    core.set_global_value(DB_PATH, "AlastorTaskShownDay", current_day)
    return _build_alastor_resolution_payload(success, mood, reward_text)


def get_choose_bonus_preview(user_id, anomaly_id=None):
    anomaly_id = int(anomaly_id or _current_work_anomaly_id(user_id))
    if anomaly_id != 31:
        raise ValueError("Особый эффект доступен только для аномалии 31.")
    _ensure_work_entry(user_id, anomaly_id)
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(STAT4, 1) AS STAT4,
                   COALESCE(w.ChooseBonusDamage, 5) AS ChooseBonusDamage,
                   COALESCE(p.KLIPOTA, 0) AS KLIPOTA
            FROM PLAYERS p
            JOIN WORK w ON w.user_id = p.ID AND w.anomaly_id = ?
            WHERE p.ID = ?
            """,
            (int(anomaly_id), int(user_id)),
        ).fetchone()
    if not row:
        raise ValueError("Игрок не найден.")
    next_damage = int(row["ChooseBonusDamage"] or 5) + 5
    stat4_level = int(row["STAT4"] or 1)
    current_klipota = int(row["KLIPOTA"] or 0)
    cp_reward = int(round(250 * float(CHOOSE_BONUS_STAT4_MULTIPLIERS.get(stat4_level, 1))))
    return {
        "action": {
            "intro": "Предложение",
            "effect": "Что попросить у аномалии? Не забывайте, что все имеет свою цену",
            "icon": "/photo/work_room/neutralresult.png",
            "iconAlt": "Предложение",
            "options": [
                {"key": "cp", "label": f"Сор. очки ({next_damage} HP)", "reward_label": f"+{cp_reward} CP"},
                {"key": "rt", "label": f"2 очка прокачки ({next_damage} HP)", "reward_label": "+2 RT"},
                {
                    "key": "klipota",
                    "label": f"Обнуление клипоты ({next_damage} HP)",
                    "reward_label": "KLIPOTA = 0",
                    "disabled": current_klipota <= 0,
                    "blocked_reason": "Клипота уже обнулена." if current_klipota <= 0 else "",
                },
                {"key": "inventory", "label": f"Чистка инвентаря ({next_damage} HP)", "reward_label": "Инвентарь очищен"},
                {"key": "door", "label": f"Как уйти? ({next_damage} HP)", "reward_label": "Попросить дверь"},
            ],
        }
    }


def apply_choose_bonus_action(user_id, action_key):
    anomaly_id = int(_current_work_anomaly_id(user_id) or 0)
    if anomaly_id != 31:
        raise ValueError("Особый эффект доступен только для аномалии 31.")
    action_key = str(action_key or "").strip().lower()
    if action_key not in {"cp", "rt", "klipota", "inventory", "door"}:
        raise ValueError("Недопустимый вариант бонуса.")
    _ensure_work_entry(user_id, anomaly_id)
    with db_connect_write() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(p.STAT4, 1) AS STAT4,
                   COALESCE(w.ChooseBonusDamage, 5) AS ChooseBonusDamage
            FROM PLAYERS p
            JOIN WORK w ON w.user_id = p.ID AND w.anomaly_id = ?
            WHERE p.ID = ?
            """,
            (int(anomaly_id), int(user_id)),
        ).fetchone()
        if not row:
            raise ValueError("Игрок не найден.")
        current_damage = int(row["ChooseBonusDamage"] or 5)
        next_damage = current_damage + 5
        stat4_level = int(row["STAT4"] or 1)
        cp_reward = int(round(250 * float(CHOOSE_BONUS_STAT4_MULTIPLIERS.get(stat4_level, 1))))
        message = ""
        if action_key == "cp":
            conn.execute("UPDATE PLAYERS SET CP = COALESCE(CP, 0) + ? WHERE ID = ?", (int(cp_reward), int(user_id)))
            message = f"Вы получили {cp_reward} соревновательных очков, потратив {next_damage} HP."
        elif action_key == "rt":
            conn.execute("UPDATE PLAYERS SET RT = COALESCE(RT, 0) + 2 WHERE ID = ?", (int(user_id),))
            message = f"Вы получили 2 очка прокачки, потратив {next_damage} HP."
        elif action_key == "klipota":
            current_klipota = int(
                (
                    conn.execute(
                        "SELECT COALESCE(KLIPOTA, 0) AS KLIPOTA FROM PLAYERS WHERE ID = ?",
                        (int(user_id),),
                    ).fetchone()
                    or {"KLIPOTA": 0}
                )["KLIPOTA"]
                or 0
            )
            if current_klipota <= 0:
                raise ValueError("Клипота уже обнулена.")
            conn.execute("UPDATE PLAYERS SET KLIPOTA = 0 WHERE ID = ?", (int(user_id),))
            message = f"Клипота обнулена ценой {next_damage} HP."
        elif action_key == "inventory":
            conn.execute(
                """
                UPDATE PLAYERS
                SET INVSLOT1 = 0,
                    SLOT1AMOUNT = 0,
                    INVSLOT2 = 0,
                    SLOT2AMOUNT = 0
                WHERE ID = ?
                """,
                (int(user_id),),
            )
            message = f"Инвентарь очищен ценой {next_damage} HP."
        elif action_key == "door":
            message = f"Вы тратите {next_damage} HP, чтобы попросить у аномалии выход."
        conn.execute(
            """
            UPDATE WORK
            SET ChooseBonusDamage = ?,
                PendingChooseBonus = CASE WHEN ? = 'door' THEN 0 ELSE PendingChooseBonus END
            WHERE user_id = ? AND anomaly_id = ?
            """,
            (int(next_damage), action_key, int(user_id), int(anomaly_id)),
        )
        conn.commit()
    damage_result = core.apply_damage(DB_PATH, int(user_id), hp_damage=int(next_damage), sp_damage=0, reason="choose_bonus_hp_price")
    player_dead = bool((damage_result or {}).get("is_dead"))
    game_state = None
    final_results = {"exists": False, "winner_id": None, "winner_name": "", "standings": []}
    death_reason = "Сотрудник был поглощен сердцем дракона из-за своей алчности"
    if player_dead:
        with db_connect_write() as conn:
            conn.execute("UPDATE PLAYERS SET DEATHREASON = ? WHERE ID = ?", (death_reason, int(user_id)))
            conn.commit()
        game_state = _advance_after_nonwork_death(int(user_id), "choose_bonus_death")
        final_results = runtime_game.get("final_results") or game_state.get("final_results") or final_results
        return {
            "ok": True,
            "message": message,
            "damage": damage_result,
            "player_dead": True,
            "death_reason": death_reason,
            "game_state": game_state,
            "final_results": final_results,
        }
    return {
        "ok": True,
        "message": message,
        "damage": damage_result,
        "player_dead": False,
        "door_prompt": action_key == "door",
        "action": get_choose_bonus_preview(int(user_id), int(anomaly_id)).get("action"),
        "room": get_work_room_payload(int(user_id), int(anomaly_id)),
        "details": get_details_payload(int(user_id), int(anomaly_id)),
    }


def apply_contract_target(user_id, target_id):
    anomaly_id = _current_work_anomaly_id(user_id)
    if int(anomaly_id) != 19:
        raise ValueError("Особый эффект доступен только для аномалии 19.")
    state = _contract_state()
    if state.get("pending"):
        raise ValueError("Убийца уже ожидает исполнения другого заказа.")
    valid_targets = {int(target["id"]) for target in _living_contract_candidates(exclude_user_id=int(user_id))}
    if int(target_id) not in valid_targets:
        raise ValueError("Недопустимая цель.")
    with db_connect_write() as conn:
        player_row = conn.execute(
            "SELECT COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
        if not player_row:
            raise ValueError("Игрок не найден.")
        if int(player_row["CP"] or 0) < 1000:
            raise ValueError("Недостаточно СО (нужно 1000).")
        conn.execute("UPDATE PLAYERS SET CP = COALESCE(CP, 0) - 1000 WHERE ID = ?", (int(user_id),))
        conn.commit()
    current_day = max(1, _current_day_number())
    _set_contract_state(
        pending=True,
        bidder_id=int(user_id),
        target_id=int(target_id),
        exec_day=int(current_day + 2),
        payers=[],
        responded=[],
        summary=None,
        summary_seen=[],
    )
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET ContractOfferPending = 0 WHERE user_id = ? AND anomaly_id = 19",
            (int(user_id),),
        )
        conn.commit()
    return {
        "ok": True,
        "room": get_work_room_payload(int(user_id), int(anomaly_id)),
        "details": get_details_payload(int(user_id), int(anomaly_id)),
        "message": "Заказ принят. Остальные сотрудники будут предупреждены позже.",
    }


def decline_contract_offer(user_id):
    anomaly_id = _current_work_anomaly_id(user_id)
    if int(anomaly_id) != 19:
        raise ValueError("Особый эффект доступен только для аномалии 19.")
    with db_connect_write() as conn:
        row = conn.execute(
            "SELECT COALESCE(ContractOfferPending, 0) AS pending FROM WORK WHERE user_id = ? AND anomaly_id = 19",
            (int(user_id),),
        ).fetchone()
        if not row or int(row["pending"] or 0) != 1:
            raise ValueError("Ожидающего решения по контракту нет.")
        conn.execute(
            "UPDATE WORK SET ContractOfferPending = 0 WHERE user_id = ? AND anomaly_id = 19",
            (int(user_id),),
        )
        conn.commit()
    return {
        "ok": True,
        "room": get_work_room_payload(int(user_id), 19),
        "details": get_details_payload(int(user_id), 19),
        "message": "Предложение контракта отклонено.",
    }


CURSE137_TRIGGERS = {
    "mixed_damage": "Смешанный урон (HP + SP)",
    "daily_after_death": "Каждый день после смерти игрока (или если уже есть погибший)",
    "on_psychosis": "При психозе",
    "on_anomaly_chosen": "При выборе аномалии",
    "on_stat_upgrade": "При прокачке характеристики",
}
CURSE137_EFFECTS = {
    "random_curse": "Случайное проклятие",
    "damage30_hp": "30 красного урона",
    "klipota_plus2": "+2 к клипоте",
    "lose_item_or_maxhp25": "−1 предмет или −25 MAXHP",
    "burn_10pct_cp": "Сгорает 10% СО",
}
CURSE137_RANDOM_CURSE_POOL = (
    "FleeIsDeath",
    "PisosCurse",
    "CinderPlague",
    "UnderCurse2",
    "UnderCurse3",
    "WormEggs",
    "CrimsonVirus",
    "NoResult",
    "NoResultPermanent",
)
CURSE137_RANDOM_CURSE_LIMIT = 3


def get_curse137_preview(user_id, anomaly_id=137):
    if int(anomaly_id) != 137 or int(_current_work_anomaly_id(user_id) or 0) != 137:
        raise ValueError("Предложение доступно только при исследовании аномалии 137.")
    progress = _work_progress(int(user_id), 137)
    if int(progress.get("Curse137Pending") or 0) != 1:
        raise ValueError("Ожидающего выбора проклятия нет.")
    trigger = str(progress.get("Curse137Trigger") or "").strip()
    return {
        "ok": True,
        "action": {
            "step": "effect" if trigger else "trigger",
            "intro": "Создание проклятия",
            "effect": (
                "Теперь выберите, что произойдёт при выполнении условия."
                if trigger else
                "Привет. Я ещё не завершена. Помоги создать тебе проклятие :)\n\nВыбери одно из условий. Что под ними скрывается, узнаешь позже."
            ),
            "options": [
                {"key": key, "label": str(index)}
                for index, key in enumerate(
                    (CURSE137_EFFECTS if trigger else CURSE137_TRIGGERS).keys(), start=1
                )
            ],
        },
    }


def resolve_curse137_choice(user_id, choice, anomaly_id=137):
    if int(anomaly_id) != 137 or int(_current_work_anomaly_id(user_id) or 0) != 137:
        raise ValueError("Предложение доступно только при исследовании аномалии 137.")
    progress = _work_progress(int(user_id), 137)
    if int(progress.get("Curse137Pending") or 0) != 1:
        raise ValueError("Ожидающего выбора проклятия нет.")
    selected = str(choice or "").strip()
    trigger = str(progress.get("Curse137Trigger") or "").strip()
    if not trigger:
        if selected not in CURSE137_TRIGGERS:
            raise ValueError("Недопустимое условие проклятия.")
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE WORK SET Curse137Trigger = ? WHERE user_id = ? AND anomaly_id = 137",
                (selected, int(user_id)),
            )
            conn.commit()
        return get_curse137_preview(int(user_id), 137)
    if selected not in CURSE137_EFFECTS:
        raise ValueError("Недопустимое последствие проклятия.")
    core.set_global_value(DB_PATH, "CURSE_ENABLED", 1)
    core.set_global_value(DB_PATH, "CURSE_OWNER_ID", int(user_id))
    core.set_global_value(DB_PATH, "CURSE_TRIGGER", trigger)
    core.set_global_value(DB_PATH, "CURSE_EFFECT", selected)
    core.set_global_value(DB_PATH, "CURSE_DEATH_SEEN", 0)
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET Curse137Pending = 0, Curse137Trigger = '' WHERE user_id = ? AND anomaly_id = 137",
            (int(user_id),),
        )
        conn.commit()
    return {
        "ok": True,
        "resolved": True,
        "message": "Сделка заключена. Условия проклятия запечатаны.",
        "trigger": CURSE137_TRIGGERS[trigger],
        "consequence": CURSE137_EFFECTS[selected],
        "room": get_work_room_payload(int(user_id), 137),
        "details": get_details_payload(int(user_id), 137),
    }


def respond_contract_warning(user_id, pay):
    state = _contract_state()
    if not state.get("pending"):
        raise ValueError("Активного предложения убийцы нет.")
    current_user = int(user_id)
    bidder_id = int(state.get("bidder_id") or 0)
    if current_user == bidder_id:
        raise ValueError("Заказчик не может отвечать на собственное предупреждение.")
    responded = {int(value) for value in (state.get("responded") or [])}
    payers = {int(value) for value in (state.get("payers") or [])}
    if current_user in responded:
        raise ValueError("Ответ уже был дан.")
    if bool(pay):
        with db_connect_write() as conn:
            row = conn.execute("SELECT COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID = ?", (current_user,)).fetchone()
            if not row:
                raise ValueError("Игрок не найден.")
            if int(row["CP"] or 0) < 500:
                raise ValueError("Недостаточно СО (нужно 500).")
            conn.execute("UPDATE PLAYERS SET CP = COALESCE(CP, 0) - 500 WHERE ID = ?", (current_user,))
            conn.commit()
        payers.add(current_user)
    responded.add(current_user)
    _set_contract_state(payers=sorted(payers), responded=sorted(responded))
    anomaly_id = _current_work_anomaly_id(user_id)
    return {
        "ok": True,
        "paid": bool(pay),
        "room": get_work_room_payload(int(user_id), int(anomaly_id)) if anomaly_id else None,
    }


def consume_contract_summary(user_id, anomaly_id=None):
    state = _resolve_contract_if_due()
    summary = state.get("summary") or {}
    seen = {int(value) for value in (state.get("summary_seen") or [])}
    seen.add(int(user_id))
    _set_contract_state(summary_seen=sorted(seen))
    player_dead = int(summary.get("killed_id") or 0) == int(user_id)
    game_state = get_game_state(int(user_id))
    final_results = runtime_game.get("final_results") or {"exists": False, "winner_id": None, "winner_name": "", "standings": []}
    if player_dead:
        core_state = (game_state.get("core") or {})
        if core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) == int(user_id):
            previous_day = int(runtime_game.get("current_day") or _current_day_number() or 1)
            with state_lock:
                player_ids_before = [int(player["id"]) for player in lobby_state["players"]]
                lobby_state["game_assignments"][int(user_id)] = []
            advance_payload = core.advance_turn(DB_PATH, reason="contract_assassination")
            advanced_state = advance_payload.get("state", {})
            runtime_game["started"] = advanced_state.get("status") == "started"
            runtime_game["current_day"] = int(advanced_state.get("current_day") or 0)
            runtime_game["winner_id"] = advanced_state.get("winner_user_id")
            if advanced_state.get("status") == "started" and int(advanced_state.get("current_day") or 0) > previous_day:
                runtime_game["day_started_at"] = time.time()
                _cleanup_new_day_effects(player_ids_before)
                _apply_new_day_companion_effects(player_ids_before)
                _prepare_alastor_new_day_task()
                with state_lock:
                    lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
            elif advanced_state.get("status") == "finished":
                _finalize_finished_game(player_ids_before)
            game_state = get_game_state(int(user_id))
            final_results = runtime_game.get("final_results") or game_state.get("final_results") or final_results
    room = None
    if anomaly_id is not None:
        try:
            room = get_work_room_payload(int(user_id), int(anomaly_id))
        except Exception:
            room = None
    return {
        "ok": True,
        "player_dead": player_dead,
        "death_reason": str(summary.get("death_reason") or "Был устранен по заказу убийцы."),
        "room": room,
        "game_state": game_state,
        "final_results": final_results,
    }


def resolve_cheaptrick_fatal(user_id, anomaly_id):
    anomaly_id = int(anomaly_id)
    user_id = int(user_id)
    death_reason = "Cheap Trick убил своего владельца после неудачной работы Интуиции."
    recipient_id = None
    with db_connect() as conn:
        player_row = conn.execute(
            "SELECT COALESCE(IsDead, 0) AS IsDead, COALESCE(COMPSLOT, 0) AS COMPSLOT FROM PLAYERS WHERE ID = ?",
            (user_id,),
        ).fetchone()
    if not player_row:
        raise ValueError("Игрок не найден.")
    if int(player_row["IsDead"] or 0) == 0:
        core.set_player_dead(DB_PATH, user_id, reason=death_reason)
    if int(player_row["COMPSLOT"] or 0) == 4:
        recipient_id = _transfer_companion_to_next_player(4, user_id)
    previous_day = int(runtime_game.get("current_day") or _current_day_number() or 1)
    with state_lock:
        player_ids_before = [int(player["id"]) for player in lobby_state["players"]]
        lobby_state["game_assignments"][int(user_id)] = []
    advance_payload = core.advance_turn(DB_PATH, reason="cheaptrick_owner_death")
    core_state = advance_payload.get("state", {})
    runtime_game["started"] = core_state.get("status") == "started"
    runtime_game["current_day"] = int(core_state.get("current_day") or 0)
    runtime_game["winner_id"] = core_state.get("winner_user_id")
    if core_state.get("status") == "started" and int(core_state.get("current_day") or 0) > previous_day:
        runtime_game["day_started_at"] = time.time()
        _cleanup_new_day_effects(player_ids_before)
        _apply_new_day_companion_effects(player_ids_before)
        _prepare_alastor_new_day_task()
        with state_lock:
            lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
    elif core_state.get("status") == "finished":
        _finalize_finished_game(player_ids_before)
    return {
        "ok": True,
        "player_dead": True,
        "death_reason": death_reason,
        "recipient_id": recipient_id,
        "game_state": get_game_state(user_id),
        "final_results": runtime_game.get("final_results") or {"exists": False, "winner_id": None, "winner_name": "", "standings": []},
    }


def get_reset_action_preview(user_id):
    anomaly_id = _current_work_anomaly_id(user_id)
    if int(anomaly_id) != 11:
        raise ValueError("Особый эффект доступен только для аномалии 11.")
    progress = _work_progress(user_id, anomaly_id)
    if int(progress.get("ResetUsed") or 0) == 1:
        raise ValueError("Сброс уже был произведен.")
    with db_connect() as conn:
        player_row = conn.execute("SELECT COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    if not player_row:
        raise ValueError("Игрок не найден.")
    if int(player_row["CP"] or 0) < 1000:
        raise ValueError("Недостаточно СО (нужно 1000).")
    targets = _get_reset_targets(user_id)
    if not targets:
        raise ValueError("Нет доступных целей для применения Сброса.")
    return {
        "action": {
            "intro": "Особый эффект аномалии",
            "effect": "Вы можете заплатить аномалии 1000 СО и выбрать целью игрока, который получит 50 урона по здоровью. Действие доступно 1 раз.",
            "targets": targets,
        }
    }


def apply_reset_action(user_id, target_id):
    anomaly_id = _current_work_anomaly_id(user_id)
    if int(anomaly_id) != 11:
        raise ValueError("Особый эффект доступен только для аномалии 11.")
    valid_targets = {int(target["id"]) for target in _get_reset_targets(user_id)}
    if int(target_id) not in valid_targets:
        raise ValueError("Недопустимая цель для Сброса.")
    with db_connect_write() as conn:
        work_row = conn.execute(
            "SELECT COALESCE(ResetUsed, 0) AS ResetUsed FROM WORK WHERE user_id = ? AND anomaly_id = ?",
            (int(user_id), int(anomaly_id)),
        ).fetchone()
        if not work_row:
            raise ValueError("Рабочая запись не найдена.")
        if int(work_row["ResetUsed"] or 0) == 1:
            raise ValueError("Сброс уже был произведен.")
        player_row = conn.execute(
            "SELECT COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
        if not player_row:
            raise ValueError("Игрок не найден.")
        if int(player_row["CP"] or 0) < 1000:
            raise ValueError("Недостаточно СО (нужно 1000).")
        conn.execute("UPDATE PLAYERS SET CP = COALESCE(CP, 0) - 1000 WHERE ID = ?", (int(user_id),))
        conn.execute("UPDATE WORK SET ResetUsed = 1 WHERE user_id = ? AND anomaly_id = ?", (int(user_id), int(anomaly_id)))
    damage_result = core.apply_damage(DB_PATH, int(target_id), hp_damage=50, sp_damage=0, reason="reset_anomaly_11")
    target_name = f"Игрок {int(target_id)}"
    with db_connect() as conn:
        target_row = conn.execute("SELECT COALESCE(NAME, 'Сотрудник') AS NAME FROM PLAYERS WHERE ID = ?", (int(target_id),)).fetchone()
    if target_row:
        target_name = str(target_row["NAME"] or target_name)
    actor_name = _player_display_name(int(user_id))
    remaining_hp = max(0, int((damage_result or {}).get("hp") or 0))
    _append_game_action_log(
        "effect",
        f"{actor_name} применил Сброс Бетонного осла. Цель — {target_name}: −50 HP, осталось {remaining_hp} HP.",
        int(user_id),
    )
    _queue_target_notice(
        int(target_id),
        "Атака Бетонного осла",
        f"Вы стали целью атаки игрока {actor_name}. Бетонный осёл нанёс 50 урона. Осталось {remaining_hp} HP.",
        source_id=int(user_id),
    )
    return {
        "ok": True,
        "target_id": int(target_id),
        "target_dead": bool(damage_result.get("is_dead")),
        "message": f"{target_name} получает 50 урона по здоровью. 1000 СО списано.",
        "room": get_work_room_payload(int(user_id), int(anomaly_id)),
        "damage": damage_result,
    }


def get_anomaly68_donation_preview(user_id):
    user_id = int(user_id)
    if int(_current_work_anomaly_id(user_id) or 0) != 68:
        raise ValueError("Передать предмет можно только аномалии 68.")
    if int(_safe_global_value(f"A68Boost_{user_id}", 0) or 0) == 1:
        raise ValueError("Предмет уже был передан.")
    with db_connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(INVSLOT1,0) AS i1, COALESCE(SLOT1AMOUNT,0) AS a1, COALESCE(INVSLOT2,0) AS i2, COALESCE(SLOT2AMOUNT,0) AS a2 FROM PLAYERS WHERE ID = ?",
            (user_id,),
        ).fetchone()
        if not row:
            raise ValueError("Игрок не найден.")
        choices = []
        for slot, item_id, amount in ((1, int(row["i1"] or 0), int(row["a1"] or 0)), (2, int(row["i2"] or 0), int(row["a2"] or 0))):
            if item_id in (0, 1) or amount <= 0:
                continue
            item = conn.execute("SELECT COALESCE(NAME, '') AS NAME FROM ITEMS WHERE ID = ?", (item_id,)).fetchone()
            name = str(item["NAME"] or f"ID {item_id}") if item else f"ID {item_id}"
            choices.append({"slot": slot, "item_id": item_id, "name": name, "amount": amount, "label": f"{name} ×{amount}"})
    if not choices:
        raise ValueError("Нет предметов для передачи.")
    return {"action": {"intro": "Передать предмет", "effect": "Выберите предмет, который будет передан аномалии.", "items": choices}}


def get_gish125_feed_preview(user_id, anomaly_id=125):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id or 125)
    if anomaly_id != 125 or int(_current_work_anomaly_id(user_id) or 0) != 125:
        raise ValueError("Покормить Гиша можно только при исследовании аномалии 125.")
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Сейчас не ваш ход.")
    with db_connect() as conn:
        row = _player_row_for_inventory(conn, user_id)
        if not row:
            raise ValueError("Игрок не найден.")
        choices = []
        for slot, data in _inventory_slot_state(row).items():
            item_id, amount = int(data["item_id"]), int(data["amount"])
            if item_id in (0, 1) or amount <= 0:
                continue
            item = conn.execute("SELECT COALESCE(NAME, '') AS NAME FROM ITEMS WHERE ID = ?", (item_id,)).fetchone()
            item_name = str(item["NAME"] or f"ID {item_id}") if item else f"ID {item_id}"
            choices.append({"slot": slot, "item_id": item_id, "name": item_name, "amount": amount, "label": f"{item_name} ×{amount}"})
    return {
        "pending": bool(choices),
        "intro": "Покормить Гиша",
        "effect": "Выберите предмет, который Гиш съест." if choices else "У вас нет предметов, которыми можно покормить Гиша.",
        "choices": choices,
    }


def feed_gish125_item(user_id, selected_slot, anomaly_id=125):
    user_id = int(user_id)
    selected_slot = int(selected_slot or 0)
    preview = get_gish125_feed_preview(user_id, anomaly_id)
    allowed = {int(choice["slot"]): choice for choice in preview.get("choices", [])}
    if selected_slot not in allowed:
        raise ValueError("Выбранного предмета больше нет в инвентаре.")
    choice = allowed[selected_slot]
    with db_connect_write() as conn:
        row = _player_row_for_inventory(conn, user_id)
        slots = _inventory_slot_state(row) if row else {}
        current = slots.get(selected_slot, {})
        if int(current.get("item_id", 0)) != int(choice["item_id"]) or int(current.get("amount", 0)) <= 0:
            raise ValueError("Выбранного предмета больше нет в инвентаре.")
        new_amount = int(current["amount"]) - 1
        conn.execute(
            f"UPDATE PLAYERS SET INVSLOT{selected_slot} = ?, SLOT{selected_slot}AMOUNT = ? WHERE ID = ?",
            (int(choice["item_id"]) if new_amount > 0 else 1, max(0, new_amount), user_id),
        )
        conn.commit()
    _x125_mark("item_used")
    return {
        "ok": True,
        "item_id": int(choice["item_id"]),
        "item_name": str(choice["name"]),
        "message": f"Гиш проглотил предмет «{choice['name']}». Никакого заметного эффекта не произошло.",
        "room": get_work_room_payload(user_id, 125),
        "inventory": get_inventory_payload(user_id),
    }


def get_bloodbot133_preview(user_id, anomaly_id=133):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id or 133)
    if anomaly_id != 133 or int(_current_work_anomaly_id(user_id) or 0) != 133:
        raise ValueError("Пожертвовать кровь можно только при исследовании аномалии 133.")
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Сейчас не ваш ход.")
    _bloodbot_ensure_inited()
    dead = int(_safe_global_value("BLOODBOT_DEAD", 0) or 0) == 1
    hp = max(0, int(_safe_global_value("BLOODBOT_HP", 0) or 0))
    return {
        "pending": not dead,
        "intro": "Пожертвовать кровь",
        "effect": "Выберите, сколько HP пожертвовать. Каждое 1 HP восстановит механизму 10 HP." if not dead else "Механизм уже разрушен. Кровь больше ничему не поможет.",
        "machine_hp": hp,
        "choices": [{"amount": amount, "label": f"−{amount} HP → +{amount * 10} HP механизму"} for amount in (1, 10, 25, 50)] if not dead else [],
    }


def donate_bloodbot133_hp(user_id, amount_hp, anomaly_id=133):
    user_id = int(user_id)
    amount_hp = int(amount_hp or 0)
    preview = get_bloodbot133_preview(user_id, anomaly_id)
    if not preview.get("pending"):
        raise ValueError("Механизм уже разрушен. Кровь больше ничему не поможет.")
    if amount_hp not in (1, 10, 25, 50):
        raise ValueError("Недопустимый объём пожертвования.")
    with db_connect_write() as conn:
        row = conn.execute("SELECT COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?", (user_id,)).fetchone()
        current_hp = int(row["HP"] or 0) if row else 0
        if current_hp <= amount_hp:
            raise ValueError(f"Недостаточно HP. Нужно хотя бы {amount_hp + 1} HP, чтобы пожертвовать {amount_hp}.")
        conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (current_hp - amount_hp, user_id))
        conn.commit()
    gain = amount_hp * 10
    machine_hp = max(0, int(_safe_global_value("BLOODBOT_HP", 0) or 0)) + gain
    core.set_global_value(DB_PATH, "BLOODBOT_HP", machine_hp)
    _x125_mark("damage")
    return {
        "ok": True,
        "amount": amount_hp,
        "gain": gain,
        "machine_hp": machine_hp,
        "message": f"Вы пожертвовали {amount_hp} HP. Механизм восстановил {gain} HP. Текущее HP механизма: {machine_hp}.",
        "room": get_work_room_payload(user_id, 133),
    }


def _pandora_choices_key(user_id):
    return f"PandoraChoices_{int(user_id)}"


def _pandora_resolved_key(user_id):
    return f"PandoraResolved_{int(user_id)}"


def get_pandora_box_preview(user_id, anomaly_id=113):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id or 113)
    if anomaly_id != 113 or int(_current_work_anomaly_id(user_id) or 0) != 113:
        raise ValueError("Ящик Пандоры доступен только при исследовании аномалии 113.")
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Сейчас не ваш ход.")
    if int(_safe_global_value(_pandora_resolved_key(user_id), 0) or 0) == 1:
        raise ValueError("Предмет из Ящика Пандоры уже выбран.")

    saved = _safe_global_value(_pandora_choices_key(user_id), "")
    try:
        item_ids = [int(value) for value in json.loads(str(saved or "[]"))]
    except (TypeError, ValueError, json.JSONDecodeError):
        item_ids = []
    with db_connect() as conn:
        available_rows = conn.execute(
            "SELECT ID, NAME FROM ITEMS WHERE ID NOT IN (0, 1) AND TRIM(COALESCE(NAME, '')) <> '' ORDER BY ID"
        ).fetchall()
        available = {int(row["ID"]): str(row["NAME"]) for row in available_rows}
        item_ids = [item_id for item_id in item_ids if item_id in available]
        if len(item_ids) != 3:
            pool = list(available.keys())
            if not pool:
                raise ValueError("Ящик Пандоры оказался пуст.")
            item_ids = random.sample(pool, min(3, len(pool)))
            core.set_global_value(DB_PATH, _pandora_choices_key(user_id), json.dumps(item_ids))
        choices = [{"item_id": item_id, "name": available[item_id], "label": available[item_id]} for item_id in item_ids]
    return {
        "pending": True,
        "intro": "Ящик Пандоры",
        "effect": "Выберите один предмет:",
        "choices": choices,
    }


def choose_pandora_box_item(user_id, item_id, anomaly_id=113):
    user_id = int(user_id)
    item_id = int(item_id)
    preview = get_pandora_box_preview(user_id, anomaly_id)
    allowed = {int(choice["item_id"]): str(choice["name"]) for choice in preview.get("choices", [])}
    if item_id not in allowed:
        raise ValueError("Этот предмет не был предложен Ящиком Пандоры.")

    granted = True
    inventory_full = False
    if item_id == BRASS_SPHERE_ITEM_ID:
        _give_brass_sphere_to_player(user_id, needs_activate=True)
    else:
        with db_connect_write() as conn:
            granted = bool(_add_item_to_inventory(conn, user_id, item_id, 1))
            conn.commit()
        inventory_full = not granted
        if granted and item_id == VIOLIN_ITEM_ID:
            core.set_global_value(DB_PATH, "ViolinIsTaken", 1)
            core.set_global_value(DB_PATH, "ViolinOwnerPid", user_id)
            if int(_safe_global_value("ViolinDamage", 0) or 0) <= 0:
                core.set_global_value(DB_PATH, "ViolinDamage", 40)
                core.set_global_value(DB_PATH, "ViolinSteals", 0)
            core.set_global_value(DB_PATH, "ViolinOwnerStreak", 1)
            core.set_global_value(DB_PATH, "ViolinTriggeredToday", 0)

    if granted:
        _x125_mark("item_gained")

    core.set_global_value(DB_PATH, _pandora_resolved_key(user_id), 1)
    core.set_global_value(DB_PATH, _pandora_choices_key(user_id), "")
    item_name = allowed[item_id]
    message = (
        f"Вы получили предмет «{item_name}»."
        if granted
        else f"Предмет «{item_name}» не выдан: инвентарь переполнен."
    )
    return {
        "ok": bool(granted),
        "item_id": item_id,
        "item_name": item_name,
        "inventory_full": inventory_full,
        "message": message,
        "room": get_work_room_payload(user_id, 113),
    }


PORTAL116_STAT_LABELS = {
    "stat1": "Выносливость",
    "stat2": "Удача",
    "stat3": "Гибкость ума",
    "stat4": "Адаптация",
}


def _portal116_stage_key(user_id):
    return f"Portal116Stage_{int(user_id)}"


def _portal116_payload(user_id):
    stage = int(_safe_global_value(_portal116_stage_key(user_id), 0) or 0)
    if stage <= 0:
        stage = 1
        core.set_global_value(DB_PATH, _portal116_stage_key(user_id), stage)
    if stage == 1:
        return {
            "pending": True,
            "stage": 1,
            "intro": "Лесной портал",
            "effect": "Можно пройти в портал, чтобы узнать, что находится на той стороне?",
            "choices": [
                {"key": "yes", "label": "Да"},
                {"key": "no", "label": "Нет"},
            ],
        }
    if stage == 2:
        return {
            "pending": True,
            "stage": 2,
            "intro": "По ту сторону портала",
            "effect": "На той стороне растут грибы очень странного цвета. Съесть их?",
            "choices": [
                {"key": "yes", "label": "Да"},
                {"key": "no", "label": "Нет"},
            ],
        }
    if stage == 3:
        return {
            "pending": True,
            "stage": 3,
            "intro": "Прилив сил",
            "effect": (
                "Грибы оказались странными на вкус. Вас охватила сильная головная боль, и вы потеряли сознание. "
                "Придя в себя, вы ощущаете прилив сил. Выберите характеристику для повышения."
            ),
            "choices": [
                {"key": key, "label": f"{label} (+1)"}
                for key, label in PORTAL116_STAT_LABELS.items()
            ],
        }
    return {
        "pending": False,
        "stage": stage,
        "intro": "Лесной портал",
        "effect": "Больше ничего необычного тут нет.",
        "choices": [],
    }


def get_portal116_preview(user_id, anomaly_id=116):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id or 116)
    if anomaly_id != 116 or int(_current_work_anomaly_id(user_id) or 0) != 116:
        raise ValueError("Лесной портал доступен только при исследовании аномалии 116.")
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Сейчас не ваш ход.")
    return _portal116_payload(user_id)


def resolve_portal116_action(user_id, action, anomaly_id=116):
    user_id = int(user_id)
    action = str(action or "").strip().lower()
    current = get_portal116_preview(user_id, anomaly_id)
    stage = int(current.get("stage") or 0)
    if stage in (1, 2) and action == "no":
        core.set_global_value(DB_PATH, _portal116_stage_key(user_id), 4)
        return {
            "ok": True,
            "resolved": True,
            "message": "Больше ничего необычного тут нет.",
            "portal": _portal116_payload(user_id),
            "room": get_work_room_payload(user_id, 116),
        }
    if stage == 1 and action == "yes":
        core.set_global_value(DB_PATH, _portal116_stage_key(user_id), 2)
        return {"ok": True, "resolved": False, "portal": _portal116_payload(user_id)}
    if stage == 2 and action == "yes":
        core.set_global_value(DB_PATH, _portal116_stage_key(user_id), 3)
        return {"ok": True, "resolved": False, "portal": _portal116_payload(user_id)}
    if stage == 3 and action in PORTAL116_STAT_LABELS:
        column = action.upper()
        with db_connect_write() as conn:
            row = conn.execute(
                f"SELECT COALESCE({column}, 1) AS stat_value, COALESCE(HP, 0) AS HP, COALESCE(MAXHP, 100) AS MAXHP FROM PLAYERS WHERE ID = ?",
                (user_id,),
            ).fetchone()
            if not row:
                raise ValueError("Игрок не найден.")
            old_value = int(row["stat_value"] or 1)
            if old_value >= 5:
                raise ValueError(f"Характеристика «{PORTAL116_STAT_LABELS[action]}» уже достигла максимума.")
            new_value = old_value + 1
            if action == "stat1":
                old_hp = int(row["HP"] or 0)
                old_maxhp = int(row["MAXHP"] or 100)
                new_maxhp = min(300, old_maxhp + 50)
                new_hp = min(new_maxhp, old_hp + 50)
                conn.execute(
                    "UPDATE PLAYERS SET STAT1 = ?, HP = ?, MAXHP = ? WHERE ID = ?",
                    (new_value, new_hp, new_maxhp, user_id),
                )
                message = (
                    f"Выносливость повышена до {new_value}. "
                    f"HP: {old_hp} → {new_hp}, максимальное HP: {old_maxhp} → {new_maxhp}."
                )
            else:
                conn.execute(f"UPDATE PLAYERS SET {column} = ? WHERE ID = ?", (new_value, user_id))
                message = f"{PORTAL116_STAT_LABELS[action]} повышена до {new_value}."
            conn.commit()
        core.set_global_value(DB_PATH, _portal116_stage_key(user_id), 4)
        return {
            "ok": True,
            "resolved": True,
            "message": f"Вы чувствуете прилив сил. {message}",
            "portal": _portal116_payload(user_id),
            "room": get_work_room_payload(user_id, 116),
        }
    raise ValueError("Этот вариант сейчас недоступен.")


DICE120_ITEMS = {
    "d1": (14, "D1"),
    "d4": (15, "D4"),
    "d6": (16, "D6"),
    "d20": (17, "D20"),
}


def _dice120_resolved_key(user_id):
    return f"Dice120Resolved_{int(user_id)}"


def get_dice120_preview(user_id, anomaly_id=120):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id or 120)
    if anomaly_id != 120 or int(_current_work_anomaly_id(user_id) or 0) != 120:
        raise ValueError("Набор кубиков доступен только при исследовании аномалии 120.")
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Сейчас не ваш ход.")
    resolved = int(_safe_global_value(_dice120_resolved_key(user_id), 0) or 0) == 1
    return {
        "pending": not resolved,
        "intro": "Набор игральных кубиков",
        "effect": (
            "Вы находите набор странных кубиков. Можно выбрать один и забрать с собой."
            if not resolved else "Кубик из набора уже выбран."
        ),
        "choices": [
            {"key": key, "item_id": item_id, "label": label}
            for key, (item_id, label) in DICE120_ITEMS.items()
        ] if not resolved else [],
    }


def choose_dice120(user_id, choice, anomaly_id=120):
    user_id = int(user_id)
    choice = str(choice or "").strip().lower()
    preview = get_dice120_preview(user_id, anomaly_id)
    if not preview.get("pending"):
        raise ValueError("Кубик из этого набора уже выбран.")
    if choice not in DICE120_ITEMS:
        raise ValueError("Неизвестный кубик.")
    item_id, label = DICE120_ITEMS[choice]
    with db_connect_write() as conn:
        granted = bool(_add_item_to_inventory(conn, user_id, item_id, 1))
        conn.commit()
    if granted:
        _x125_mark("item_gained")
    core.set_global_value(DB_PATH, _dice120_resolved_key(user_id), 1)
    return {
        "ok": granted,
        "choice": choice,
        "item_id": item_id,
        "item_name": label,
        "inventory_full": not granted,
        "message": (
            f"Вы выбрали {label}. Кубик добавлен в инвентарь."
            if granted else f"Нет свободных слотов — {label} не удалось выдать."
        ),
        "room": get_work_room_payload(user_id, 120),
    }


def _pet122_resolved_key(user_id):
    return f"Pet122Resolved_{int(user_id)}"


def get_pet122_preview(user_id, anomaly_id=122):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id or 122)
    if anomaly_id != 122 or int(_current_work_anomaly_id(user_id) or 0) != 122:
        raise ValueError("Взаимодействие доступно только при исследовании аномалии 122.")
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Сейчас не ваш ход.")
    resolved = int(_safe_global_value(_pet122_resolved_key(user_id), 0) or 0) == 1
    return {
        "pending": not resolved,
        "intro": "Кот Вельмондт",
        "effect": "Погладить аномалию?" if not resolved else "Взаимодействие уже завершено.",
        "choices": [
            {"key": "pet", "label": "Погладить"},
            {"key": "skip", "label": "Нет"},
        ] if not resolved else [],
    }


def resolve_pet122_action(user_id, action, anomaly_id=122):
    user_id = int(user_id)
    action = str(action or "").strip().lower()
    preview = get_pet122_preview(user_id, anomaly_id)
    if not preview.get("pending"):
        raise ValueError("Взаимодействие с котом уже завершено.")
    if action == "pet":
        message = "…похоже, что кот не реагирует, хотя в его пустых глазах читается благодарность. Возможно ли?"
    elif action == "skip":
        message = "Кот смотрит сквозь вас."
    else:
        raise ValueError("Неизвестный вариант взаимодействия.")
    core.set_global_value(DB_PATH, _pet122_resolved_key(user_id), 1)
    return {
        "ok": True,
        "action": action,
        "message": message,
        "room": get_work_room_payload(user_id, 122),
    }


def donate_anomaly68_item(user_id, selected_slot):
    user_id = int(user_id)
    if int(_current_work_anomaly_id(user_id) or 0) != 68:
        raise ValueError("Передать предмет можно только аномалии 68.")
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Сейчас не ваш ход.")
    boost_key = f"A68Boost_{user_id}"
    if int(_safe_global_value(boost_key, 0) or 0) == 1:
        raise ValueError("Предмет уже был передан.")
    with db_connect_write() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(INVSLOT1, 0) AS INVSLOT1, COALESCE(SLOT1AMOUNT, 0) AS SLOT1AMOUNT,
                   COALESCE(INVSLOT2, 0) AS INVSLOT2, COALESCE(SLOT2AMOUNT, 0) AS SLOT2AMOUNT
            FROM PLAYERS WHERE ID = ?
            """,
            (user_id,),
        ).fetchone()
        if not row:
            raise ValueError("Игрок не найден.")
        selected_slot = int(selected_slot or 0)
        if selected_slot not in (1, 2):
            raise ValueError("Выберите предмет для передачи.")
        item_column = "INVSLOT1" if selected_slot == 1 else "INVSLOT2"
        amount_column = "SLOT1AMOUNT" if selected_slot == 1 else "SLOT2AMOUNT"
        selected_item_id = int(row[item_column] or 0)
        selected_amount = int(row[amount_column] or 0)
        if selected_item_id in (0, 1) or selected_amount <= 0:
            raise ValueError("Выбранного предмета больше нет в инвентаре.")
        item = conn.execute("SELECT COALESCE(NAME, '') AS NAME FROM ITEMS WHERE ID = ?", (selected_item_id,)).fetchone()
        item_name = str(item["NAME"] or f"ID {selected_item_id}") if item else f"ID {selected_item_id}"
        new_amount = selected_amount - 1
        if selected_slot == 1:
            conn.execute(
                "UPDATE PLAYERS SET INVSLOT1 = ?, SLOT1AMOUNT = ? WHERE ID = ?",
                (selected_item_id if new_amount > 0 else 1, max(0, new_amount), user_id),
            )
        else:
            conn.execute(
                "UPDATE PLAYERS SET INVSLOT2 = ?, SLOT2AMOUNT = ? WHERE ID = ?",
                (selected_item_id if new_amount > 0 else 1, max(0, new_amount), user_id),
            )
        conn.commit()
    core.set_global_value(DB_PATH, boost_key, 1)
    return {
        "ok": True,
        "item_id": selected_item_id,
        "item_name": item_name,
        "message": f"Пожертвован предмет «{item_name}». Шансы повышены на одну ступень до конца исследования.",
        "room": get_work_room_payload(user_id, 68),
    }


INSTRUMENT_CHOICES_106 = {
    "guitar": {"item_id": 29, "name": "Гитара", "message": "Через 3 дня она сработает непредсказуемо…"},
    "drums": {"item_id": 30, "name": "Барабаны", "message": "Пока они у вас, любой полученный урон становится чёрным."},
    "synth": {"item_id": 31, "name": "Синтезатор", "message": "По окончании дня реальность ускорится. Побег становится невозможен."},
    "none": {"item_id": 0, "name": "Ничего", "message": "Базовый шанс всех работ теперь равен 10%."},
}


def get_instrument_choice_preview(user_id, anomaly_id=106):
    if int(anomaly_id) != 106:
        raise ValueError("Выбор инструментов доступен только у аномалии 106.")
    chosen = str(_safe_global_value(f"A106Choice_{int(user_id)}", "") or "")
    return {
        "pending": not bool(chosen),
        "chosen": chosen,
        "intro": "Какой инструмент вы выберете?",
        "effect": "Выберите один вариант. Инструмент займёт место в инвентаре и сразу активирует свой эффект.",
        "choices": [
            {"key": key, "label": value["name"], "description": value["message"]}
            for key, value in INSTRUMENT_CHOICES_106.items()
        ],
    }


def resolve_instrument_choice(user_id, anomaly_id, choice):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id)
    choice = str(choice or "").strip().lower()
    if anomaly_id != 106 or choice not in INSTRUMENT_CHOICES_106:
        raise ValueError("Недоступный выбор инструмента.")
    with db_connect() as conn:
        work = conn.execute("SELECT anomaly_id FROM WORK WHERE user_id = ?", (user_id,)).fetchone()
    if not work or int(work["anomaly_id"] or 0) != 106:
        raise ValueError("Сейчас игрок не исследует аномалию 106.")
    if str(_safe_global_value(f"A106Choice_{user_id}", "") or ""):
        raise ValueError("Инструмент уже был выбран.")
    meta = INSTRUMENT_CHOICES_106[choice]
    replaced = False
    item_id = int(meta["item_id"])
    if item_id > 0:
        with db_connect_write() as conn:
            granted = _add_item_to_inventory(conn, user_id, item_id, 1)
            if not granted:
                conn.execute(
                    "UPDATE PLAYERS SET INVSLOT1 = ?, SLOT1AMOUNT = 1 WHERE ID = ?",
                    (item_id, user_id),
                )
                replaced = True
            conn.commit()
    if choice == "guitar":
        core.set_global_value(DB_PATH, f"GuitarTurnsLeft_{user_id}", 3)
    elif choice == "synth":
        core.set_global_value(DB_PATH, "NoEscape", 1)
        core.set_global_value(DB_PATH, "SYNTH_WARP", 1)
    elif choice == "none":
        core.set_global_value(DB_PATH, "WorkBase10", 1)
    core.set_global_value(DB_PATH, f"A106Choice_{user_id}", choice)
    replacement_note = " Первый слот инвентаря был заменён." if replaced else ""
    return {
        "ok": True,
        "choice": choice,
        "item_id": item_id,
        "message": f"Вы выбрали «{meta['name']}». {meta['message']}{replacement_note}",
        "room": get_work_room_payload(user_id, anomaly_id),
        "inventory": get_inventory_payload(user_id),
    }


def _inventory_slot_state(player_row):
    return {
        1: {"item_id": int(player_row["INVSLOT1"] or 1), "amount": int(player_row["SLOT1AMOUNT"] or 0)},
        2: {"item_id": int(player_row["INVSLOT2"] or 1), "amount": int(player_row["SLOT2AMOUNT"] or 0)},
    }


def _player_row_for_inventory(conn, user_id):
    return conn.execute(
        """
        SELECT COALESCE(INVSLOT1, 1) AS INVSLOT1,
               COALESCE(INVSLOT2, 1) AS INVSLOT2,
               COALESCE(SLOT1AMOUNT, 0) AS SLOT1AMOUNT,
               COALESCE(SLOT2AMOUNT, 0) AS SLOT2AMOUNT,
               COALESCE(HP, 0) AS HP,
               COALESCE(MAXHP, 100) AS MAXHP,
               COALESCE(SP, 0) AS SP,
               COALESCE(MAXSP, 200) AS MAXSP,
               COALESCE(STAT1, 1) AS STAT1,
               COALESCE(STAT4, 1) AS STAT4,
               COALESCE(IsDead, 0) AS IsDead,
               COALESCE(NAME, 'Сотрудник') AS NAME
        FROM PLAYERS
        WHERE ID = ?
        """,
        (int(user_id),),
    ).fetchone()


def _effects_for_player_conn(conn, user_id):
    row = conn.execute(
        f"SELECT {', '.join(core.EFFECT_COLUMNS)} FROM PLAYERS WHERE ID = ?",
        (int(user_id),),
    ).fetchone()
    if not row:
        return []
    return [row[column] for column in core.EFFECT_COLUMNS if row[column] not in (None, "", "0")]


def _clear_all_player_effects_conn(conn, user_id):
    effects = list(_effects_for_player_conn(conn, user_id))
    if not effects:
        return []
    assignments = ", ".join(f"{column} = NULL" for column in core.EFFECT_COLUMNS)
    conn.execute(f"UPDATE PLAYERS SET {assignments} WHERE ID = ?", (int(user_id),))
    return effects


def _save_sue_snapshot(conn, user_id):
    player_row = conn.execute("SELECT * FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    if not player_row:
        return False
    # Competitive points are deliberately outside the rollback. Everything
    # else in PLAYERS (stats, health, stress, inventory, artifact, companion,
    # curses and technical player state) belongs to the saved state.
    payload = {
        "player": {
            key: player_row[key]
            for key in player_row.keys()
            if str(key).upper() not in {"ID", "CP"}
        }
    }
    conn.execute(
        """
        INSERT INTO SUE_SNAPSHOTS (USER_ID, SNAP)
        VALUES (?, ?)
        ON CONFLICT(USER_ID) DO UPDATE SET SNAP = excluded.SNAP
        """,
        (int(user_id), json.dumps(payload, ensure_ascii=False)),
    )
    return True


def _restore_sue_snapshot(conn, user_id):
    row = conn.execute("SELECT SNAP FROM SUE_SNAPSHOTS WHERE USER_ID = ?", (int(user_id),)).fetchone()
    if not row or not row["SNAP"]:
        return False
    try:
        payload = json.loads(row["SNAP"])
    except Exception:
        return False
    player_data = dict((payload or {}).get("player") or {})
    if not player_data:
        return False
    columns = [key for key in player_data.keys() if str(key).upper() not in {"ID", "CP"}]
    if not columns:
        return False
    assignments = ", ".join(f"{column} = ?" for column in columns)
    values = [player_data[column] for column in columns]
    values.append(int(user_id))
    conn.execute(f"UPDATE PLAYERS SET {assignments} WHERE ID = ?", tuple(values))
    conn.execute("DELETE FROM SUE_SNAPSHOTS WHERE USER_ID = ?", (int(user_id),))
    return True


def _add_item_to_inventory(conn, user_id, item_id, amount=1):
    if int(item_id) == int(core.CLAY_ITEM_ID):
        current_holder = int(_safe_global_value("ClayHolder", 0) or 0)
        if current_holder not in (0, int(user_id)):
            return False
        core.set_global_value(DB_PATH, "ClayHolder", int(user_id))
        popup_id = int(_safe_global_value("ClayPopupId", 0) or 0) + 1
        core.set_global_value(DB_PATH, "ClayPopupId", popup_id)
        core.set_global_value(DB_PATH, f"ClayPopup_{int(user_id)}", {
            "id": popup_id,
            "title": "Глиняная статуя",
            "text": "Вы получили Глиняную статую. Она помещена в отдельный специальный слот.",
            "acknowledged": False,
        })
        return True
    row = _player_row_for_inventory(conn, user_id)
    if not row:
        return False
    item_id = int(item_id)
    amount = int(amount)
    slots = _inventory_slot_state(row)
    for slot_idx, info in slots.items():
        if info["item_id"] == item_id and info["amount"] > 0:
            conn.execute(f"UPDATE PLAYERS SET SLOT{slot_idx}AMOUNT = COALESCE(SLOT{slot_idx}AMOUNT, 0) + ? WHERE ID = ?", (amount, int(user_id)))
            if item_id == 8:
                effects = list(_effects_for_player_conn(conn, int(user_id)))
                core._effect_remove_prefix(effects, "IcicleUsed")
                core._effect_token_write(effects, "IcicleMeltDay", int(_current_day_number() or 1) + 3)
                core._save_effects(conn, int(user_id), effects)
            if item_id == 29:
                effects = list(_effects_for_player_conn(conn, int(user_id)))
                core._effect_token_write(effects, "GuitarTurnsLeft", 3)
                core._save_effects(conn, int(user_id), effects)
            if item_id == 31:
                effects = list(_effects_for_player_conn(conn, int(user_id)))
                if "NoEscape" not in effects:
                    effects.append("NoEscape")
                if "SynthWarpPending" not in effects:
                    effects.append("SynthWarpPending")
                core._save_effects(conn, int(user_id), effects)
            return True
    for slot_idx, info in slots.items():
        if info["item_id"] in (0, 1) or info["amount"] <= 0:
            conn.execute(
                f"UPDATE PLAYERS SET INVSLOT{slot_idx} = ?, SLOT{slot_idx}AMOUNT = ? WHERE ID = ?",
                (item_id, amount, int(user_id)),
            )
            if item_id == 8:
                effects = list(_effects_for_player_conn(conn, int(user_id)))
                core._effect_remove_prefix(effects, "IcicleUsed")
                core._effect_token_write(effects, "IcicleMeltDay", int(_current_day_number() or 1) + 3)
                core._save_effects(conn, int(user_id), effects)
            if item_id == 29:
                effects = list(_effects_for_player_conn(conn, int(user_id)))
                core._effect_token_write(effects, "GuitarTurnsLeft", 3)
                core._save_effects(conn, int(user_id), effects)
            if item_id == 31:
                effects = list(_effects_for_player_conn(conn, int(user_id)))
                if "NoEscape" not in effects:
                    effects.append("NoEscape")
                if "SynthWarpPending" not in effects:
                    effects.append("SynthWarpPending")
                core._save_effects(conn, int(user_id), effects)
            return True
    return False


def _consume_inventory_item(conn, user_id, item_id):
    row = _player_row_for_inventory(conn, user_id)
    if not row:
        raise ValueError("Игрок не найден.")
    item_id = int(item_id)
    slots = _inventory_slot_state(row)
    for slot_idx, info in slots.items():
        if info["item_id"] == item_id and info["amount"] > 0:
            new_amount = int(info["amount"]) - 1
            if new_amount > 0:
                conn.execute(f"UPDATE PLAYERS SET SLOT{slot_idx}AMOUNT = ? WHERE ID = ?", (new_amount, int(user_id)))
            else:
                conn.execute(
                    f"UPDATE PLAYERS SET INVSLOT{slot_idx} = 1, SLOT{slot_idx}AMOUNT = 0 WHERE ID = ?",
                    (int(user_id),),
                )
            return max(0, new_amount)
    raise ValueError("У вас нет этого предмета.")


def _player_has_inventory_item(conn, user_id, item_id):
    row = _player_row_for_inventory(conn, user_id)
    if not row:
        return False
    slots = _inventory_slot_state(row)
    return any(info["item_id"] == int(item_id) and info["amount"] > 0 for info in slots.values())


def _rift_stash_item_id():
    try:
        item_id = int(_safe_global_value("RIFT_STASH_ITEM_ID", 0) or 0)
    except (TypeError, ValueError):
        return None
    return item_id if item_id not in (0, 1) else None


def _rift_item_name(conn, item_id):
    row = conn.execute("SELECT NAME FROM ITEMS WHERE ID = ?", (int(item_id),)).fetchone()
    return str(row["NAME"] or f"ID {int(item_id)}") if row else f"ID {int(item_id)}"


def _rift_inventory_choices(conn, user_id):
    row = _player_row_for_inventory(conn, int(user_id))
    if not row:
        raise ValueError("Игрок не найден.")
    choices = []
    for slot_idx, info in _inventory_slot_state(row).items():
        item_id = int(info["item_id"] or 0)
        amount = int(info["amount"] or 0)
        if item_id in (0, 1) or amount <= 0:
            continue
        name = _rift_item_name(conn, item_id)
        choices.append({
            "slot": int(slot_idx),
            "item_id": item_id,
            "amount": amount,
            "name": name,
            "label": f"Слот {slot_idx}: {name} ×{amount}",
        })
    return choices


def _rift_consume_slot(conn, user_id, slot_idx):
    if int(slot_idx) not in (1, 2):
        raise ValueError("Неизвестный слот инвентаря.")
    row = _player_row_for_inventory(conn, int(user_id))
    if not row:
        raise ValueError("Игрок не найден.")
    info = _inventory_slot_state(row)[int(slot_idx)]
    item_id = int(info["item_id"] or 0)
    amount = int(info["amount"] or 0)
    if item_id in (0, 1) or amount <= 0:
        raise ValueError("Выбранный слот пуст.")
    if amount > 1:
        conn.execute(
            f"UPDATE PLAYERS SET SLOT{int(slot_idx)}AMOUNT = ? WHERE ID = ?",
            (amount - 1, int(user_id)),
        )
    else:
        conn.execute(
            f"UPDATE PLAYERS SET INVSLOT{int(slot_idx)} = 1, SLOT{int(slot_idx)}AMOUNT = 0 WHERE ID = ?",
            (int(user_id),),
        )
    return item_id


def get_global_rift_preview(user_id, anomaly_id=135):
    stash_id = _rift_stash_item_id()
    with db_connect() as conn:
        choices = _rift_inventory_choices(conn, int(user_id))
        stash_name = _rift_item_name(conn, stash_id) if stash_id is not None else None
    if stash_id is None:
        effect = (
            "Тонкая рваная щель в пространстве тянется холодом. Можно положить внутрь "
            "один предмет, чтобы он ждал в будущих исследованиях.\n\n"
            "Сейчас разлом пуст. Выберите предмет, который хотите оставить."
        )
        mode = "deposit"
    else:
        effect = (
            "Тонкая рваная щель в пространстве тянется холодом. Внутри мерцает: "
            f"«{stash_name}». Чтобы забрать его, необходимо оставить один предмет взамен."
        )
        mode = "swap"
    return {
        "pending": True,
        "anomaly_id": int(anomaly_id or 135),
        "intro": "Межпространственный разлом",
        "effect": effect,
        "mode": mode,
        "stash_item": ({"item_id": stash_id, "name": stash_name} if stash_id is not None else None),
        "choices": choices,
    }


def resolve_global_rift_action(user_id, action, slot, anomaly_id=135):
    action = str(action or "").strip().lower()
    if action not in ("deposit", "swap"):
        raise ValueError("Неизвестное действие с разломом.")
    with state_lock:
        stash_id = _rift_stash_item_id()
        with db_connect_write() as conn:
            if action == "deposit":
                if stash_id is not None:
                    raise ValueError("Пока вы выбирали, разлом уже заняли. Теперь доступен только обмен.")
                put_id = _rift_consume_slot(conn, int(user_id), int(slot))
                put_name = _rift_item_name(conn, put_id)
                conn.execute(
                    """
                    INSERT INTO GAME_GLOBALS (key, value_text, value_type, updated_at)
                    VALUES ('RIFT_STASH_ITEM_ID', ?, 'int', ?)
                    ON CONFLICT(key) DO UPDATE SET value_text = excluded.value_text,
                        value_type = excluded.value_type, updated_at = excluded.updated_at
                    """,
                    (str(int(put_id)), time.time()),
                )
                message = f"Вы положили в разлом «{put_name}» (1 шт.). Теперь предмет доступен в будущих играх."
                gained_item = False
            else:
                if stash_id is None:
                    raise ValueError("Пока вы выбирали, разлом опустел.")
                row = _player_row_for_inventory(conn, int(user_id))
                if not row:
                    raise ValueError("Игрок не найден.")
                slots = _inventory_slot_state(row)
                can_receive = any(
                    info["item_id"] in (0, 1)
                    or info["amount"] <= 0
                    or (info["item_id"] == int(stash_id) and info["amount"] > 0)
                    for info in slots.values()
                )
                if not can_receive:
                    raise ValueError(f"Нет места, чтобы забрать «{_rift_item_name(conn, stash_id)}». Освободите слот или стакайте.")
                put_id = _rift_consume_slot(conn, int(user_id), int(slot))
                if not _add_item_to_inventory(conn, int(user_id), int(stash_id), 1):
                    _add_item_to_inventory(conn, int(user_id), int(put_id), 1)
                    raise ValueError("Не получилось добавить предмет из разлома в инвентарь.")
                got_name = _rift_item_name(conn, stash_id)
                put_name = _rift_item_name(conn, put_id)
                conn.execute(
                    """
                    INSERT INTO GAME_GLOBALS (key, value_text, value_type, updated_at)
                    VALUES ('RIFT_STASH_ITEM_ID', ?, 'int', ?)
                    ON CONFLICT(key) DO UPDATE SET value_text = excluded.value_text,
                        value_type = excluded.value_type, updated_at = excluded.updated_at
                    """,
                    (str(int(put_id)), time.time()),
                )
                message = f"Обмен завершён: вы получили «{got_name}» (1 шт.) и оставили взамен «{put_name}»."
                gained_item = True
            conn.commit()
    if gained_item:
        _x125_mark("item_gained")
    return {
        "ok": True,
        "message": message,
        "inventory": get_inventory_payload(int(user_id)),
        "room": get_work_room_payload(int(user_id), int(anomaly_id or 135)),
    }


def _mark_item_used(item_id):
    with db_connect_write() as conn:
        conn.execute("UPDATE ITEMS SET IsUsed = 1 WHERE ID = ? AND COALESCE(IsUsed, 0) <> 1", (int(item_id),))


def _remove_effect_exact(player_id, effect_name):
    try:
        core.remove_player_effect(DB_PATH, int(player_id), effect_name)
    except sqlite3.OperationalError:
        pass


def _replace_effect_exact(player_id, old_effect, new_effect):
    effects = list(_safe_player_effects(int(player_id)))
    if old_effect not in effects:
        return False
    effects = [new_effect if effect == old_effect else effect for effect in effects]
    deduplicated = []
    for effect in effects:
        if effect and effect not in deduplicated:
            deduplicated.append(effect)
    with db_connect_write() as conn:
        core._save_effects(conn, int(player_id), deduplicated)
        conn.commit()
    return True


def _toggle_effect_flag(player_id, effect_name):
    effects = list(_safe_player_effects(player_id))
    with db_connect_write() as conn:
        if effect_name in effects:
            effects = [effect for effect in effects if effect != effect_name]
            core._save_effects(conn, int(player_id), effects)
            return False
        effects.append(effect_name)
        core._save_effects(conn, int(player_id), effects)
        return True


def _apply_item_effect(user_id, item_row, anomaly_id):
    item_id = int(item_row["ID"])
    item_name = str(item_row["NAME"] or f"Предмет {item_id}")
    effect_name = str(item_row["EFFECT"] or "").strip()

    with db_connect_write() as conn:
        player = _player_row_for_inventory(conn, user_id)
        if not player:
            raise ValueError("Игрок не найден.")

        if effect_name == "swap_hp_sp":
            hp = int(player["HP"] or 0)
            sp = int(player["SP"] or 0)
            maxhp = int(player["MAXHP"] or 0)
            new_hp = max(0, min(sp, min(300, maxhp if maxhp > 0 else 300)))
            new_sp = max(0, min(hp, 200))
            conn.execute("UPDATE PLAYERS SET HP = ?, SP = ? WHERE ID = ?", (new_hp, new_sp, int(user_id)))
            return _build_item_modal(item_name, f"Здоровье и рассудок поменялись местами. Теперь: {new_hp} HP и {new_sp} SP.")

        if effect_name == "heal_player":
            heal_amount = max(0, int(player["STAT1"] or 0) * 10)
            new_hp = min(int(player["MAXHP"] or 0), int(player["HP"] or 0) + heal_amount)
            conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (new_hp, int(user_id)))
            return _build_item_modal(item_name, f"Восстановлено {heal_amount} HP. Текущее здоровье: {new_hp}/{int(player['MAXHP'] or 0)}.")

        if effect_name == "cowmeat":
            new_hp = min(int(player["MAXHP"] or 0), int(player["HP"] or 0) + 25)
            new_sp = min(int(player["MAXSP"] or 200), int(player["SP"] or 0) + 25)
            conn.execute("UPDATE PLAYERS SET HP = ?, SP = ? WHERE ID = ?", (new_hp, new_sp, int(user_id)))
            return _build_item_modal(item_name, f"Вы получили +25 HP и +25 SP. Теперь: {new_hp}/{int(player['MAXHP'] or 0)} HP и {new_sp}/{int(player['MAXSP'] or 200)} SP.")

        if effect_name == "apple_hp_boost":
            effects = list(_effects_for_player_conn(conn, user_id))
            if core.APPLE_FLAG in effects:
                return _build_item_modal(item_name, "Эффект яблока уже активен до конца исследования.")
            extra_max = int((int(player["MAXHP"] or 0) + 1) / 2)
            extra_cur = int((int(player["HP"] or 0) + 1) / 2)
            effects.append(core.APPLE_FLAG)
            core._effect_token_write(effects, core.TOK_EXTRA_MAX, extra_max)
            core._effect_token_write(effects, core.TOK_EXTRA_CUR, 0)
            core._save_effects(conn, int(user_id), effects)
            conn.execute(
                "UPDATE PLAYERS SET MAXHP = COALESCE(MAXHP,0) + ?, HP = COALESCE(HP,0) + ? WHERE ID = ?",
                (extra_max, extra_cur, int(user_id)),
            )
            return _build_item_modal(item_name, f"До конца исследования получено +{extra_max} к запасу здоровья и +{extra_cur} к текущему здоровью.")

        if effect_name == "icicle_restore_sp":
            existing_effects = list(_effects_for_player_conn(conn, user_id))
            if "IcicleUsed" in existing_effects:
                return _build_item_modal(item_name, "Осколок уже использован и постепенно тает.")
            maxsp = int(player["MAXSP"] or 200)
            sp = int(player["SP"] or 0)
            if sp >= maxsp:
                return _build_item_modal(item_name, f"Рассудок уже на максимуме ({sp}/{maxsp}).")
            conn.execute("UPDATE PLAYERS SET SP = ? WHERE ID = ?", (maxsp, int(user_id)))
            effects = list(_effects_for_player_conn(conn, user_id))
            effects.append("IcicleUsed")
            core._effect_token_write(effects, "IcicleMeltDay", int(_current_day_number() or 1) + 3)
            core._save_effects(conn, int(user_id), effects)
            return _build_item_modal(item_name, f"Рассудок полностью восстановлен: {sp} -> {maxsp}.")

        if effect_name == "oduvani":
            maxsp = int(player["MAXSP"] or 200)
            sp = int(player["SP"] or 0)
            new_sp = min(maxsp, sp + 10)
            conn.execute("UPDATE PLAYERS SET SP = ? WHERE ID = ?", (new_sp, int(user_id)))
            return _build_item_modal(item_name, f"Рассудок немного успокоился: {sp} -> {new_sp}.")

        if effect_name in ("material_cookie", "antimaterial_cookie"):
            effects = list(_effects_for_player_conn(conn, user_id))
            flag_m = "cookie_m_eaten"
            flag_a = "cookie_a_eaten"
            hp = int(player["HP"] or 0)
            maxhp = int(player["MAXHP"] or 0)
            sp = int(player["SP"] or 0)
            maxsp = int(player["MAXSP"] or 200)
            if effect_name == "material_cookie":
                new_hp = min(maxhp, hp + 50)
                conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (new_hp, int(user_id)))
                if flag_m not in effects:
                    effects.append(flag_m)
                extra = ""
                if flag_a in effects:
                    cur_hp = max(0, new_hp - (new_hp // 2))
                    cur_sp = max(0, sp - (sp // 2))
                    conn.execute("UPDATE PLAYERS SET HP = ?, SP = ? WHERE ID = ?", (cur_hp, cur_sp, int(user_id)))
                    effects = [effect for effect in effects if effect not in (flag_m, flag_a)]
                    extra = " Сочетание с антиматериальным печеньем оказалось опасным: -50% HP и -50% SP."
                core._save_effects(conn, int(user_id), effects)
                return _build_item_modal(item_name, f"Восстановлено 50 HP.{extra}")
            new_sp = min(maxsp, sp + 50)
            conn.execute("UPDATE PLAYERS SET SP = ? WHERE ID = ?", (new_sp, int(user_id)))
            if flag_a not in effects:
                effects.append(flag_a)
            extra = ""
            if flag_m in effects:
                cur_hp = max(0, hp - (hp // 2))
                cur_sp = max(0, new_sp - (new_sp // 2))
                conn.execute("UPDATE PLAYERS SET HP = ?, SP = ? WHERE ID = ?", (cur_hp, cur_sp, int(user_id)))
                effects = [effect for effect in effects if effect not in (flag_m, flag_a)]
                extra = " Сочетание с материальным печеньем оказалось опасным: -50% HP и -50% SP."
            core._save_effects(conn, int(user_id), effects)
            return _build_item_modal(item_name, f"Восстановлено 50 SP.{extra}")

        if effect_name == "crunchik":
            new_hp = min(int(player["MAXHP"] or 0), int(player["HP"] or 0) + 5)
            conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (new_hp, int(user_id)))
            added = _add_item_to_inventory(conn, int(user_id), 19, 2)
            suffix = " Добавлено 2x Таралинька." if added else " Но в инвентаре не хватило места для Таралиньки."
            return _build_item_modal(item_name, f"Вы получили +5 HP.{suffix}")

        if effect_name == "taralinka":
            added = _add_item_to_inventory(conn, int(user_id), 20, 5)
            suffix = " Получено 5x Пробутс." if added else " Но инвентарь переполнен, и пробутсы не поместились."
            return _build_item_modal(item_name, suffix.strip())

        if effect_name == "proboots":
            return _build_item_modal(item_name, "…Пробутс использован… Ничего не произошло.")

        if effect_name == "bloody_corn":
            hp_before = int(player["HP"] or 0)
            sp_before = int(player["SP"] or 0)
            hp_after = min(int(player["MAXHP"] or 0), hp_before + 25)
            sp_after = max(0, sp_before - 10)
            conn.execute("UPDATE PLAYERS SET HP = ?, SP = ? WHERE ID = ?", (hp_after, sp_after, int(user_id)))
            return _build_item_modal(item_name, f"HP {hp_before} -> {hp_after}, SP {sp_before} -> {sp_after}. Кукуруза не вызывает сердечный приступ или психоз.")

        if effect_name == "lovecraft_hotdog":
            effects = list(_effects_for_player_conn(conn, user_id))
            if core.HOTDOG_FLAG in effects:
                return _build_item_modal(item_name, "Эффект хот-дога уже активен до конца исследования.")
            effects.append(core.HOTDOG_FLAG)
            core._effect_remove_prefix(effects, core.HOTDOG_PEND_PREFIX)
            core._save_effects(conn, int(user_id), effects)
            return _build_item_modal(item_name, "До конца исследования летальный урон будет оставлять сотрудника на 1 HP.")

        if effect_name == "neko_ark_figure":
            sp_now = int(player["SP"] or 0)
            maxsp = int(player["MAXSP"] or 200)
            restore = max(1, (maxsp - sp_now + 1) // 2)
            new_sp = min(maxsp, sp_now + restore)
            conn.execute("UPDATE PLAYERS SET SP = ? WHERE ID = ?", (new_sp, int(user_id)))
            return _build_item_modal(item_name, f"Восстановлено {new_sp - sp_now} SP. Теперь {new_sp}/{maxsp}.")

        if effect_name == "panacea_of_doom":
            effects = list(_effects_for_player_conn(conn, user_id))
            effects = [
                effect for effect in effects
                if not (
                    str(effect).isdigit()
                    or str(effect) in effect_dictionary.CURSES_CATALOG
                    or str(effect).startswith("PANACEA_DOOM_IN=")
                )
            ]
            core._effect_token_write(effects, "PANACEA_DOOM_IN", 2)
            core._save_effects(conn, int(user_id), effects)
            conn.execute("UPDATE PLAYERS SET HP = COALESCE(MAXHP, 100), SP = COALESCE(MAXSP, 200) WHERE ID = ?", (int(user_id),))
            return _build_item_modal(item_name, "Вы полностью исцелены, рассудок очищен. Но панацея оставила отложенный рок на 2 дня.")

        if effect_name == "ring_red_king_toggle":
            effects = list(_effects_for_player_conn(conn, user_id))
            if core.RING_RED_KING_FLAG in effects:
                effects = [effect for effect in effects if effect != core.RING_RED_KING_FLAG]
                enabled = False
            else:
                effects.append(core.RING_RED_KING_FLAG)
                enabled = True
            core._save_effects(conn, int(user_id), effects)
            return _build_item_modal(item_name, "Кольцо Красного Короля надето." if enabled else "Кольцо Красного Короля снято.")

        if effect_name == "use_timeshift_drug":
            effects = list(_effects_for_player_conn(conn, user_id))
            if core.TSD_FLAG in effects:
                return _build_item_modal(item_name, "Препарат уже действует.")
            effects.append(core.TSD_FLAG)
            core._effect_token_write(effects, core.TSD_ACC_TOK, 0)
            core._save_effects(conn, int(user_id), effects)
            return _build_item_modal(item_name, "Эффективность снижения любого входящего урона стала максимальной.")

        if effect_name == "activate_brass_sphere":
            return _build_item_modal(item_name, "Латунный шар активирован. Его дальнейшая сложная логика пока сведена к прототипу.")

        if effect_name == "use_mimic":
            pool = []
            with state_lock:
                ids = [int(player["id"]) for player in lobby_state.get("players", [])]
            if not ids:
                ids = [int(user_id)]
            rows = conn.execute(
                f"""
                SELECT ID, COALESCE(INVSLOT1, 1) AS INVSLOT1, COALESCE(SLOT1AMOUNT, 0) AS SLOT1AMOUNT,
                       COALESCE(INVSLOT2, 1) AS INVSLOT2, COALESCE(SLOT2AMOUNT, 0) AS SLOT2AMOUNT
                FROM PLAYERS
                WHERE ID IN ({','.join('?' for _ in ids)})
                """,
                tuple(ids),
            ).fetchall()
            for row in rows:
                for slot_key, amount_key in (("INVSLOT1", "SLOT1AMOUNT"), ("INVSLOT2", "SLOT2AMOUNT")):
                    candidate = int(row[slot_key] or 1)
                    amount = int(row[amount_key] or 0)
                    if candidate not in (0, 1, item_id) and amount > 0 and not _is_cursed_item(candidate):
                        pool.append(candidate)
            if not pool:
                return _build_item_modal(item_name, "Мимику не во что превратиться. Он просто исчез.")
            new_item_id = random.choice(pool)
            added = _add_item_to_inventory(conn, int(user_id), new_item_id, 1)
            new_item = conn.execute("SELECT NAME FROM ITEMS WHERE ID = ?", (int(new_item_id),)).fetchone()
            new_name = str(new_item["NAME"] if new_item and new_item["NAME"] else f"Предмет {new_item_id}")
            if not added:
                return _build_item_modal(item_name, f"Мимик попытался превратиться в {new_name}, но инвентарь переполнен.")
            return _build_item_modal(item_name, f"Мимик превратился в предмет {new_name}.")

        if effect_name == "doomsday_button":
            result = _build_item_modal(item_name, "Кнопка Судного дня завершила текущий день.")
            if int(_current_day_number() or 0) == 15:
                result["doomsday_vn"] = True
            return result

        if effect_name == "sue_beatrice":
            effects = list(_effects_for_player_conn(conn, user_id))
            if "sue_saved" not in effects:
                if not _save_sue_snapshot(conn, int(user_id)):
                    return _build_item_modal(item_name, "Не удалось сохранить текущее состояние сотрудника.", "/photo/work_room/fail.png", "Ошибка")
                effects.append("sue_saved")
                core._save_effects(conn, int(user_id), effects)
                result = _build_item_modal(item_name, "Игрушка тихо щелкнула. Текущее состояние сотрудника сохранено.", "/photo/work_room/neutralresult.png", "Сохранение")
                result["sue_phase"] = "save"
                return result
            restored = _restore_sue_snapshot(conn, int(user_id))
            if not restored:
                effects = [effect for effect in effects if effect != "sue_saved"]
                core._save_effects(conn, int(user_id), effects)
                return _build_item_modal(item_name, "Сохраненная точка не найдена. Флаг отката был очищен.", "/photo/work_room/fail.png", "Ошибка")
            # The restored snapshot contains the second remaining use of the
            # toy. Consume it again after rollback so it cannot be duplicated.
            _consume_inventory_item(conn, int(user_id), item_id)
            result = _build_item_modal(item_name, "Состояние сотрудника откатилось к сохраненной точке. Игрушка сломалась.", "/photo/work_room/success.png", "Откат")
            result["sue_phase"] = "restore"
            return result

        if effect_name == "die_d1":
            row = conn.execute(
                """
                SELECT COALESCE(NAME, 'Неизвестная аномалия') AS NAME,
                       COALESCE(PDESCRIPTION, 'Описание отсутствует.') AS PDESCRIPTION
                FROM ANOMALY
                WHERE COALESCE(CLASS_ID, 0) = 5 AND ID NOT IN (4, 13, 33)
                ORDER BY RANDOM()
                LIMIT 1
                """
            ).fetchone()
            if not row:
                return _build_item_modal(item_name, "Не удалось найти ни одной аномалии класса ALEPH.", "/photo/work_room/neutralresult.png", "D1")
            return _build_item_modal(
                item_name,
                f"D1 вытянул описание ALEPH.\n\n{row['NAME']}\n{row['PDESCRIPTION']}",
                "/photo/work_room/neutralresult.png",
                "D1",
            )

        if effect_name == "die_d4":
            rolled = random.randint(1, 4)
            added = _add_item_to_inventory(conn, int(user_id), item_id, 1)
            if added:
                return _build_item_modal(item_name, f"D4 показал значение {rolled}. Кубик породил копию самого себя: +1 D4 в инвентарь.", "/photo/work_room/success.png", "D4")
            return _build_item_modal(item_name, f"D4 показал значение {rolled}, но инвентарь переполнен и копия не поместилась.", "/photo/work_room/neutralresult.png", "D4")

        if effect_name == "die_d6":
            rolled = random.randint(1, 6)
            pct_map = {1: 10, 2: 15, 3: 25, 4: 50, 5: 80, 6: 100}
            pct = int(pct_map[rolled])
            hp = int(player["HP"] or 0)
            maxhp = int(player["MAXHP"] or 0)
            heal = int((maxhp * pct) // 100)
            new_hp = min(maxhp, hp + heal)
            conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (new_hp, int(user_id)))
            return _build_item_modal(
                item_name,
                f"D6 показал значение {rolled}. Восстановлено {new_hp - hp} HP ({pct}% от максимального здоровья). Теперь: {new_hp}/{maxhp}.",
                "/photo/work_room/success.png",
                "D6",
            )

        if effect_name == "die_d20":
            rolled = random.randint(1, 20)
            if rolled == 1:
                hp = int(player["HP"] or 0)
                new_hp = max(1, hp // 2)
                conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (new_hp, int(user_id)))
                return _build_item_modal(item_name, f"D20 показал 1. Здоровье сотрудника сократилось до {new_hp}.", "/photo/work_room/fail.png", "D20")
            if 2 <= rolled <= 5:
                target_sp = 90 + rolled * 10
                conn.execute("UPDATE PLAYERS SET SP = ? WHERE ID = ?", (target_sp, int(user_id)))
                return _build_item_modal(item_name, f"D20 показал {rolled}. Рассудок установлен на {target_sp}.", "/photo/work_room/neutralresult.png", "D20")
            if 6 <= rolled <= 10:
                return _build_item_modal(item_name, f"D20 показал {rolled}. Ничего не произошло.", "/photo/work_room/neutralresult.png", "D20")
            if 11 <= rolled <= 15:
                heal = rolled * 2
                hp = int(player["HP"] or 0)
                maxhp = int(player["MAXHP"] or 0)
                new_hp = min(maxhp, hp + heal)
                conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (new_hp, int(user_id)))
                return _build_item_modal(item_name, f"D20 показал {rolled}. Восстановлено {new_hp - hp} HP. Теперь: {new_hp}/{maxhp}.", "/photo/work_room/success.png", "D20")
            if 16 <= rolled <= 19:
                rt_reward = rolled - 15
                conn.execute("UPDATE PLAYERS SET RT = COALESCE(RT, 0) + ? WHERE ID = ?", (rt_reward, int(user_id)))
                return _build_item_modal(item_name, f"D20 показал {rolled}. Получено {rt_reward} очк. прокачки.", "/photo/work_room/success.png", "D20")
            bonus_now = int(conn.execute("SELECT COALESCE(BONUS, 0) AS BONUS FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()["BONUS"] or 0)
            removed_effects = _clear_all_player_effects_conn(conn, int(user_id))
            cp_reward = 1000 * len(removed_effects)
            conn.execute(
                "UPDATE PLAYERS SET BONUS = COALESCE(BONUS, 0) + 10, CP = COALESCE(CP, 0) + ? WHERE ID = ?",
                (cp_reward, int(user_id)),
            )
            return _build_item_modal(
                item_name,
                f"D20 показал 20. Постоянный бонус к исследованию вырос на 10% ({bonus_now} -> {bonus_now + 10}). Снято эффектов: {len(removed_effects)}. Получено {cp_reward} CP.",
                "/photo/work_room/success.png",
                "D20",
            )

        return _build_item_modal(item_name, "Эффект предмета пока не перенесен в веб-версию.")


def use_inventory_item(user_id, item_id):
    item_id = int(item_id)
    if item_id == BLACK_HOLE_ITEM_ID:
        return use_black_hole(int(user_id))
    anomaly_id = _current_work_anomaly_id(user_id)
    if item_id == BRASS_SPHERE_ITEM_ID:
        _mark_item_used(item_id)
        _x125_mark("item_used")
        result = activate_brass_sphere(int(user_id))
        result["inventory"] = get_inventory_payload(int(user_id))
        result["room"] = get_work_room_payload(int(user_id), anomaly_id) if anomaly_id and not result.get("player_dead") else None
        if result.get("game_state") is None:
            result["game_state"] = get_game_state(int(user_id))
        return result
    item_row = None
    with db_connect_write() as conn:
        item_row = conn.execute(
            """
            SELECT ID, NAME, EFFECT, COALESCE(IsPassive, 0) AS IsPassive, COALESCE(REWARD, -1) AS REWARD
            FROM ITEMS
            WHERE ID = ?
            """,
            (item_id,),
        ).fetchone()
        if not item_row:
            raise ValueError("Предмет не найден.")
        if int(item_row["IsPassive"] or 0) == 1:
            raise ValueError("Пассивный предмет нельзя использовать вручную.")
        owns_special_clay = item_id == core.CLAY_ITEM_ID and int(_safe_global_value("ClayHolder", 0) or 0) == int(user_id)
        if not owns_special_clay and not _player_has_inventory_item(conn, int(user_id), item_id):
            raise ValueError("У вас нет этого предмета.")
        if item_id == core.CLAY_ITEM_ID:
            candidates = _clay_transfer_candidates(int(user_id))
            if not candidates:
                return {
                    "inventory": get_inventory_payload(int(user_id)),
                    "room": get_work_room_payload(int(user_id), anomaly_id) if anomaly_id else None,
                    "item_result": _build_item_modal(
                        "Глиняная статуя",
                        "Статую некому передать: нет другого живого игрока. Предмет остался у вас.",
                        "/photo/work_room/neutralresult.png",
                        "Глиняная статуя",
                    ),
                }
            return {
                "inventory": get_inventory_payload(int(user_id)),
                "room": get_work_room_payload(int(user_id), anomaly_id) if anomaly_id else None,
                "clay_transfer": {"pending": True, "candidates": candidates},
            }
        if item_id not in (27, 35):
            _consume_inventory_item(conn, int(user_id), item_id)
    _x125_mark("item_used")
    item_result = _apply_item_effect(int(user_id), item_row, anomaly_id)
    sue_phase = str(item_result.get("sue_phase") or "")
    should_finalize_item = item_id != 13 or sue_phase == "restore"
    if should_finalize_item:
        _mark_item_used(item_id)
    gained_cp = _grant_item_use_reward(int(user_id), item_id) if should_finalize_item else 0
    if gained_cp > 0:
        modal = item_result.setdefault("modal", {})
        base_text = modal.get("effect") or item_result.get("description") or ""
        extra = f" Получено {gained_cp} CP за использование."
        modal["effect"] = f"{base_text}{extra}".strip()
        item_result["description"] = modal["effect"]
    response = {
        "inventory": get_inventory_payload(int(user_id)),
        "room": get_work_room_payload(int(user_id), anomaly_id) if anomaly_id else None,
        "item_result": item_result,
    }
    if item_id == 23:
        response["doomsday_vn"] = bool(item_result.get("doomsday_vn"))
        if response["doomsday_vn"]:
            core.set_global_value(DB_PATH, "DoomsdayVnPending", int(user_id))
        else:
            response.update(_force_start_next_day_from_doomsday(int(user_id)))
    return response


def _move_clay_to_special_slot(user_id):
    """Migrate legacy/incoming clay from a normal slot into its own slot."""
    user_id = int(user_id)
    holder_id = int(_safe_global_value("ClayHolder", 0) or 0)
    if holder_id == user_id:
        return True
    with db_connect_write() as conn:
        if not _player_has_inventory_item(conn, user_id, core.CLAY_ITEM_ID):
            return False
        _consume_inventory_item(conn, user_id, core.CLAY_ITEM_ID)
        conn.commit()
    core.set_global_value(DB_PATH, "ClayHolder", user_id)
    return True


def get_inventory_payload(user_id):
    _move_clay_to_special_slot(int(user_id))
    with db_connect() as conn:
        player_row = conn.execute(
            """
            SELECT COALESCE(INVSLOT1, 1) AS INVSLOT1,
                   COALESCE(INVSLOT2, 1) AS INVSLOT2,
                   COALESCE(SLOT1AMOUNT, 0) AS SLOT1AMOUNT,
                   COALESCE(SLOT2AMOUNT, 0) AS SLOT2AMOUNT
            FROM PLAYERS
            WHERE ID = ?
            """,
            (int(user_id),),
        ).fetchone()
        if not player_row:
            raise ValueError("Игрок не найден.")

        invslot1 = int(player_row["INVSLOT1"] or 1)
        invslot2 = int(player_row["INVSLOT2"] or 1)
        slot1amount = int(player_row["SLOT1AMOUNT"] or 0)
        slot2amount = int(player_row["SLOT2AMOUNT"] or 0)

        item_rows = conn.execute(
            """
            SELECT ID, NAME, DESCRIPTION, COALESCE(IsPassive, 0) AS IsPassive, COALESCE(IsUsed, 0) AS IsUsed,
                   COALESCE(EFFECT, '') AS EFFECT
            FROM ITEMS
            WHERE ID IN (?, ?) AND ID != 1
            ORDER BY CASE ID WHEN ? THEN 0 WHEN ? THEN 1 ELSE 2 END
            """,
            (invslot1, invslot2, invslot1, invslot2),
        ).fetchall()

    amount_by_item = {}
    if invslot1 != 1:
        amount_by_item[invslot1] = slot1amount
    if invslot2 != 1:
        amount_by_item[invslot2] = slot2amount

    items = []
    for row in item_rows:
        item_id = int(row["ID"])
        item_amount = int(amount_by_item.get(item_id, 0))
        is_passive = int(row["IsPassive"] or 0) == 1
        is_used = int(row["IsUsed"] or 0) == 1
        effect_opened = is_passive or is_used
        shown_desc = (row["DESCRIPTION"] or "—") if effect_opened else "Эффект предмета пока не изучен."
        items.append(
            {
                "id": item_id,
                "name": str(row["NAME"] or f"Предмет {item_id}"),
                "amount": item_amount,
                "is_passive": is_passive,
                "is_used": is_used,
                "effect_opened": effect_opened,
                "description": shown_desc,
                "depleted": item_amount <= 0,
                "can_use": (not is_passive) and item_amount > 0 and bool(str(row["EFFECT"] or "").strip()),
            }
        )

    with db_connect() as conn:
        artifact_row = conn.execute("SELECT COALESCE(ART, 0) AS ART FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    if artifact_row and int(artifact_row["ART"] or 0) == 1:
        used = _black_hole_uses(int(user_id))
        items.append({
            "id": BLACK_HOLE_ITEM_ID,
            "name": "Чёрная дыра",
            "amount": max(0, 3 - used),
            "is_passive": False,
            "is_used": True,
            "effect_opened": True,
            "description": f"Полностью очищает два обычных слота и специальный слот Глиняной статуи. Осталось применений: {max(0, 3 - used)}/3.",
            "depleted": used >= 3,
            "can_use": used < 3,
            "artifact_slot": True,
        })
    if int(_safe_global_value("ClayHolder", 0) or 0) == int(user_id):
        with db_connect() as conn:
            clay_row = conn.execute(
                "SELECT COALESCE(NAME, 'Глиняная статуя') AS NAME, COALESCE(DESCRIPTION, '') AS DESCRIPTION FROM ITEMS WHERE ID = ?",
                (core.CLAY_ITEM_ID,),
            ).fetchone()
        items.append({
            "id": core.CLAY_ITEM_ID,
            "name": str(clay_row["NAME"] if clay_row else "Глиняная статуя"),
            "amount": 1,
            "is_passive": False,
            "is_used": True,
            "effect_opened": True,
            "description": str((clay_row["DESCRIPTION"] if clay_row else "") or "Поглощает урон рассудку и может быть передана другому игроку."),
            "depleted": False,
            "can_use": True,
            "special_slot": "clay",
        })
    return {
        "title": "Инвентарь",
        "empty": len(items) == 0,
        "items": items,
    }


def _rotated_day_first_alive(turn_order, alive_ids, day_number):
    order = [int(pid) for pid in (turn_order or [])]
    alive = {int(pid) for pid in (alive_ids or [])}
    if not order or not alive:
        return None, None
    start_index = (max(1, int(day_number)) - 1) % len(order)
    for offset in range(len(order)):
        index = (start_index + offset) % len(order)
        if order[index] in alive:
            return index, order[index]
    return None, None


def _force_start_next_day_from_doomsday(user_id):
    """Immediately discard the remaining turns and enter the following day."""
    state = core.get_game_state(DB_PATH)
    current_day = int(state.get("current_day") or 1)
    target_day = current_day + 1
    order = [int(pid) for pid in state.get("turn_order", [])]
    alive = [pid for pid in order if not _is_player_dead(pid)]
    with state_lock:
        player_ids = [int(player["id"]) for player in lobby_state.get("players", [])]
        for pid in player_ids:
            lobby_state["game_assignments"][pid] = []
    if not alive:
        finished = core.finish_game(DB_PATH, reason="doomsday_no_survivors")
        _finalize_finished_game(player_ids)
        return {"game_state": get_game_state(int(user_id)), "advanced": True, "finished": True}
    total_days = int(state.get("total_days") or TOTAL_GAME_DAYS)
    if target_day > total_days:
        core.finish_game(DB_PATH, reason="doomsday_days_completed")
        _finalize_finished_game(player_ids)
        return {"game_state": get_game_state(int(user_id)), "advanced": True, "finished": True}
    first_index, first_alive = _rotated_day_first_alive(order, alive, target_day)
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE CORE_GAME_STATE SET current_day = ?, turn_index = ?, current_turn_user_id = ?, last_event_at = ? WHERE id = 1",
            (target_day, first_index, first_alive, time.time()),
        )
        conn.commit()
    core.set_global_value(DB_PATH, "CurrentDay", target_day)
    core.set_global_value(DB_PATH, "ActiveWorker", first_alive)
    runtime_game["current_day"] = target_day
    runtime_game["day_started_at"] = time.time()
    _cleanup_new_day_effects(player_ids)
    _apply_new_day_companion_effects(player_ids)
    _prepare_alastor_new_day_task()
    with state_lock:
        lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
    return {"game_state": get_game_state(int(user_id)), "advanced": True, "finished": False}


def complete_doomsday_vn(user_id):
    """Close the day-15 secret scene and immediately finish the game."""
    user_id = int(user_id)
    if int(_safe_global_value("DoomsdayVnPending", 0) or 0) != user_id:
        raise ValueError("Секретная сцена Кнопки Судного дня уже завершена.")
    core.set_global_value(DB_PATH, "DoomsdayVnPending", 0)
    with state_lock:
        player_ids = [int(player["id"]) for player in lobby_state.get("players", [])]
        for pid in player_ids:
            lobby_state["game_assignments"][pid] = []
    winner_id = determine_winner_by_cp(player_ids)
    core.finish_game(DB_PATH, winner_user_id=winner_id, reason="doomsday_secret_vn_completed")
    runtime_game["winner_id"] = winner_id
    _finalize_finished_game(player_ids)
    return {"ok": True, "game_state": get_game_state(user_id)}


def upgrade_player_stat(user_id, stat_key):
    stat_key = str(stat_key or "").strip().lower()
    meta = STAT_UPGRADE_META.get(stat_key)
    if not meta:
        raise ValueError("Неизвестный атрибут.")

    with db_connect_write() as conn:
        row = conn.execute(
            f"""
            SELECT COALESCE(RT, 0) AS RT,
                   COALESCE({meta['column']}, 1) AS level,
                   COALESCE(HP, 0) AS HP,
                   COALESCE(MAXHP, 100) AS MAXHP,
                   COALESCE(SP, 0) AS SP,
                   COALESCE(MAXSP, 200) AS MAXSP
            FROM PLAYERS
            WHERE ID = ?
            """,
            (int(user_id),),
        ).fetchone()
        if not row:
            raise ValueError("Игрок не найден.")

        current_level = int(row["level"] or 1)
        if _is_sparing_curse_upgrade_blocked(user_id, current_level):
            raise ValueError(f"Вы не можете прокачивать {meta['label']} выше 3, пока кто-то не изучит ALEPH.")
        cost = _stat_upgrade_cost(current_level)
        if cost is None:
            raise ValueError("Этот атрибут уже максимален.")
        available = int(row["RT"] or 0)
        if available < int(cost):
            raise ValueError("Недостаточно очков прокачки.")

        conn.execute(
            f"UPDATE PLAYERS SET RT = RT - ?, {meta['column']} = MIN(5, COALESCE({meta['column']}, 1) + 1) WHERE ID = ?",
            (int(cost), int(user_id)),
        )

        if stat_key == "fortitude":
            conn.execute(
                """
                UPDATE PLAYERS
                SET MAXHP = MIN(COALESCE(MAXHP, 100) + 50, 300),
                    HP = MIN(COALESCE(HP, 0) + 50, MIN(COALESCE(MAXHP, 100) + 50, 300))
                WHERE ID = ?
                """,
                (int(user_id),),
            )
        conn.commit()

    if stat_key == "fortitude":
        _remove_utilizer_if_fortitude_too_high(int(user_id))

    return {"upgrade": get_upgrade_payload(int(user_id))}


def _reward_already_claimed(user_id, anomaly_id):
    progress = _work_progress(user_id, anomaly_id)
    return int(progress.get("RewardClaimed") or 0) == 1


def _grant_research_reward(user_id, anomaly_id, *, require_completed=True):
    progress = _update_work_completion(user_id, anomaly_id)
    if require_completed and int(progress["IsCompleted"] or 0) != 1:
        raise ValueError("Исследование ещё не завершено.")
    if _reward_already_claimed(user_id, anomaly_id):
        return {"details": get_details_payload(user_id, anomaly_id), "reward": {"cp": 0, "rt": 0, "already_claimed": True}}

    anomaly = _get_anomaly_row(anomaly_id)
    if not anomaly:
        raise ValueError("Аномалия не найдена.")
    should_set_aleph_studied = False
    ilvetal_triggered = []
    with db_connect_write() as conn:
        player = conn.execute(
            "SELECT COALESCE(STAT2, 1) AS STAT2, COALESCE(STAT4, 1) AS STAT4 FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
        if not player:
            raise ValueError("Игрок не найден.")
        stat2 = int(player["STAT2"] or 1)
        stat4 = int(player["STAT4"] or 1)
        effective_class_id = int(anomaly["CLASS_ID"] or 1)
        reward_map = BASE_CP_REWARD
        if int(anomaly_id) == 83:
            stored_class = int(_safe_global_value("NonAnomalyClass", 0) or 0)
            effective_class_id = stored_class if stored_class in (1, 2, 3, 4, 5) else 3
            # В оригинальном боте награда 83-й строго равна награде принятого
            # класса и не изменяется адаптивностью, идолом или Щитом смерти.
            reward_cp = int(BASE_CP_REWARD.get(effective_class_id, 1000))
        elif int(_safe_global_value("idolcurse", 0) or 0) == 1:
            reward_map = {class_id: BASE_CP_REWARD.get(6 - class_id, 100) for class_id in range(1, 6)}
            reward_cp = int(reward_map.get(effective_class_id, 100) * _get_stat4_multiplier(stat4))
        else:
            reward_cp = int(reward_map.get(effective_class_id, 100) * _get_stat4_multiplier(stat4))
        effects = _safe_player_effects(user_id)
        if int(anomaly_id) != 83 and "death_shield" in effects:
            reward_cp //= 2
        # In the original bot the fivefold CP payout was a special interaction
        # with anomaly 62, not a blanket multiplier for every researched object.
        if int(anomaly_id) == 62 and "CinderPlague" in effects:
            reward_cp *= 5
        if _should_award_cp_on_item_use(anomaly_id):
            reward_cp = 0
        reward_rt = effective_class_id * (2 if stat2 >= effective_class_id else 1)
        conn.execute("UPDATE PLAYERS SET CP = COALESCE(CP, 0) + ?, RT = COALESCE(RT, 0) + ? WHERE ID = ?", (reward_cp, reward_rt, int(user_id)))
        if effective_class_id == 5 and int(_safe_global_value("AlephWasStudied", 0) or 0) == 0:
            should_set_aleph_studied = True
        conn.execute(
            "UPDATE WORK SET RewardClaimed = 1 WHERE user_id = ? AND anomaly_id = ?",
            (int(user_id), int(anomaly_id)),
        )
        if not _is_guest_user(user_id):
            studied_cursor = conn.execute(
                "INSERT OR IGNORE INTO PLAYER_STUDIED_ANOMALIES (user_id, anomaly_id) VALUES (?, ?)",
                (int(user_id), int(anomaly_id)),
            )
            if int(studied_cursor.rowcount or 0) > 0:
                conn.execute(
                    "UPDATE ANOMALY SET IsDone = COALESCE(IsDone, 0) + 1 WHERE ID = ?",
                    (int(anomaly_id),),
                )
        sync_leaderboard_entry(int(user_id), conn=conn)
        conn.commit()
    if should_set_aleph_studied:
        _x125_mark("aleph")
        with state_lock:
            active_ids = [int(player["id"]) for player in lobby_state.get("players", [])]
        if not active_ids:
            active_ids = [int(user_id)]
        core.set_global_value(DB_PATH, "AlephWasStudied", 1)
        ilvetal_triggered = _apply_ilvetal_aleph_trigger(active_ids)
    return {
        "details": get_details_payload(user_id, anomaly_id),
        "reward": {"cp": reward_cp, "rt": reward_rt, "already_claimed": False},
        "ilvetal_triggered": ilvetal_triggered,
    }


def _apply_post_research_companion_effects(user_id, anomaly_id, reward_payload):
    companion_id = _player_companion_id(int(user_id))
    updated_reward = dict(reward_payload or {})
    if companion_id == 13:
        effects = set(core.list_player_effects(DB_PATH, int(user_id)))
        if core.COMP13_TOKEN in effects:
            with db_connect_write() as conn:
                row = conn.execute("SELECT COALESCE(RT, 0) AS RT FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
                if row:
                    current_rt = int(row["RT"] or 0)
                    new_rt = max(0, current_rt - 1)
                    conn.execute("UPDATE PLAYERS SET RT = ? WHERE ID = ?", (int(new_rt), int(user_id)))
                    conn.commit()
            updated_reward["rt"] = max(0, int(updated_reward.get("rt") or 0) - 1)
    return updated_reward


def _finish_temporary_research_items(user_id):
    """Remove effects that last through one research and resolve their aftermath."""
    user_id = int(user_id)
    hotdog_killed = False
    with db_connect_write() as conn:
        effects = list(_effects_for_player_conn(conn, user_id))
        if core.APPLE_FLAG in effects:
            extra_max = int(core._effect_token_read(effects, core.TOK_EXTRA_MAX, 0) or 0)
            core._effect_remove_prefix(effects, core.APPLE_FLAG)
            core._effect_remove_prefix(effects, core.TOK_EXTRA_MAX)
            core._effect_remove_prefix(effects, core.TOK_EXTRA_CUR)
            if extra_max > 0:
                conn.execute(
                    "UPDATE PLAYERS SET MAXHP = MAX(1, COALESCE(MAXHP,1) - ?), HP = MIN(COALESCE(HP,0), MAX(1, COALESCE(MAXHP,1) - ?)) WHERE ID = ?",
                    (extra_max, extra_max, user_id),
                )
        hotdog_active = core.HOTDOG_FLAG in effects
        hotdog_pending = int(core._effect_token_read(effects, core.HOTDOG_PEND_PREFIX, 0) or 0) == 1
        core._effect_remove_prefix(effects, core.HOTDOG_FLAG)
        core._effect_remove_prefix(effects, core.HOTDOG_PEND_PREFIX)
        core._save_effects(conn, user_id, effects)
        conn.commit()
        hotdog_killed = bool(hotdog_active and hotdog_pending)
    if hotdog_killed:
        core.set_player_dead(DB_PATH, user_id, reason="Отложенный урон Хот-дога Лавкрафта")
    return {"hotdog_killed": hotdog_killed}


def _get_alastor_finish_payload(user_id, anomaly_id):
    state = _alastor_current_task_state(int(user_id))
    if state and int(state.get("task_id") or 0) == 10:
        visual = _alastor_task_visual(4)
        return {
            "pending": True,
            "final_task": True,
            "nameplate": "Аластор",
            "portrait": visual["portrait"],
            "background": visual["background"],
            "text": "ПОРА УМИРАТЬ",
            "confirm_label": "Умереть",
        }
    if state and int(state.get("task_id") or 0) == 7:
        return None
    return _resolve_alastor_task_result(int(user_id), int(anomaly_id))


def resolve_alastor_final_task(user_id):
    state = _alastor_current_task_state(int(user_id))
    if not state or int(state.get("task_id") or 0) != 10 or int(state.get("mood") or 0) != 4:
        raise ValueError("Финальное задание Аластора сейчас недоступно.")
    death_reason = "Бездушная оболочка сотрудника осталась в камере..."
    core.set_player_dead(DB_PATH, int(user_id), reason=death_reason)
    core.set_global_value(DB_PATH, "AlastorTaskShownDay", int(state.get("day") or _current_day_number() or 0))
    _clear_alastor_task_runtime()
    game_state = _advance_after_nonwork_death(int(user_id), "alastor_final_mood")
    return {
        "ok": True,
        "player_dead": True,
        "death_reason": death_reason,
        "game_state": game_state,
        "final_results": game_state.get("final_results"),
    }


def _build_details_payload(user_id, anomaly_id):
    _ensure_work_entry(user_id, anomaly_id)
    anomaly = _get_anomaly_row(anomaly_id)
    if not anomaly:
        raise ValueError("Аномалия не найдена.")
    progress = _update_work_completion(user_id, anomaly_id)
    with db_connect() as conn:
        player = conn.execute(
            """SELECT COALESCE(RP, 0) AS RP, COALESCE(ART, 0) AS ART,
                      COALESCE(STAT1, 1) AS STAT1, COALESCE(STAT2, 1) AS STAT2,
                      COALESCE(STAT3, 1) AS STAT3, COALESCE(STAT4, 1) AS STAT4
               FROM PLAYERS WHERE ID = ?""",
            (int(user_id),),
        ).fetchone()
    devil_sight = bool(player and _player_has_effect(int(user_id), "DevilsDeal"))
    rp_hidden = bool(
        _player_has_effect(int(user_id), "NoResult")
        or _player_has_effect(int(user_id), "NoResultPermanent")
    )
    preferences = []
    if devil_sight:
        preference_meta = (
            ("intuition", "Интуиция", "STAT1", "FortitudeIcon.png"),
            ("insight", "Понимание", "STAT2", "JusticeIcon.png"),
            ("affection", "Привязанность", "STAT3", "PrudenceIcon.png"),
            ("suppression", "Подавление", "STAT4", "TemperanceIcon.png"),
        )
        with db_connect() as conn:
            for work_key, label, stat_key, icon_name in preference_meta:
                level = max(1, min(5, int(player[stat_key] or 1)))
                chance_row = conn.execute(
                    f"SELECT COALESCE({work_key}{level}, 0) AS chance FROM ANOMALY WHERE ID = ?",
                    (int(anomaly_id),),
                ).fetchone()
                preferences.append({
                    "key": work_key,
                    "label": label,
                    "stat_level": level,
                    "chance": (
                        int(calculate_work_chance(int(anomaly_id), work_key, int(user_id))["chance"] or 0)
                        if int(anomaly_id) == 105
                        else (int(chance_row["chance"] or 0) if chance_row else 0)
                    ),
                    "icon": f"/photo/stats/{icon_name}",
                })
    hints = _anomaly_hint_list(anomaly)
    damage = _get_damage_display(anomaly["CLASS_ID"], anomaly["DMGTYPE"])
    thresholds = _result_thresholds(anomaly["CLASS_ID"])
    hidden_hint_text = (anomaly.get("HINTHIDDEN") or "").strip()
    hidden_hint_exists = bool(hidden_hint_text)
    hidden_hint_access = _player_has_hidden_hint_artifact(user_id)
    pending_companion = _pending_companion_offer(progress)
    skibidi_active = _player_has_effect(int(user_id), "skibidi")
    hint_cards = []
    unlocked_hints = int(progress["hintunlocked"] or 0)
    for index, text in enumerate(hints, start=1):
        unlocked = index <= unlocked_hints
        pending_contract = bool(
            int(anomaly["ID"] or 0) == 19
            and int(progress.get("ContractOfferPending") or 0) == 1
            and index == 2
        )
        pending_stat_conversion = bool(
            int(anomaly["ID"] or 0) == 21
            and int(progress.get("StatConversionPending") or 0) == 1
            and index == 1
        )
        pending_choose_bonus = bool(
            int(anomaly["ID"] or 0) == 31
            and int(progress.get("PendingChooseBonus") or 0) == 1
            and index == 1
        )
        pending_death_shield = bool(
            int(anomaly["ID"] or 0) == 35
            and int(progress.get("DeathShieldOfferPending") or 0) == 1
            and index == 1
        )
        pending_altar_offering = bool(
            int(anomaly["ID"] or 0) == 37
            and int(progress.get("AltarOfferingPending") or 0) == 1
            and index == 1
        )
        pending_devil_deal = bool(
            int(anomaly["ID"] or 0) == 41
            and int(progress.get("DevilDealPending") or 0) == 1
            and index == 2
        )
        pending_free_stat = bool(
            int(anomaly["ID"] or 0) == 49
            and int(progress.get("FreeStatPending") or 0) == 1
            and index == 2
        )
        pending_curse137 = bool(
            int(anomaly["ID"] or 0) == 137
            and int(progress.get("Curse137Pending") or 0) == 1
            and index == 1
        )
        hint_cards.append(
            {
                "index": index,
                "unlocked": unlocked,
                "cost": _hint_unlock_cost(index - 1),
                "text": (_skibidi_text(user_id, anomaly_id, "hint", index) if skibidi_active else text) if unlocked else None,
                "pending_companion": bool(pending_companion and int(pending_companion["hint_index"]) == int(index)),
                "pending_contract": pending_contract,
                "pending_stat_conversion": pending_stat_conversion,
                "pending_choose_bonus": pending_choose_bonus,
                "pending_death_shield": pending_death_shield,
                "pending_altar_offering": pending_altar_offering,
                "pending_devil_deal": pending_devil_deal,
                "pending_free_stat": pending_free_stat,
                "pending_curse137": pending_curse137,
            }
        )
    photo_ref = (anomaly.get("PHOTO") or "").strip()
    photo_url = f"/photo/anomaly/{photo_ref}.png" if photo_ref else "/photo/work_room/404.png"
    return {
        "anomaly_id": int(anomaly["ID"]),
        "rp": None if rp_hidden else (int(player["RP"] or 0) if player else 0),
        "rp_hidden": rp_hidden,
        "progress_percent": _progress_percent(progress),
        "progress": progress,
        "base_unlock_cost": BASE_RESEARCH_COST,
        "description_unlock_cost": DESCRIPTION_COST,
        "base_unlocked": int(progress["photounlocked"] or 0) == 1,
        "description_unlocked": int(progress["descriptionunlocked"] or 0) == 1,
        "can_finish": int(progress["IsCompleted"] or 0) == 1,
        "reward_claimed": _reward_already_claimed(user_id, anomaly_id),
        "base_info": {
            "photo_url": photo_url,
            "name": anomaly["NAME"],
            "code_name": str(anomaly.get("codename") or anomaly["ID"]),
            "risk_label": (RISK_META.get(int(anomaly["CLASS_ID"] or 0), {}) or {}).get("label", "UNKNOWN"),
            "risk_color": DETAIL_RISK_COLORS.get(int(anomaly["CLASS_ID"] or 0), "#ffffff"),
            "dmg_type": damage["label"],
            "dmg_amount": damage["amount"],
            "good_range": thresholds["good"],
            "bad_range": thresholds["bad"],
        },
        "hidden_hint": {
            "exists": hidden_hint_exists,
            "can_open": hidden_hint_access,
            "unlocked": int(progress.get("HiddenHintUnlocked") or 0) == 1,
            "text": (_skibidi_text(user_id, anomaly_id, "hidden") if skibidi_active else hidden_hint_text) if hidden_hint_access else None,
        },
        "companion_offer": _build_companion_offer_payload(user_id, anomaly_id, progress),
        "choose_bonus_pending": bool(int(progress.get("PendingChooseBonus") or 0) == 1 and int(anomaly_id) == 31),
        "hints": hint_cards,
        "description": _skibidi_text(user_id, anomaly_id, "description") if skibidi_active else (anomaly["DESCRIPTION"] or "Описание пока отсутствует."),
        "klipota": int(anomaly["KLIPOTA"] or 0) if int(progress["photounlocked"] or 0) == 1 else "?",
        "escape_text": "НЕ СБЕГАЕТ" if int(progress["photounlocked"] or 0) == 1 else "",
        "chance_locked": not devil_sight,
        "preferences": preferences,
    }


def get_details_payload(user_id, anomaly_id):
    return _build_details_payload(user_id, anomaly_id)


def _spend_rp(user_id, amount):
    with db_connect_write() as conn:
        row = conn.execute("SELECT COALESCE(RP, 0) AS RP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        current = int(row["RP"] or 0) if row else 0
        if current < amount:
            raise ValueError("Недостаточно RP.")
        conn.execute("UPDATE PLAYERS SET RP = RP - ? WHERE ID = ?", (int(amount), int(user_id)))
        conn.commit()


def _assert_research_not_blocked(user_id, anomaly_id):
    progress = _work_progress(user_id, anomaly_id)
    if _research_is_locked(progress):
        raise ValueError(_research_lock_reason(progress))
    return progress


def unlock_base_info(user_id, anomaly_id):
    _assert_current_turn(user_id)
    if int(anomaly_id) == 12:
        raise ValueError("Базовая информация для этого объекта недоступна.")
    if _player_has_effect(int(user_id), "BlockedPhoto"):
        raise ValueError("Базовая информация для этого объекта недоступна из-за эффекта аномалии.")
    _ensure_work_entry(user_id, anomaly_id)
    progress = _assert_research_not_blocked(user_id, anomaly_id)
    damage_result = None
    if int(progress["photounlocked"] or 0) != 1:
        hint_count_before = int(progress.get("hintunlocked") or 0)
        _spend_rp(user_id, BASE_RESEARCH_COST)
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE WORK SET photounlocked = 1 WHERE user_id = ? AND anomaly_id = ?",
                (int(user_id), int(anomaly_id)),
            )
            conn.commit()
        _reset_player_penalty(int(user_id))
        if int(anomaly_id) == 27 and hint_count_before < 3:
            damage_result = core.apply_damage(
                DB_PATH,
                int(user_id),
                hp_damage=25,
                sp_damage=25,
                reason="anomaly27_photo_open",
            )
    _update_work_completion(user_id, anomaly_id)
    return {
        "details": get_details_payload(user_id, anomaly_id),
        "room": get_work_room_payload(user_id, anomaly_id),
        "damage": damage_result,
    }


def unlock_description_info(user_id, anomaly_id):
    _assert_current_turn(user_id)
    if int(anomaly_id) == 12:
        raise ValueError("Полное описание для этого объекта недоступно.")
    if _player_has_effect(int(user_id), "BlockedDescription"):
        raise ValueError("Полное описание для этого объекта недоступно из-за эффекта аномалии.")
    _ensure_work_entry(user_id, anomaly_id)
    progress = _assert_research_not_blocked(user_id, anomaly_id)
    if int(progress["descriptionunlocked"] or 0) != 1:
        _spend_rp(user_id, DESCRIPTION_COST)
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE WORK SET descriptionunlocked = 1 WHERE user_id = ? AND anomaly_id = ?",
                (int(user_id), int(anomaly_id)),
            )
            conn.commit()
        _reset_player_penalty(int(user_id))
    _update_work_completion(user_id, anomaly_id)
    return {
        "details": get_details_payload(user_id, anomaly_id),
        "room": get_work_room_payload(user_id, anomaly_id),
    }


def unlock_next_hint(user_id, anomaly_id):
    _assert_current_turn(user_id)
    _ensure_work_entry(user_id, anomaly_id)
    progress = _assert_research_not_blocked(user_id, anomaly_id)
    if int(anomaly_id) == 19 and int(progress.get("ContractOfferPending") or 0) == 1:
        raise ValueError("Сначала примите предложение контракта или откажитесь от него.")
    if int(anomaly_id) == 21 and int(progress.get("StatConversionPending") or 0) == 1:
        raise ValueError("Сначала завершите обмен характеристик или откажитесь от него.")
    if int(anomaly_id) == 31 and int(progress.get("PendingChooseBonus") or 0) == 1:
        raise ValueError("Сначала завершите разговор с аномалией, выбрав «Как уйти?».")
    if int(anomaly_id) == 35 and int(progress.get("DeathShieldOfferPending") or 0) == 1:
        raise ValueError("Сначала примите предложение аномалии.")
    if int(anomaly_id) == 37 and int(progress.get("AltarOfferingPending") or 0) == 1:
        raise ValueError("Без подношения дальнейшие подсказки недоступны.")
    if int(anomaly_id) == 41 and int(progress.get("DevilDealPending") or 0) == 1:
        raise ValueError("Сначала ответьте на предложение сделки.")
    if int(anomaly_id) == 49 and int(progress.get("FreeStatPending") or 0) == 1:
        raise ValueError("Сначала выберите характеристику для дара.")
    if int(anomaly_id) == 137 and int(progress.get("Curse137Pending") or 0) == 1:
        raise ValueError("Сначала завершите создание проклятия.")
    current = int(progress["hintunlocked"] or 0)
    total = int(progress["hintcount"] or 0)
    if current >= total:
        return {"details": get_details_payload(user_id, anomaly_id), "effect_result": None}
    next_slot = current + 1
    if int(anomaly_id) == 71 and int(next_slot) == 2:
        first_work = str(_safe_global_value("first_work_type", "") or "").strip()
        if not first_work:
            raise ValueError("Сначала выполните первую работу — старуха должна сделать первое предсказание.")
    anomaly = _get_anomaly_row(anomaly_id)
    _spend_rp(user_id, _hint_unlock_cost(current))
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET hintunlocked = ? WHERE user_id = ? AND anomaly_id = ?",
            (next_slot, int(user_id), int(anomaly_id)),
        )
        if int(anomaly_id) == 6 and int(next_slot) >= 3:
            conn.execute("UPDATE PLAYERS SET PisosCurseRevealed = 1 WHERE ID = ?", (int(user_id),))
        if int(anomaly_id) == 6 and int(next_slot) >= int(total):
            conn.execute("UPDATE PLAYERS SET FleeIsDeathRevealed = 1 WHERE ID = ?", (int(user_id),))
        conn.commit()
    _reset_player_penalty(int(user_id))
    _update_work_completion(user_id, anomaly_id)
    if int(anomaly_id) == 3 and int(next_slot) >= int(total):
        with db_connect_write() as conn:
            player_row = conn.execute(
                "SELECT COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID = ?",
                (int(user_id),),
            ).fetchone()
            cp_before = int(player_row["CP"] or 0) if player_row else 0
            cp_eaten = min(200, max(0, cp_before))
            conn.execute(
                "UPDATE PLAYERS SET CP = MAX(0, COALESCE(CP, 0) - 200) WHERE ID = ?",
                (int(user_id),),
            )
            conn.commit()
        return {
            "details": get_details_payload(user_id, anomaly_id),
            "room": get_work_room_payload(user_id, anomaly_id),
            "effect_result": {
                "status": "implemented",
                "title": "АНОМАЛИЯ СЪЕЛА 200 СО",
                "description": "Кот был слишком голоден...",
                "cp_lost": cp_eaten,
                "modal": {
                    "intro": "АНОМАЛИЯ СЪЕЛА 200 СО",
                    "effect": "Кот был слишком голоден...",
                    "icon": "/photo/work_room/badresult.png",
                    "iconAlt": "Аномалия съела 200 СО",
                },
            },
        }
    if int(anomaly_id) == 82 and int(next_slot) == 2:
        with db_connect() as conn:
            player_row = conn.execute(
                "SELECT COALESCE(KLIPOTA, 0) AS KLIPOTA FROM PLAYERS WHERE ID = ?",
                (int(user_id),),
            ).fetchone()
        klipota_at_open = max(0, int(player_row["KLIPOTA"] or 0)) if player_row else 0
        damage_amount = klipota_at_open * 15 if klipota_at_open > 0 else 100
        damage = core.apply_damage(
            DB_PATH,
            int(user_id),
            hp_damage=int(damage_amount),
            sp_damage=0,
            reason="anomaly82_second_hint",
        )
        description = (
            f"Накопленная клипота ({klipota_at_open}) отозвалась болью. Получено {damage_amount} урона."
            if klipota_at_open > 0
            else "Клипота не была накоплена. Аномалия нанесла 100 урона."
        )
        effect_result = {
            "status": "implemented",
            "title": "Воздействие аномалии",
            "description": description,
            "klipota_at_open": klipota_at_open,
            "damage_amount": damage_amount,
            "damage": damage,
            "modal": {
                "intro": "Воздействие аномалии",
                "effect": description,
                "icon": "/photo/work_room/badresult.png",
                "iconAlt": "Урон от аномалии 82",
            },
        }
        result_payload = {
            "details": get_details_payload(user_id, anomaly_id),
            "effect_result": effect_result,
        }
        if bool(damage.get("is_dead")):
            death_reason = "Погиб от воздействия аномалии 82"
            game_state = _advance_after_nonwork_death(int(user_id), "anomaly82_second_hint")
            effect_result["fatal_after_modal"] = {"reason": death_reason, "game_state": game_state}
            result_payload.update({
                "player_dead": True,
                "death_reason": death_reason,
                "game_state": game_state,
                "final_results": game_state.get("final_results"),
            })
        else:
            result_payload["room"] = get_work_room_payload(int(user_id), int(anomaly_id))
        return result_payload
    if int(anomaly_id) == 51 and int(next_slot) == 1:
        return {
            "details": get_details_payload(user_id, anomaly_id),
            "room": get_work_room_payload(user_id, anomaly_id),
            "effect_result": {
                "status": "implemented",
                "title": "Укажите вес",
                "description": "Введите свой настоящий вес.",
                "event": {
                    "type": "anomaly51_number_input",
                    "anomaly_id": int(anomaly_id),
                },
            },
        }
    if int(anomaly_id) == 12 and int(next_slot) >= int(total):
        codename = _anomaly_codename(anomaly)
        player_name = "Сотрудник"
        with db_connect() as conn:
            player_row = conn.execute("SELECT COALESCE(NAME, 'Сотрудник') AS NAME FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        if player_row:
            player_name = str(player_row["NAME"] or player_name)
        cat_saved = _player_companion_id(int(user_id)) == 6
        attack_text = (
            f"Пока сотрудник {player_name} был занят прочтением протокола, он почувствовал шевеление у себя за спиной. "
            f"Он обернулся и на этом моменте на камере, через которую происходило наблюдение за работой, появились помехи. "
            f"Когда помехи кончились, в камере остался лишь объект \"{codename}\". Сотрудник пропал без вести."
        )
        if cat_saved:
            attack_text += " … Атаку отразил компаньон"
        effect_result = {
            "status": "implemented",
            "title": "Аномалия атаковала!",
            "description": "Пока сотрудник был занят прочтением протокола, он почувствовал шевеление у себя за спиной.",
            "modal": {
                "intro": "Аномалия атаковала!",
                "effect": attack_text,
                "icon": "/photo/work_room/badresult.png",
                "iconAlt": "Аномалия атаковала",
            },
            "deferred_fatal_action": {
                "type": "anomaly12_last_hint",
                "anomaly_id": int(anomaly_id),
            },
        }
        return {"details": get_details_payload(user_id, anomaly_id), "effect_result": effect_result, "game_state": get_game_state(int(user_id))}
    effect_name = _get_hint_effect_name(anomaly, next_slot)
    # The Lava Salamander offers companionship on its first revealed hint.
    # Ignore the legacy database binding on hint 2 so it cannot trigger twice.
    if int(anomaly_id) == 112:
        effect_name = "salamander" if int(next_slot) == 1 else (
            None if effect_name == "salamander" else effect_name
        )
    if int(anomaly_id) == 60 and int(next_slot) == 1:
        effect_name = "give_brass_sphere"
    if effect_name in COMPANION_OFFER_EFFECTS:
        _queue_companion_offer(user_id, anomaly_id, next_slot, effect_name, COMPANION_OFFER_EFFECTS[effect_name])
        return {
            "details": get_details_payload(user_id, anomaly_id),
            "effect_result": {
                "status": "implemented",
                "companion_offer": _build_companion_offer_payload(user_id, anomaly_id),
            },
        }
    effect_result = None
    effect_result_for_log = None
    if effect_name:
        with state_lock:
            active_effect_player_ids = [int(player["id"]) for player in lobby_state.get("players", [])]
        if not active_effect_player_ids:
            try:
                active_effect_player_ids = [int(pid) for pid in core.get_game_state(DB_PATH).get("turn_order", [])]
            except sqlite3.OperationalError:
                active_effect_player_ids = [int(user_id)]
        effect_result = anomaly_effects.execute_hint_effect(
            effect_name,
            player_id=int(user_id),
            anomaly_id=int(anomaly_id),
            hint_slot=int(next_slot),
            db_path=DB_PATH,
            runtime_state={
                "active_player_ids": active_effect_player_ids,
                "player_triggered_effects": {int(user_id): _current_psychosis_id(int(user_id)) is not None},
            },
        )
        effect_result_for_log = effect_result
        _x125_mark_effect_result(effect_result, anomaly_id, effect_name)
        if str(effect_result.get("status") or "") == "missing":
            effect_result = {
                "status": "missing",
                "title": "404",
                "description": "404: нет активного кода для эффекта",
                "effect_name": effect_name,
                "hint_slot": int(next_slot),
            }
        # Проклятье Романа действует с первой подсказки, но не объявляется
        # игроку и остаётся неопознанным до открытия третьей подсказки.
        if str((effect_result or {}).get("effect_key") or "") == "PisosCurse":
            with db_connect_write() as conn:
                conn.execute("UPDATE PLAYERS SET PisosCurseRevealed = 0 WHERE ID = ?", (int(user_id),))
                conn.commit()
            effect_result = None
        if (
            int(anomaly_id) == 19
            and str(((effect_result or {}).get("event") or {}).get("type") or "") == "kill_contract_offer"
        ):
            with db_connect_write() as conn:
                conn.execute(
                    "UPDATE WORK SET ContractOfferPending = 1 WHERE user_id = ? AND anomaly_id = 19",
                    (int(user_id),),
                )
                conn.commit()
        if (
            int(anomaly_id) == 21
            and str(((effect_result or {}).get("event") or {}).get("type") or "") == "stat_conversion_offer"
        ):
            with db_connect_write() as conn:
                conn.execute(
                    "UPDATE WORK SET StatConversionPending = 1 WHERE user_id = ? AND anomaly_id = 21",
                    (int(user_id),),
                )
                conn.commit()
        if (
            int(anomaly_id) == 35
            and str(((effect_result or {}).get("event") or {}).get("type") or "") == "death_shield_offer"
        ):
            with db_connect_write() as conn:
                conn.execute(
                    "UPDATE WORK SET DeathShieldOfferPending = 1 WHERE user_id = ? AND anomaly_id = 35",
                    (int(user_id),),
                )
                conn.commit()
        if (
            int(anomaly_id) == 37
            and str(((effect_result or {}).get("event") or {}).get("type") or "") == "altar_offering"
        ):
            with db_connect_write() as conn:
                conn.execute(
                    "UPDATE WORK SET AltarOfferingPending = 1 WHERE user_id = ? AND anomaly_id = 37",
                    (int(user_id),),
                )
                conn.commit()
        if (
            int(anomaly_id) == 41
            and str(((effect_result or {}).get("event") or {}).get("type") or "") == "devil_deal_offer"
        ):
            with db_connect_write() as conn:
                conn.execute(
                    "UPDATE WORK SET DevilDealPending = 1 WHERE user_id = ? AND anomaly_id = 41",
                    (int(user_id),),
                )
                conn.commit()
        if (
            int(anomaly_id) == 49
            and str(((effect_result or {}).get("event") or {}).get("type") or "") == "free_stat_offer"
        ):
            with db_connect_write() as conn:
                conn.execute(
                    "UPDATE WORK SET FreeStatPending = 1 WHERE user_id = ? AND anomaly_id = 49",
                    (int(user_id),),
                )
                conn.commit()
        if (
            int(anomaly_id) == 137
            and str(((effect_result or {}).get("event") or {}).get("type") or "") == "curse_anomaly_dialog"
        ):
            with db_connect_write() as conn:
                conn.execute(
                    "UPDATE WORK SET Curse137Pending = 1, Curse137Trigger = '' WHERE user_id = ? AND anomaly_id = 137",
                    (int(user_id),),
                )
                conn.commit()
    result_payload = {"details": get_details_payload(user_id, anomaly_id), "effect_result": effect_result}
    if int(anomaly_id) == 109 and effect_result:
        damage = effect_result.get("damage") or {}
        if bool(damage.get("is_dead")):
            death_reason = "Погиб при исследовании аномалии"
            game_state = _advance_after_nonwork_death(int(user_id), f"anomaly109_hint_{int(next_slot)}")
            effect_result["fatal_after_modal"] = {"reason": death_reason, "game_state": game_state}
            result_payload.update({
                "player_dead": True,
                "death_reason": death_reason,
                "game_state": game_state,
                "final_results": game_state.get("final_results"),
            })
        else:
            result_payload["room"] = get_work_room_payload(int(user_id), int(anomaly_id))
    if int(anomaly_id) == 65 and effect_result and bool(effect_result.get("dead")):
        death_reason = "Сотрудник погиб, пока Кот-висельник поглощал Пепельную чуму."
        game_state = _advance_after_nonwork_death(int(user_id), "anomaly65_plague_absorbed_death")
        effect_result["fatal_after_modal"] = {"reason": death_reason, "game_state": game_state}
        result_payload.update({
            "player_dead": True,
            "death_reason": death_reason,
            "game_state": game_state,
            "final_results": game_state.get("final_results"),
        })
    if int(anomaly_id) == 81 and effect_result and str(effect_result.get("reason") or "") == "absorbed_by_companion":
        effect_result["title"] = "Кот-висельник поглотил заражение"
        effect_result["description"] = "Кот-висельник защитил нулевого пациента от Багрового вируса, забрав 20 HP."
        effect_result["modal"] = {
            "intro": "Кот-висельник поглотил заражение",
            "effect": effect_result["description"],
            "icon": "/photo/work_room/neutralresult.png",
            "iconAlt": "Кот-висельник защитил владельца",
        }
        if bool(effect_result.get("dead")):
            death_reason = "Сотрудник погиб, пока Кот-висельник поглощал Багровый вирус"
            game_state = _advance_after_nonwork_death(int(user_id), "crimson_zero_patient_cat_death")
            effect_result["fatal_after_modal"] = {"reason": death_reason, "game_state": game_state}
            result_payload.update({"player_dead": True, "death_reason": death_reason, "game_state": game_state, "final_results": game_state.get("final_results")})
        else:
            result_payload["room"] = get_work_room_payload(int(user_id), int(anomaly_id))
    if int(anomaly_id) == 64 and effect_result and str(((effect_result.get("event") or {}).get("type") or "")) == "stat_checks":
        damage = effect_result.get("damage") or {}
        if bool(damage.get("is_dead")):
            death_reason = "Не выдержал проверки характеристик"
            game_state = _advance_after_nonwork_death(int(user_id), "anomaly64_stat_checks")
            effect_result["event"].update({"player_dead": True, "death_reason": death_reason, "game_state": game_state})
            result_payload.update({"player_dead": True, "death_reason": death_reason, "game_state": game_state, "final_results": game_state.get("final_results")})
        else:
            result_payload["room"] = get_work_room_payload(int(user_id), int(anomaly_id))
    if int(anomaly_id) == 47 and effect_result:
        damage = effect_result.get("damage") or {}
        effect_result["modal"] = {
            "intro": effect_result.get("title") or "Голодный рюкзак",
            "effect": effect_result.get("description") or "Эффект подсказки применён.",
            "icon": "/photo/work_room/badresult.png" if damage else "/photo/work_room/neutralresult.png",
            "iconAlt": "Эффект Голодного рюкзака",
        }
        if bool(damage.get("is_dead")):
            game_state = _advance_after_nonwork_death(int(user_id), f"hungry_bag_hint_{int(next_slot)}")
            death_reason = "Стал пищей Голодного рюкзака"
            effect_result["fatal_after_modal"] = {"reason": death_reason, "game_state": game_state}
            result_payload.update({"player_dead": True, "death_reason": death_reason, "game_state": game_state, "final_results": game_state.get("final_results")})
        else:
            result_payload["room"] = get_work_room_payload(int(user_id), int(anomaly_id))
    if int(anomaly_id) == 46 and int(next_slot) == 1 and effect_result:
        effect_result["modal"] = {
            "intro": effect_result.get("title") or "Ярость идола",
            "effect": effect_result.get("description") or "Эффект первой подсказки применён.",
            "icon": "/photo/work_room/badresult.png",
            "iconAlt": "Ярость Пепельного идола",
        }
        dead_ids = [int(pid) for pid in (effect_result.get("player_dead_ids") or [])]
        if int(user_id) in dead_ids:
            game_state = _advance_after_nonwork_death(int(user_id), "cinder_idol_first_hint")
            death_reason = "Погиб от ярости Пепельного идола"
            effect_result["fatal_after_modal"] = {"reason": death_reason, "game_state": game_state}
            result_payload.update({"player_dead": True, "death_reason": death_reason, "game_state": game_state, "final_results": game_state.get("final_results")})
    if int(anomaly_id) == 71 and int(next_slot) >= int(total) and effect_result:
        damage = effect_result.get("damage") or {}
        if bool(damage.get("is_dead")):
            death_reason = "Стал частью Старой избушки плоти"
            game_state = _advance_after_nonwork_death(int(user_id), "anomaly71_three_predictions")
            effect_result["fatal_after_modal"] = {"reason": death_reason, "game_state": game_state}
            result_payload.update({"player_dead": True, "death_reason": death_reason, "game_state": game_state, "final_results": game_state.get("final_results")})
        else:
            result_payload["room"] = get_work_room_payload(int(user_id), int(anomaly_id))
    # A lethal hint effect must always advance away from the dead player's
    # turn. Some generic damage effects do not have an anomaly-specific block.
    if effect_result and "game_state" not in result_payload:
        effect_damage = effect_result.get("damage") if isinstance(effect_result.get("damage"), dict) else {}
        effect_killed_player = bool(
            effect_result.get("player_dead")
            or effect_result.get("dead")
            or effect_damage.get("is_dead")
            or _is_player_dead(int(user_id))
        )
        if effect_killed_player and _is_player_dead(int(user_id)):
            death_reason = str(
                result_payload.get("death_reason")
                or effect_result.get("death_reason")
                or effect_damage.get("death_reason")
                or effect_result.get("description")
                or "Погиб при открытии подсказки"
            )
            game_state = _advance_after_nonwork_death(
                int(user_id),
                f"hint_effect_death_{int(anomaly_id)}_{int(next_slot)}",
            )
            effect_result.setdefault("modal", {
                "intro": effect_result.get("title") or "Воздействие аномалии",
                "effect": effect_result.get("description") or death_reason,
                "icon": "/photo/work_room/badresult.png",
                "iconAlt": "Смертельный эффект",
            })
            effect_result["fatal_after_modal"] = {"reason": death_reason, "game_state": game_state}
            result_payload.update({
                "player_dead": True,
                "death_reason": death_reason,
                "game_state": game_state,
                "final_results": game_state.get("final_results"),
            })
    if int(anomaly_id) == 6 and int(next_slot) >= int(total):
        result_payload["room"] = get_work_room_payload(user_id, anomaly_id)
    hint_text = str((anomaly or {}).get(f"HINT{int(next_slot)}") or "").strip()
    _log_player_effect(
        int(user_id),
        effect_result_for_log or effect_result,
        effect_name or "",
        hint_text=hint_text,
    )
    return result_payload


def confirm_details_fatal_action(user_id, anomaly_id, action_type):
    action = str(action_type or "").strip()
    if action != "anomaly12_last_hint" or int(anomaly_id) != 12:
        raise ValueError("Неизвестное фатальное действие.")
    _ensure_work_entry(user_id, anomaly_id)
    progress = _work_progress(user_id, anomaly_id)
    if int(progress.get("hintunlocked") or 0) < int(progress.get("hintcount") or 0):
        raise ValueError("Фатальное действие ещё недоступно.")
    anomaly = _get_anomaly_row(anomaly_id)
    codename = _anomaly_codename(anomaly)
    death_reason = f"Сотрудник пропал без вести после изучения {codename}"
    with db_connect() as conn:
        player_row = conn.execute(
            "SELECT COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
    if not player_row:
        raise ValueError("Игрок не найден.")
    if int(player_row["IsDead"] or 0) == 1:
        state_payload = get_game_state(int(user_id))
        print(
            "[DEBUG A12 already_dead]",
            json.dumps(
                {
                    "user_id": int(user_id),
                    "anomaly_id": int(anomaly_id),
                    "runtime_started": runtime_game.get("started"),
                    "runtime_final_player_ids": runtime_game.get("final_player_ids"),
                    "runtime_final_results": runtime_game.get("final_results"),
                    "state_status": (state_payload.get("core") or {}).get("status"),
                    "state_final_results": state_payload.get("final_results"),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        return {
            "ok": True,
            "player_dead": True,
            "death_reason": death_reason,
            "game_state": state_payload,
            "final_results": state_payload.get("final_results"),
        }
    if _player_companion_id(int(user_id)) == 6:
        return {
            "ok": True,
            "player_dead": False,
            "companion_saved": True,
            "companion_notice": "… Атаку отразил компаньон",
            "death_reason": "",
            "game_state": get_game_state(int(user_id)),
            "final_results": {"exists": False, "winner_id": None, "winner_name": "", "standings": []},
        }
    damage_result = core.apply_damage(
        DB_PATH,
        int(user_id),
        hp_damage=999,
        sp_damage=0,
        reason=death_reason,
    )
    player_dead = bool(damage_result.get("is_dead"))
    if not player_dead:
        return {
            "ok": True,
            "player_dead": False,
            "death_reason": "",
            "game_state": get_game_state(int(user_id)),
            "final_results": {"exists": False, "winner_id": None, "winner_name": "", "standings": []},
        }
    final_results = {"exists": False, "winner_id": None, "winner_name": "", "standings": []}
    with state_lock:
        player_ids_before = [int(player["id"]) for player in lobby_state["players"]]
        lobby_state["game_assignments"][int(user_id)] = []
    previous_day = int(runtime_game.get("current_day") or 0)
    advance_payload = core.advance_turn(DB_PATH, reason="anomaly12_last_hint_death")
    core_state = advance_payload.get("state", {})
    runtime_game["started"] = core_state.get("status") == "started"
    runtime_game["current_day"] = int(core_state.get("current_day") or 0)
    runtime_game["winner_id"] = core_state.get("winner_user_id")
    final_player_ids = [int(pid) for pid in core_state.get("turn_order", [])] or list(player_ids_before) or [int(user_id)]
    if core_state.get("status") == "started" and int(core_state.get("current_day") or 0) > previous_day:
        _cleanup_new_day_effects(player_ids_before)
        _apply_new_day_companion_effects(player_ids_before)
        _prepare_alastor_new_day_task()
        with state_lock:
            lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
    elif core_state.get("status") == "finished":
        final_results = get_final_results_payload(final_player_ids)
        runtime_game["final_results"] = final_results
        with state_lock:
            runtime_game["final_player_ids"] = list(final_player_ids)
            _reset_lobby_state()
    elif core_state.get("status") != "started":
        runtime_game["started"] = False
        final_results = get_final_results_payload(final_player_ids)
        runtime_game["final_results"] = final_results
        with state_lock:
            runtime_game["final_player_ids"] = list(final_player_ids)
            _reset_lobby_state()
    if not final_results.get("standings") and not runtime_game.get("started"):
        final_results = get_final_results_payload(runtime_game.get("final_player_ids") or final_player_ids)
    state_payload = get_game_state(int(user_id))
    print(
        "[DEBUG A12 confirm_fatal]",
        json.dumps(
            {
                "user_id": int(user_id),
                "anomaly_id": int(anomaly_id),
                "damage_result": damage_result,
                "advance_ok": advance_payload.get("ok"),
                "advance_state": core_state,
                "runtime_started": runtime_game.get("started"),
                "runtime_current_day": runtime_game.get("current_day"),
                "runtime_winner_id": runtime_game.get("winner_id"),
                "runtime_final_player_ids": runtime_game.get("final_player_ids"),
                "runtime_final_results": runtime_game.get("final_results"),
                "returned_final_results": final_results,
                "state_status": (state_payload.get("core") or {}).get("status"),
                "state_game": state_payload.get("game"),
                "state_final_results": state_payload.get("final_results"),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return {
        "ok": True,
        "player_dead": True,
        "death_reason": death_reason,
        "game_state": state_payload,
        "final_results": final_results,
    }


def unlock_hidden_hint(user_id, anomaly_id):
    _assert_current_turn(user_id)
    _ensure_work_entry(user_id, anomaly_id)
    _assert_research_not_blocked(user_id, anomaly_id)
    anomaly = _get_anomaly_row(anomaly_id)
    if not anomaly:
        raise ValueError("Аномалия не найдена.")
    hidden_hint_text = str(anomaly.get("HINTHIDDEN") or "").strip()
    if not hidden_hint_text:
        return {"details": get_details_payload(user_id, anomaly_id)}
    if not _player_has_hidden_hint_artifact(user_id):
        raise ValueError("Для открытия требуется артефакт.")
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET HiddenHintUnlocked = 1 WHERE user_id = ? AND anomaly_id = ?",
            (int(user_id), int(anomaly_id)),
        )
        conn.commit()
    return {"details": get_details_payload(user_id, anomaly_id)}


def accept_companion_offer(user_id, anomaly_id):
    _ensure_work_entry(user_id, anomaly_id)
    progress = _work_progress(user_id, anomaly_id)
    pending = _pending_companion_offer(progress)
    if not pending:
        raise ValueError("Предложение компаньона не найдено.")
    acceptance = _can_accept_companion_offer(user_id, pending["companion_id"])
    if not acceptance["allowed"]:
        raise ValueError(acceptance["reason"] or "Нельзя сменить имеющегося компаньона.")
    current_companion_id = int(acceptance["current_companion_id"] or 0)
    new_companion_id = int(pending["companion_id"] or 0)
    if current_companion_id not in (0, new_companion_id):
        _cleanup_companion_on_replace(user_id, current_companion_id)
    with db_connect_write() as conn:
        conn.execute("UPDATE PLAYERS SET COMPSLOT = ? WHERE ID = ?", (new_companion_id, int(user_id)))
        conn.commit()
    _run_companion_accept_side_effect(pending["effect_name"], user_id, previous_companion_id=current_companion_id)
    _x125_mark("companion_gained")
    _clear_companion_offer_state(user_id, anomaly_id, declined=False)
    return {
        "ok": True,
        "details": get_details_payload(user_id, anomaly_id),
        "room": get_work_room_payload(int(user_id), int(anomaly_id)),
        "companion_offer": None,
    }


def decline_companion_offer(user_id, anomaly_id):
    _ensure_work_entry(user_id, anomaly_id)
    progress = _work_progress(user_id, anomaly_id)
    if not _pending_companion_offer(progress):
        raise ValueError("Предложение компаньона не найдено.")
    _clear_companion_offer_state(user_id, anomaly_id, declined=True)
    return {
        "ok": True,
        "details": get_details_payload(user_id, anomaly_id),
        "room": get_work_room_payload(int(user_id), int(anomaly_id)),
        "companion_offer": None,
    }


def finish_research(user_id, anomaly_id, *, advance_on_clay_death=True):
    _assert_research_not_blocked(user_id, anomaly_id)
    reward_was_claimed = _reward_already_claimed(user_id, anomaly_id)
    payload = _grant_research_reward(user_id, anomaly_id, require_completed=True)
    payload["reward"] = _apply_post_research_companion_effects(user_id, anomaly_id, payload.get("reward"))
    if not reward_was_claimed:
        with db_connect() as conn:
            has_clay = (
                int(_safe_global_value("ClayHolder", 0) or 0) == int(user_id)
                or _player_has_inventory_item(conn, int(user_id), core.CLAY_ITEM_ID)
            )
        if has_clay:
            core.set_global_value(DB_PATH, "CLAY_BYPASS", 1)
            try:
                clay_damage = core.apply_damage(
                    DB_PATH, int(user_id), sp_damage=200,
                    reason="Глиняная статуя истощила разум владельца",
                )
            finally:
                core.set_global_value(DB_PATH, "CLAY_BYPASS", 0)
            with db_connect_write() as conn:
                if _player_has_inventory_item(conn, int(user_id), core.CLAY_ITEM_ID):
                    _consume_inventory_item(conn, int(user_id), core.CLAY_ITEM_ID)
            if int(_safe_global_value("ClayHolder", 0) or 0) == int(user_id):
                core.set_global_value(DB_PATH, "ClayHolder", 0)
            core.set_global_value(DB_PATH, "CLAY_ABSORB", 0)
            core.set_global_value(DB_PATH, "ClayAbsorbed", 0)
            payload["clay_penalty"] = {
                "triggered": True,
                "message": "Глиняная статуя истощает ваш разум: −200 SP. Предмет рассыпается и исчезает.",
                "damage": clay_damage,
                "player_dead": bool(clay_damage.get("is_dead")),
            }
            if bool(clay_damage.get("is_dead")) and advance_on_clay_death:
                payload["game_state"] = _advance_after_nonwork_death(int(user_id), "clay_statue_end_of_research")
    if int(anomaly_id) == 111 and _player_has_effect(int(user_id), "NoResult"):
        _remove_effect_exact(int(user_id), "NoResult")
        payload["no_result_curse_removed"] = True
    # The final teaching of the Cinder God makes completed research fatal.
    # RewardClaimed is the one-shot guard because this function is called by
    # both the finish preview and final turn confirmation.
    if int(anomaly_id) == 62 and not reward_was_claimed:
        with db_connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(HP, 0) AS HP, COALESCE(MAXHP, 100) AS MAXHP FROM PLAYERS WHERE ID = ?",
                (int(user_id),),
            ).fetchone()
        hp_now = int(row["HP"] or 0) if row else 0
        max_hp = int(row["MAXHP"] or 100) if row else 100
        fate_damage = core.apply_damage(
            DB_PATH,
            int(user_id),
            hp_damage=max(1, hp_now, max_hp) + 100000,
            sp_damage=0,
            reason="Принял свою судьбу по воле Бога пепельной чумы",
        )
        payload["anomaly62_fate"] = {
            "triggered": True,
            "message": "А ТЕПЕРЬ ПРИМИ СВОЮ СУДЬБУ. Завершение исследования оказалось смертельным.",
            "damage": fate_damage,
            "player_dead": bool((fate_damage or {}).get("is_dead")),
        }
        if bool((fate_damage or {}).get("is_dead")) and advance_on_clay_death:
            payload["game_state"] = _advance_after_nonwork_death(int(user_id), "anomaly62_completed_research")
    payload["details"] = get_details_payload(user_id, anomaly_id)
    return payload


def resolve_sovuh_zombie_action(user_id, anomaly_id, action):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id)
    action = str(action or "").strip().lower()
    if anomaly_id != 32:
        raise ValueError("VN-сценарий Совы-зомби доступен только для аномалии 32.")
    lethal_actions = {
        "go", "grenade", "flamethrower", "barricade", "helicopter",
        "shoot", "door", "cabinet", "timeout",
    }
    if action in lethal_actions:
        damage = core.apply_damage(
            DB_PATH,
            user_id,
            hp_damage=9999,
            bypass_death_shield=True,
            reason="Сова-зомби настигла сотрудника во время разведки.",
        )
        player_dead = bool((damage or {}).get("is_dead"))
        game_state = _advance_after_nonwork_death(user_id, "sovuh_zombie_vn_death") if player_dead else get_game_state(user_id)
        return {
            "ok": True,
            "outcome": "death",
            "player_dead": player_dead,
            "death_reason": "Сова-зомби настигла сотрудника во время разведки.",
            "damage": damage,
            "game_state": game_state,
            "final_results": game_state.get("final_results"),
        }
    if action == "finish":
        _ensure_work_entry(user_id, anomaly_id)
        with db_connect_write() as conn:
            conn.execute(
                """
                UPDATE WORK
                SET photounlocked = 1,
                    descriptionunlocked = 1,
                    hintunlocked = hintcount,
                    IsCompleted = 1
                WHERE user_id = ? AND anomaly_id = ?
                """,
                (user_id, anomaly_id),
            )
            conn.commit()
        return {
            "ok": True,
            "outcome": "completed",
            "details": get_details_payload(user_id, anomaly_id),
            "room": get_work_room_payload(user_id, anomaly_id),
            "game_state": get_game_state(user_id),
        }
    raise ValueError("Неизвестное действие VN-сценария Совы-зомби.")


def resolve_predator_action(user_id, anomaly_id, action, speech=""):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id)
    action = str(action or "").strip().lower()
    speech = str(speech or "").strip()[:200]
    if anomaly_id != 107:
        raise ValueError("VN-сценарий Predator доступен только для аномалии 107.")

    death_reasons = {
        "ignore": "Сигнал кассеты вызвал смертельные конвульсии.",
        "escape": "Попытка покинуть комнату активировала смертельный эффект аномалии.",
        "jump": "Сотрудник погиб, прыгнув с обрыва в логове хищника.",
        "beast": "Стал добычей высшего хищника",
        "knife_attack": "Стал добычей высшего хищника",
    }
    if action in death_reasons:
        damage = core.apply_damage(
            DB_PATH,
            user_id,
            hp_damage=9999,
            bypass_death_shield=True,
            reason=death_reasons[action],
        )
        player_dead = bool((damage or {}).get("is_dead"))
        game_state = _advance_after_nonwork_death(user_id, "predator_vn_death") if player_dead else get_game_state(user_id)
        return {
            "ok": True,
            "outcome": "death",
            "player_dead": player_dead,
            "death_reason": death_reasons[action],
            "damage": damage,
            "game_state": game_state,
            "final_results": game_state.get("final_results"),
        }

    damage_map = {
        "forest_stress": (0, 25, "Стресс в аномальном лесу."),
        "house_stress": (0, 15, "Стресс в доме лесного хищника."),
        "thorns": (25, 0, "Раны от колючих зарослей."),
        "attack": (25, 0, "Ответная атака лесного хищника."),
        "shout": (50, 0, "Стал добычей высшего хищника"),
    }
    if action in damage_map:
        hp_damage, sp_damage, reason = damage_map[action]
        damage = core.apply_damage(DB_PATH, user_id, hp_damage=hp_damage, sp_damage=sp_damage, reason=reason)
        player_dead = bool((damage or {}).get("is_dead"))
        game_state = _advance_after_nonwork_death(user_id, "predator_vn_damage_death") if player_dead else get_game_state(user_id)
        death_narrative = {
            "shout": "Кровь не останавливается. Это конец.",
            "thorns": "Кровь не останавливается. Это конец.",
        }.get(action, reason)
        return {
            "ok": True,
            "outcome": "death" if player_dead else "continue",
            "player_dead": player_dead,
            "death_reason": reason if player_dead else "",
            "death_narrative": death_narrative if player_dead else "",
            "damage": damage,
            "game_state": game_state,
            "final_results": game_state.get("final_results"),
        }

    if action == "photo":
        _ensure_work_entry(user_id, anomaly_id)
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE WORK SET photounlocked = 1 WHERE user_id = ? AND anomaly_id = ?",
                (user_id, anomaly_id),
            )
            conn.commit()
        return {"ok": True, "outcome": "continue", "room": get_work_room_payload(user_id, anomaly_id)}

    if action == "description":
        _ensure_work_entry(user_id, anomaly_id)
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE WORK SET descriptionunlocked = 1 WHERE user_id = ? AND anomaly_id = ?",
                (user_id, anomaly_id),
            )
            conn.commit()
        return {"ok": True, "outcome": "continue", "room": get_work_room_payload(user_id, anomaly_id)}

    if action == "finish":
        profanity_tokens = ("нах", "пизд", "еб", "ёб", "бля", "хуй", "сука", "мраз", "пидор", "гандон", "шлюх", "залуп", "дроч", "муд", "хер", "дтф", "dtf")
        profanity = any(token in speech.lower() for token in profanity_tokens)
        damage = None
        if profanity:
            damage = core.apply_damage(DB_PATH, user_id, hp_damage=50, reason="Последние слова разозлили лесного хищника.")
            if bool((damage or {}).get("is_dead")):
                game_state = _advance_after_nonwork_death(user_id, "predator_vn_speech_death")
                return {
                    "ok": True,
                    "outcome": "death",
                    "player_dead": True,
                    "death_reason": "Хищник лишил сотрудника языка за последние слова.",
                    "death_narrative": "Хищник прищурился: «Возможно, тебе ни к чему твой грязный язык…»\n\n…вы чувствуете, как рот наполняется кровью.",
                    "damage": damage,
                    "game_state": game_state,
                    "final_results": game_state.get("final_results"),
                }
        _ensure_work_entry(user_id, anomaly_id)
        with db_connect_write() as conn:
            conn.execute(
                """
                UPDATE WORK
                SET hintunlocked = hintcount,
                    PredatorVnResolved = 1
                WHERE user_id = ? AND anomaly_id = ?
                """,
                (user_id, anomaly_id),
            )
            conn.commit()
        progress = _update_work_completion(user_id, anomaly_id)
        return {
            "ok": True,
            "outcome": "completed",
            "speech": speech,
            "profanity_penalty": profanity,
            "damage": damage,
            "details": get_details_payload(user_id, anomaly_id),
            "all_research_unlocked": int(progress.get("IsCompleted") or 0) == 1,
            "room": get_work_room_payload(user_id, anomaly_id),
            "game_state": get_game_state(user_id),
        }

    raise ValueError("Неизвестное действие VN-сценария Predator.")


def resolve_puppy_action(user_id, anomaly_id, action, touched=False):
    user_id = int(user_id)
    anomaly_id = int(anomaly_id)
    action = str(action or "").strip().lower()
    if anomaly_id != 66:
        raise ValueError("VN-сценарий Симпатяги Убиваки доступен только для аномалии 66.")

    if action in {"die", "finish"}:
        if action == "die" or bool(touched):
            death_reason = "Разрыв грудной клетки"
            damage = core.apply_damage(
                DB_PATH,
                user_id,
                hp_damage=9999,
                bypass_death_shield=True,
                reason=death_reason,
            )
            player_dead = bool((damage or {}).get("is_dead"))
            game_state = _advance_after_nonwork_death(user_id, "puppy_vn_touch_death") if player_dead else get_game_state(user_id)
            return {
                "ok": True,
                "outcome": "death",
                "player_dead": player_dead,
                "death_reason": death_reason,
                "damage": damage,
                "game_state": game_state,
                "final_results": game_state.get("final_results"),
            }

        _ensure_work_entry(user_id, anomaly_id)
        with db_connect_write() as conn:
            conn.execute(
                """
                UPDATE WORK
                SET photounlocked = 1,
                    descriptionunlocked = 1,
                    hintunlocked = hintcount,
                    IsCompleted = 1
                WHERE user_id = ? AND anomaly_id = ?
                """,
                (user_id, anomaly_id),
            )
            conn.commit()
        return {
            "ok": True,
            "outcome": "completed",
            "details": get_details_payload(user_id, anomaly_id),
            "room": get_work_room_payload(user_id, anomaly_id),
            "game_state": get_game_state(user_id),
        }

    raise ValueError("Неизвестное действие VN-сценария Симпатяги Убиваки.")


def _safe_global_value(key, default=0):
    try:
        return core.get_global_value(DB_PATH, key, default)
    except sqlite3.OperationalError:
        return default


BRASS_SPHERE_ITEM_ID = 35
BRASS_SPHERE_EFFECT = "metalcrusher"


def _give_brass_sphere_to_player(user_id, needs_activate=True):
    with db_connect_write() as conn:
        row = conn.execute(
            f"SELECT {', '.join(core.EFFECT_COLUMNS)} FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
        if not row:
            raise ValueError("Игрок для передачи латунного шара не найден.")
        effects = [row[column] for column in core.EFFECT_COLUMNS if row[column] not in (None, "", "0")]
        effects = [effect for effect in effects if str(effect) != BRASS_SPHERE_EFFECT]
        effects.append(BRASS_SPHERE_EFFECT)
        conn.execute(
            "UPDATE PLAYERS SET INVSLOT1 = ?, SLOT1AMOUNT = 1, INVSLOT2 = 1, SLOT2AMOUNT = 0 WHERE ID = ?",
            (BRASS_SPHERE_ITEM_ID, int(user_id)),
        )
        core._save_effects(conn, int(user_id), effects)
        conn.commit()
    core.set_global_value(DB_PATH, "BrassSphereOwner", int(user_id))
    core.set_global_value(DB_PATH, "BrassSphereNeedsActivate", 1 if needs_activate else 0)


def _remove_brass_sphere_from_player(user_id):
    with db_connect_write() as conn:
        row = conn.execute(
            f"SELECT {', '.join(core.EFFECT_COLUMNS)} FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
        if row:
            effects = [row[column] for column in core.EFFECT_COLUMNS if row[column] not in (None, "", "0")]
            effects = [effect for effect in effects if str(effect) != BRASS_SPHERE_EFFECT]
            core._save_effects(conn, int(user_id), effects)
        conn.execute(
            """
            UPDATE PLAYERS
            SET INVSLOT1 = CASE WHEN INVSLOT1 = ? THEN 1 ELSE INVSLOT1 END,
                SLOT1AMOUNT = CASE WHEN INVSLOT1 = ? THEN 0 ELSE SLOT1AMOUNT END,
                INVSLOT2 = CASE WHEN INVSLOT2 = ? THEN 1 ELSE INVSLOT2 END,
                SLOT2AMOUNT = CASE WHEN INVSLOT2 = ? THEN 0 ELSE SLOT2AMOUNT END
            WHERE ID = ?
            """,
            (BRASS_SPHERE_ITEM_ID, BRASS_SPHERE_ITEM_ID, BRASS_SPHERE_ITEM_ID, BRASS_SPHERE_ITEM_ID, int(user_id)),
        )
        conn.commit()


def _transfer_brass_sphere_from_dead_owner(dead_user_id):
    if int(_safe_global_value("BrassSphereOwner", 0) or 0) != int(dead_user_id):
        return None
    _remove_brass_sphere_from_player(int(dead_user_id))
    state = core.get_game_state(DB_PATH)
    candidates = [int(pid) for pid in state.get("turn_order", []) if int(pid) != int(dead_user_id) and not _is_player_dead(int(pid))]
    if not candidates:
        core.set_global_value(DB_PATH, "BrassSphereOwner", 0)
        core.set_global_value(DB_PATH, "BrassSphereNeedsActivate", 0)
        return None
    new_owner = random.choice(candidates)
    _give_brass_sphere_to_player(new_owner, needs_activate=True)
    return new_owner


def _brass_transfer_if_owner_dead():
    owner_id = int(_safe_global_value("BrassSphereOwner", 0) or 0)
    if owner_id > 0 and _is_player_dead(owner_id):
        return _transfer_brass_sphere_from_dead_owner(owner_id)
    return None


def _brass_sphere_on_anomaly_chosen(user_id, anomaly_id):
    if int(_safe_global_value("BrassSphereOwner", 0) or 0) != int(user_id):
        return False
    anomaly = _get_anomaly_row(int(anomaly_id))
    if anomaly and int(anomaly["CLASS_ID"] or 0) < 5:
        core.set_global_value(DB_PATH, "BrassSphereNeedsActivate", 1)
        return True
    return False


def _brass_sphere_end_of_day():
    owner_id = int(_safe_global_value("BrassSphereOwner", 0) or 0)
    needs_activate = int(_safe_global_value("BrassSphereNeedsActivate", 0) or 0) == 1
    if owner_id <= 0 or not needs_activate or _is_player_dead(owner_id):
        return None
    death_reason = "Был поглощён металлическим шаром из латуни"
    core.set_player_dead(DB_PATH, owner_id, reason=death_reason)
    event_id = int(_safe_global_value("BrassSphereEventId", 0) or 0) + 1
    core.set_global_value(DB_PATH, "BrassSphereEventId", event_id)
    core.set_global_value(DB_PATH, "BrassSphereEventUserId", owner_id)
    new_owner = _transfer_brass_sphere_from_dead_owner(owner_id)
    return {"event_id": event_id, "user_id": owner_id, "death_reason": death_reason, "new_owner_id": new_owner}


def get_brass_sphere_event_payload(user_id):
    event_id = int(_safe_global_value("BrassSphereEventId", 0) or 0)
    event_user_id = int(_safe_global_value("BrassSphereEventUserId", 0) or 0)
    if event_id <= 0 or event_user_id != int(user_id):
        return None
    return {
        "id": event_id,
        "player_dead": True,
        "death_reason": "Был поглощён металлическим шаром из латуни",
    }


def activate_brass_sphere(user_id):
    owner_id = int(_safe_global_value("BrassSphereOwner", 0) or 0)
    with db_connect_write() as conn:
        player = _player_row_for_inventory(conn, int(user_id))
        if not player or not _player_has_inventory_item(conn, int(user_id), BRASS_SPHERE_ITEM_ID):
            raise ValueError("У вас нет латунного шара.")
        if owner_id not in (0, int(user_id)):
            raise ValueError("Латунный шар принадлежит другому игроку.")
        effects = list(_effects_for_player_conn(conn, int(user_id)))
        blessing_keys = set(effect_dictionary.BLESS_CATALOG.keys())
        effects = [effect for effect in effects if effect_dictionary.base_key(effect) not in blessing_keys]
        if BRASS_SPHERE_EFFECT not in effects:
            effects.append(BRASS_SPHERE_EFFECT)
        core._save_effects(conn, int(user_id), effects)
        hp = int(player["HP"] or 0)
        sp = int(player["SP"] or 0)
        maxsp = int(player["MAXSP"] or 200)
        conn.commit()
    core.set_global_value(DB_PATH, "BrassSphereOwner", int(user_id))
    core.set_global_value(DB_PATH, "BrassSphereNeedsActivate", 0)
    lost_sp = max(0, maxsp - sp)
    sp_damage = hp - lost_sp if lost_sp < hp else 50
    first_damage = core.apply_damage(DB_PATH, int(user_id), sp_damage=max(0, int(sp_damage)), reason="Активация латунного шара")
    second_damage = None
    if first_damage.get("heart_attack_triggered") and not first_damage.get("is_dead"):
        second_damage = core.apply_damage(DB_PATH, int(user_id), sp_damage=100, reason="Активация латунного шара после сердечного приступа")
    damage = second_damage or first_damage
    player_dead = bool(damage.get("is_dead"))
    new_owner = _transfer_brass_sphere_from_dead_owner(int(user_id)) if player_dead else None
    game_state = None
    core_state = core.get_game_state(DB_PATH)
    if player_dead and int(core_state.get("current_turn_user_id") or 0) == int(user_id):
        game_state = _advance_after_nonwork_death(int(user_id), "brass_sphere_activation")
    description = f"Латунный шар активирован. Сняты все положительные эффекты. Получено {int(first_damage.get('sp_damage_final') or 0)} чёрного урона."
    if second_damage:
        description += " Сердечный приступ вызвал ещё 100 чёрного урона."
    return {
        "item_result": _build_item_modal("Металлический шар из латуни", description, "/photo/work_room/badresult.png", "Латунный шар"),
        "damage": damage,
        "player_dead": player_dead,
        "death_reason": "Активация латунного шара после сердечного приступа" if player_dead else "",
        "new_owner_id": new_owner,
        "game_state": game_state,
    }


def _process_train_timer():
    """Apply one persistent Hell Express hit when its deadline expires."""
    with train_timer_lock:
        owner_id = int(_safe_global_value("TrainDeadlineUserId", 0) or 0)
        deadline_at = float(_safe_global_value("TrainDeadlineAt", 0) or 0)
        paused_at = float(_safe_global_value("TrainPausedAt", 0) or 0)
        if owner_id <= 0 or deadline_at <= 0 or paused_at > 0 or time.time() < deadline_at:
            return
        with db_connect() as conn:
            player = conn.execute(
                "SELECT COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID = ?",
                (owner_id,),
            ).fetchone()
        if not player or int(player["IsDead"] or 0) == 1:
            core.set_global_value(DB_PATH, "TrainDeadlineUserId", 0)
            core.set_global_value(DB_PATH, "TrainDeadlineAt", 0)
            return

        death_reason = "Был раздавлен адским экспрессом"
        damage = core.apply_damage(DB_PATH, owner_id, hp_damage=200, reason=death_reason)
        player_dead = bool(damage.get("is_dead"))
        event_id = int(_safe_global_value("TrainEventId", 0) or 0) + 1
        core.set_global_value(DB_PATH, "TrainEventId", event_id)
        core.set_global_value(DB_PATH, "TrainEventUserId", owner_id)
        core.set_global_value(DB_PATH, "TrainEventAt", time.time())
        core.set_global_value(DB_PATH, "TrainEventDamage", int(damage.get("hp_damage_final") or damage.get("hp_damage") or 0))
        core.set_global_value(DB_PATH, "TrainEventDead", 1 if player_dead else 0)
        if player_dead:
            _append_game_action_log(
                "effect",
                f"{_player_display_name(owner_id)} был раздавлен адским экспрессом.",
                owner_id,
            )
            core.set_global_value(DB_PATH, "TrainDeadlineUserId", 0)
            core.set_global_value(DB_PATH, "TrainDeadlineAt", 0)
            core_state = core.get_game_state(DB_PATH)
            if int(core_state.get("current_turn_user_id") or 0) == owner_id:
                _advance_after_nonwork_death(owner_id, "hell_express")
        else:
            core.set_global_value(DB_PATH, "TrainDeadlineAt", time.time() + 180)


def get_train_ticket_payload(user_id):
    owner_id = int(_safe_global_value("TrainDeadlineUserId", 0) or 0)
    deadline_at = float(_safe_global_value("TrainDeadlineAt", 0) or 0)
    paused_at = float(_safe_global_value("TrainPausedAt", 0) or 0)
    event = None
    event_id = int(_safe_global_value("TrainEventId", 0) or 0)
    if event_id > 0 and int(_safe_global_value("TrainEventUserId", 0) or 0) == int(user_id):
        event = {
            "id": event_id,
            "damage": {"hp_damage_final": int(_safe_global_value("TrainEventDamage", 0) or 0)},
            "player_dead": bool(int(_safe_global_value("TrainEventDead", 0) or 0)),
            "death_reason": "Был раздавлен адским экспрессом",
        }
    return {
        "active": owner_id == int(user_id) and deadline_at > 0,
        "paused": owner_id == int(user_id) and paused_at > 0,
        "deadline_at": deadline_at if owner_id == int(user_id) else None,
        "event": event,
    }


VIOLIN_ITEM_ID = 33


def _violin_owner_id():
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT ID FROM PLAYERS
            WHERE (COALESCE(INVSLOT1, 0) = ? AND COALESCE(SLOT1AMOUNT, 0) > 0)
               OR (COALESCE(INVSLOT2, 0) = ? AND COALESCE(SLOT2AMOUNT, 0) > 0)
            ORDER BY ID
            LIMIT 1
            """,
            (VIOLIN_ITEM_ID, VIOLIN_ITEM_ID),
        ).fetchone()
    return int(row["ID"]) if row else 0


def get_violin_button_payload(user_id):
    user_id = int(user_id)
    owner_id = _violin_owner_id()
    core_state = core.get_game_state(DB_PATH)
    is_turn = core_state.get("status") == "started" and int(core_state.get("current_turn_user_id") or 0) == user_id
    with db_connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID = ?",
            (user_id,),
        ).fetchone()
    alive = bool(row) and int(row["IsDead"] or 0) == 0
    available = owner_id > 0 and owner_id != user_id and is_turn and alive
    return {
        "visible": bool(available),
        "available": bool(available),
        "owner_id": owner_id or None,
        "damage": int(_safe_global_value("ViolinDamage", 40) or 40),
        "steals": int(_safe_global_value("ViolinSteals", 0) or 0),
    }


def _remove_violin_from_player(conn, user_id):
    row = conn.execute(
        """
        SELECT COALESCE(INVSLOT1, 0) AS i1, COALESCE(SLOT1AMOUNT, 0) AS a1,
               COALESCE(INVSLOT2, 0) AS i2, COALESCE(SLOT2AMOUNT, 0) AS a2
        FROM PLAYERS WHERE ID = ?
        """,
        (int(user_id),),
    ).fetchone()
    if not row:
        return False
    for slot, amount in ((1, int(row["a1"] or 0)), (2, int(row["a2"] or 0))):
        if int(row[f"i{slot}"] or 0) != VIOLIN_ITEM_ID or amount <= 0:
            continue
        new_amount = amount - 1
        item_col = "INVSLOT1" if slot == 1 else "INVSLOT2"
        amount_col = "SLOT1AMOUNT" if slot == 1 else "SLOT2AMOUNT"
        conn.execute(
            f"UPDATE PLAYERS SET {item_col} = ?, {amount_col} = ? WHERE ID = ?",
            (VIOLIN_ITEM_ID if new_amount > 0 else 1, max(0, new_amount), int(user_id)),
        )
        return True
    return False


def _force_grant_violin(conn, user_id):
    row = conn.execute(
        """
        SELECT COALESCE(INVSLOT1, 0) AS i1, COALESCE(SLOT1AMOUNT, 0) AS a1,
               COALESCE(INVSLOT2, 0) AS i2, COALESCE(SLOT2AMOUNT, 0) AS a2
        FROM PLAYERS WHERE ID = ?
        """,
        (int(user_id),),
    ).fetchone()
    if not row:
        raise ValueError("Игрок не найден.")
    for slot in (1, 2):
        if int(row[f"i{slot}"] or 0) == VIOLIN_ITEM_ID and int(row[f"a{slot}"] or 0) > 0:
            return
    target_slot = 1
    for slot in (1, 2):
        if int(row[f"i{slot}"] or 0) in (0, 1) or int(row[f"a{slot}"] or 0) <= 0:
            target_slot = slot
            break
    item_col = "INVSLOT1" if target_slot == 1 else "INVSLOT2"
    amount_col = "SLOT1AMOUNT" if target_slot == 1 else "SLOT2AMOUNT"
    conn.execute(
        f"UPDATE PLAYERS SET {item_col} = ?, {amount_col} = 1 WHERE ID = ?",
        (VIOLIN_ITEM_ID, int(user_id)),
    )


def steal_violin(user_id):
    user_id = int(user_id)
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") != "started" or int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Украсть скрипку можно только во время своего хода.")
    with state_lock:
        owner_id = _violin_owner_id()
        if owner_id <= 0:
            raise ValueError("Скрипка сейчас никому не принадлежит.")
        if owner_id == user_id:
            raise ValueError("Скрипка уже находится у вас.")
        with db_connect_write() as conn:
            thief = conn.execute(
                "SELECT COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID = ?",
                (user_id,),
            ).fetchone()
            if not thief or int(thief["IsDead"] or 0) == 1:
                raise ValueError("Мёртвый игрок не может украсть скрипку.")
            if not _remove_violin_from_player(conn, owner_id):
                raise ValueError("Владелец скрипки уже изменился. Обновите экран.")
            _force_grant_violin(conn, user_id)
            conn.commit()

        steals = int(_safe_global_value("ViolinSteals", 0) or 0) + 1
        damage = int(_safe_global_value("ViolinDamage", 40) or 40) + 20
        core.set_global_value(DB_PATH, "ViolinIsTaken", 1)
        core.set_global_value(DB_PATH, "ViolinOwnerPid", user_id)
        core.set_global_value(DB_PATH, "ViolinOwnerStreak", 1)
        core.set_global_value(DB_PATH, "ViolinSteals", steals)
        core.set_global_value(DB_PATH, "ViolinDamage", damage)

        chance = min(1.0, 0.25 + 0.10 * steals)
        wave_triggered = random.random() < chance
        victims = []
        dead_ids = []
        if wave_triggered:
            core.set_global_value(DB_PATH, "ViolinTriggeredToday", 1)
            active_ids = [int(pid) for pid in core_state.get("turn_order", [])]
            for player_id in active_ids:
                if _is_player_dead(player_id) or int(player_id) == int(user_id):
                    continue
                hit = core.apply_damage(
                    DB_PATH,
                    player_id,
                    hp_damage=0,
                    sp_damage=damage,
                    reason="Беззвучная волна Скрипки Безмолвного Дирижёра",
                )
                victims.append({"player_id": player_id, "damage": hit})
                if bool(hit.get("is_dead")):
                    dead_ids.append(player_id)

    game_state = None
    if user_id in dead_ids:
        game_state = _advance_after_nonwork_death(user_id, "violin_steal_wave")
    owner_name = f"Игрок {owner_id}"
    with db_connect() as conn:
        row = conn.execute("SELECT COALESCE(NAME, '') AS NAME FROM PLAYERS WHERE ID = ?", (owner_id,)).fetchone()
        if row and str(row["NAME"] or "").strip():
            owner_name = str(row["NAME"])
    message = f"Вы украли скрипку у {owner_name}. Сила волны увеличилась до {damage}."
    if wave_triggered:
        message += f" Скрипка беззвучно завыла: все живые получили {damage} урона рассудку."
    else:
        message += f" Волна не сработала (шанс был {int(chance * 100)}%)."
    return {
        "ok": True,
        "message": message,
        "owner_id": user_id,
        "previous_owner_id": owner_id,
        "damage": damage,
        "steals": steals,
        "wave_triggered": wave_triggered,
        "wave_chance": int(chance * 100),
        "victims": victims,
        "player_dead": user_id in dead_ids,
        "dead_ids": dead_ids,
        "death_reason": "Погиб от беззвучной волны скрипки" if user_id in dead_ids else "",
        "game_state": game_state,
        "final_results": (game_state or {}).get("final_results"),
        "violin_button": get_violin_button_payload(user_id),
    }


def reset_train_timer(user_id):
    with train_timer_lock:
        owner_id = int(_safe_global_value("TrainDeadlineUserId", 0) or 0)
        if owner_id != int(user_id):
            raise ValueError("Билет принадлежит другому игроку или эффект поезда не активен.")
        if float(_safe_global_value("TrainPausedAt", 0) or 0) > 0:
            raise ValueError("Во время визуальной новеллы билет недоступен.")
        with db_connect() as conn:
            player = conn.execute("SELECT COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        if not player or int(player["IsDead"] or 0) == 1:
            raise ValueError("Мёртвый игрок не может использовать билет.")
        core.set_global_value(DB_PATH, "TrainDeadlineAt", time.time() + 180)
    return {"ok": True, "message": "Таймер поезда сброшен!", "train_ticket": get_train_ticket_payload(int(user_id))}


def set_train_timer_paused(user_id, paused):
    with train_timer_lock:
        owner_id = int(_safe_global_value("TrainDeadlineUserId", 0) or 0)
        if owner_id != int(user_id):
            return {"ok": True, "train_ticket": get_train_ticket_payload(int(user_id))}
        paused_at = float(_safe_global_value("TrainPausedAt", 0) or 0)
        now = time.time()
        if bool(paused) and paused_at <= 0:
            core.set_global_value(DB_PATH, "TrainPausedAt", now)
        elif not bool(paused) and paused_at > 0:
            deadline_at = float(_safe_global_value("TrainDeadlineAt", now + 180) or (now + 180))
            core.set_global_value(DB_PATH, "TrainDeadlineAt", deadline_at + max(0, now - paused_at))
            core.set_global_value(DB_PATH, "TrainPausedAt", 0)
    return {"ok": True, "train_ticket": get_train_ticket_payload(int(user_id))}


def _is_active_global_value(value):
    if value is None:
        return False
    if value is False:
        return False
    if isinstance(value, (int, float)) and value == 0:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict, tuple, set)) and len(value) == 0:
        return False
    return True


def _safe_active_globals():
    try:
        globals_map = core.list_globals(DB_PATH)
    except sqlite3.OperationalError:
        return []
    active = []
    train_owner = int(globals_map.get("TrainDeadlineUserId", 0) or 0)
    train_deadline = float(globals_map.get("TrainDeadlineAt", 0) or 0)
    train_paused = float(globals_map.get("TrainPausedAt", 0) or 0) > 0
    if train_owner > 0 and train_deadline > 0:
        remaining = max(0, int(train_deadline - time.time() + 0.999))
        minutes, seconds = divmod(remaining, 60)
        suffix = " (пауза VN)" if train_paused else ""
        active.append({"key": "TrainTimer", "value": f"{minutes:02d}:{seconds:02d}{suffix}"})
    for key in sorted(globals_map.keys()):
        # Счетчик Х-125 и его служебные данные должны оставаться скрытыми.
        if str(key).startswith("X125_") or str(key).startswith("KlipotaApplied_") or str(key).startswith("KLIPOTA_"):
            continue
        value = globals_map.get(key)
        if not _is_active_global_value(value):
            continue
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, ensure_ascii=False)
        else:
            rendered = str(value)
        active.append({"key": str(key), "value": rendered})
    return active


VOYAGER_WORK_LABELS = {
    "intuition": "Интуиция",
    "insight": "Понимание",
    "affection": "Привязанность",
    "suppression": "Подавление",
}

BLOODBOT_INIT_HP = 1000
BLOODBOT_DAILY_LOSS = 250


def _bloodbot_ensure_inited():
    # Destruction clears ACTIVE, so DEAD must also block initialization;
    # otherwise reopening room 133 resurrects the mechanism at full HP.
    if (
        int(_safe_global_value("BLOODBOT_ACTIVE", 0) or 0) == 1
        or int(_safe_global_value("BLOODBOT_DEAD", 0) or 0) == 1
    ):
        return
    core.set_global_value(DB_PATH, "BLOODBOT_ACTIVE", 1)
    core.set_global_value(DB_PATH, "BLOODBOT_DEAD", 0)
    core.set_global_value(DB_PATH, "BLOODBOT_HP", BLOODBOT_INIT_HP)


def _bloodbot_event_for_player(player_id):
    event = _safe_global_value(f"BloodbotEvent_{int(player_id)}", {})
    return event if isinstance(event, dict) and int(event.get("id") or 0) > 0 else None


def _apply_bloodbot_daily_tick(player_ids):
    if int(_safe_global_value("BLOODBOT_ACTIVE", 0) or 0) != 1:
        return
    if int(_safe_global_value("BLOODBOT_DEAD", 0) or 0) == 1:
        return
    hp = max(0, int(_safe_global_value("BLOODBOT_HP", 0) or 0) - BLOODBOT_DAILY_LOSS)
    event_id = int(_safe_global_value("BloodbotEventId", 0) or 0) + 1
    core.set_global_value(DB_PATH, "BloodbotEventId", event_id)
    core.set_global_value(DB_PATH, "BLOODBOT_HP", hp)
    player_ids = [int(pid) for pid in (player_ids or [])]
    if hp > 0:
        text = f"Механизм слабеет: −{BLOODBOT_DAILY_LOSS} HP (осталось {hp})."
        for player_id in player_ids:
            core.set_global_value(DB_PATH, f"BloodbotEvent_{player_id}", {"id": event_id, "text": text, "dead": False, "hp": hp})
        return
    core.set_global_value(DB_PATH, "BLOODBOT_DEAD", 1)
    core.set_global_value(DB_PATH, "BLOODBOT_ACTIVE", 0)
    with db_connect_write() as conn:
        alive_rows = []
        if player_ids:
            placeholders = ",".join("?" for _ in player_ids)
            alive_rows = conn.execute(
                f"SELECT ID FROM PLAYERS WHERE ID IN ({placeholders}) AND COALESCE(IsDead, 0) = 0",
                tuple(player_ids),
            ).fetchall()
            conn.executemany("UPDATE PLAYERS SET SP = 100 WHERE ID = ?", [(int(row["ID"]),) for row in alive_rows])
            conn.commit()
    text = "Робот разрушен. Волна ужаса накрывает отдел: у всех живых SP установлен на 100."
    for row in alive_rows:
        player_id = int(row["ID"])
        psychosis = _roll_psychosis(player_id) if _current_psychosis_id(player_id) is None else None
        core.set_global_value(DB_PATH, f"BloodbotEvent_{player_id}", {
            "id": event_id, "text": text, "dead": True, "hp": 0, "psychosis": psychosis,
        })


def _clear_voyager_state(player_id):
    player_id = int(player_id)
    core.remove_player_effect(DB_PATH, player_id, "VoyagerCurse")
    for key, value in (
        (f"VoyagerCount_{player_id}", 0),
        (f"VoyagerBan_{player_id}", ""),
        (f"VoyagerBanDay_{player_id}", 0),
        (f"VoyagerSolo_{player_id}", {}),
    ):
        core.set_global_value(DB_PATH, key, value)


def _voyager_warning_payload(player_id):
    warning = _safe_global_value(f"VoyagerWarning_{int(player_id)}", {})
    if not isinstance(warning, dict) or warning.get("acknowledged"):
        return None
    if int(warning.get("day") or 0) != int(_current_day_number() or 0):
        return None
    return warning


def acknowledge_voyager_warning(player_id, event_id):
    key = f"VoyagerWarning_{int(player_id)}"
    warning = _safe_global_value(key, {})
    if isinstance(warning, dict) and int(warning.get("id") or 0) == int(event_id or 0):
        warning = dict(warning)
        warning["acknowledged"] = True
        core.set_global_value(DB_PATH, key, warning)
    return {"ok": True}


def _clay_popup_payload(player_id):
    popup = _safe_global_value(f"ClayPopup_{int(player_id)}", {})
    if not isinstance(popup, dict) or popup.get("acknowledged") or int(popup.get("id") or 0) <= 0:
        return None
    return popup


def _sync_death_action_log(player_ids):
    """Publish each actual player death exactly once per game."""
    ids = [int(pid) for pid in (player_ids or [])]
    if not ids:
        return
    with db_connect() as conn:
        rows = conn.execute(
            f"SELECT ID, COALESCE(NAME, 'Сотрудник') AS NAME, COALESCE(DEATHREASON, '') AS DEATHREASON FROM PLAYERS WHERE ID IN ({','.join('?' for _ in ids)}) AND COALESCE(IsDead, 0) = 1",
            tuple(ids),
        ).fetchall()
    for row in rows:
        dead_id = int(row["ID"])
        if int(_safe_global_value(f"DeathLog_{dead_id}", 0) or 0) == 1:
            continue
        reason = str(row["DEATHREASON"] or "Причина неизвестна")
        _append_game_action_log("effect", f"Игрок {str(row['NAME'] or dead_id)} умер. Причина: {reason}", dead_id)
        core.set_global_value(DB_PATH, f"DeathLog_{dead_id}", 1)


def acknowledge_clay_popup(player_id, event_id):
    key = f"ClayPopup_{int(player_id)}"
    popup = _safe_global_value(key, {})
    if isinstance(popup, dict) and int(popup.get("id") or 0) == int(event_id or 0):
        popup = dict(popup)
        popup["acknowledged"] = True
        core.set_global_value(DB_PATH, key, popup)
    return {"ok": True}


def _apply_voyager_daily_tick(player_ids):
    current_day = int(_current_day_number() or 0)
    player_ids = [int(pid) for pid in (player_ids or [])]
    if current_day <= 0 or not player_ids:
        return
    with db_connect() as conn:
        placeholders = ",".join("?" for _ in player_ids)
        rows = conn.execute(
            f"SELECT ID, COALESCE(NAME, '') AS NAME, COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID IN ({placeholders})",
            tuple(player_ids),
        ).fetchall()
    players = {int(row["ID"]): {"name": str(row["NAME"] or f"Игрок {row['ID']}"), "alive": int(row["IsDead"] or 0) == 0} for row in rows}
    alive_ids = [pid for pid in player_ids if players.get(pid, {}).get("alive")]
    for cursed_id in player_ids:
        if not _player_has_effect(cursed_id, "VoyagerCurse"):
            continue
        if not players.get(cursed_id, {}).get("alive"):
            _clear_voyager_state(cursed_id)
            continue
        active_ban = str(_safe_global_value(f"VoyagerBan_{cursed_id}", "") or "").strip().lower()
        ban_day = int(_safe_global_value(f"VoyagerBanDay_{cursed_id}", 0) or 0)
        if active_ban:
            if current_day > ban_day:
                _clear_voyager_state(cursed_id)
            continue
        count = int(_safe_global_value(f"VoyagerCount_{cursed_id}", 3) or 3) - 1
        if count > 0:
            core.set_global_value(DB_PATH, f"VoyagerCount_{cursed_id}", count)
            continue
        banned_work = random.choice(list(VOYAGER_WORK_LABELS))
        event_id = int(_safe_global_value("VoyagerEventId", 0) or 0) + 1
        core.set_global_value(DB_PATH, "VoyagerEventId", event_id)
        core.set_global_value(DB_PATH, f"VoyagerCount_{cursed_id}", 0)
        core.set_global_value(DB_PATH, f"VoyagerBan_{cursed_id}", banned_work)
        core.set_global_value(DB_PATH, f"VoyagerBanDay_{cursed_id}", current_day)
        candidates = [pid for pid in alive_ids if pid != cursed_id]
        victim_name = players.get(cursed_id, {}).get("name") or f"Игрок {cursed_id}"
        if candidates:
            watcher_id = random.choice(candidates)
            warning = {
                "id": event_id,
                "day": current_day,
                "work": banned_work,
                "work_label": VOYAGER_WORK_LABELS[banned_work],
                "victim_id": cursed_id,
                "victim_name": victim_name,
                "acknowledged": False,
                "text": f"Кажется, что работа {VOYAGER_WORK_LABELS[banned_work]} сегодня приведёт к гибели {victim_name}. Сообщать об этом ему или нет — ваше решение.",
            }
            core.set_global_value(DB_PATH, f"VoyagerWarning_{watcher_id}", warning)
        else:
            core.set_global_value(DB_PATH, f"VoyagerSolo_{cursed_id}", {
                "id": event_id, "day": current_day, "work": banned_work,
            })


def _voyager_forbidden_work(player_id, work_type):
    player_id = int(player_id)
    if not _player_has_effect(player_id, "VoyagerCurse"):
        return False
    ban = str(_safe_global_value(f"VoyagerBan_{player_id}", "") or "").strip().lower()
    ban_day = int(_safe_global_value(f"VoyagerBanDay_{player_id}", 0) or 0)
    return bool(ban and ban == str(work_type or "").strip().lower() and ban_day == int(_current_day_number() or 0))


def _voyager_lethal_day(player_id):
    """Return True throughout the day selected by the Voyager curse."""
    player_id = int(player_id)
    if not _player_has_effect(player_id, "VoyagerCurse"):
        return False
    banned_work = str(_safe_global_value(f"VoyagerBan_{player_id}", "") or "").strip().lower()
    banned_day = int(_safe_global_value(f"VoyagerBanDay_{player_id}", 0) or 0)
    return bool(banned_work and banned_day == int(_current_day_number() or 0))


def _cleanup_new_day_effects(player_ids):
    player_ids = [int(pid) for pid in (player_ids or [])]
    if not player_ids:
        return
    if int(_current_day_number() or 0) == 10:
        _x125_mark("day10")
    _apply_worm_infection_daily_tick()
    _apply_companion_doom_daily_tick()
    _apply_bloodbot_daily_tick(player_ids)
    _apply_voyager_daily_tick(player_ids)
    _apply_item_new_day_ticks(player_ids)
    brass_death = _brass_sphere_end_of_day()
    if brass_death:
        state = core.get_game_state(DB_PATH)
        if state.get("status") == "started" and int(state.get("current_turn_user_id") or 0) == int(brass_death["user_id"]):
            skipped = core.advance_turn(DB_PATH, reason="brass_sphere_end_of_day")
            skipped_state = skipped.get("state", {})
            runtime_game["started"] = skipped_state.get("status") == "started"
            runtime_game["current_day"] = int(skipped_state.get("current_day") or runtime_game.get("current_day") or 0)
            runtime_game["winner_id"] = skipped_state.get("winner_user_id")
    for player_id in player_ids:
        for effect_name in TEMP_EFFECTS_TO_CLEAN:
            try:
                core.remove_player_effect(DB_PATH, int(player_id), effect_name)
            except sqlite3.OperationalError:
                continue
    try:
        core.set_global_value(DB_PATH, "UnderCurse2", 0)
        core.set_global_value(DB_PATH, "UnderCurse3", 0)
        core.set_global_value(DB_PATH, "DeathsToday", 0)
    except sqlite3.OperationalError:
        pass


def _remove_inventory_item_by_id(conn, player_id, item_id):
    row = _player_row_for_inventory(conn, int(player_id))
    if not row:
        return False
    for slot, amount in ((1, int(row["SLOT1AMOUNT"] or 0)), (2, int(row["SLOT2AMOUNT"] or 0))):
        item_col = f"INVSLOT{slot}"
        amount_col = f"SLOT{slot}AMOUNT"
        if int(row[item_col] or 0) != int(item_id) or amount <= 0:
            continue
        if amount > 1:
            conn.execute(f"UPDATE PLAYERS SET {amount_col} = ? WHERE ID = ?", (amount - 1, int(player_id)))
        else:
            conn.execute(f"UPDATE PLAYERS SET {item_col} = 1, {amount_col} = 0 WHERE ID = ?", (int(player_id),))
        return True
    return False


def _apply_item_new_day_ticks(player_ids):
    """Run delayed item mechanics once when the game enters a new day."""
    player_ids = [int(pid) for pid in (player_ids or [])]
    current_day = int(_current_day_number() or 0)
    alive_ids = [pid for pid in player_ids if not _is_player_dead(pid)]

    # Fresh icicles melt three days after activation.
    with db_connect_write() as conn:
        for pid in player_ids:
            effects = list(_effects_for_player_conn(conn, pid))
            melt_day = core._effect_token_read(effects, "IcicleMeltDay", None)
            if melt_day is None or current_day < int(melt_day):
                continue
            row = _player_row_for_inventory(conn, pid)
            changed = False
            if row:
                for slot in (1, 2):
                    if int(row[f"INVSLOT{slot}"] or 0) == 8 and int(row[f"SLOT{slot}AMOUNT"] or 0) > 0:
                        conn.execute(f"UPDATE PLAYERS SET INVSLOT{slot} = 9 WHERE ID = ?", (pid,))
                        changed = True
            core._effect_remove_prefix(effects, "IcicleMeltDay")
            core._effect_remove_prefix(effects, "IcicleUsed")
            core._save_effects(conn, pid, effects)
            if changed:
                core.record_turn_event(DB_PATH, "icicle_melted", user_id=pid, day_number=current_day)

    # Panacea's delayed doom.
    for pid in list(alive_ids):
        effects = list(_safe_player_effects(pid))
        days = core._effect_token_read(effects, "PANACEA_DOOM_IN", None)
        if days is None:
            continue
        days = int(days) - 1
        if days > 0:
            with db_connect_write() as conn:
                current = list(_effects_for_player_conn(conn, pid))
                core._effect_token_write(current, "PANACEA_DOOM_IN", days)
                core._save_effects(conn, pid, current)
            continue
        with db_connect_write() as conn:
            current = list(_effects_for_player_conn(conn, pid))
            core._effect_remove_prefix(current, "PANACEA_DOOM_IN")
            core._save_effects(conn, pid, current)
        core.apply_damage(DB_PATH, pid, hp_damage=6666, reason="Устранён Фондом после действия Панацеи")

    # The guitar counts down for its owner and then bursts over every survivor.
    exploding = []
    for pid in player_ids:
        effects = list(_safe_player_effects(pid))
        left = int(core._effect_token_read(effects, "GuitarTurnsLeft", _safe_global_value(f"GuitarTurnsLeft_{pid}", 0)) or 0)
        if left <= 0:
            continue
        left -= 1
        core.set_global_value(DB_PATH, f"GuitarTurnsLeft_{pid}", left)
        with db_connect_write() as conn:
            current = list(_effects_for_player_conn(conn, pid))
            if left > 0:
                core._effect_token_write(current, "GuitarTurnsLeft", left)
            else:
                core._effect_remove_prefix(current, "GuitarTurnsLeft")
            core._save_effects(conn, pid, current)
            conn.commit()
        if left == 0:
            exploding.append(pid)
    if exploding:
        with db_connect_write() as conn:
            for owner_id in exploding:
                _remove_inventory_item_by_id(conn, owner_id, 29)
        for pid in alive_ids:
            core.apply_damage(DB_PATH, pid, sp_damage=75, reason="Взрыв Мясной гитары")

    # Synthesizer advances the next entered day to day 15.
    synth_pending_players = [pid for pid in player_ids if "SynthWarpPending" in _safe_player_effects(pid)]
    if int(_safe_global_value("SYNTH_WARP", 0) or 0) == 1 or synth_pending_players:
        core.set_global_value(DB_PATH, "SYNTH_WARP", 0)
        core.set_global_value(DB_PATH, "NoEscape", 1)
        with db_connect_write() as conn:
            for pid in synth_pending_players:
                current = list(_effects_for_player_conn(conn, pid))
                core._effect_remove_prefix(current, "SynthWarpPending")
                core._save_effects(conn, pid, current)
            conn.commit()
        if current_day < 15:
            with db_connect_write() as conn:
                conn.execute("UPDATE CORE_GAME_STATE SET current_day = 15 WHERE id = 1")
                conn.commit()
            core.set_global_value(DB_PATH, "CurrentDay", 15)
            runtime_game["current_day"] = 15

    # Violin: daily wave excludes the owner; keeping it for three days kills them.
    owner_id = _violin_owner_id()
    if owner_id > 0 and not _is_player_dead(owner_id):
        previous_owner = int(_safe_global_value("ViolinOwnerPid", 0) or 0)
        streak = int(_safe_global_value("ViolinOwnerStreak", 0) or 0)
        streak = streak + 1 if previous_owner == owner_id else 1
        core.set_global_value(DB_PATH, "ViolinOwnerPid", owner_id)
        core.set_global_value(DB_PATH, "ViolinOwnerStreak", streak)
        triggered = int(_safe_global_value("ViolinTriggeredToday", 0) or 0) == 1
        core.set_global_value(DB_PATH, "ViolinTriggeredToday", 0)
        if streak >= 3:
            core.set_player_dead(DB_PATH, owner_id, reason="Наказан Скрипкой Безмолвного Дирижёра")
            with db_connect_write() as conn:
                _remove_inventory_item_by_id(conn, owner_id, 33)
            core.set_global_value(DB_PATH, "ViolinOwnerPid", 0)
            core.set_global_value(DB_PATH, "ViolinOwnerStreak", 0)
        elif not triggered:
            damage = int(_safe_global_value("ViolinDamage", 40) or 40)
            for pid in alive_ids:
                if pid != owner_id:
                    core.apply_damage(DB_PATH, pid, sp_damage=damage, reason="Беззвучная волна Скрипки")

    # Accumulated time-shift pain returns at the end of the day.
    for pid in alive_ids:
        effects = list(_safe_player_effects(pid))
        if core.TSD_FLAG not in effects:
            continue
        accumulated = int(core._effect_token_read(effects, core.TSD_ACC_TOK, 0) or 0)
        if accumulated <= 0:
            continue
        core.set_global_value(DB_PATH, "TSD_BYPASS", 1)
        try:
            core.apply_damage(DB_PATH, pid, hp_damage=accumulated, sp_damage=accumulated, reason="Возврат урона временного сдвига")
        finally:
            core.set_global_value(DB_PATH, "TSD_BYPASS", 0)

    # Шнублик is a daily companion, not a post-research effect.
    shnublik_ids = []
    with db_connect_write() as conn:
        for pid in alive_ids:
            row = conn.execute("SELECT COALESCE(COMPSLOT,0), COALESCE(HP,0), COALESCE(MAXHP,100), COALESCE(SP,0) FROM PLAYERS WHERE ID = ?", (pid,)).fetchone()
            if not row or int(row[0] or 0) != 12:
                continue
            heal = max(5, min(15, int(round(int(row[2] or 100) * 0.05))))
            conn.execute("UPDATE PLAYERS SET HP = MIN(COALESCE(MAXHP,100), COALESCE(HP,0) + ?) WHERE ID = ?", (heal, pid))
            shnublik_ids.append(pid)
        conn.commit()
    for pid in shnublik_ids:
        core.apply_damage(DB_PATH, pid, sp_damage=5, reason="Цена лечения Шнублика")
    state_after_ticks = core.get_game_state(DB_PATH)
    current_turn_id = int(state_after_ticks.get("current_turn_user_id") or 0)
    if current_turn_id > 0 and _is_player_dead(current_turn_id):
        advanced = core.advance_turn(DB_PATH, reason="new_day_item_effect_death")
        advanced_state = advanced.get("state", {})
        runtime_game["started"] = advanced_state.get("status") == "started"
        runtime_game["current_day"] = int(advanced_state.get("current_day") or runtime_game.get("current_day") or 0)
        runtime_game["winner_id"] = advanced_state.get("winner_user_id")


def _clear_worm_infection(victim_id=0):
    victim_id = int(victim_id or _safe_global_value("WormVictim", 0) or 0)
    if victim_id > 0:
        try:
            core.remove_player_effect(DB_PATH, victim_id, "WormEggs")
        except sqlite3.OperationalError:
            pass
    for key in ("WormActive", "WormStartDay", "WormVictim", "WormLastTickDay"):
        try:
            core.set_global_value(DB_PATH, key, 0)
        except sqlite3.OperationalError:
            pass


def _apply_worm_infection_daily_tick():
    if int(_safe_global_value("WormActive", 0) or 0) != 1:
        return None
    victim_id = int(_safe_global_value("WormVictim", 0) or 0)
    start_day = int(_safe_global_value("WormStartDay", 0) or 0)
    current_day = int(_current_day_number() or 0)
    last_tick_day = int(_safe_global_value("WormLastTickDay", 0) or 0)
    if victim_id <= 0 or start_day <= 0 or _is_player_dead(victim_id):
        _clear_worm_infection(victim_id)
        return None
    if current_day <= start_day or current_day == last_tick_day:
        return None
    core.set_global_value(DB_PATH, "WormLastTickDay", current_day)
    infection_day = current_day - start_day
    if 1 <= infection_day <= 3:
        damage = core.apply_damage(
            DB_PATH, victim_id, hp_damage=17, sp_damage=0,
            reason="Был съеден изнутри плотоядными эндопаразитами",
        )
        if bool(damage.get("is_dead")):
            _clear_worm_infection(victim_id)
            _advance_after_worm_death_if_needed(victim_id)
        return {"stage": "red", "day": infection_day, "damage": damage}
    if 4 <= infection_day <= 6:
        damage = core.apply_damage(
            DB_PATH, victim_id, hp_damage=0, sp_damage=17,
            reason="Был съеден изнутри плотоядными эндопаразитами",
        )
        if bool(damage.get("is_dead")):
            _clear_worm_infection(victim_id)
            _advance_after_worm_death_if_needed(victim_id)
        return {"stage": "black", "day": infection_day, "damage": damage}
    if infection_day == 7:
        return {"stage": "maturing", "day": infection_day}
    if infection_day >= 8:
        death_reason = "Был съеден изнутри плотоядными эндопаразитами"
        core.set_player_dead(DB_PATH, victim_id, reason=death_reason)
        _clear_worm_infection(victim_id)
        _advance_after_worm_death_if_needed(victim_id)
        return {"stage": "fatal", "day": infection_day, "player_dead": True, "death_reason": death_reason}
    return None


def _advance_after_worm_death_if_needed(victim_id):
    state = core.get_game_state(DB_PATH)
    if state.get("status") != "started" or int(state.get("current_turn_user_id") or 0) != int(victim_id):
        return state
    advanced = core.advance_turn(DB_PATH, reason="worm_infection_death")
    next_state = advanced.get("state", {})
    runtime_game["started"] = next_state.get("status") == "started"
    runtime_game["current_day"] = int(next_state.get("current_day") or 0)
    runtime_game["winner_id"] = next_state.get("winner_user_id")
    if next_state.get("status") == "finished":
        _finalize_finished_game([int(pid) for pid in state.get("turn_order", [])])
    return next_state


def _clear_companion_doom():
    for key in ("CompanionDoomActive", "CompanionDoomStartDay", "CompanionDoomVictim", "CompanionDoomLastTickDay"):
        try:
            core.set_global_value(DB_PATH, key, 0)
        except sqlite3.OperationalError:
            pass


def _apply_companion_doom_daily_tick():
    if int(_safe_global_value("CompanionDoomActive", 0) or 0) != 1:
        return None
    victim_id = int(_safe_global_value("CompanionDoomVictim", 0) or 0)
    start_day = int(_safe_global_value("CompanionDoomStartDay", 0) or 0)
    current_day = int(_current_day_number() or 0)
    last_tick_day = int(_safe_global_value("CompanionDoomLastTickDay", 0) or 0)
    if victim_id <= 0 or start_day <= 0 or _is_player_dead(victim_id):
        _clear_companion_doom()
        return None
    with db_connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(COMPSLOT, 0) AS COMPSLOT FROM PLAYERS WHERE ID = ?",
            (victim_id,),
        ).fetchone()
    companion_id = int(row["COMPSLOT"] or 0) if row else 0
    if companion_id <= 0:
        _clear_companion_doom()
        return {"stage": "cleared", "owner_id": victim_id, "reason": "companion_missing"}
    if current_day <= start_day or current_day == last_tick_day:
        return None
    core.set_global_value(DB_PATH, "CompanionDoomLastTickDay", current_day)
    days_passed = current_day - start_day
    if days_passed < 3:
        return {"stage": "countdown", "owner_id": victim_id, "companion_id": companion_id, "days_passed": days_passed, "days_total": 3}
    _cleanup_companion_on_replace(victim_id, companion_id)
    with db_connect_write() as conn:
        conn.execute("UPDATE PLAYERS SET COMPSLOT = 0 WHERE ID = ?", (victim_id,))
        conn.commit()
    _clear_companion_doom()
    return {"stage": "dead", "owner_id": victim_id, "companion_id": companion_id, "days_passed": days_passed, "days_total": 3}


def _resolve_alastor_task7_at_day_boundary(prey_id, current_day):
    """Resolve yesterday's death task only after every player has acted."""
    task_id = int(_safe_global_value("AlastorTask", 0) or 0)
    task_day = _alastor_task_day()
    if task_id != 7 or task_day <= 0 or task_day >= int(current_day):
        return
    mood = int(_safe_global_value("AlastorMood", 3) or 3)
    success = _alastor_task_completed(int(prey_id), 0, 7)
    if success:
        success_count = int(_safe_global_value("AlastorSuccessCount", 0) or 0) + 1
        if success_count >= 3:
            mood = min(4, mood + 1)
            success_count = 0
            core.set_global_value(DB_PATH, "AlastorMood", mood)
        core.set_global_value(DB_PATH, "AlastorSuccessCount", success_count)
        core.set_global_value(
            DB_PATH,
            "AlastorPendingSuccessText",
            "Прошлое задание выполнено.\nПолучена награда: Сегодня ты не умрешь.",
        )
    else:
        core.set_global_value(DB_PATH, "AlastorMood", min(4, mood + 1))
        core.set_global_value(DB_PATH, "AlastorSuccessCount", 0)
        core.set_global_value(DB_PATH, "AlastorPendingSuccessText", "")
    _clear_alastor_task_runtime()


def _prepare_alastor_new_day_task():
    prey_id = int(_safe_global_value("AlastorPrey", 0) or 0)
    if prey_id <= 0:
        return
    pact = _alastor_get_pact_state(prey_id)
    if not pact["accepted"]:
        return
    current_day = int(_current_day_number() or 0)
    if current_day <= _alastor_accepted_day():
        return
    _resolve_alastor_task7_at_day_boundary(prey_id, current_day)
    if _alastor_task_day() == current_day and int(_safe_global_value("AlastorTask", 0) or 0) > 0:
        return
    _assign_alastor_task_for_current_day(prey_id)


def _safe_player_effects(player_id):
    try:
        return core.list_player_effects(DB_PATH, int(player_id))
    except sqlite3.OperationalError:
        return []


def _player_companion_id(user_id):
    with db_connect() as conn:
        row = conn.execute("SELECT COALESCE(COMPSLOT, 0) AS COMPSLOT FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    return int(row["COMPSLOT"] or 0) if row else 0


def _mature_active_companions(player_ids):
    player_ids = [int(pid) for pid in (player_ids or [])]
    if not player_ids:
        return
    placeholders = ",".join("?" for _ in player_ids)
    with db_connect_write() as conn:
        conn.execute(
            f"""
            UPDATE COMPANIONS
               SET DAYS = CASE
                            WHEN COALESCE(DAYS, 0) >= 3 THEN 3
                            ELSE COALESCE(DAYS, 0) + 1
                          END
             WHERE ID IN (
                   SELECT DISTINCT COALESCE(COMPSLOT, 0)
                     FROM PLAYERS
                    WHERE ID IN ({placeholders})
                      AND COALESCE(COMPSLOT, 0) <> 0
             )
            """,
            tuple(player_ids),
        )
        conn.commit()


def _is_player_dead(player_id):
    with db_connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID = ?",
            (int(player_id),),
        ).fetchone()
    return bool(row and int(row["IsDead"] or 0) == 1)


def _apply_reptile_bite(player_ids):
    count = int(_safe_global_value("bitecount", 0) or 0)
    if count <= 0:
        return
    alive_ids = [int(pid) for pid in (player_ids or []) if not _is_player_dead(int(pid))]
    if not alive_ids:
        return
    placeholders = ",".join("?" for _ in alive_ids)
    with db_connect() as conn:
        rows = conn.execute(
            f"SELECT ID FROM PLAYERS WHERE COALESCE(COMPSLOT, 0) = 7 AND ID IN ({placeholders})",
            tuple(alive_ids),
        ).fetchall()
    owners = [int(row["ID"]) for row in rows]
    for owner_id in owners:
        try:
            core.apply_damage(DB_PATH, int(owner_id), hp_damage=10, sp_damage=0, reason="Варан с человеческим лицом укусил владельца.")
        except sqlite3.OperationalError:
            continue
    try:
        core.set_global_value(DB_PATH, "bitecount", max(0, count - 1))
    except sqlite3.OperationalError:
        pass


def _apply_salamander_daily_tick(player_ids):
    alive_ids = [int(pid) for pid in (player_ids or []) if not _is_player_dead(int(pid))]
    if not alive_ids:
        return
    placeholders = ",".join("?" for _ in alive_ids)
    with db_connect_write() as conn:
        rows = conn.execute(
            f"""
            SELECT ID, COALESCE(HP, 0) AS HP, COALESCE(MAXHP, 100) AS MAXHP
            FROM PLAYERS
            WHERE COALESCE(COMPSLOT, 0) = 14 AND ID IN ({placeholders})
            """,
            tuple(alive_ids),
        ).fetchall()
        for row in rows:
            effects = core.list_player_effects(DB_PATH, int(row["ID"]))
            mult = max(1, int(core._effect_token_read(effects, core.SALA_MULT_TOK, 1) or 1))
            heal_amount = 10 * mult
            shield_add = 10 * mult
            new_hp = min(int(row["MAXHP"] or 100), int(row["HP"] or 0) + heal_amount)
            core._effect_token_write(effects, core.SALA_SHIELD_TOK, int(core._effect_token_read(effects, core.SALA_SHIELD_TOK, 0) or 0) + shield_add)
            conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (int(new_hp), int(row["ID"])))
            core._save_effects(conn, int(row["ID"]), effects)
        conn.commit()


def _apply_new_day_companion_effects(player_ids):
    player_ids = [int(pid) for pid in (player_ids or [])]
    if not player_ids:
        return
    _mature_active_companions(player_ids)
    _apply_salamander_daily_tick(player_ids)
    _apply_reptile_bite(player_ids)
    _apply_utilizer_daily_tick(player_ids)


UTILIZER_ITEM_ID = 26


def _remove_utilizer_if_fortitude_too_high(user_id):
    with db_connect_write() as conn:
        row = conn.execute(
            "SELECT COALESCE(STAT1, 1) AS STAT1, COALESCE(INVSLOT1, 0) AS I1, COALESCE(INVSLOT2, 0) AS I2 FROM PLAYERS WHERE ID = ?",
            (int(user_id),),
        ).fetchone()
        if not row or int(row["STAT1"] or 1) < 4:
            return False
        changed = False
        if int(row["I1"] or 0) == UTILIZER_ITEM_ID:
            conn.execute("UPDATE PLAYERS SET INVSLOT1 = 1, SLOT1AMOUNT = 0 WHERE ID = ?", (int(user_id),))
            changed = True
        if int(row["I2"] or 0) == UTILIZER_ITEM_ID:
            conn.execute("UPDATE PLAYERS SET INVSLOT2 = 1, SLOT2AMOUNT = 0 WHERE ID = ?", (int(user_id),))
            changed = True
        if changed:
            conn.commit()
    if changed:
        _set_utilizer_notice(int(user_id), "Утилизатор замолкает и ломается.", "Утилизатор сломан")
    return changed


def _set_utilizer_notice(user_id, message, title="Утилизатор"):
    core.set_global_value(DB_PATH, f"UTILIZER_NOTICE_{int(user_id)}", {
        "pending": True,
        "title": str(title),
        "message": str(message),
    })


def _get_utilizer_notice(user_id):
    notice = _safe_global_value(f"UTILIZER_NOTICE_{int(user_id)}", {})
    return notice if isinstance(notice, dict) and notice.get("pending") else {"pending": False}


def consume_utilizer_notice(user_id):
    core.set_global_value(DB_PATH, f"UTILIZER_NOTICE_{int(user_id)}", {})
    return {"ok": True}


def _apply_utilizer_daily_tick(player_ids):
    for user_id in [int(pid) for pid in (player_ids or [])]:
        if _is_player_dead(user_id):
            continue
        if _remove_utilizer_if_fortitude_too_high(user_id):
            continue
        notice_message = ""
        consumed_companion_id = 0
        with db_connect_write() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(INVSLOT1, 0) AS I1, COALESCE(SLOT1AMOUNT, 0) AS A1,
                       COALESCE(INVSLOT2, 0) AS I2, COALESCE(SLOT2AMOUNT, 0) AS A2,
                       COALESCE(COMPSLOT, 0) AS COMP, COALESCE(HP, 0) AS HP,
                       COALESCE(MAXHP, 1) AS MAXHP
                FROM PLAYERS WHERE ID = ?
                """,
                (user_id,),
            ).fetchone()
            if not row or UTILIZER_ITEM_ID not in (int(row["I1"] or 0), int(row["I2"] or 0)):
                continue

            consumed = False
            for slot in (1, 2):
                item_id = int(row[f"I{slot}"] or 0)
                amount = int(row[f"A{slot}"] or 0)
                if item_id not in (0, 1, UTILIZER_ITEM_ID) and amount > 0:
                    item_row = conn.execute("SELECT COALESCE(NAME, '') AS NAME FROM ITEMS WHERE ID = ?", (item_id,)).fetchone()
                    item_name = str(item_row["NAME"] or f"Предмет {item_id}") if item_row else f"Предмет {item_id}"
                    if amount > 1:
                        conn.execute(f"UPDATE PLAYERS SET SLOT{slot}AMOUNT = ? WHERE ID = ?", (amount - 1, user_id))
                    else:
                        conn.execute(f"UPDATE PLAYERS SET INVSLOT{slot} = 1, SLOT{slot}AMOUNT = 0 WHERE ID = ?", (user_id,))
                    consumed = True
                    notice_message = f"Утилизатор съел предмет «{item_name}» из слота {slot}."
                    break
            if not consumed:
                for slot in (1, 2):
                    if int(row[f"I{slot}"] or 0) == 1:
                        conn.execute(f"UPDATE PLAYERS SET INVSLOT{slot} = 0, SLOT{slot}AMOUNT = 0 WHERE ID = ?", (user_id,))
                        consumed = True
                        notice_message = f"Утилизатор перекусил остатками предмета: пустой слот {slot} исчез."
                        break
            if not consumed and int(row["COMP"] or 0) > 0:
                companion_id = int(row["COMP"] or 0)
                companion_row = conn.execute("SELECT COALESCE(NAME, '') AS NAME FROM COMPANIONS WHERE ID = ?", (companion_id,)).fetchone()
                companion_name = str(companion_row["NAME"] or f"Компаньон {companion_id}") if companion_row else f"Компаньон {companion_id}"
                conn.execute("UPDATE PLAYERS SET COMPSLOT = 0 WHERE ID = ?", (user_id,))
                consumed = True
                consumed_companion_id = companion_id
                notice_message = f"Утилизатор пожрал компаньона «{companion_name}»."
            if not consumed:
                new_max = max(1, int(row["MAXHP"] or 1) - 25)
                conn.execute(
                    "UPDATE PLAYERS SET MAXHP = ?, HP = MIN(COALESCE(HP, 0), ?) WHERE ID = ?",
                    (new_max, new_max, user_id),
                )
                notice_message = f"Утилизатор избавил вас от «лишней конечности». Максимальное здоровье уменьшено до {new_max}."
            conn.commit()
        if consumed_companion_id:
            _cleanup_companion_on_replace(user_id, consumed_companion_id)
        if notice_message:
            _set_utilizer_notice(user_id, notice_message)


def _build_companion9_notice(user_id):
    if _player_companion_id(user_id) != 9:
        return None
    current_day = int(_current_day_number() or 0)
    effects = _safe_player_effects(user_id)
    next_day = core._effect_token_read(effects, "comp9_next", None)
    if not isinstance(next_day, int) or next_day <= 0:
        anomaly_effects.apply_player_effect(f"comp9_next={current_day + 2}", player_id=int(user_id), db_path=DB_PATH)
        return None
    if current_day < next_day:
        return None
    core.remove_player_effect(DB_PATH, int(user_id), f"comp9_next={next_day}")
    anomaly_effects.apply_player_effect(f"comp9_next={current_day + 2}", player_id=int(user_id), db_path=DB_PATH)
    return {
        "pending": True,
        "title": "Ценный комментарий",
        "description": random.choice(XQC_LINES),
        "icon": "/photo/work_room/neutralresult.png",
        "iconAlt": "XqC",
    }


def _effect_base_key(effect_value):
    text = "" if effect_value is None else str(effect_value).strip()
    return text.split("=", 1)[0].strip() if "=" in text else text


def _effect_debug_info(effect_value):
    raw = "" if effect_value is None else str(effect_value).strip()
    if not raw:
        return None
    base_key = _effect_base_key(raw)
    info = None
    if base_key.isdigit():
        info = effect_dictionary.PSYCHOSIS_EFFECTS_S.get(base_key)
    if info is None:
        info = (
            effect_dictionary.CURSES_CATALOG.get(base_key)
            or effect_dictionary.BLESS_CATALOG.get(base_key)
            or effect_dictionary.NEUTRAL_CATALOG.get(base_key)
        )
    return {
        "raw": raw,
        "key": base_key,
        "name": (info or {}).get("name") or base_key,
        "description": (info or {}).get("desc") or "Описание эффекта пока не добавлено.",
    }


def get_player_effect_debug(player_id):
    effects = []
    with db_connect() as conn:
        row = conn.execute(
            f"""
            SELECT {', '.join(core.EFFECT_COLUMNS)},
                   COALESCE(PisosCurseRevealed, 0) AS PisosCurseRevealed,
                   COALESCE(FleeIsDeathRevealed, 0) AS FleeIsDeathRevealed,
                   COALESCE(FleeIsDeathHidden, 0) AS FleeIsDeathHidden,
                   COALESCE((SELECT anomaly_id FROM WORK WHERE user_id = PLAYERS.ID LIMIT 1), 0) AS CurrentWorkAnomalyId,
                   COALESCE((SELECT hintunlocked FROM WORK WHERE user_id = PLAYERS.ID LIMIT 1), 0) AS CurrentHintsUnlocked,
                   COALESCE((SELECT hintcount FROM WORK WHERE user_id = PLAYERS.ID LIMIT 1), 0) AS CurrentHintsTotal
            FROM PLAYERS WHERE ID = ?
            """,
            (int(player_id),),
        ).fetchone()
    if not row:
        return effects
    pisos_revealed = int(row["PisosCurseRevealed"] or 0) == 1
    current_is_unfinished_anomaly6 = (
        int(row["CurrentWorkAnomalyId"] or 0) == 6
        and int(row["CurrentHintsUnlocked"] or 0) < int(row["CurrentHintsTotal"] or 0)
    )
    flee_is_death_hidden = (
        current_is_unfinished_anomaly6
        or (int(row["FleeIsDeathHidden"] or 0) == 1 and int(row["FleeIsDeathRevealed"] or 0) == 0)
    )
    for index, column in enumerate(core.EFFECT_COLUMNS, start=1):
        effect = _effect_debug_info(row[column])
        if effect:
            # Internal counters drive mechanics, but must never be exposed as
            # player-facing status names.
            if str(effect.get("key") or "").lower() in {"comp9_next", "guitarturnsleft"}:
                continue
            if effect.get("key") == core.SALA_MULT_TOK:
                try:
                    if int(str(effect.get("raw") or "").split("=", 1)[1]) < 2:
                        continue
                except (IndexError, TypeError, ValueError):
                    continue
            if effect.get("key") == core.SALA_SHIELD_TOK:
                try:
                    shield_value = max(0, int(str(effect.get("raw") or "").split("=", 1)[1]))
                except (IndexError, TypeError, ValueError):
                    shield_value = 0
                effect["name"] = f"{effect['name']} ({shield_value})"
                effect["description"] = f"Может поглотить ещё {shield_value} урона."
            if str(effect.get("key") or "").lower() in {"sue_saved", core.COMP11_TOK.lower()}:
                continue
            if effect.get("key") == "PisosCurse":
                if pisos_revealed:
                    pisos_value = _pisos_curse_floor(player_id)
                    effect["name"] = f"{effect['name']} ({pisos_value})"
                else:
                    effect["raw"] = ""
                    effect["key"] = ""
                    effect["name"] = "Неизвестный эффект"
                    effect["description"] = "Эффект пока не раскрыт."
                    effect["hidden"] = True
            if effect.get("key") == "FleeIsDeath" and flee_is_death_hidden:
                effect["raw"] = ""
                effect["key"] = ""
                effect["name"] = "Неизвестный эффект"
                effect["description"] = "Эффект пока не раскрыт."
                effect["hidden"] = True
            if effect.get("key") == "TimeDebt69":
                revealed = int(row["CurrentWorkAnomalyId"] or 0) == 69 and int(row["CurrentHintsUnlocked"] or 0) >= 2
                if not revealed:
                    effect["raw"] = ""
                    effect["key"] = ""
                    effect["name"] = "Неизвестный эффект"
                    effect["description"] = "Эффект пока не раскрыт."
                    effect["hidden"] = True
            effect["slot"] = index
            effects.append(effect)
    bloodbot_active = int(_safe_global_value("BLOODBOT_ACTIVE", 0) or 0) == 1
    bloodbot_dead = int(_safe_global_value("BLOODBOT_DEAD", 0) or 0) == 1
    if bloodbot_active or bloodbot_dead:
        bloodbot_hp = max(0, int(_safe_global_value("BLOODBOT_HP", 0) or 0))
        effects.append({
            "raw": "BloodbotStatus",
            "key": "BloodbotStatus",
            "name": (
                f"Машина разрушена: {bloodbot_hp} / {BLOODBOT_INIT_HP} HP"
                if bloodbot_dead
                else f"Машина: {bloodbot_hp} / {BLOODBOT_INIT_HP} HP"
            ),
            "description": (
                "Механизм разрушен."
                if bloodbot_dead
                else f"Общее здоровье механизма: {bloodbot_hp} из {BLOODBOT_INIT_HP}."
            ),
            "global": True,
        })
    if int(_safe_global_value("CURSE_ENABLED", 0) or 0) == 1:
        trigger_key = str(_safe_global_value("CURSE_TRIGGER", "") or "")
        effect_key = str(_safe_global_value("CURSE_EFFECT", "") or "")
        if trigger_key in CURSE137_TRIGGERS and effect_key in CURSE137_EFFECTS:
            effects.append({
                "raw": "Curse137",
                "key": "Curse137",
                "name": "Проклятие незавершённой аномалии",
                "description": (
                    f"Условие: {CURSE137_TRIGGERS[trigger_key]}. "
                    f"Последствие: {CURSE137_EFFECTS[effect_key]}."
                ),
                "global": True,
            })
    return effects


def calculate_work_chance(anomaly_id, work_type, player_id, chosen_class=None, chosen_type=None):
    meta = WORK_TYPES.get(work_type)
    if not meta:
        return {"chance": 0, "debug": {}}
    active_psychosis = _current_psychosis_id(player_id)
    if active_psychosis and BLOCKED_WORK_BY_PSYCHOSIS.get(int(active_psychosis)) == work_type:
        return {
            "chance": 0,
            "debug": {
                "stat_column": meta["stat"],
                "stat_value": "-",
                "work_type": work_type,
                "base_column": "psychosis_block",
                "base_chance": 0,
                "class_modifier": 0,
                "type_modifier": 0,
                "final_chance": 0,
                "blocked_by_psychosis": int(active_psychosis),
            },
        }
    try:
        chosen_class = int(chosen_class) if chosen_class is not None else None
    except (TypeError, ValueError):
        chosen_class = None
    try:
        chosen_type = int(chosen_type) if chosen_type is not None else None
    except (TypeError, ValueError):
        chosen_type = None
    if chosen_class == 6:
        chosen_class = None
    if chosen_type == 6:
        chosen_type = None
    stat_column = meta["stat"]
    with db_connect() as conn:
        player = conn.execute(
            f"""
            SELECT {stat_column} AS stat_value,
                   COALESCE(COMPSLOT, 0) AS COMPSLOT,
                   COALESCE(STAT3, 1) AS STAT3,
                   COALESCE(PENALTY, 0) AS PENALTY,
                   COALESCE(BONUS, 0) AS BONUS,
                   COALESCE(HP, 0) AS HP,
                   COALESCE(MAXHP, 100) AS MAXHP
            FROM PLAYERS WHERE ID = ?
            """,
            (int(player_id),),
        ).fetchone()
        anomaly = conn.execute(
            """
            SELECT ID, CLASS_ID, TYPE, COALESCE(MODEL, '') AS MODEL, COALESCE(KLIPOTA, 0) AS KLIPOTA,
                   intuition1, intuition2, intuition3, intuition4, intuition5,
                   insight1, insight2, insight3, insight4, insight5,
                   affection1, affection2, affection3, affection4, affection5,
                   suppression1, suppression2, suppression3, suppression4, suppression5
            FROM ANOMALY WHERE ID = ?
            """,
            (int(anomaly_id),),
        ).fetchone()
        if not player or not anomaly:
            return {"chance": 0, "debug": {}}

        work_progress = _work_progress(player_id, anomaly_id)
        stat_value = max(1, min(5, int(player["stat_value"] or 1)))
        stat3_level = max(1, min(5, int(player["STAT3"] or 1)))
        stored_penalty = int(player["PENALTY"] or 0)
        current_bonus = int(player["BONUS"] or 0)
        base_column = f"{work_type}{stat_value}"
        base_chance = int(anomaly[base_column] or 0)
        original_base_chance = base_chance
        correct_class = int(anomaly["CLASS_ID"] or 0)
        correct_type = int(anomaly["TYPE"] or 0)
        current_penalty = _effective_penalty_for_work(player_id, correct_class, stored_penalty, int(work_progress.get("WorkCount") or 0))
        compslot = int(player["COMPSLOT"] or 0)
        class_modifier = 0
        type_modifier = 0
        companion_modifier = 0

        if int(anomaly_id) == 59:
            hp_sp = conn.execute("SELECT COALESCE(SP, 0) AS SP, COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?", (int(player_id),)).fetchone()
            sp = int(hp_sp["SP"] or 0)
            hp = int(hp_sp["HP"] or 0)
            if sp <= 50 and hp == 1:
                sp = 0
            if sp >= 100:
                return {"chance": 10, "debug": {"stat_column": stat_column, "stat_value": stat_value, "work_type": work_type, "base_column": "special_59", "base_chance": 10, "class_modifier": 0, "type_modifier": 0, "final_chance": 10}}
            if 71 <= sp <= 99:
                return {"chance": 25, "debug": {"stat_column": stat_column, "stat_value": stat_value, "work_type": work_type, "base_column": "special_59", "base_chance": 25, "class_modifier": 0, "type_modifier": 0, "final_chance": 25}}
            if 51 <= sp <= 70:
                return {"chance": 50, "debug": {"stat_column": stat_column, "stat_value": stat_value, "work_type": work_type, "base_column": "special_59", "base_chance": 50, "class_modifier": 0, "type_modifier": 0, "final_chance": 50}}
            if 1 <= sp <= 50:
                return {"chance": 65, "debug": {"stat_column": stat_column, "stat_value": stat_value, "work_type": work_type, "base_column": "special_59", "base_chance": 65, "class_modifier": 0, "type_modifier": 0, "final_chance": 65}}
            return {"chance": 80, "debug": {"stat_column": stat_column, "stat_value": stat_value, "work_type": work_type, "base_column": "special_59", "base_chance": 80, "class_modifier": 0, "type_modifier": 0, "final_chance": 80}}

        if int(anomaly_id) == 83:
            first_work_class = int(_safe_global_value("first_work_class", 0) or 0)
            base_for_83 = {1: 80, 2: 65, 3: 50, 4: 25, 5: 10}
            base_chance = base_for_83.get(first_work_class, 50)
            original_base_chance = base_chance
            correct_class = first_work_class if first_work_class in (1, 2, 3, 4, 5) else 3
            current_penalty = _effective_penalty_for_work(
                player_id, correct_class, stored_penalty, int(work_progress.get("WorkCount") or 0)
            )
            if chosen_type in (1, 2, 3, 4, 5):
                base_chance += 5
                type_modifier += 5

        if int(anomaly_id) == 105:
            work_chances = _anomaly105_work_chances(int(player_id), create=True)
            base_chance = int(work_chances.get(str(work_type), base_chance))
            original_base_chance = base_chance
            base_column = f"special_105_{work_type}"

        if compslot == 3 and correct_type == 2:
            base_chance += 10
            companion_modifier += 10
        if compslot == 4 and work_type == "intuition":
            base_chance += 5
            companion_modifier += 5
        if compslot == 10 and correct_type == 1:
            base_chance = max(base_chance, 50)

        progress = work_progress
        if int(_safe_global_value("babymonster", 0) or 0) == 1:
            base_chance -= 10 * (
                int(progress["photounlocked"] or 0) +
                int(progress["descriptionunlocked"] or 0) +
                int(progress["hintunlocked"] or 0)
            )

        effects = _safe_player_effects(player_id)
        if "CrimsonVirus" in effects:
            base_chance -= 10
        if "CinderPlague" in effects:
            if int(_safe_global_value("cinderplagueupgrade", 0) or 0) != 1 and correct_class == 5:
                base_chance += 10
            if correct_class == 4:
                base_chance -= 10

        if int(_safe_global_value("WorkBase10", 0) or 0) == 1:
            base_chance = 10

        if int(anomaly_id) == 14:
            current_hp = max(0, int(player["HP"] or 0))
            max_hp = max(1, int(player["MAXHP"] or 100))
            missing_hp_percent = max(0, ((max_hp - current_hp) * 100) // max_hp)
            passive_penalty_steps = missing_hp_percent // 10
            if passive_penalty_steps > 0:
                base_chance -= passive_penalty_steps * 5

        if int(anomaly_id) == 27:
            research_penalty_steps = (
                int(progress["photounlocked"] or 0)
                + int(progress["descriptionunlocked"] or 0)
                + int(progress["hintunlocked"] or 0)
            )
            if research_penalty_steps > 0:
                base_chance -= min(50, research_penalty_steps * 10)

        stat3_bonus = max(0, stat3_level - 1) * 5
        base_chance += stat3_bonus

        if int(anomaly_id) != 83:
            if chosen_class in (1, 2, 3, 4, 5):
                if chosen_class == correct_class:
                    base_chance += 10
                    class_modifier += 10
                else:
                    base_chance -= 10
                    class_modifier -= 10
            if chosen_type in (1, 2, 3, 4, 5):
                if chosen_type == correct_type:
                    base_chance += 5
                    type_modifier += 5
                else:
                    base_chance -= 5
                    type_modifier -= 5

    adjusted_chance = min(100, int(base_chance))
    final_chance = max(0, min(100, int(adjusted_chance - current_penalty + current_bonus)))
    anomaly68_boost = False
    if int(anomaly_id) == 68:
        tiers = (10, 25, 50, 65, 80)
        final_chance = next((tier for tier in tiers if final_chance <= tier), 80)
        anomaly68_boost = int(_safe_global_value(f"A68Boost_{int(player_id)}", 0) or 0) == 1
        if anomaly68_boost:
            final_chance = {10: 25, 25: 50, 50: 65, 65: 80, 80: 80}[final_chance]
    return {
        "chance": final_chance,
        "companion_slot": compslot,
        "debug": {
            "stat_column": stat_column,
            "stat_value": stat_value,
            "work_type": work_type,
            "base_column": base_column,
            "base_chance": original_base_chance,
            "temperance_bonus": stat3_bonus,
            "penalty": current_penalty,
            "stored_penalty": stored_penalty,
            "bonus": current_bonus,
            "adjusted_chance": adjusted_chance,
            "class_modifier": class_modifier,
            "type_modifier": type_modifier,
            "companion_modifier": companion_modifier,
            "companion_slot": compslot,
            "final_chance": final_chance,
            "anomaly68_boost": anomaly68_boost,
        },
    }


def get_work_room_payload(user_id, anomaly_id):
    ensure_player_registered(int(user_id))
    _ensure_work_entry(user_id, anomaly_id)
    if int(anomaly_id) == 133:
        _bloodbot_ensure_inited()
    _resolve_contract_if_due()
    progress = _work_progress(user_id, anomaly_id)
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT a.ID, a.NAME, a.CLASS_ID, a.TYPE, COALESCE(a.KLIPOTA, 0) AS KLIPOTA, COALESCE(a.MODEL, '') AS MODEL,
                   COALESCE(a.HINT, 0) AS HINTS_TOTAL, COALESCE(p.RP, 0) AS RP, COALESCE(p.PENALTY, 0) AS PENALTY,
                   COALESCE(p.BONUS, 0) AS BONUS, COALESCE(p.KLIPOTA, 0) AS PLAYER_KLIPOTA,
                   COALESCE(p.HP, 0) AS HP, COALESCE(p.MAXHP, 100) AS MAXHP,
                   COALESCE(p.SP, 0) AS SP, COALESCE(p.MAXSP, 200) AS MAXSP, COALESCE(p.RT, 0) AS RT, COALESCE(p.CP, 0) AS CP,
                   COALESCE(p.STAT1, 1) AS STAT1, COALESCE(p.STAT2, 1) AS STAT2, COALESCE(p.STAT3, 1) AS STAT3, COALESCE(p.STAT4, 1) AS STAT4,
                   COALESCE(p.IsDead, 0) AS IsDead, COALESCE(p.DEATHREASON, '') AS DEATHREASON, COALESCE(p.COMPSLOT, 0) AS COMPSLOT,
                   COALESCE(w.SnapshotHP, p.HP, 0) AS SnapshotHP,
                   COALESCE(w.SnapshotMaxHP, p.MAXHP, 100) AS SnapshotMaxHP,
                   COALESCE(w.SnapshotSP, p.SP, 0) AS SnapshotSP,
                   COALESCE(w.SnapshotMaxSP, p.MAXSP, 200) AS SnapshotMaxSP
            FROM ANOMALY a
            JOIN PLAYERS p ON p.ID = ?
            JOIN WORK w ON w.user_id = p.ID AND w.anomaly_id = a.ID
            WHERE a.ID = ?
            """,
            (int(user_id), int(anomaly_id)),
        ).fetchone()
    if not row:
        raise ValueError("Аномалия или игрок не найдены.")

    rp_hidden = bool(
        _player_has_effect(int(user_id), "NoResult")
        or _player_has_effect(int(user_id), "NoResultPermanent")
    )

    risk = RISK_META.get(int(row["CLASS_ID"] or 0), {"label": "UNKNOWN", "icon": None})
    show_risk = bool(progress["photounlocked"])
    show_name = bool(progress["photounlocked"])
    hints_total = int(progress["hintcount"] or 0)
    opened_hints = int(progress["hintunlocked"] or 0)
    show_klipota = bool(progress["photounlocked"])
    penalty_value = int(row["PENALTY"] or 0)
    class_id = int(row["CLASS_ID"] or 0)
    show_penalty = class_id in (4, 5) and penalty_value > 0
    psychosis = _current_psychosis_info(user_id)
    companion_offer = _build_companion_offer_payload(user_id, anomaly_id, progress)
    research_locked = _research_is_locked(progress)
    research_locked_reason = _research_lock_reason(progress)
    contract_warning = _build_contract_warning_payload(int(user_id))
    contract_summary = _build_contract_summary_payload(int(user_id))
    companion_notice = _build_companion9_notice(int(user_id))
    room_model = _room_model_for_anomaly(int(row["ID"]))
    with state_lock:
        lobby_player = next(
            (player for player in lobby_state.get("players", []) if int(player.get("id") or 0) == int(user_id)),
            None,
        )
        agent_character = int((lobby_player or {}).get("agent_character") or 0)
    voyager_solo = _safe_global_value(f"VoyagerSolo_{int(user_id)}", {})
    voyager_danger = None
    if (
        isinstance(voyager_solo, dict)
        and int(voyager_solo.get("day") or 0) == int(_current_day_number() or 0)
        and str(voyager_solo.get("work") or "") in VOYAGER_WORK_LABELS
        and _player_has_effect(int(user_id), "VoyagerCurse")
    ):
        voyager_danger = {
            "event_id": int(voyager_solo.get("id") or 0),
            "work": str(voyager_solo["work"]),
            "flash_ms": 1000,
        }

    return {
        "anomaly_id": int(row["ID"]),
        "name": row["NAME"],
        "display_name": row["NAME"] if show_name else "НЕИЗВЕСТНЫЙ ОБЪЕКТ",
        "class_id": class_id,
        "risk_label": risk["label"],
        "risk_icon": risk["icon"],
        "show_risk": show_risk,
        "show_klipota": show_klipota,
        "klipota": int(row["KLIPOTA"] or 0),
        "rp": None if rp_hidden else int(row["RP"] or 0),
        "rp_hidden": rp_hidden,
        "penalty": penalty_value,
        "show_penalty": show_penalty,
        "progress": progress,
        "can_finish_turn": int(progress.get("IsCompleted") or 0) == 1 or (int(row["ID"]) == 63 and int(progress.get("AlastorDealAccepted") or 0) == 1),
        "reward_claimed": _reward_already_claimed(user_id, anomaly_id),
        "model_url": room_model["url"],
        "model_size": room_model["size"],
        "model_placeholder": bool(room_model["placeholder"]),
        "model_dimmed": not show_name and not bool(room_model["placeholder"]),
        "agent_character": agent_character,
        "agent_model_url": f"/photo/agents/char{agent_character}.png" if 1 <= agent_character <= 6 else None,
        "research_locked": research_locked,
        "research_locked_reason": research_locked_reason,
        "companion_offer": companion_offer,
        "contract_warning": contract_warning,
        "contract_summary": contract_summary,
        "companion_notice": companion_notice,
        "voyager_danger": voyager_danger,
        "protocol_x": _protocol_x_payload(int(user_id)),
        "brainrot_music": _brainrot_music_payload(int(user_id)),
        "curse137_pending": int(row["ID"]) == 137 and int(progress.get("Curse137Pending") or 0) == 1,
        "predator_vn_resolved": int(row["ID"]) == 107 and int(progress.get("PredatorVnResolved") or 0) == 1,
        "player_status": {
            "hp": int(row["SnapshotHP"] or 0),
            "max_hp": int(row["SnapshotMaxHP"] or 100),
            "sp": int(row["SnapshotSP"] or 0),
            "max_sp": int(row["SnapshotMaxSP"] or 200),
            "bonus": int(row["BONUS"] or 0),
            "klipota": int(row["PLAYER_KLIPOTA"] or 0),
            "cp": int(row["CP"] or 0),
            "rt": int(row["RT"] or 0),
            "stats": [
                {"key": "stat1", "name": "Выносливость", "value": int(row["STAT1"] or 1), "icon": "/photo/stats/FortitudeIcon.png"},
                {"key": "stat2", "name": "Удача", "value": int(row["STAT2"] or 1), "icon": "/photo/stats/PrudenceIcon.png"},
                {"key": "stat3", "name": "Гибкость Ума", "value": int(row["STAT3"] or 1), "icon": "/photo/stats/TemperanceIcon.png"},
                {"key": "stat4", "name": "Адаптивность", "value": int(row["STAT4"] or 1), "icon": "/photo/stats/JusticeIcon.png"},
            ],
            "psychosis": psychosis,
            "effects": get_player_effect_debug(user_id),
            "companion": _get_companion_debug(int(row["COMPSLOT"] or 0), user_id),
        },
        "player_stats": {
            "hp": int(row["HP"] or 0),
            "sp": int(row["SP"] or 0),
            "rp": int(row["RP"] or 0),
            "rt": int(row["RT"] or 0),
            "cp": int(row["CP"] or 0),
            "bonus": int(row["BONUS"] or 0),
            "penalty": int(row["PENALTY"] or 0),
            "stat1": int(row["STAT1"] or 1),
            "stat2": int(row["STAT2"] or 1),
            "stat3": int(row["STAT3"] or 1),
            "stat4": int(row["STAT4"] or 1),
            "companion": _get_companion_debug(int(row["COMPSLOT"] or 0), user_id),
            "is_dead": int(row["IsDead"] or 0) == 1,
            "death_reason": _normalize_death_reason(row["DEATHREASON"]),
            "psychosis": psychosis,
            "effects": get_player_effect_debug(user_id),
            "companion_id": int(row["COMPSLOT"] or 0),
        } if debug_mode_enabled() else None,
        "works": [
            {
                "key": key,
                "label": meta["label"],
                "chance": calculate_work_chance(int(row["ID"]), key, int(user_id))["chance"],
                "blocked": bool(psychosis and BLOCKED_WORK_BY_PSYCHOSIS.get(int(psychosis["id"])) == key),
                "blocked_reason": f"Работа заблокирована психозом: {psychosis['name']}" if psychosis and BLOCKED_WORK_BY_PSYCHOSIS.get(int(psychosis["id"])) == key else "",
            }
            for key, meta in WORK_TYPES.items()
        ],
        "special_actions": {
            "reset": {
                "available": int(row["ID"]) == 11 and int(progress.get("ResetUsed") or 0) == 0
            },
            "anomaly68_donation": {
                "available": int(row["ID"]) == 68 and int(_safe_global_value(f"A68Boost_{int(user_id)}", 0) or 0) == 0,
                "used": int(row["ID"]) == 68 and int(_safe_global_value(f"A68Boost_{int(user_id)}", 0) or 0) == 1,
            }
        },
        "alastor_deal": {
            "pending": int(row["ID"]) == 63 and int(progress.get("AlastorDealStarted") or 0) == 1 and int(progress.get("AlastorDealAccepted") or 0) == 0,
            "accepted": int(progress.get("AlastorDealAccepted") or 0) == 1,
            "refusals": int(progress.get("AlastorDealRefusals") or 0),
        },
        "alastor_task": _build_alastor_task_prompt(int(user_id)),
        "alastor_debug": {
            "prey": int(_safe_global_value("AlastorPrey", 0) or 0),
            "mood": int(_safe_global_value("AlastorMood", 0) or 0),
            "task": int(_safe_global_value("AlastorTask", 0) or 0),
            "accepted_day": int(_safe_global_value("AlastorAcceptedDay", 0) or 0),
            "task_day": int(_safe_global_value("AlastorTaskDay", 0) or 0),
            "shown_day": int(_safe_global_value("AlastorTaskShownDay", 0) or 0),
            "current_day": int(_current_day_number() or 0),
        } if debug_mode_enabled() else None,
        "ilvetal_notice": _get_ilvetal_notice(int(user_id)),
        "cheaptrick_notice": _get_cheaptrick_notice(int(user_id)),
        "klipota_event": _klipota_event_payload(int(user_id)),
        "debug": None,
        "debug_globals": _safe_active_globals() if debug_mode_enabled() else [],
    }


def _record_alastor_anomaly_selection(user_id, anomaly_id, selection_position):
    position = int(selection_position or 0)
    if position < 1 or position > 5:
        raise ValueError("Позиция аномалии должна быть в диапазоне от 1 до 5.")
    with state_lock:
        assignments = list(lobby_state["game_assignments"].get(int(user_id), []))
    if position > len(assignments):
        raise ValueError("Выбранной позиции нет в текущем пуле аномалий.")
    selected = assignments[position - 1]
    if int(selected.get("id") or 0) != int(anomaly_id):
        raise ValueError("Позиция карточки не соответствует выбранной аномалии.")
    state = _alastor_current_task_state(int(user_id))
    if state and int(state.get("task_id") or 0) == 1:
        # Retained for request validation and backward compatibility. Task 1 is
        # now checked directly against the selected anomaly ID at resolution.
        core.set_global_value(DB_PATH, "ChosenAnomalyNumber", int(anomaly_id))
    return position


def run_initial_effect(user_id, anomaly_id):
    if int(anomaly_id or 0) in DISABLED_ANOMALY_IDS:
        raise ValueError(DISABLED_ANOMALY_MESSAGE)
    anomaly = _get_anomaly_row(anomaly_id)
    _apply_klipota_on_anomaly_taken(int(user_id), int(anomaly_id))
    _brass_sphere_on_anomaly_chosen(int(user_id), int(anomaly_id))
    effect_name = _get_initial_effect_name(anomaly)
    if int(anomaly_id) == 37:
        core.set_global_value(DB_PATH, "A37Guarantee46", 1)
    if int(anomaly_id) == 60:
        effect_name = None
    if int(anomaly_id) == 105:
        core.set_global_value(DB_PATH, f"A105WorkChances_{int(user_id)}", {})
        _anomaly105_work_chances(int(user_id), create=True)
    if int(anomaly_id) == 123:
        # The battle belongs to the employee who actually took X-125. Later
        # counter triggers must never replace this owner.
        core.set_global_value(DB_PATH, "X125_ANOMALY_OWNER_ID", int(user_id))
    # Anomaly 61 must start the Leviathan game even with an older database
    # where INITIALEFFECT has not yet been populated.
    if int(anomaly_id) == 61:
        effect_name = "start_battle_with_heli2"
    if int(anomaly_id) == 136:
        effect_name = "start_po3_trials"
    if int(anomaly_id) == 69:
        effect_name = "TimeDebt69"
        core.set_global_value(DB_PATH, "A69_HP", 0)
        core.set_global_value(DB_PATH, "A69_SP", 0)
        core.set_global_value(DB_PATH, "A69_CNT", 0)
    if not effect_name:
        return None
    effect_result = anomaly_effects.execute_hint_effect(
        effect_name,
        player_id=int(user_id),
        anomaly_id=int(anomaly_id),
        hint_slot=None,
        db_path=DB_PATH,
        runtime_state={
            "active_player_ids": [player["id"] for player in lobby_state.get("players", [])],
            "player_triggered_effects": {},
        },
    )
    _x125_mark_effect_result(effect_result, anomaly_id, effect_name)
    if int(anomaly_id) == 136 and effect_result:
        start_po3_web_event(int(user_id), int(anomaly_id))
    if int(anomaly_id) == 69 and effect_result:
        effect_result["title"] = "Неизвестный эффект"
        effect_result["description"] = "На сотрудника наложен неизвестный эффект."
        effect_result["modal"] = {
            "intro": "Неизвестный эффект",
            "effect": "Эффект пока не раскрыт.",
            "icon": "/photo/work_room/neutralresult.png",
            "iconAlt": "Неизвестный эффект",
        }
    if str((effect_result or {}).get("effect_key") or "") == "FleeIsDeath":
        is_secret_flee_effect = int(anomaly_id) == 6
        progress = _work_progress(user_id, anomaly_id) if is_secret_flee_effect else {}
        revealed = bool(
            not is_secret_flee_effect
            or int(progress.get("hintunlocked") or 0) >= int(progress.get("hintcount") or 0)
        )
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE PLAYERS SET FleeIsDeathHidden = ?, FleeIsDeathRevealed = ? WHERE ID = ?",
                (1 if is_secret_flee_effect else 0, 1 if revealed else 0, int(user_id)),
            )
            conn.commit()
        if is_secret_flee_effect:
            return None
    if str(effect_result.get("status") or "") == "missing":
        return {
            "status": "missing",
            "title": "403",
            "description": "403: нет кода мгновенного эффекта",
            "effect_name": effect_name,
        }
    return effect_result


def _admin_load_anomaly_card(anomaly_id):
    row = _get_anomaly_row(anomaly_id)
    if not row:
        raise ValueError("Аномалия не найдена.")
    anomaly_id = int(row["ID"])
    return {
        "id": anomaly_id,
        "name": row["NAME"] if int(row.get("IsDone") or 0) == 1 else (row.get("codename") or f"SC-UN-U-{anomaly_id}"),
        "description": row.get("PDESCRIPTION") or row.get("DESCRIPTION") or "Описание пока отсутствует.",
        "class_id": int(row.get("CLASS_ID") or 0),
        "photo": f"/photo/anomaly/{row['PHOTO']}.png" if row.get("PHOTO") else None,
    }


def admin_apply_action(user_id, action, value=None):
    ensure_player_registered(int(user_id))
    action = str(action or "").strip()
    if action == "add_stats":
        with db_connect_write() as conn:
            conn.execute(
                """
                UPDATE PLAYERS
                SET HP = CASE
                        WHEN COALESCE(STAT1, 1) < 5
                        THEN MIN(MIN(300, COALESCE(MAXHP, 100) + 50), COALESCE(HP, 0) + 50)
                        ELSE COALESCE(HP, 0)
                    END,
                    MAXHP = CASE
                        WHEN COALESCE(STAT1, 1) < 5
                        THEN MIN(300, COALESCE(MAXHP, 100) + 50)
                        ELSE COALESCE(MAXHP, 100)
                    END,
                    STAT1 = MIN(5, COALESCE(STAT1, 1) + 1),
                    STAT2 = MIN(5, COALESCE(STAT2, 1) + 1),
                    STAT3 = MIN(5, COALESCE(STAT3, 1) + 1),
                    STAT4 = MIN(5, COALESCE(STAT4, 1) + 1)
                WHERE ID = ?
                """,
                (int(user_id),),
            )
            conn.commit()
    elif action == "add_rp":
        with db_connect_write() as conn:
            conn.execute("UPDATE PLAYERS SET RP = COALESCE(RP, 0) + 900 WHERE ID = ?", (int(user_id),))
            conn.commit()
    elif action == "set_day":
        day = max(1, min(TOTAL_GAME_DAYS, int(value)))
        with db_connect_write() as conn:
            conn.execute(
                "UPDATE CORE_GAME_STATE SET current_day = ?, last_event_at = ? WHERE id = 1",
                (day, time.time()),
            )
            conn.commit()
        runtime_game["current_day"] = day
        runtime_game["day_started_at"] = time.time()
        core.set_global_value(DB_PATH, "CurrentDay", day)
        with state_lock:
            lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
        return {"ok": True, "game_state": get_game_state(int(user_id))}
    elif action == "spawn_anomaly":
        anomaly_id = int(value)
        if anomaly_id in DISABLED_ANOMALY_IDS:
            return {
                "ok": False,
                "warning": True,
                "message": DISABLED_ANOMALY_MESSAGE,
                "game_state": get_game_state(int(user_id)),
            }
        card = _admin_load_anomaly_card(anomaly_id)
        with state_lock:
            lobby_state["game_assignments"][int(user_id)] = [card]
        effect_result = run_initial_effect(int(user_id), anomaly_id)
        return {
            "ok": True,
            "game_state": get_game_state(int(user_id)),
            "room": get_work_room_payload(int(user_id), anomaly_id),
            "initial_effect_result": effect_result,
        }
    elif action == "force_next_anomaly":
        anomaly_id = int(value)
        if anomaly_id in DISABLED_ANOMALY_IDS:
            core.set_global_value(DB_PATH, "DebugForcedNextAnomaly", 0)
            return {
                "ok": False,
                "warning": True,
                "message": DISABLED_ANOMALY_MESSAGE,
                "game_state": get_game_state(int(user_id)),
            }
        card = _admin_load_anomaly_card(anomaly_id)
        core.set_global_value(DB_PATH, "DebugForcedNextAnomaly", anomaly_id)
        return {
            "ok": True,
            "message": f"Аномалия #{anomaly_id} ({card['name']}) гарантирована в следующем дневном пуле.",
            "forced_anomaly_id": anomaly_id,
            "game_state": get_game_state(int(user_id)),
        }
    elif action == "force_d20_roll":
        forced_roll = int(value)
        if forced_roll < 1 or forced_roll > 20:
            raise ValueError("Значение D20 должно быть от 1 до 20.")
        current_day = max(1, int(_current_day_number() or 1))
        if current_day >= TOTAL_GAME_DAYS:
            raise ValueError("После последнего дня следующего броска D20 не будет.")
        target_day = current_day + 1
        core.set_global_value(DB_PATH, "forcedroll", forced_roll)
        core.set_global_value(DB_PATH, "forcedroll_day", target_day)
        return {
            "ok": True,
            "message": f"На {target_day}-й день бросок D20 гарантированно даст {forced_roll}.",
            "forced_roll": forced_roll,
            "target_day": target_day,
            "game_state": get_game_state(int(user_id)),
        }
    elif action == "force_alastor_task":
        task_id = int(value)
        if task_id not in ALASTOR_TASKS:
            raise ValueError("Номер задания Аластора должен быть от 1 до 10.")
        current_day = max(1, int(_current_day_number() or 1))
        if current_day >= TOTAL_GAME_DAYS:
            raise ValueError("После последнего дня новое задание Аластора не запустится.")
        target_day = current_day + 1
        forced_mood = 4 if task_id == 10 else ((task_id - 1) // 3) + 1
        core.set_global_value(DB_PATH, "DebugForcedAlastorTask", task_id)
        core.set_global_value(DB_PATH, "DebugForcedAlastorTaskDay", target_day)
        return {
            "ok": True,
            "message": f"На {target_day}-й день будет назначено задание Аластора №{task_id}; mood будет установлен на {forced_mood}.",
            "forced_task": task_id,
            "forced_mood": forced_mood,
            "target_day": target_day,
            "game_state": get_game_state(int(user_id)),
        }
    elif action == "train_10_seconds":
        train_owner = int(_safe_global_value("TrainDeadlineUserId", 0) or 0)
        if train_owner <= 0 or float(_safe_global_value("TrainDeadlineAt", 0) or 0) <= 0:
            raise ValueError("Таймер Адского экспресса сейчас не активен.")
        core.set_global_value(DB_PATH, "TrainDeadlineAt", time.time() + 10)
        return {
            "ok": True,
            "message": "Таймер Адского экспресса установлен на 10 секунд.",
            "game_state": get_game_state(int(user_id)),
        }
    elif action == "x125_random_task":
        token = int(time.time() * 1000)
        core.set_global_value(DB_PATH, "X125_ACTIVE", 1)
        core.set_global_value(DB_PATH, "X125_OWNER_ID", int(user_id))
        core.set_global_value(DB_PATH, "X125_RUN_TOKEN", token)
        core.set_global_value(DB_PATH, "X125_EVENT_FIRED", 1)
        core.set_global_value(DB_PATH, "X125_SPECIAL_EVENT_ID", token)
        core.set_global_value(DB_PATH, "X125_SPECIAL_EVENT_DAY", int(_current_day_number() or 1))
        core.set_global_value(DB_PATH, "X125_BATTLE", {})
        special_event = _x125_special_event_payload()
        return {
            "ok": True,
            "message": "Отладка Х-125: событие запущено.",
            "x125_special_event": special_event,
            "game_state": get_game_state(int(user_id)),
        }
    elif action == "roll_psychosis":
        psychosis = _roll_psychosis(int(user_id), force=True)
        heart_attack = (psychosis or {}).get("heart_attack")
        if heart_attack is None:
            heart_attack = _apply_heart_attack_if_needed(int(user_id))
        current_work = None
        with db_connect() as conn:
            row = conn.execute("SELECT anomaly_id FROM WORK WHERE user_id = ?", (int(user_id),)).fetchone()
            current_work = int(row["anomaly_id"]) if row and row["anomaly_id"] is not None else None
        payload = {"ok": True, "psychosis": psychosis, "heart_attack": heart_attack, "game_state": get_game_state(int(user_id))}
        if current_work is not None:
            payload["room"] = get_work_room_payload(int(user_id), current_work)
        return payload
    else:
        raise ValueError("Неизвестное admin-действие.")
    current_work = None
    with db_connect() as conn:
        row = conn.execute("SELECT anomaly_id FROM WORK WHERE user_id = ?", (int(user_id),)).fetchone()
        current_work = int(row["anomaly_id"]) if row and row["anomaly_id"] is not None else None
    payload = {"ok": True, "game_state": get_game_state(int(user_id))}
    if current_work is not None:
        payload["room"] = get_work_room_payload(int(user_id), current_work)
    return payload


def _assert_current_turn(user_id):
    """Reject normal game actions submitted for somebody else's turn."""
    state = core.get_game_state(DB_PATH)
    if state.get("status") == "started":
        current_id = int(state.get("current_turn_user_id") or 0)
        if current_id and current_id != int(user_id):
            raise ValueError("Сейчас ход другого игрока.")


def update_camera_view(user_id, screen, anomaly_id=None, revision=None, vn_state=None, details_scroll_ratio=None, mini_game_state=None):
    _assert_current_turn(user_id)
    core_state = core.get_game_state(DB_PATH)
    normalized = str(screen or "selection").strip().lower()
    if normalized not in {"selection", "room", "details", "vn", "emoji_game", "sea_game"}:
        normalized = "selection"
    try:
        incoming_revision = int(revision or 0)
    except (TypeError, ValueError):
        incoming_revision = 0
    try:
        scroll_ratio = max(0.0, min(1.0, float(details_scroll_ratio or 0)))
    except (TypeError, ValueError):
        scroll_ratio = 0.0
    with state_lock:
        previous = camera_view_states.get(int(user_id)) or {}
        if incoming_revision > 0 and incoming_revision < int(previous.get("revision") or 0):
            return {"ok": True, "ignored": True}
        camera_view_states[int(user_id)] = {
            "screen": normalized,
            "anomaly_id": int(anomaly_id) if anomaly_id not in (None, "") else None,
            "updated_at": time.time(),
            "revision": incoming_revision,
            "vn_state": dict(vn_state) if normalized == "vn" and isinstance(vn_state, dict) else None,
            "mini_game_state": dict(mini_game_state) if normalized in {"emoji_game", "sea_game"} and isinstance(mini_game_state, dict) else None,
            "details_scroll_ratio": scroll_ratio if normalized == "details" else 0.0,
            # Bind the camera state to the actual turn. last_event_at cannot be
            # used for this: opening a hint and many other ordinary actions
            # update it without transferring the turn.
            "turn_index": int(core_state.get("turn_index") or 0),
            "day_number": int(core_state.get("current_day") or 0),
            "turn_user_id": int(core_state.get("current_turn_user_id") or 0),
        }
    return {"ok": True}


def _softlock_vote_payload(user_id):
    with state_lock:
        vote = dict(softlock_vote_state)
    if not vote:
        return None
    vote["voted"] = int(user_id) in {int(value) for value in vote.get("approvals", [])}
    vote["is_requester"] = int(vote.get("requester_id") or 0) == int(user_id)
    vote.pop("approvals", None)
    vote.pop("eligible_ids", None)
    return vote


def _interrupt_events_for_softlock():
    moon_eye_game_sessions.clear()
    emoji_glasses_game_sessions.clear()
    sea_monster_game_sessions.clear()
    tenna_game_sessions.clear()
    po3_sessions.clear()
    camera_view_states.clear()
    core.set_global_value(DB_PATH, "X125_BATTLE", {})
    core.set_global_value(DB_PATH, "X125_EVENT_FIRED", 0)
    paused_at = float(_safe_global_value("TrainPausedAt", 0) or 0)
    if paused_at > 0:
        deadline = float(_safe_global_value("TrainDeadlineAt", 0) or 0)
        if deadline > 0:
            core.set_global_value(DB_PATH, "TrainDeadlineAt", deadline + max(0, time.time() - paused_at))
        core.set_global_value(DB_PATH, "TrainPausedAt", 0)


def _force_next_day_after_softlock():
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") != "started":
        return core_state
    previous_day = int(core_state.get("current_day") or 1)
    target_day = previous_day + 1
    total_days = int(core_state.get("total_days") or TOTAL_GAME_DAYS)
    turn_order = [int(value) for value in core_state.get("turn_order", [])]
    alive_ids = [player_id for player_id in turn_order if not _is_player_dead(player_id)]
    _interrupt_events_for_softlock()
    if not alive_ids:
        finished = core.finish_game(DB_PATH, winner_user_id=None, reason="softlock_no_alive_players")
        runtime_game["started"] = False
        runtime_game["winner_id"] = finished.get("winner_user_id")
        _finalize_finished_game(turn_order)
        return finished
    if target_day > total_days:
        finished = core.finish_game(DB_PATH, reason="softlock_days_completed")
        runtime_game["started"] = False
        runtime_game["winner_id"] = finished.get("winner_user_id")
        _finalize_finished_game(turn_order)
        return finished
    first_index, first_alive = _rotated_day_first_alive(turn_order, alive_ids, target_day)
    with db_connect_write() as conn:
        conn.execute(
            """UPDATE CORE_GAME_STATE
               SET current_day = ?, turn_index = ?, current_turn_user_id = ?, last_event_at = ?
               WHERE id = 1""",
            (target_day, first_index, first_alive, time.time()),
        )
        conn.commit()
    core.set_global_value(DB_PATH, "CurrentDay", target_day)
    core.set_global_value(DB_PATH, "ActiveWorker", first_alive)
    runtime_game["started"] = True
    runtime_game["current_day"] = target_day
    runtime_game["day_started_at"] = time.time()
    _cleanup_new_day_effects(alive_ids)
    _apply_new_day_companion_effects(alive_ids)
    _prepare_alastor_new_day_task()
    with state_lock:
        lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
    return core.get_game_state(DB_PATH)


def start_softlock_vote(user_id):
    user_id = int(user_id)
    core_state = core.get_game_state(DB_PATH)
    if core_state.get("status") != "started" or _is_player_dead(user_id):
        raise ValueError("Запрос доступен только живому игроку во время игры.")
    eligible_ids = [int(pid) for pid in core_state.get("turn_order", []) if not _is_player_dead(int(pid))]
    if user_id not in eligible_ids:
        raise ValueError("Игрок не участвует в текущей игре.")
    with state_lock:
        if softlock_vote_state.get("status") == "active":
            return {"ok": True, "softlock_vote": _softlock_vote_payload(user_id)}
        vote_id = int(time.time() * 1000000)
        softlock_vote_state.clear()
        softlock_vote_state.update({
            "id": vote_id, "status": "active", "requester_id": user_id,
            "requester_name": _player_display_name(user_id), "eligible_ids": eligible_ids,
            "approvals": [user_id], "created_at": time.time(),
        })
    if len(eligible_ids) == 1:
        return vote_softlock(user_id, True)
    return {"ok": True, "softlock_vote": _softlock_vote_payload(user_id)}


def vote_softlock(user_id, approve):
    user_id = int(user_id)
    with state_lock:
        if softlock_vote_state.get("status") != "active":
            raise ValueError("Активного голосования о софтлоке нет.")
        eligible = {
            int(value) for value in softlock_vote_state.get("eligible_ids", [])
            if not _is_player_dead(int(value))
        }
        softlock_vote_state["eligible_ids"] = sorted(eligible)
        if user_id not in eligible or _is_player_dead(user_id):
            raise ValueError("Вы не можете участвовать в этом голосовании.")
        if not bool(approve):
            softlock_vote_state["status"] = "rejected"
            softlock_vote_state["resolved_at"] = time.time()
            return {"ok": True, "softlock_vote": _softlock_vote_payload(user_id)}
        approvals = {int(value) for value in softlock_vote_state.get("approvals", [])}
        approvals.add(user_id)
        softlock_vote_state["approvals"] = sorted(approvals)
        unanimous = eligible.issubset(approvals)
    if unanimous:
        _force_next_day_after_softlock()
        with state_lock:
            softlock_vote_state["status"] = "advanced"
            softlock_vote_state["resolved_at"] = time.time()
    return {"ok": True, "softlock_vote": _softlock_vote_payload(user_id), "game_state": get_game_state(user_id)}


def finish_turn_for_user(user_id):
    _assert_current_turn(user_id)
    state_before = core.get_game_state(DB_PATH)
    previous_day = int(state_before.get("current_day") or 1)
    reward = {"cp": 0, "rt": 0, "already_claimed": True}
    alastor_resolution = None
    with state_lock:
        player_ids_before = [int(player["id"]) for player in lobby_state["players"]]
    with db_connect() as conn:
        work_row = conn.execute(
            "SELECT anomaly_id FROM WORK WHERE user_id = ?",
            (int(user_id),),
        ).fetchone()
    anomaly_id = int(work_row["anomaly_id"]) if work_row and work_row["anomaly_id"] is not None else None
    if anomaly_id is not None:
        _assert_research_not_blocked(user_id, anomaly_id)
        progress = _update_work_completion(user_id, anomaly_id)
        if int(progress.get("IsCompleted") or 0) == 1:
            finish_payload = finish_research(user_id, anomaly_id, advance_on_clay_death=False)
            reward = finish_payload["reward"]
            if int(anomaly_id) == 67:
                _laplace67_arm(int(user_id))
        alastor_resolution = _get_alastor_finish_payload(user_id, anomaly_id)
        if int(anomaly_id) == 68:
            core.set_global_value(DB_PATH, f"A68Boost_{int(user_id)}", 0)
        if int(anomaly_id) == 69:
            _clear_anomaly69_runtime(int(user_id))

    temporary_item_result = _finish_temporary_research_items(int(user_id))

    with state_lock:
        lobby_state["game_assignments"][int(user_id)] = []

    advance_payload = core.advance_turn(DB_PATH, reason="finish_work")
    core_state = advance_payload.get("state", {})
    runtime_game["started"] = core_state.get("status") == "started"
    runtime_game["current_day"] = int(core_state.get("current_day") or 0)
    runtime_game["winner_id"] = core_state.get("winner_user_id")

    if core_state.get("status") == "started" and int(core_state.get("current_day") or 0) > previous_day:
        runtime_game["day_started_at"] = time.time()
        _cleanup_new_day_effects(player_ids_before)
        _apply_new_day_companion_effects(player_ids_before)
        _prepare_alastor_new_day_task()
        with state_lock:
            lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
    elif core_state.get("status") == "finished":
        _finalize_finished_game(player_ids_before)

    return {
        "reward": reward,
        "alastor_resolution": alastor_resolution,
        "advanced": advance_payload.get("ok", False),
        "game_state": get_game_state(int(user_id)),
        "player_dead": bool(temporary_item_result.get("hotdog_killed")),
        "death_reason": "Отложенный урон Хот-дога Лавкрафта" if temporary_item_result.get("hotdog_killed") else "",
    }


def surrender_player(user_id):
    user_id = int(user_id)
    if _is_player_dead(user_id):
        raise ValueError("Игрок уже погиб.")
    state_before = core.get_game_state(DB_PATH)
    was_current_turn = (
        state_before.get("status") == "started"
        and int(state_before.get("current_turn_user_id") or 0) == user_id
    )
    death_reason = "Сдался"
    core.set_player_dead(DB_PATH, user_id, reason=death_reason)
    with state_lock:
        lobby_state["game_assignments"][user_id] = []
    game_state = (
        _advance_after_nonwork_death(user_id, "player_surrendered")
        if was_current_turn else get_game_state(user_id)
    )
    return {
        "ok": True,
        "player_dead": True,
        "death_reason": death_reason,
        "game_state": game_state,
    }


def prepare_finish_turn(user_id):
    _assert_current_turn(user_id)
    reward = {"cp": 0, "rt": 0, "already_claimed": True}
    alastor_resolution = None
    with db_connect() as conn:
        work_row = conn.execute(
            "SELECT anomaly_id FROM WORK WHERE user_id = ?",
            (int(user_id),),
        ).fetchone()
    anomaly_id = int(work_row["anomaly_id"]) if work_row and work_row["anomaly_id"] is not None else None
    room = None
    if anomaly_id is not None:
        _assert_research_not_blocked(user_id, anomaly_id)
        progress = _update_work_completion(user_id, anomaly_id)
        if int(progress.get("IsCompleted") or 0) == 1:
            finish_payload = finish_research(user_id, anomaly_id)
            reward = finish_payload["reward"]
        alastor_resolution = _get_alastor_finish_payload(user_id, anomaly_id)
        room = get_work_room_payload(int(user_id), int(anomaly_id))
    return {
        "reward": reward,
        "upgrade": get_upgrade_payload(int(user_id)),
        "room": room,
        "ilvetal_notice": _get_ilvetal_notice(int(user_id)),
        "alastor_resolution": alastor_resolution,
        "clay_penalty": finish_payload.get("clay_penalty") if anomaly_id is not None and 'finish_payload' in locals() else None,
        "anomaly62_fate": finish_payload.get("anomaly62_fate") if anomaly_id is not None and 'finish_payload' in locals() else None,
        "game_state": finish_payload.get("game_state") if anomaly_id is not None and 'finish_payload' in locals() else None,
    }


def consume_ilvetal_notice(user_id, anomaly_id=None):
    _clear_ilvetal_notice(int(user_id))
    room = None
    if anomaly_id is not None:
        try:
            room = get_work_room_payload(int(user_id), int(anomaly_id))
        except Exception:
            room = None
    return {"ok": True, "room": room}


def consume_cheaptrick_notice(user_id, anomaly_id=None):
    _clear_cheaptrick_notice(int(user_id))
    room = None
    if anomaly_id is not None:
        try:
            room = get_work_room_payload(int(user_id), int(anomaly_id))
        except Exception:
            room = None
    return {"ok": True, "room": room}


def flee_from_work(user_id):
    _assert_current_turn(user_id)
    with state_lock:
        player_ids_before = [int(player["id"]) for player in lobby_state["players"]]
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT p.NAME AS player_name, w.anomaly_id
            FROM PLAYERS p
            LEFT JOIN WORK w ON w.user_id = p.ID
            WHERE p.ID = ?
            """,
            (int(user_id),),
        ).fetchone()
    if not row or row["anomaly_id"] is None:
        raise ValueError("У игрока нет активной аномалии для побега.")

    anomaly_id = int(row["anomaly_id"])
    _x125_mark("flee")
    player_name = str(row["player_name"] or "Сотрудник").strip() or "Сотрудник"
    anomaly = _get_anomaly_row(anomaly_id)
    codename = _anomaly_codename(anomaly)
    if int(anomaly_id) == 137 and int(_work_progress(int(user_id), 137).get("Curse137Pending") or 0) == 1:
        raise ValueError("Нельзя сбежать, пока создание проклятия не завершено.")
    effects = set(core.list_player_effects(DB_PATH, int(user_id)))
    flee_is_death = "FleeIsDeath" in effects
    no_escape = "NoEscape" in effects or int(_safe_global_value("NoEscape", 0) or 0) == 1
    # On the foretold day any escape attempt attracts the Voyager. The Moth
    # (anomaly 12) is the sole exception to this part of the curse.
    voyager_flee_death = _voyager_lethal_day(int(user_id)) and int(anomaly_id) != 12
    if int(anomaly_id) == 111 and "NoResult" in effects:
        _replace_effect_exact(int(user_id), "NoResult", "NoResultPermanent")
        effects.discard("NoResult")
        effects.add("NoResultPermanent")

    message = f'Сотрудник "{player_name}" решил прекратить изучение и сбежал из камеры заключения аномалии {codename}...'
    death_reason = ""
    player_dead = False
    reward = {"cp": 0, "rt": 0, "already_claimed": True}
    alastor_resolution = None
    if int(anomaly_id) == 68:
        core.set_global_value(DB_PATH, f"A68Boost_{int(user_id)}", 0)
    if int(anomaly_id) == 69:
        _clear_anomaly69_runtime(int(user_id))
    alastor_state = _alastor_current_task_state(int(user_id))
    if alastor_state and int(alastor_state.get("task_id") or 0) == 10 and not voyager_flee_death:
        # The flee action has been chosen; hold the turn until the player
        # presses Alastor's final button.
        alastor_resolution = _get_alastor_finish_payload(int(user_id), int(anomaly_id))
        return {
            "ok": True,
            "message": message,
            "player_dead": False,
            "death_reason": "",
            "flee_is_death": flee_is_death,
            "no_escape": no_escape,
            "reward": reward,
            "alastor_resolution": alastor_resolution,
            "awaiting_alastor_final": True,
            "game_state": get_game_state(int(user_id)),
        }
    if int(_safe_global_value("AlastorPrey", 0) or 0) == int(user_id) and int(_safe_global_value("AlastorTask", 0) or 0) == 4:
        core.set_global_value(DB_PATH, "AlastorFledPlayer", int(user_id))
    alastor_resolution = _resolve_alastor_task_result(int(user_id), int(anomaly_id), forced_failure=True)

    if voyager_flee_death:
        death_reason = "Был настигнут Вояжером при попытке сбежать"
        core.set_player_dead(DB_PATH, int(user_id), reason=death_reason)
        _clear_voyager_state(int(user_id))
        player_dead = True
        message += " В роковой день попытка побега привлекла Вояжера. Сотрудник погиб мгновенно."
    elif no_escape:
        death_reason = "Погиб при попытке сбежать из камеры содержания"
        core.set_player_dead(DB_PATH, int(user_id), reason=death_reason)
        player_dead = True
        message += " Попытка побега оказалась невозможной, и аномалия однозначно убила сотрудника."
    elif flee_is_death:
        death_reason = "Погиб при попытке сбежать из камеры содержания"
        core.set_player_dead(DB_PATH, int(user_id), reason=death_reason)
        player_dead = True
        message += " Но аномалия прикончила сотрудника."
    elif int(anomaly_id) == 12:
        reward = _grant_research_reward(int(user_id), int(anomaly_id), require_completed=False)["reward"]
        reward = _apply_post_research_companion_effects(user_id, anomaly_id, reward)

    temporary_item_result = _finish_temporary_research_items(int(user_id))
    if temporary_item_result.get("hotdog_killed"):
        player_dead = True
        death_reason = "Отложенный урон Хот-дога Лавкрафта"
        message += " Отложенный урон Хот-дога Лавкрафта настиг сотрудника после завершения исследования."

    previous_day = int(runtime_game.get("current_day") or 1)
    with state_lock:
        lobby_state["game_assignments"][int(user_id)] = []

    advance_payload = core.advance_turn(DB_PATH, reason="player_fled_dead" if player_dead else "player_fled")
    core_state = advance_payload.get("state", {})
    runtime_game["started"] = core_state.get("status") == "started"
    runtime_game["current_day"] = int(core_state.get("current_day") or 0)
    runtime_game["winner_id"] = core_state.get("winner_user_id")

    if core_state.get("status") == "started" and int(core_state.get("current_day") or 0) > previous_day:
        runtime_game["day_started_at"] = time.time()
        _cleanup_new_day_effects(player_ids_before)
        _apply_new_day_companion_effects(player_ids_before)
        _prepare_alastor_new_day_task()
        with state_lock:
            lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
    elif core_state.get("status") == "finished":
        _finalize_finished_game(player_ids_before)

    payload = {
        "ok": True,
        "message": message,
        "player_dead": player_dead,
        "death_reason": death_reason,
        "flee_is_death": flee_is_death,
        "no_escape": no_escape,
        "voyager_flee_death": voyager_flee_death,
        "reward": reward,
        "alastor_resolution": alastor_resolution,
        "game_state": get_game_state(int(user_id)),
    }
    return payload


def run_work_action(user_id, anomaly_id, work_type, chosen_class=None, chosen_type=None):
    _assert_current_turn(user_id)
    _assert_research_not_blocked(user_id, anomaly_id)
    if _voyager_forbidden_work(int(user_id), work_type):
        death_reason = "Был настигнут Вояжером"
        core.set_player_dead(DB_PATH, int(user_id), reason=death_reason)
        _clear_voyager_state(int(user_id))
        game_state = _advance_after_nonwork_death(int(user_id), "voyager_forbidden_work")
        return {
            "ok": True,
            "room": None,
            "player_dead": True,
            "death_reason": death_reason,
            "message": "Выбранная работа привлекла Вояжера. Сотрудник погиб мгновенно.",
            "game_state": game_state,
        }
    active_psychosis = _current_psychosis_id(user_id)
    if active_psychosis and BLOCKED_WORK_BY_PSYCHOSIS.get(int(active_psychosis)) == str(work_type):
        info = PSYCHOSIS_EFFECTS.get(int(active_psychosis), {"name": "Психоз"})
        raise ValueError(f"Работа заблокирована психозом: {info['name']}.")
    _track_first_work_after_cat(work_type)
    _track_langust_work(int(user_id), work_type)
    anomaly = _get_anomaly_row(anomaly_id)
    with state_lock:
        player_ids_before = [int(player["id"]) for player in lobby_state["players"]]
    progress_before_work = _work_progress(int(user_id), int(anomaly_id))
    work_count_before = int(progress_before_work.get("WorkCount") or 0)
    if int(anomaly_id) == 47 and work_count_before <= 0:
        core.set_global_value(DB_PATH, "first_work_type", str(work_type or ""))
        core.set_global_value(DB_PATH, "first_work_class", int(chosen_class or 0) if chosen_class not in (None, 6) else 0)
        core.set_global_value(DB_PATH, "first_work_anomalytype", int(chosen_type or 0) if chosen_type not in (None, 6) else 0)
    alastor_state = _alastor_current_task_state(int(user_id))
    should_capture_alastor_first_work = bool(
        work_count_before <= 0
        and int(_safe_global_value("check_work", 0) or 0) == 1
        and (
            int(anomaly_id) in (71, 100)
            or (
                alastor_state
                and int(alastor_state.get("task_id") or 0) == 3
            )
        )
    )
    if should_capture_alastor_first_work:
        core.set_global_value(DB_PATH, "first_work_type", str(work_type or ""))
        core.set_global_value(DB_PATH, "first_work_class", int(chosen_class or 0) if chosen_class not in (None, 6) else 0)
        core.set_global_value(DB_PATH, "first_work_anomalytype", int(chosen_type or 0) if chosen_type not in (None, 6) else 0)
        core.set_global_value(DB_PATH, "check_work", 0)
    effective_penalty_class = int((anomaly or {}).get("CLASS_ID") or 0)
    if int(anomaly_id) == 83:
        stored_non_anomaly_class = int(_safe_global_value("first_work_class", 0) or 0)
        effective_penalty_class = stored_non_anomaly_class if stored_non_anomaly_class in (1, 2, 3, 4, 5) else 3
        stored_non_anomaly_type = int(_safe_global_value("first_work_anomalytype", 0) or 0)
        effective_anomaly_type = stored_non_anomaly_type if stored_non_anomaly_type in (1, 2, 3, 4, 5) else 3
        # После первой работы 83-я принимает выбранные класс и тип целиком:
        # они участвуют не только в шансе, но и в пороге результата, уроне,
        # фобиях и взаимодействиях со спутниками.
        anomaly = dict(anomaly or {})
        anomaly["CLASS_ID"] = effective_penalty_class
        anomaly["TYPE"] = effective_anomaly_type
    penalty_should_apply = _should_apply_progress_penalty(
        int(user_id),
        int(anomaly_id),
        effective_penalty_class,
    )
    anomaly_class = int((anomaly or {}).get("CLASS_ID") or 0)
    if anomaly_class in (4, 5) and work_count_before == 0:
        _set_player_penalty(int(user_id), _pisos_curse_floor(int(user_id)))
    if int(anomaly_id) == 6 and str(work_type or "").strip() == "affection" and _player_has_effect(int(user_id), "PisosCurse"):
        _increment_global_int("PisosCurseCount", 1)
    chance_payload = calculate_work_chance(anomaly_id, work_type, user_id, chosen_class, chosen_type)
    chance = int(chance_payload["chance"] or 0)
    raw_successes = sum(1 for _ in range(10) if random.randint(1, 100) <= chance)
    if chance >= 80:
        successes = max(7, min(9, raw_successes))
    elif chance >= 65:
        successes = max(5, min(8, raw_successes))
    elif chance >= 50:
        successes = max(4, min(6, raw_successes))
    elif chance >= 25:
        successes = max(1, min(4, raw_successes))
    else:
        successes = max(0, min(2, raw_successes))
    result_hidden = (
        _player_has_effect(int(user_id), "NoResult")
        or _player_has_effect(int(user_id), "NoResultPermanent")
    )
    siph_penalty = _apply_siph_research_penalty(int(anomaly_id), work_type)
    if int(siph_penalty) > 0:
        successes = max(0, int(successes) - int(siph_penalty))
    core.set_global_value(DB_PATH, "LastWorkResult", int(successes))
    rp_penalty = 2 if int(_safe_global_value("UnderCurse3", 0) or 0) == 1 else 0
    earned_rp = max(0, int(successes) - int(rp_penalty))
    hidden_companion_rp_bonus = _get_hidden_companion_rp_bonus(int(user_id), anomaly)
    failures = 10 - successes
    rolls = ([0] * failures) + ([1] * successes)
    work_label = (WORK_TYPES.get(str(work_type)) or {}).get("label", str(work_type or "Работа"))
    class_label = (RISK_META.get(int(chosen_class or 0)) or {}).get("label", "Не выбрано")
    type_label = ANOMALY_TYPE_LABELS.get(int(chosen_type or 0), "Не выбрано")
    shown_result = "?" if result_hidden else str(int(successes))
    _append_game_action_log(
        "work",
        f"{_player_display_name(user_id)} провёл работу {work_label}, класс {class_label}, тип {type_label}. Результат — {shown_result}/10",
        user_id,
    )
    class_id = anomaly_class or 1
    bad_max = max(0, int(GOOD_RESULT_MIN.get(class_id, 4)) - 1)
    damage_result = {"ok": True, "hp": 0, "sp": 0, "is_dead": False}
    cheaptrick_fatal_action = None
    is_anomaly69 = int(anomaly_id) == 69
    anomaly69_count = int(_safe_global_value("A69_CNT", 0) or 0) + 1 if is_anomaly69 else 0
    if is_anomaly69:
        core.set_global_value(DB_PATH, "A69_CNT", anomaly69_count)
    under_curse2_result = _apply_under_curse2_work_penalty(int(user_id), int(anomaly_id), work_type)
    if bool(under_curse2_result.get("dead")):
        damage_result = {
            "ok": True,
            "hp": 5,
            "sp": 0,
            "is_dead": True,
            "source": "UnderCurse2",
        }
    else:
        dmg_values = {"hp": 0, "sp": 0}
        if successes <= bad_max and anomaly:
            dmg_values = _damage_values(anomaly.get("CLASS_ID"), anomaly.get("DMGTYPE"))
            active_psychosis = _current_psychosis_id(user_id)
            if active_psychosis and PSYCHOSIS_PHOBIA_TYPES.get(int(active_psychosis)) == int(anomaly.get("TYPE") or 0):
                if int(anomaly.get("DMGTYPE") or 0) in (1, 3):
                    dmg_values["hp"] += 10
                if int(anomaly.get("DMGTYPE") or 0) in (2, 3):
                    dmg_values["sp"] += 10
            dmg_values = _apply_anomaly_work_damage_passives(int(anomaly_id), int(user_id), dmg_values)
        if is_anomaly69:
            stacked_hp = int(_safe_global_value("A69_HP", 0) or 0) + int(dmg_values.get("hp") or 0)
            stacked_sp = int(_safe_global_value("A69_SP", 0) or 0) + int(dmg_values.get("sp") or 0)
            core.set_global_value(DB_PATH, "A69_HP", stacked_hp)
            core.set_global_value(DB_PATH, "A69_SP", stacked_sp)
            if anomaly69_count >= 12:
                core.set_global_value(DB_PATH, "A69_HP", 0)
                core.set_global_value(DB_PATH, "A69_SP", 0)
                core.set_global_value(DB_PATH, "A69_CNT", 0)
                damage_result = core.apply_damage(
                    DB_PATH, int(user_id), hp_damage=stacked_hp, sp_damage=stacked_sp,
                    reason=_work_death_reason(int(anomaly_id)),
                )
                damage_result["anomaly69_released"] = True
            else:
                with db_connect() as conn:
                    current = conn.execute("SELECT COALESCE(HP,0) AS HP, COALESCE(SP,0) AS SP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
                damage_result = {
                    "ok": True, "hp": int(current["HP"] or 0) if current else 0,
                    "sp": int(current["SP"] or 0) if current else 0, "is_dead": False,
                    "hp_damage_final": 0, "sp_damage_final": 0,
                    "anomaly69_deferred": True, "anomaly69_count": anomaly69_count,
                }
        elif successes <= bad_max and anomaly:
            damage_result = core.apply_damage(
                DB_PATH, int(user_id), hp_damage=int(dmg_values["hp"] or 0),
                sp_damage=int(dmg_values["sp"] or 0), reason=_work_death_reason(int(anomaly_id)),
                source_anomaly_id=int(anomaly_id),
            )
            if bool(damage_result.get("laplace_rescued")):
                _laplace67_clear()
                damage_result["laplace_message"] = "Игрок разорвал цепи демона. Здоровье полностью восстановлено, проклятие Лапласа исчезло."
    cheaptrick_should_trigger = (
        int(chance_payload.get("companion_slot") or 0) == 4
        and str(work_type or "").strip() == "intuition"
        and int(anomaly_class or 0) in (4, 5)
        and (
            int((damage_result or {}).get("hp_damage_final") or 0) > 0
            or int((damage_result or {}).get("sp_damage_final") or 0) > 0
        )
        and not bool((damage_result or {}).get("is_dead"))
    )
    if cheaptrick_should_trigger:
        cheaptrick_fatal_action = {
            "pending": True,
            "anomaly_id": int(anomaly_id),
            "reason": "Чиптрик убил своего владельца.",
        }
    if penalty_should_apply:
        _increase_player_penalty(int(user_id), effective_penalty_class)
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET WorkCount = COALESCE(WorkCount, 0) + 1 WHERE user_id = ? AND anomaly_id = ?",
            (int(user_id), int(anomaly_id)),
        )
        conn.commit()
    tsd_effects = list(_safe_player_effects(int(user_id)))
    if core.TSD_FLAG in tsd_effects:
        with db_connect_write() as conn:
            current = list(_effects_for_player_conn(conn, int(user_id)))
            accumulated = int(core._effect_token_read(current, core.TSD_ACC_TOK, 0) or 0) + 5
            core._effect_token_write(current, core.TSD_ACC_TOK, accumulated)
            core._save_effects(conn, int(user_id), current)
            conn.commit()
    if int(anomaly_id) == 83 and work_count_before <= 0 and int(_safe_global_value("check_work", 0) or 0) == 1:
        core.set_global_value(DB_PATH, "first_work_type", str(work_type or ""))
        core.set_global_value(DB_PATH, "first_work_class", int(chosen_class or 0) if chosen_class not in (None, 6) else 0)
        core.set_global_value(DB_PATH, "first_work_anomalytype", int(chosen_type or 0) if chosen_type not in (None, 6) else 0)
        core.set_global_value(DB_PATH, "check_work", 0)
    if int(anomaly_id) == 105:
        _anomaly105_work_chances(int(user_id), reroll=True)
    next_debug = calculate_work_chance(anomaly_id, work_type, user_id, chosen_class, chosen_type).get("debug")
    psychosis_result = (damage_result or {}).get("psychosis")
    if int((damage_result or {}).get("sp") or 999999) <= 100 and _current_psychosis_id(user_id) is None:
        psychosis_result = _roll_psychosis(user_id)
    heart_attack = None
    if damage_result.get("heart_attack_triggered"):
        heart_attack = {
            "triggered": True,
            "dead": bool(damage_result.get("heart_attack_dead")),
            "message": "Сердечный приступ оказался смертельным." if bool(damage_result.get("heart_attack_dead")) else "Сердечный приступ! HP -> 1, SP -> 50.",
        }
    elif psychosis_result and psychosis_result.get("heart_attack"):
        heart_attack = psychosis_result.get("heart_attack")
    else:
        heart_attack = _apply_heart_attack_if_needed(user_id)
    with db_connect() as conn:
        death_row = conn.execute("SELECT COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
    game_state = None
    psychosis_damage = (psychosis_result or {}).get("damage") or {}
    player_dead = (
        bool(heart_attack and heart_attack.get("dead"))
        or bool(damage_result.get("is_dead"))
        or bool(psychosis_damage.get("is_dead"))
        or bool(death_row and int(death_row["IsDead"] or 0) == 1)
    )
    if cheaptrick_fatal_action:
        player_dead = False
    if player_dead:
        if is_anomaly69:
            _clear_anomaly69_runtime(int(user_id))
        previous_day = int(runtime_game.get("current_day") or 1)
        with state_lock:
            lobby_state["game_assignments"][int(user_id)] = []
        advance_payload = core.advance_turn(DB_PATH, reason="player_dead_on_work")
        core_state = advance_payload.get("state", {})
        runtime_game["started"] = core_state.get("status") == "started"
        runtime_game["current_day"] = int(core_state.get("current_day") or 0)
        runtime_game["winner_id"] = core_state.get("winner_user_id")
        if core_state.get("status") == "started" and int(core_state.get("current_day") or 0) > previous_day:
            runtime_game["day_started_at"] = time.time()
            _cleanup_new_day_effects(player_ids_before)
            _apply_new_day_companion_effects(player_ids_before)
            _prepare_alastor_new_day_task()
            with state_lock:
                lobby_state["game_assignments"] = assign_anomalies_to_lobby_players()
        elif core_state.get("status") == "finished":
            _finalize_finished_game(player_ids_before)
        game_state = get_game_state(int(user_id))
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE PLAYERS SET RP = COALESCE(RP, 0) + ? WHERE ID = ?",
            (int(earned_rp) + int(hidden_companion_rp_bonus), int(user_id)),
        )
        conn.commit()
    room = get_work_room_payload(user_id, anomaly_id)
    return {
        "chance": chance,
        "debug": chance_payload.get("debug") if debug_mode_enabled() else None,
        "debug_after": next_debug if debug_mode_enabled() else None,
        "successes": successes,
        "failures": failures,
        "rolls": rolls,
        "result_hidden": bool(result_hidden),
        "earned_rp": earned_rp,
        "hidden_companion_rp_bonus": hidden_companion_rp_bonus,
        "rp_penalty": rp_penalty,
        "room": room,
        "work_type": work_type,
        "damage": damage_result,
        "under_curse2": under_curse2_result,
        "psychosis": psychosis_result,
        "heart_attack": heart_attack,
        "player_dead": player_dead,
        "cheaptrick_fatal_action": cheaptrick_fatal_action,
        "game_state": game_state,
    }


def _selection_description(row, conn=None):
    anomaly_id = int(row["ID"] if "ID" in row.keys() else row["AnomalyID"])
    if anomaly_id != 105:
        return row["PDESCRIPTION"] or row["DESCRIPTION"] or "Описание пока отсутствует."
    owns_connection = conn is None
    if owns_connection:
        conn = db_connect()
    try:
        stolen = conn.execute(
            """
            SELECT PDESCRIPTION
            FROM ANOMALY
            WHERE ID <> 105 AND ID NOT IN (4, 13, 33) AND COALESCE(TRIM(PDESCRIPTION), '') <> ''
            ORDER BY RANDOM()
            LIMIT 1
            """
        ).fetchone()
        return str(stolen["PDESCRIPTION"] or "Описание скрыто.").strip() if stolen else "Описание скрыто."
    finally:
        if owns_connection:
            conn.close()


def select_day_anomalies(day):
    def pick_weighted(rows):
        if not rows:
            return None
        weighted_rows = []
        total_weight = 0.0
        for row in rows:
            is_done_count = max(0, int(row["IsDone"] or 0))
            reduction = min(0.30, is_done_count * 0.03)
            weight = max(0.70, 1.0 - reduction)
            total_weight += weight
            weighted_rows.append((row, total_weight))
        roll = random.uniform(0.0, total_weight)
        for row, edge in weighted_rows:
            if roll <= edge:
                return row
        return weighted_rows[-1][0]

    stored_seen = _safe_global_value("SeenAnomaliesThisGame", []) or []
    if isinstance(stored_seen, list):
        runtime_taken_anomalies.update(int(value) for value in stored_seen if str(value).isdigit())
    offered_aleph = {
        int(value)
        for value in (_safe_global_value("OfferedAlephAnomaliesThisGame", []) or [])
        if str(value).isdigit()
    }
    selected_aleph = {
        int(value)
        for value in (_safe_global_value("SelectedAlephAnomaliesThisGame", []) or [])
        if str(value).isdigit()
    }
    chosen = []
    anomaly46_seen_before_today = 46 in runtime_taken_anomalies
    forced_anomaly_id = int(_safe_global_value("DebugForcedNextAnomaly", 0) or 0)
    if forced_anomaly_id in DISABLED_ANOMALY_IDS:
        forced_anomaly_id = 0
        core.set_global_value(DB_PATH, "DebugForcedNextAnomaly", 0)
    forced_row = None
    classes = day_classes(day)
    with db_connect() as conn:
        if forced_anomaly_id > 0:
            forced_row = conn.execute(
                """
                SELECT ID, NAME, PDESCRIPTION, DESCRIPTION, PHOTO, IsDone, CLASS_ID, codename
                FROM ANOMALY WHERE ID = ?
                """,
                (forced_anomaly_id,),
            ).fetchone()
        for class_id in classes:
            requested_class_id = int(class_id)
            available = conn.execute(
                """
                SELECT ID, NAME, PDESCRIPTION, DESCRIPTION, PHOTO, IsDone, CLASS_ID, codename
                FROM ANOMALY
                WHERE CLASS_ID = ? AND ID NOT IN (4, 13, 33)
                ORDER BY RANDOM()
                """,
                (requested_class_id,),
            ).fetchall()
            if requested_class_id == 5:
                # First show ALEPH that have never appeared. When those run
                # out, previously offered but unselected ALEPH may return.
                # Once every ALEPH has actually been selected, use WAW.
                not_selected = [
                    candidate for candidate in available
                    if int(candidate["ID"]) not in selected_aleph
                    and all(int(item["id"]) != int(candidate["ID"]) for item in chosen)
                ]
                never_offered = [
                    candidate for candidate in not_selected
                    if int(candidate["ID"]) not in offered_aleph
                ]
                available = never_offered or not_selected
                if not available:
                    available = conn.execute(
                        """
                        SELECT ID, NAME, PDESCRIPTION, DESCRIPTION, PHOTO, IsDone, CLASS_ID, codename
                        FROM ANOMALY
                        WHERE CLASS_ID = 4 AND ID NOT IN (4, 13, 33)
                        ORDER BY RANDOM()
                        """
                    ).fetchall()
                    available = [
                        candidate for candidate in available
                        if int(candidate["ID"]) not in runtime_taken_anomalies
                        and all(int(item["id"]) != int(candidate["ID"]) for item in chosen)
                    ]
            else:
                available = [
                    candidate for candidate in available
                    if int(candidate["ID"]) not in runtime_taken_anomalies
                    and all(int(item["id"]) != int(candidate["ID"]) for item in chosen)
                ]
            row = pick_weighted(available)
            if row is None:
                # The day table is authoritative; never replace a missing class
                # with an anomaly from another class.
                continue
            anomaly_id = int(row["ID"])
            runtime_taken_anomalies.add(anomaly_id)
            chosen.append(
                {
                    "id": anomaly_id,
                    "name": row["NAME"] if int(row["IsDone"] or 0) == 1 else (row["codename"] or f"SC-UN-U-{anomaly_id}"),
                    "description": _selection_description(row, conn),
                    "class_id": int(row["CLASS_ID"] or 0),
                    "photo": f"/photo/anomaly/{row['PHOTO']}.png" if row["PHOTO"] else None,
                }
            )
    if forced_row is not None and all(int(item["id"]) != forced_anomaly_id for item in chosen):
        if chosen:
            removed = chosen.pop()
            runtime_taken_anomalies.discard(int(removed["id"]))
        runtime_taken_anomalies.add(forced_anomaly_id)
        chosen.append(
            {
                "id": forced_anomaly_id,
                "name": forced_row["NAME"] if int(forced_row["IsDone"] or 0) == 1 else (forced_row["codename"] or f"SC-UN-U-{forced_anomaly_id}"),
                "description": _selection_description(forced_row),
                "class_id": int(forced_row["CLASS_ID"] or 0),
                "photo": f"/photo/anomaly/{forced_row['PHOTO']}.png" if forced_row["PHOTO"] else None,
            }
        )
    if (
        int(day) == 12
        and int(_safe_global_value("A37Guarantee46", 0) or 0) == 1
        and not anomaly46_seen_before_today
        and all(int(item.get("id") or 0) != 46 for item in chosen)
    ):
        with db_connect() as conn:
            idol = conn.execute(
                "SELECT ID, NAME, PDESCRIPTION, DESCRIPTION, PHOTO, IsDone, CLASS_ID, codename FROM ANOMALY WHERE ID = 46"
            ).fetchone()
        if idol is not None:
            replace_index = next(
                (index for index in range(len(chosen) - 1, -1, -1) if int(chosen[index]["id"]) != forced_anomaly_id),
                None,
            )
            if replace_index is not None:
                removed = chosen.pop(replace_index)
                runtime_taken_anomalies.discard(int(removed["id"]))
            runtime_taken_anomalies.add(46)
            chosen.append({
                "id": 46,
                "name": idol["NAME"] if int(idol["IsDone"] or 0) == 1 else (idol["codename"] or "SH-AB-A-46"),
                "description": _selection_description(idol),
                "class_id": int(idol["CLASS_ID"] or 0),
                "photo": f"/photo/anomaly/{idol['PHOTO']}.png" if idol["PHOTO"] else None,
            })
    aleph_target_day = int(_safe_global_value("alephsummoned", 0) or 0)
    if aleph_target_day > 0 and int(day) >= aleph_target_day:
        if int(day) == aleph_target_day and not any(int(item.get("class_id") or 0) == 5 for item in chosen):
            with db_connect() as conn:
                aleph_rows = conn.execute(
                    """
                    SELECT ID, NAME, PDESCRIPTION, DESCRIPTION, PHOTO, IsDone, CLASS_ID, codename
                    FROM ANOMALY
                    WHERE CLASS_ID = 5 AND ID NOT IN (4, 13, 33)
                    ORDER BY RANDOM()
                    """
                ).fetchall()
            current_ids = {int(item["id"]) for item in chosen}
            eligible_aleph = [
                row for row in aleph_rows
                if int(row["ID"]) not in selected_aleph and int(row["ID"]) not in current_ids
            ]
            aleph_row = next(
                (row for row in eligible_aleph if int(row["ID"]) not in offered_aleph),
                eligible_aleph[0] if eligible_aleph else None,
            )
            if aleph_row is not None:
                replace_index = next(
                    (index for index in range(len(chosen) - 1, -1, -1) if int(chosen[index]["id"]) != forced_anomaly_id),
                    None,
                )
                if replace_index is not None:
                    removed = chosen.pop(replace_index)
                    runtime_taken_anomalies.discard(int(removed["id"]))
                if len(chosen) < len(classes):
                    aleph_id = int(aleph_row["ID"])
                    runtime_taken_anomalies.add(aleph_id)
                    chosen.append(
                        {
                            "id": aleph_id,
                            "name": aleph_row["NAME"] if int(aleph_row["IsDone"] or 0) == 1 else (aleph_row["codename"] or f"SC-UN-U-{aleph_id}"),
                            "description": _selection_description(aleph_row),
                            "class_id": 5,
                            "photo": f"/photo/anomaly/{aleph_row['PHOTO']}.png" if aleph_row["PHOTO"] else None,
                        }
                    )
        core.set_global_value(DB_PATH, "alephsummoned", 0)
    if forced_anomaly_id > 0:
        core.set_global_value(DB_PATH, "DebugForcedNextAnomaly", 0)
    # A daily pool must always contain five cards. Late-game class schedules
    # can exhaust their unique rows, especially after forced anomalies. Fill
    # only the missing positions with WAW: unseen WAW first, and recycle one
    # only when no unseen WAW remains.
    if len(chosen) < 5:
        with db_connect() as conn:
            waw_rows = conn.execute(
                """
                SELECT ID, NAME, PDESCRIPTION, DESCRIPTION, PHOTO, IsDone, CLASS_ID, codename
                FROM ANOMALY
                WHERE CLASS_ID = 4 AND ID NOT IN (4, 13, 33)
                ORDER BY RANDOM()
                """
            ).fetchall()
            while len(chosen) < 5:
                current_ids = {int(item["id"]) for item in chosen}
                candidates = [
                    row for row in waw_rows
                    if int(row["ID"]) not in current_ids
                    and int(row["ID"]) not in runtime_taken_anomalies
                ]
                if not candidates:
                    candidates = [row for row in waw_rows if int(row["ID"]) not in current_ids]
                row = pick_weighted(candidates)
                if row is None:
                    break
                anomaly_id = int(row["ID"])
                runtime_taken_anomalies.add(anomaly_id)
                chosen.append({
                    "id": anomaly_id,
                    "name": row["NAME"] if int(row["IsDone"] or 0) == 1 else (row["codename"] or f"SC-UN-U-{anomaly_id}"),
                    "description": _selection_description(row, conn),
                    "class_id": int(row["CLASS_ID"] or 0),
                    "photo": f"/photo/anomaly/{row['PHOTO']}.png" if row["PHOTO"] else None,
                })
    # Count only cards that survived every forced replacement and were
    # actually shown in the final pool for this day.
    offered_aleph.update(
        int(item["id"]) for item in chosen if int(item.get("class_id") or 0) == 5
    )
    core.set_global_value(DB_PATH, "OfferedAlephAnomaliesThisGame", sorted(offered_aleph))
    core.set_global_value(DB_PATH, "SeenAnomaliesThisGame", sorted(runtime_taken_anomalies))
    return chosen


def _assign_unique_agent_characters_locked():
    """Assign unique agents. Every player has an exact 20% marginal chance for char6."""
    players = list(lobby_state.get("players") or [])
    if not players:
        return
    shuffled_players = players[:]
    random.shuffle(shuffled_players)
    secret_probability = min(1.0, 0.20 * len(shuffled_players))
    secret_player_id = None
    if random.random() < secret_probability:
        secret_player_id = int(random.choice(shuffled_players)["id"])
    regular_characters = [1, 2, 3, 4, 5]
    random.shuffle(regular_characters)
    regular_index = 0
    for player in shuffled_players:
        if secret_player_id is not None and int(player["id"]) == secret_player_id:
            player["agent_character"] = 6
        else:
            player["agent_character"] = regular_characters[regular_index]
            regular_index += 1


def maybe_progress_countdown():
    with state_lock:
        if lobby_state["status"] != "countdown" or lobby_state["countdown_started_at"] is None:
            return
        if time.time() - lobby_state["countdown_started_at"] < 5:
            return
        player_ids = [player["id"] for player in lobby_state["players"]]
        _assign_unique_agent_characters_locked()
        _reset_work_state_for_new_game(player_ids)
        _laplace67_clear()
        lobby_state["status"] = "started"
        lobby_state["game_started_at"] = time.time()
        runtime_game["started"] = True
        runtime_game["current_day"] = 1
        runtime_game["day_started_at"] = time.time()
        runtime_game["winner_id"] = None
        runtime_game["final_player_ids"] = []
        runtime_game["final_results"] = {"exists": False, "winner_id": None, "winner_name": "", "standings": []}
        moon_eye_game_sessions.clear()
        emoji_glasses_game_sessions.clear()
        sea_monster_game_sessions.clear()
        tenna_game_sessions.clear()
        po3_sessions.clear()
        camera_view_states.clear()
        game_action_log.clear()
        softlock_vote_state.clear()
        core.start_game(DB_PATH, player_ids, total_days=TOTAL_GAME_DAYS)
        runtime_taken_anomalies.clear()
        core.set_global_value(DB_PATH, "SeenAnomaliesThisGame", [])
        core.set_global_value(DB_PATH, "OfferedAlephAnomaliesThisGame", [])
        core.set_global_value(DB_PATH, "SelectedAlephAnomaliesThisGame", [])
        assignments = assign_anomalies_to_lobby_players()
        lobby_state["game_assignments"] = assignments
        add_system_message("РРіСЂР° РЅР°С‡Р°Р»Р°СЃСЊ. РљРѕРЅС‚РµР№РЅРµСЂС‹ РґРѕСЃС‚СѓРїРЅС‹ РґР»СЏ С‚РµРєСѓС‰РµРіРѕ С…РѕРґР°.")


def serialize_lobby():
    maybe_progress_countdown()
    with state_lock:
        players = [normalize_lobby_player(player) for player in lobby_state["players"]]
        return {
            "exists": bool(lobby_state.get("created") or len(players) > 0),
            "capacity": MAX_LOBBY_PLAYERS,
            "status": lobby_state["status"],
            "countdown_started_at": lobby_state["countdown_started_at"],
            "game_started_at": lobby_state["game_started_at"],
            "players": players,
            "messages": list(lobby_state["messages"][-25:]),
        }


def create_empty_lobby():
    with state_lock:
        lobby_state["created"] = True
        lobby_state["status"] = "idle"
        lobby_state["countdown_started_at"] = None
        lobby_state["game_started_at"] = None
        lobby_state["game_assignments"] = {}
    reset_runtime_game()


def assign_anomalies_to_lobby_players():
    picked = select_day_anomalies(runtime_game["current_day"] or 1)
    with state_lock:
        player_ids = [player["id"] for player in lobby_state["players"]]
    assignments = {player_id: [dict(item) for item in picked] for player_id in player_ids}
    _laplace67_capture(assignments)
    return assignments


def _personalize_assignment_names(player_id, assignments):
    cards = [dict(item) for item in (assignments or [])]
    anomaly_ids = [int(item.get("id") or 0) for item in cards if int(item.get("id") or 0) > 0]
    if not anomaly_ids:
        return cards
    studied_ids = {
        int(value) for value in core.get_player_studied_anomalies(DB_PATH, int(player_id))
    }
    placeholders = ",".join("?" for _ in anomaly_ids)
    with db_connect() as conn:
        rows = conn.execute(
            f"SELECT ID, COALESCE(NAME, '') AS NAME, COALESCE(codename, '') AS codename FROM ANOMALY WHERE ID IN ({placeholders})",
            tuple(anomaly_ids),
        ).fetchall()
    names = {int(row["ID"]): row for row in rows}
    for card in cards:
        anomaly_id = int(card.get("id") or 0)
        row = names.get(anomaly_id)
        if not row:
            continue
        card["name"] = (
            str(row["NAME"] or anomaly_id)
            if anomaly_id in studied_ids
            else str(row["codename"] or f"SC-UN-U-{anomaly_id}")
        )
    return cards


def _claim_day_anomaly(user_id, anomaly_id):
    """Reserve a selected anomaly and remove it from every other player's pool."""
    user_id = int(user_id)
    anomaly_id = int(anomaly_id)
    with state_lock:
        own_pool = lobby_state.get("game_assignments", {}).get(user_id, [])
        if not any(int(item.get("id") or 0) == anomaly_id for item in own_pool):
            raise ValueError("Эта аномалия уже выбрана другим игроком или недоступна.")
        for player_id, pool in list(lobby_state.get("game_assignments", {}).items()):
            if int(player_id) == user_id:
                continue
            lobby_state["game_assignments"][player_id] = [
                item for item in pool if int(item.get("id") or 0) != anomaly_id
            ]

    # Offered ALEPH may return on later days, but a selected ALEPH is retired
    # for the rest of this game.
    with db_connect() as conn:
        selected_row = conn.execute(
            "SELECT COALESCE(CLASS_ID, 0) AS CLASS_ID FROM ANOMALY WHERE ID = ?",
            (anomaly_id,),
        ).fetchone()
    if selected_row and int(selected_row["CLASS_ID"] or 0) == 5:
        selected = {
            int(value)
            for value in (_safe_global_value("SelectedAlephAnomaliesThisGame", []) or [])
            if str(value).isdigit()
        }
        selected.add(anomaly_id)
        core.set_global_value(DB_PATH, "SelectedAlephAnomaliesThisGame", sorted(selected))

    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT d.AnomalyID, d.IsTaken, a.IsDone, a.PDESCRIPTION, a.DESCRIPTION, a.NAME AS RealName, a.codename
            FROM DAILY_ANOMALIES d
            LEFT JOIN ANOMALY a ON a.ID = d.AnomalyID
            WHERE d.IsTaken = 0 AND d.AnomalyID NOT IN (4, 13, 33)
            ORDER BY d.AnomalyID
            """
        ).fetchall()
        rows = [row for row in rows if row["AnomalyID"] not in runtime_taken_anomalies]
        if len(rows) < 5:
            rows = conn.execute(
                """
                SELECT ID AS AnomalyID, NAME AS RealName, PDESCRIPTION, DESCRIPTION, IsDone, codename
                FROM ANOMALY
                WHERE ID NOT IN (4, 13, 33)
                ORDER BY RANDOM()
                LIMIT 5
                """
            ).fetchall()

        picked = []
        for row in rows[:5]:
            anomaly_id = row["AnomalyID"]
            picked.append(
                {
                    "id": anomaly_id,
                    "name": row["RealName"] if row["IsDone"] == 1 else (row["codename"] or f"SC-UN-U-{anomaly_id}"),
                    "real_name": row["RealName"],
                    "description": row["PDESCRIPTION"] or row["DESCRIPTION"] or "РћРїРёСЃР°РЅРёРµ РїРѕРєР° РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚.",
                }
            )
            runtime_taken_anomalies.add(anomaly_id)

    with state_lock:
        player_ids = [player["id"] for player in lobby_state["players"]]

    return {player_id: picked[:] for player_id in player_ids}


def create_or_join_lobby(player):
    with state_lock:
        lobby_state["created"] = True
        existing = next((p for p in lobby_state["players"] if p["id"] == player["id"]), None)
        if existing:
            existing["name"] = player["name"]
            existing["avatar_url"] = player.get("avatar_url")
            existing["art_id"] = player.get("art_id") or existing.get("art_id") or 0
            existing["ready"] = False
            return
        if len(lobby_state["players"]) >= MAX_LOBBY_PLAYERS:
            raise ValueError("Р›РѕР±Р±Рё СѓР¶Рµ Р·Р°РїРѕР»РЅРµРЅРѕ.")
        lobby_state["players"].append(
            {"id": player["id"], "name": player["name"], "avatar_url": player.get("avatar_url"), "art_id": player.get("art_id") or 0, "ready": False, "agent_character": 0}
        )
        lobby_state["status"] = "idle"
        lobby_state["countdown_started_at"] = None
        lobby_state["game_started_at"] = None
        lobby_state["game_assignments"] = {}
        add_system_message(f"{player['name']} РїРѕРґРєР»СЋС‡Р°РµС‚СЃСЏ Рє Р»РѕР±Р±Рё.")


def _replace_guest_lobby_identity(guest_profile, discord_player):
    """Replace the current browser's stale guest slot after Discord login."""
    if not guest_profile or not bool(guest_profile.get("is_guest")):
        return False
    guest_id = int(guest_profile.get("id") or 0)
    discord_id = int(discord_player.get("id") or 0)
    if guest_id <= 0 or discord_id <= 0 or guest_id == discord_id:
        return False
    transferred_art = 0
    with state_lock:
        if lobby_state.get("status") == "started":
            return False
        guest_index = next(
            (index for index, entry in enumerate(lobby_state.get("players", [])) if int(entry.get("id") or 0) == guest_id),
            None,
        )
        if guest_index is None:
            return False
        existing_index = next(
            (index for index, entry in enumerate(lobby_state.get("players", [])) if int(entry.get("id") or 0) == discord_id),
            None,
        )
        guest_entry = lobby_state["players"][guest_index]
        transferred_art = int(discord_player.get("art_id") or guest_entry.get("art_id") or 0)
        if existing_index is not None:
            lobby_state["players"].pop(guest_index)
        else:
            guest_entry.update({
                "id": discord_id,
                "name": discord_player.get("name") or f"Discord-{discord_id}",
                "avatar_url": discord_player.get("avatar_url"),
                "art_id": transferred_art,
                "ready": False,
            })
        old_assignment = lobby_state.get("game_assignments", {}).pop(guest_id, None)
        if old_assignment is not None and existing_index is None:
            lobby_state["game_assignments"][discord_id] = old_assignment
        lobby_state["status"] = "idle"
        lobby_state["countdown_started_at"] = None
        lobby_state["game_started_at"] = None
    runtime_players.pop(guest_id, None)
    if transferred_art > 0:
        update_player_art(discord_id, transferred_art)
    return True


def leave_lobby_slot(player_id):
    with state_lock:
        index = next((i for i, player in enumerate(lobby_state["players"]) if player["id"] == player_id), None)
        if index is None:
            raise ValueError("Player is not in a slot.")
        lobby_state["players"].pop(index)
        lobby_state["status"] = "idle"
        lobby_state["countdown_started_at"] = None
        lobby_state["game_started_at"] = None
        lobby_state["game_assignments"] = {}


def cycle_player_art(player_id, direction):
    arts = get_arts()
    if not arts:
        raise ValueError("В таблице ARTS нет доступных артефактов.")
    with state_lock:
        player = next((p for p in lobby_state["players"] if p["id"] == player_id), None)
        if player is None:
            raise ValueError("РРіСЂРѕРє РЅРµ РЅР°Р№РґРµРЅ РІ Р»РѕР±Р±Рё.")
        art_ids = [art["ID"] for art in arts]
        current_art = player.get("art_id") or art_ids[0]
        if current_art not in art_ids:
            current_art = art_ids[0]
        current_index = art_ids.index(current_art)
        offset = 1 if direction == "right" else -1
        new_art_id = art_ids[(current_index + offset) % len(art_ids)]
        player["art_id"] = new_art_id
        if player.get("ready"):
            player["ready"] = False
            add_system_message(f"{player['name']} СЃРјРµРЅРёР» Р°СЂС‚РµС„Р°РєС‚ Рё СЃРЅСЏР» РіРѕС‚РѕРІРЅРѕСЃС‚СЊ.")
        lobby_state["status"] = "idle"
        lobby_state["countdown_started_at"] = None
        lobby_state["game_started_at"] = None
        lobby_state["game_assignments"] = {}
    update_player_art(player_id, new_art_id)


def set_player_ready(player_id, ready):
    with state_lock:
        player = next((p for p in lobby_state["players"] if p["id"] == player_id), None)
        if player is None:
            raise ValueError("РРіСЂРѕРє РЅРµ РЅР°Р№РґРµРЅ РІ Р»РѕР±Р±Рё.")
        player["ready"] = bool(ready)
        add_system_message(f"{player['name']} {'РіРѕС‚РѕРІ' if ready else 'РЅРµ РіРѕС‚РѕРІ'}.")
        everyone_ready = len(lobby_state["players"]) > 0 and all(entry.get("ready") for entry in lobby_state["players"])
        if everyone_ready:
            lobby_state["status"] = "countdown"
            lobby_state["countdown_started_at"] = time.time()
            add_system_message("РРіСЂР° РЅР°С‡РЅРµС‚СЃСЏ С‡РµСЂРµР· 5 СЃРµРєСѓРЅРґ.")
        else:
            lobby_state["status"] = "idle"
            lobby_state["countdown_started_at"] = None
            lobby_state["game_started_at"] = None
            lobby_state["game_assignments"] = {}


def add_chat_message(player_id, text):
    clean = (text or "").strip()
    if not clean:
        raise ValueError("РЎРѕРѕР±С‰РµРЅРёРµ РїСѓСЃС‚РѕРµ.")
    with state_lock:
        player = next((p for p in lobby_state["players"] if p["id"] == player_id), None)
        if player is None:
            raise ValueError("РРіСЂРѕРє РЅРµ РЅР°Р№РґРµРЅ РІ Р»РѕР±Р±Рё.")
        lobby_state["messages"].append({"author": player["name"], "text": clean[:300], "timestamp": int(time.time())})


def _force_crimson_infection(player_id):
    player_id = int(player_id)
    effects = _safe_player_effects(player_id)
    if "CrimsonVirus" in effects:
        return {"infected": True, "newly_infected": False}
    with db_connect_write() as conn:
        row = conn.execute(
            f"SELECT {', '.join(core.EFFECT_COLUMNS)} FROM PLAYERS WHERE ID = ?",
            (player_id,),
        ).fetchone()
        if not row:
            raise ValueError("Игрок не найден.")
        values = [row[column] for column in core.EFFECT_COLUMNS]
        try:
            index = next(i for i, value in enumerate(values) if value in (None, "", "0"))
        except StopIteration:
            index = len(core.EFFECT_COLUMNS) - 1
        conn.execute(
            f"UPDATE PLAYERS SET {core.EFFECT_COLUMNS[index]} = 'CrimsonVirus' WHERE ID = ?",
            (player_id,),
        )
        conn.commit()
    current_day = int(_current_day_number() or 1)
    core.set_global_value(DB_PATH, f"CrimsonInfectedDay_{player_id}", current_day)
    return {"infected": True, "newly_infected": True, "slot": index + 1}


def _crimson_bite_flag(day, player_id):
    return f"CrimsonBite_{int(day)}_{int(player_id)}"


def _build_crimson_bite_payload(player_id, core_state=None, alive_status=None, lobby_players=None):
    player_id = int(player_id)
    core_state = core_state or core.get_game_state(DB_PATH)
    current_day = int(core_state.get("current_day") or _current_day_number() or 0)
    if core_state.get("status") != "started" or int(core_state.get("current_turn_user_id") or 0) != player_id:
        return {"pending": False}
    if not _player_has_effect(player_id, "CrimsonVirus"):
        return {"pending": False}
    infected_day = int(_safe_global_value(f"CrimsonInfectedDay_{player_id}", 0) or 0)
    if infected_day > 0 and current_day <= infected_day:
        return {"pending": False, "activates_next_day": True, "infected_day": infected_day}
    if int(_safe_global_value(_crimson_bite_flag(current_day, player_id), 0) or 0) == 1:
        return {"pending": False}
    turn_order = [int(pid) for pid in core_state.get("turn_order", [])]
    if alive_status is None:
        alive_status = {}
        if turn_order:
            placeholders = ",".join("?" for _ in turn_order)
            with db_connect() as conn:
                rows = conn.execute(
                    f"SELECT ID, COALESCE(IsDead, 0) AS IsDead FROM PLAYERS WHERE ID IN ({placeholders})",
                    tuple(turn_order),
                ).fetchall()
            alive_status = {int(row["ID"]): int(row["IsDead"] or 0) == 0 for row in rows}
    lobby_players = lobby_players or []
    targets = []
    for target_id in turn_order:
        if target_id == player_id or not alive_status.get(target_id, False):
            continue
        lobby_player = next((item for item in lobby_players if int(item.get("id") or 0) == target_id), None)
        name = str((lobby_player or {}).get("name") or "").strip()
        if not name:
            with db_connect() as conn:
                row = conn.execute("SELECT COALESCE(NAME, '') AS NAME FROM PLAYERS WHERE ID = ?", (target_id,)).fetchone()
            name = str(row["NAME"] or f"Игрок {target_id}") if row else f"Игрок {target_id}"
        targets.append({"id": target_id, "label": name, "infected": _player_has_effect(target_id, "CrimsonVirus")})
    return {"pending": True, "day": current_day, "targets": targets}


TENNA_CATEGORIES = ("ZAYIN", "TETH", "HE", "WAW", "ALEPH")
TENNA_POINTS = (100, 300, 500, 700)
TENNA_CORRECT_LINES = (
    "Абсолютно верно!", "И это правильный ответ!", "Точно в цель!", "Да! Всё именно так!",
    "Есть! Ответ засчитан!", "Блестяще! Это верно!", "Ни секунды сомнений — правильно!",
    "Отличный ответ! Получаете балл!", "И-и-и… да! Это правильный ответ!",
    "Совершенно верно! Двигаемся дальше!",
)
TENNA_WRONG_LINES = (
    "Увы, это неверный ответ.", "Нет, на этот раз не угадали!", "Близко, но правильный ответ другой.",
    "Не совсем! Попытка не засчитана.", "А вот и нет! Правильный ответ был другим.",
    "К сожалению, мимо!", "Нет! Здесь вас ждал небольшой подвох.", "Ответ принят, но он неверный.",
    "Увы! В этот раз без балла.", "Не угадали! Ничего страшного — двигаемся дальше.",
)


def _tenna_alive_players():
    with state_lock:
        players = [dict(player) for player in lobby_state.get("players", [])]
    result = []
    for player in players:
        pid = int(player.get("id") or 0)
        if pid > 0 and not _is_player_dead(pid):
            result.append({"id": pid, "name": player.get("name") or f"Игрок {pid}", "avatar_url": player.get("avatar_url")})
    return result


def _tenna_session_for_user(user_id):
    uid = int(user_id)
    for session in tenna_game_sessions.values():
        # player_ids contains contestants; viewer_ids also contains players
        # who were already dead when the show began. They still receive the
        # public show state, but can never take a turn or answer for others.
        viewers = session.get("viewer_ids", session.get("player_ids", []))
        if session.get("phase") != "closed" and uid in viewers:
            return session
    return None


def _tenna_public(session, viewer_id):
    if not session:
        return None
    with state_lock:
        _tenna_process_timeout(session)
    current_id = session["player_ids"][session["turn_index"] % len(session["player_ids"])] if session.get("player_ids") else 0
    question = dict(session.get("question") or {})
    question.pop("correct", None)
    question.pop("check", None)
    question.pop("target", None)
    answered = int(viewer_id) in session.get("group_answers", {})
    return {
        "active": session.get("phase") not in {"closed"}, "session_id": session["id"],
        "owner_id": session["owner_id"], "phase": session["phase"], "players": session["players"],
        "scores": {str(k): int(v) for k, v in session["scores"].items()},
        "current_player_id": current_id, "is_current_player": current_id == int(viewer_id),
        "used": [f"{cat}:{pts}" for cat, pts in session["used"]], "question": question or None,
        "reaction": session.get("reaction"), "turns_done": session["turns_done"],
        "total_turns": session["total_turns"], "viewer_answered": answered,
        "deadline_at": float(session.get("deadline_at") or 0),
        "final_result": session.get("final_result"),
    }


def start_tenna_game(user_id, anomaly_id=104):
    existing = _tenna_session_for_user(user_id)
    if existing:
        return _tenna_public(existing, user_id)
    players = _tenna_alive_players()
    uid = int(user_id)
    if uid not in [p["id"] for p in players]:
        with db_connect() as conn:
            row = conn.execute("SELECT COALESCE(NAME, '') NAME, COALESCE(AVATAR_URL, '') AVATAR_URL FROM PLAYERS WHERE ID = ?", (uid,)).fetchone()
        players.insert(0, {"id": uid, "name": (row["NAME"] if row else "") or f"Игрок {uid}", "avatar_url": row["AVATAR_URL"] if row else ""})
    ids = [p["id"] for p in players]
    with state_lock:
        viewer_ids = [
            int(player.get("id") or 0)
            for player in lobby_state.get("players", [])
            if int(player.get("id") or 0) > 0
        ]
    if not viewer_ids:
        try:
            viewer_ids = [int(pid) for pid in core.get_game_state(DB_PATH).get("turn_order", [])]
        except Exception:
            viewer_ids = []
    if uid not in viewer_ids:
        viewer_ids.append(uid)
    owner_index = ids.index(uid)
    session = {
        "id": secrets.token_hex(8), "owner_id": uid, "anomaly_id": int(anomaly_id), "players": players,
        "player_ids": ids, "viewer_ids": viewer_ids,
        "scores": {pid: 0 for pid in ids}, "turn_index": owner_index,
        "turns_done": 0, "total_turns": len(TENNA_CATEGORIES) * len(TENNA_POINTS), "used": [], "phase": "intro",
        "question": None, "reaction": None, "group_answers": {},
        # If the owner closes the page during the intro, the show starts
        # automatically instead of blocking every participant.
        "deadline_at": time.time() + 60, "final_result": None,
    }
    tenna_game_sessions[uid] = session
    try:
        train_owner = int(_safe_global_value("TrainDeadlineUserId", 0) or 0)
        if train_owner > 0:
            set_train_timer_paused(train_owner, True)
    except Exception:
        pass
    return _tenna_public(session, uid)


def _tenna_make_question(category, points):
    key = (str(category).upper(), int(points))
    fixed = {
        ("ZAYIN", 100): ("Абстрактов среди ZAYIN-класса нет?", ["Да", "Нет"], "Да"),
        ("ZAYIN", 500): ("На содержании корпорации больше всего аномалий класса ZAYIN?", ["Да", "Нет"], "Нет"),
        ("ZAYIN", 700): ("Сколько аномальных предметов класса ZAYIN на содержании?", ["3", "5", "6", "7", "8"], "5"),
        ("TETH", 300): ("Есть ли среди TETH аномалии, которые улучшают характеристики?", ["Да", "Нет"], "Да"),
        ("TETH", 500): ("Какой эффект у сущности на фото?", ["не компаньон", "Поглощение проклятий", "Блок урона", "Упрощает исследование", "Нет правильного ответа"], "Упрощает исследование"),
        ("TETH", 700): ("Bonjour à tous! Je suis un développeur débutинт — это описание аномалии TETH?", ["Да", "Нет"], "Нет"),
        ("HE", 100): ("Тенна — лучший ведущий во Вселенной?", ["да", "да!", "конечно да", "несомненно да"], "*"),
        ("HE", 300): ("У какой аномалии тип урона — белый?", ["ZenChost", "Панацея", "Неопределившаяся аномалия", "Статуя Будды"], "Статуя Будды"),
        ("HE", 500): ("Ты встречал аномалию Х-125?", ["Да", "Нет"], "*"),
        ("HE", 700): ("У какой из аномалий регистрационный номер ближе к 1?", ["Сиф великий волк", "Человек сторук", "Колония плотоядных эндопаразитов", "Ящер кровавой топи"], "Ящер кровавой топи"),
        ("WAW", 300): ("Есть ли гуманоиды среди WAW?", ["Да", "Нет"], "Да"),
        ("ALEPH", 100): ("Какой цвет класса ALEPH?", ["зелёный", "синий", "жёлтый", "фиолетовый", "красный"], "красный"),
    }
    if key == ("ZAYIN", 300):
        with db_connect() as conn:
            rows = conn.execute("SELECT ID, NAME, PHOTO FROM ANOMALY WHERE CLASS_ID = 1 AND ID NOT IN (4, 13, 33) AND COALESCE(NAME, '') <> ''").fetchall()
        chosen = random.choice(rows)
        others = random.sample([r for r in rows if int(r["ID"]) != int(chosen["ID"])], 2)
        options = [str(chosen["NAME"])] + [str(r["NAME"]) for r in others]
        random.shuffle(options)
        photo = str(chosen["PHOTO"] or chosen["ID"])
        if photo.lower().endswith(".png"):
            photo = photo[:-4]
        return {"category": key[0], "points": key[1], "prompt": "Кто на фото?", "options": options, "correct": str(chosen["NAME"]), "image": f"/photo/anomaly/{photo}.png", "kind": "choice"}
    if key == ("WAW", 100):
        return {"category": key[0], "points": key[1], "prompt": "Имя текущего смотрителя Lobotomy Corporation?", "correct": "angela", "kind": "text"}
    if key == ("WAW", 500):
        return {"category": key[0], "points": key[1], "prompt": "Напиши имя любого объекта WAW (класс=4).", "correct": "waw", "kind": "text"}
    if key == ("WAW", 700):
        return {"category": key[0], "points": key[1], "prompt": "Сколько WAW способны мгновенно убить? Каждый живой игрок вводит число; побеждает ближайший.", "target": 6, "kind": "group_number"}
    if key == ("TETH", 100):
        return {"category": key[0], "points": key[1], "prompt": "Подарочный сектор! Вы получаете Хот-Дог Лавкрафта.", "correct": "reward", "kind": "instant"}
    if key == ("ALEPH", 300):
        return {"category": key[0], "points": key[1], "prompt": "Аномалия в мешке", "correct": "empty", "kind": "instant"}
    if key == ("ALEPH", 500):
        return {"category": key[0], "points": key[1], "prompt": "Подарочный сектор! Вы получаете компаньона ЧипТрик.", "correct": "companion", "kind": "instant"}
    if key == ("ALEPH", 700):
        return {"category": key[0], "points": key[1], "prompt": "Смута охватывает участника: Паника и Ярость.", "correct": "curse", "kind": "instant"}
    prompt, options, correct = fixed[key]
    image = "/photo/anomaly/016_kyurem.png" if key == ("TETH", 500) else None
    return {"category": key[0], "points": key[1], "prompt": prompt, "options": options, "correct": correct, "image": image, "kind": "choice"}


def tenna_intro_complete(user_id):
    session = _tenna_session_for_user(user_id)
    if not session or int(user_id) != session["owner_id"]:
        raise ValueError("Эта игровая сессия недоступна.")
    session["phase"] = "board"
    session["deadline_at"] = time.time() + 30
    return _tenna_public(session, user_id)


def tenna_pick(user_id, category, points):
    session = _tenna_session_for_user(user_id)
    if not session or session["phase"] != "board":
        raise ValueError("Сейчас нельзя выбирать вопрос.")
    current = session["player_ids"][session["turn_index"] % len(session["player_ids"])]
    if current != int(user_id):
        raise ValueError("Сейчас ход другого участника.")
    tile = (str(category).upper(), int(points))
    if tile[0] not in TENNA_CATEGORIES or tile[1] not in TENNA_POINTS or tile in session["used"]:
        raise ValueError("Этот вопрос недоступен.")
    session["phase"] = "preparing_question"
    session["used"].append(tile)
    session["question"] = _tenna_make_question(*tile)
    session["reaction"] = None
    session["group_answers"] = {}
    session["phase"] = "group_question" if session["question"]["kind"] == "group_number" else "question"
    session["deadline_at"] = time.time() + 15
    return _tenna_public(session, user_id)


def _tenna_advance(session):
    session["turns_done"] += 1
    session["question"] = None
    session["group_answers"] = {}
    if len(session["used"]) >= len(TENNA_CATEGORIES) * len(TENNA_POINTS):
        session["phase"] = "finished"
        session["deadline_at"] = 0
        with db_connect_write() as conn:
            for pid, score in session["scores"].items():
                conn.execute("UPDATE PLAYERS SET CP = MAX(0, COALESCE(CP, 0) + ?) WHERE ID = ?", (int(score), int(pid)))
            conn.execute(
                """UPDATE WORK SET photounlocked = 1, descriptionunlocked = 1,
                          hintunlocked = hintcount, IsCompleted = 1
                     WHERE user_id = ? AND anomaly_id = ?""",
                (int(session["owner_id"]), int(session["anomaly_id"])),
            )
            conn.commit()
        alive = [pid for pid in session["player_ids"] if not _is_player_dead(pid)]
        ranking = sorted(session["players"], key=lambda player: session["scores"].get(int(player["id"]), 0), reverse=True)
        winner = ranking[0] if ranking else None
        session["final_result"] = {
            "player_count": len(session["player_ids"]),
            "winner_id": int(winner["id"]) if winner else None,
            "winner_name": str(winner["name"]) if winner else "участник",
            "eliminated_id": None,
            "eliminated_name": "",
        }
        if len(session["player_ids"]) > 1 and len(alive) > 1:
            low = min(session["scores"].get(pid, 0) for pid in alive)
            losers = [pid for pid in alive if session["scores"].get(pid, 0) == low]
            if len(losers) == 1:
                core.set_player_dead(DB_PATH, losers[0], reason="Остался в шоу Тенны навсегда")
                session["eliminated_id"] = losers[0]
                eliminated = next((player for player in session["players"] if int(player["id"]) == int(losers[0])), None)
                session["final_result"]["eliminated_id"] = int(losers[0])
                session["final_result"]["eliminated_name"] = str((eliminated or {}).get("name") or f"Игрок {losers[0]}")
                try:
                    main_state = core.get_game_state(DB_PATH)
                    if int(main_state.get("current_turn_user_id") or 0) == int(losers[0]):
                        _advance_after_nonwork_death(int(losers[0]), "tenna_show_elimination")
                except Exception as exc:
                    print(f"[TENNA] turn advance after elimination failed: {exc}")
        return
    for _ in session["player_ids"]:
        session["turn_index"] = (session["turn_index"] + 1) % len(session["player_ids"])
        if not _is_player_dead(session["player_ids"][session["turn_index"]]):
            break
    session["phase"] = "board"
    session["deadline_at"] = time.time() + 30


def _tenna_process_timeout(session):
    deadline = float(session.get("deadline_at") or 0)
    if deadline <= 0 or time.time() < deadline:
        return
    if session.get("phase") == "intro":
        session["phase"] = "board"
        session["deadline_at"] = time.time() + 30
        return
    if session.get("phase") == "board":
        available = [(cat, pts) for cat in TENNA_CATEGORIES for pts in TENNA_POINTS if (cat, pts) not in session["used"]]
        if not available:
            _tenna_advance(session)
            return
        tile = random.choice(available)
        session["used"].append(tile)
        session["question"] = _tenna_make_question(*tile)
        session["reaction"] = None
        session["group_answers"] = {}
        session["phase"] = "group_question" if session["question"]["kind"] == "group_number" else "question"
        session["deadline_at"] = time.time() + 15
        if session["question"]["kind"] == "instant":
            current = session["player_ids"][session["turn_index"] % len(session["player_ids"])]
            tenna_answer(current, "")
        return
    if session.get("phase") in {"question", "group_question"}:
        question = session.get("question") or {}
        points = int(question.get("points") or 0)
        current = session["player_ids"][session["turn_index"] % len(session["player_ids"])]
        previous_phase = session.get("phase")
        session["phase"] = "resolving"
        if previous_phase == "group_question":
            alive = [pid for pid in session["player_ids"] if not _is_player_dead(pid)]
            for pid in alive:
                session["scores"][pid] -= points
        else:
            session["scores"][current] -= points
        session["reaction"] = {"correct": False, "text": "Время вышло!", "detail": f"−{points} очков"}
        _tenna_advance(session)


def tenna_answer(user_id, answer):
    session = _tenna_session_for_user(user_id)
    if session:
        _tenna_process_timeout(session)
    if not session or session["phase"] not in {"question", "group_question"}:
        raise ValueError("Сейчас нет активного вопроса.")
    question = session["question"]
    uid = int(user_id)
    current = session["player_ids"][session["turn_index"] % len(session["player_ids"])]
    if session["phase"] == "group_question":
        if uid not in session["player_ids"] or _is_player_dead(uid):
            raise ValueError("Вы не участвуете в этом вопросе.")
        if uid in session["group_answers"]:
            raise ValueError("Ваш ответ уже принят.")
        try: value = int(str(answer).strip())
        except ValueError: raise ValueError("Введите целое число.")
        session["group_answers"][uid] = value
        alive = [pid for pid in session["player_ids"] if not _is_player_dead(pid)]
        if not all(pid in session["group_answers"] for pid in alive):
            return _tenna_public(session, uid)
        session["phase"] = "resolving"
        best = min(abs(session["group_answers"][pid] - int(question["target"])) for pid in alive)
        winners = [pid for pid in alive if abs(session["group_answers"][pid] - int(question["target"])) == best]
        for pid in alive: session["scores"][pid] += int(question["points"]) if pid in winners else -int(question["points"])
        session["reaction"] = {"correct": uid in winners, "text": random.choice(TENNA_CORRECT_LINES), "detail": "Ближе всех: " + ", ".join(next(p["name"] for p in session["players"] if p["id"] == pid) for pid in winners)}
        _tenna_advance(session)
        return _tenna_public(session, uid)
    if uid != current:
        raise ValueError("Отвечать должен текущий участник.")
    session["phase"] = "resolving"
    kind = question["kind"]
    correct = False
    delta = 0
    if kind == "instant":
        correct = True
        delta = int(question["points"])
        special_detail = question["prompt"]
        if question["correct"] == "reward":
            with db_connect_write() as conn:
                granted = _add_item_to_inventory(conn, uid, 22, 1)
                conn.commit()
            special_detail = "Хот-Дог Лавкрафта добавлен в инвентарь." if granted else "Инвентарь переполнен: Хот-Дог Лавкрафта не удалось выдать."
        elif question["correct"] == "companion":
            with db_connect_write() as conn:
                conn.execute("UPDATE PLAYERS SET COMPSLOT = 4 WHERE ID = ?", (uid,))
                conn.execute("UPDATE PLAYERS SET CheapTrickPendingNotice = 1 WHERE ID = ?", (uid,))
                conn.commit()
            special_detail = "ЧипТрик становится вашим новым компаньоном. +500 очков."
        elif question["correct"] == "curse":
            applied = []
            absorbed_hp = 0
            for effect in ("CinderPlague", "1009", "1010"):
                try:
                    effect_result = core.add_player_effect(DB_PATH, uid, effect)
                    if effect_result.get("ok"):
                        applied.append(effect)
                    if effect_result.get("absorbed_by_companion"):
                        absorbed_hp += int(effect_result.get("hp_cost") or 0)
                except Exception: pass
            if absorbed_hp > 0:
                special_detail = f"Кот-висельник поглотил эффекты и взамен забрал {absorbed_hp} HP. +700 очков."
            else:
                special_detail = "На участника наложены Чума пепла, Паника и Ярость. +700 очков." if len(applied) == 3 else "Смута пытается наложить Чуму пепла, Панику и Ярость. +700 очков."
    elif question["kind"] == "text":
        normalized = str(answer or "").strip().lower().replace(" ", "")
        if question["correct"] == "angela":
            correct = any(token in normalized for token in ("анжел", "angela", "anjel", "anjela"))
        else:
            with db_connect() as conn:
                names = [str(r[0]).strip().lower() for r in conn.execute("SELECT NAME FROM ANOMALY WHERE CLASS_ID = 4").fetchall() if r[0]]
            correct = str(answer or "").strip().lower() in names
        delta = int(question["points"]) if correct else -int(question["points"])
    else:
        correct = question["correct"] == "*" or str(answer).strip().casefold() == str(question["correct"]).strip().casefold()
        delta = int(question["points"]) if correct else -int(question["points"])
    session["scores"][uid] += delta
    if kind == "instant":
        if question["correct"] == "empty":
            reaction_text = "Редакторы, похоже, забыли добавить вопрос. В таком случае просто отдадим игроку очки. Согласны, зрители?"
            special_detail = f"Игрок получает +{delta} очков."
        else:
            reaction_text = "Игрок выбрал категорию «Аномалия в мешке»!"
        session["reaction"] = {"correct": None, "text": reaction_text, "detail": special_detail, "applause": True}
    else:
        session["reaction"] = {
            "correct": correct,
            "text": random.choice(TENNA_CORRECT_LINES if correct else TENNA_WRONG_LINES),
            "detail": f"{delta:+d} очков",
        }
    _tenna_advance(session)
    return _tenna_public(session, uid)


def tenna_close(user_id):
    session = _tenna_session_for_user(user_id)
    if not session or session.get("phase") != "finished":
        raise ValueError("Шоу ещё не завершено.")
    session["phase"] = "closed"
    try:
        train_owner = int(_safe_global_value("TrainDeadlineUserId", 0) or 0)
        if train_owner > 0:
            set_train_timer_paused(train_owner, False)
    except Exception:
        pass
    return {"active": False, "finished": True}


PO3_TRIAL_NAMES = {1: "Аномалий", 2: "Математики", 3: "Обезвреживания", 4: "Памяти"}
PO3_MATH = [(1, 843), (2, 239), (3, 471), (4, 697), (5, 489)]
PO3_WIRES = ["Оранжевый", "Красный", "Жёлтый", "Синий", "Белый", "Чёрный", "Зелёный", "Пурпурный"]
PO3_SYMBOLS = ["◆", "●", "★", "✚", "☂", "♣", "♠", "♥", "♦", "✖", "✓", "▲"]


def _po3_session_for_user(user_id):
    uid = int(user_id)
    for session in po3_sessions.values():
        if uid in session.get("queue", []) and session.get("active"):
            return session
    return None


def _po3_alive_queue():
    state = core.get_game_state(DB_PATH)
    order = [int(pid) for pid in state.get("turn_order", [])]
    if not order:
        with state_lock:
            order = [int(player["id"]) for player in lobby_state.get("players", [])]
    if not order:
        return []
    placeholders = ",".join("?" for _ in order)
    with db_connect() as conn:
        rows = conn.execute(
            f"SELECT ID FROM PLAYERS WHERE ID IN ({placeholders}) AND COALESCE(IsDead,0)=0 AND COALESCE(HP,0)>0",
            tuple(order),
        ).fetchall()
    alive = {int(row["ID"]) for row in rows}
    return [pid for pid in order if pid in alive]


def _po3_player_name(player_id):
    with state_lock:
        player = next((p for p in lobby_state.get("players", []) if int(p["id"]) == int(player_id)), None)
    return str((player or {}).get("name") or f"Игрок {int(player_id)}")


def start_po3_web_event(owner_id, anomaly_id=136):
    owner_id = int(owner_id)
    existing = _po3_session_for_user(owner_id)
    if existing:
        return _po3_public(existing, owner_id)
    queue = _po3_alive_queue()
    if owner_id not in queue:
        queue.insert(0, owner_id)
    session = {
        "id": secrets.token_hex(8), "active": True, "owner_id": owner_id,
        "anomaly_id": int(anomaly_id), "queue": queue, "index": 0,
        "current_player_id": owner_id, "phase": "access", "phase_started_at": time.time(), "revision": 1,
        "choice": None, "challenge": None, "deadline": None,
        "winners": [], "losers": [], "errors": 0, "round": 0,
        "result_acks": [], "chosen_trials": [], "results_applied": False,
    }
    po3_sessions[session["id"]] = session
    return _po3_public(session, owner_id)


def _po3_random_anomaly_question():
    with db_connect() as conn:
        rows = conn.execute(
            "SELECT ID, COALESCE(NAME,'Аномалия') AS NAME, COALESCE(PDESCRIPTION,DESCRIPTION,'—') AS PDESCRIPTION, COALESCE(PHOTO,'') AS PHOTO FROM ANOMALY WHERE ID NOT IN (4, 13, 33) ORDER BY RANDOM() LIMIT 2"
        ).fetchall()
    if not rows:
        return {"prompt": "Описание отсутствует.", "options": ["Верно", "Неверно"], "answer": "Верно"}
    base = rows[0]
    truthful = len(rows) < 2 or random.random() < 0.5
    desc = str((base if truthful else rows[1])["PDESCRIPTION"] or "—")
    photo = str(base["PHOTO"] or "")
    if photo and not photo.lower().endswith(".png"):
        photo += ".png"
    return {
        "prompt": f"Описание: {desc}\n\nЭто описание верно для показанной аномалии?",
        "options": ["Верно", "Неверно"], "answer": "Верно" if truthful else "Неверно",
        "image": f"/photo/anomaly/{photo}" if photo else None,
    }


def _po3_memory_question(session):
    kind = random.choice(["symbols", "max_danger", "min_safe", "waw_min", "today", "hp", "answered", "hint3", "maxhp", "origins"])
    if kind == "symbols":
        shown = random.sample(PO3_SYMBOLS, 6)
        target = random.choice(PO3_SYMBOLS)
        return {"kind": kind, "memorize": " ".join(shown), "prompt": f"Был ли среди показанных символ {target}?", "options": ["Да", "Нет"], "answer": "Да" if target in shown else "Нет"}
    uid = int(session["current_player_id"])
    with db_connect() as conn:
        row = conn.execute("SELECT COALESCE(HP,0) AS HP, COALESCE(MAXHP,100) AS MAXHP FROM PLAYERS WHERE ID=?", (uid,)).fetchone()
    day = int(core.get_game_state(DB_PATH).get("current_day") or 1)
    data = {
        "max_danger": ("Самый опасный класс аномалий?", ["Aleph","Waw","He","Teth","Zayin"], "Aleph"),
        "min_safe": ("Самый безопасный класс аномалий?", ["Aleph","Waw","He","Teth","Zayin"], "Zayin"),
        "waw_min": ("Какой минимальный результат нужен, чтобы WAW не нанесла урон?", ["5","6","7","8","9"], "7"),
        "today": ("Какой сегодня день?", [str(max(1, day+d)) for d in (-2,-1,0,1,2)], str(day)),
        "hp": ("Сколько сейчас у тебя HP?", [str(max(0, int(row["HP"] or 0)+d)) for d in (-25,-10,0,10,25)], str(int(row["HP"] or 0))),
        "answered": ("На сколько вопросов этого испытания ты уже ответил?", ["0","1","2","3"], str(int(session.get("round") or 0))),
        "hint3": ("Сколько исследовательских очков стоит открыть 3-ю подсказку?", ["5","10","15","20","25"], "10"),
        "maxhp": ("Максимальное количество здоровья игрока без предметов и эффектов?", ["200","250","300","350","400"], "300"),
        "origins": ("Сколько типов происхождения аномалий существует?", ["3","4","5","6"], "5"),
    }
    prompt, options, answer = data[kind]
    return {"kind": kind, "prompt": prompt, "options": options, "answer": answer}


def _po3_begin_challenge(session, choice):
    session.update({"choice": int(choice), "phase": "trial", "phase_started_at": time.time(), "errors": 0, "round": 0})
    if int(choice) == 1:
        challenge = _po3_random_anomaly_question(); session["deadline"] = time.time() + 10
    elif int(choice) == 2:
        session["math_order"] = random.sample(PO3_MATH, len(PO3_MATH))
        idx, answer = session["math_order"][0]
        options = [answer, answer + random.choice([7,11,15]), answer - random.choice([6,9,13]), answer + random.choice([18,21])]
        random.shuffle(options)
        challenge = {"prompt": "Выберите правильный ответ:", "options": [str(v) for v in options], "answer": str(answer), "image": f"/photo/PO3/math{idx}.png"}
        session["deadline"] = time.time() + 60
    elif int(choice) == 3:
        challenge = {"kind": "wire_order", "prompt": "Расположите провода в порядке обезвреживания и подтвердите выбор.", "options": random.sample(PO3_WIRES, len(PO3_WIRES)), "answer_order": list(PO3_WIRES), "rules": "1) Первый провод содержит букву Ж. 2) После Пурпурного провода не режут. 3) Синий сразу после Жёлтого и перед Белым. 4) Красный до Жёлтого. 5) Чёрный сразу после Белого. 6) Красный среди первых четырёх. 7) Зелёный среди последних четырёх."}
        # Исходный код использует этот однозначный порядок, несмотря на текст первой подсказки.
        session["deadline"] = time.time() + 180
    else:
        challenge = _po3_memory_question(session)
        if challenge.get("kind") == "symbols":
            session["phase"] = "memorize"; session["phase_started_at"] = time.time(); session["deadline"] = time.time() + 10
        else:
            session["deadline"] = time.time() + 15
    session["challenge"] = challenge
    session["revision"] += 1


def _po3_finish_member(session, success):
    uid = int(session["current_player_id"])
    target = session["winners"] if success else session["losers"]
    if uid not in target:
        target.append(uid)
    session.update({"choice": None, "challenge": None, "deadline": None, "errors": 0, "round": 0})
    if not success:
        session["phase"] = "failed_notice"
        session["phase_started_at"] = time.time()
    else:
        _po3_advance_queue(session)
    session["revision"] += 1


def _po3_advance_queue(session):
    session["index"] = int(session.get("index") or 0) + 1
    while session["index"] < len(session["queue"]) and _is_player_dead(int(session["queue"][session["index"]])):
        session["index"] += 1
    if session["index"] >= len(session["queue"]):
        session["phase"] = "results_winners"
        session["phase_started_at"] = time.time()
        session["current_player_id"] = int(session["owner_id"])
    else:
        session["current_player_id"] = int(session["queue"][session["index"]])
        session["phase"] = "select"
        session["phase_started_at"] = time.time()


def _po3_finalize_results(session):
    if session.get("results_applied"):
        return
    death_reason = "Не прошел испытание PO3"
    for loser in session.get("losers", []):
        core.add_player_effect(DB_PATH, int(loser), "PO3_LOSER")
        core.set_player_dead(DB_PATH, int(loser), reason=death_reason)
    owner = int(session["owner_id"])
    with db_connect_write() as conn:
        conn.execute(
            "UPDATE WORK SET photounlocked=1, descriptionunlocked=1, hintunlocked=COALESCE(hintcount,0), IsCompleted=1 WHERE user_id=? AND anomaly_id=136",
            (owner,),
        )
        conn.commit()
    session["results_applied"] = True
    session["phase"] = "finished"
    session["phase_started_at"] = time.time()
    if _is_player_dead(owner):
        _advance_after_nonwork_death(owner, "po3_trial_failed")


def po3_continue_after_failure(user_id, expected_revision=None):
    session = _po3_session_for_user(user_id)
    if not session:
        raise ValueError("Сообщение об ошибке уже закрыто.")
    if _po3_stale_request(session, expected_revision):
        return _po3_public(session, user_id)
    if session.get("phase") != "failed_notice":
        raise ValueError("Сообщение об ошибке уже закрыто.")
    if int(user_id) != int(session.get("current_player_id") or 0):
        raise ValueError("Продолжить может только проходивший испытание игрок.")
    _po3_advance_queue(session)
    session["revision"] += 1
    return _po3_public(session, user_id)


def po3_results_next(user_id, expected_revision=None):
    session = _po3_session_for_user(user_id)
    if not session or int(user_id) != int(session.get("owner_id") or 0):
        raise ValueError("Подводить итоги может только инициатор испытаний.")
    if _po3_stale_request(session, expected_revision):
        return {"po3_event": _po3_public(session, user_id), "game_state": get_game_state(int(user_id))}
    phase = str(session.get("phase") or "")
    if phase == "results_winners":
        session["phase"] = "results_losers" if session.get("losers") else "results_all_success"
        session["phase_started_at"] = time.time()
    elif phase in ("results_losers", "results_all_success"):
        _po3_finalize_results(session)
    else:
        raise ValueError("Сейчас нельзя перейти к следующей части итогов.")
    session["revision"] += 1
    return {"po3_event": _po3_public(session, user_id), "game_state": get_game_state(int(user_id))}


def _po3_tick(session):
    if not session or not session.get("active"): return
    phase = str(session.get("phase") or "")
    phase_age = time.time() - float(session.get("phase_started_at") or time.time())
    # Confirmation phases have fallbacks so a disconnected participant cannot
    # hold the whole event forever.
    if phase == "access" and phase_age >= 60:
        session["phase"] = "dialog"; session["phase_started_at"] = time.time(); session["revision"] += 1; return
    if phase == "dialog" and phase_age >= 20:
        session["phase"] = "select"; session["current_player_id"] = session["queue"][0]; session["phase_started_at"] = time.time(); session["revision"] += 1; return
    if phase == "select" and phase_age >= 60:
        if _is_player_dead(int(session.get("current_player_id") or 0)):
            _po3_advance_queue(session); session["revision"] += 1; return
        available = [trial_id for trial_id in PO3_TRIAL_NAMES if trial_id not in session.get("chosen_trials", [])]
        if available:
            choice = random.choice(available)
            session.setdefault("chosen_trials", []).append(choice)
            _po3_begin_challenge(session, choice)
        else:
            _po3_finish_member(session, False)
        return
    if phase == "failed_notice" and phase_age >= 10:
        _po3_advance_queue(session); session["revision"] += 1; return
    if phase == "results_winners" and phase_age >= 10:
        session["phase"] = "results_losers" if session.get("losers") else "results_all_success"
        session["phase_started_at"] = time.time(); session["revision"] += 1; return
    if phase in ("results_losers", "results_all_success") and phase_age >= 10:
        _po3_finalize_results(session); session["revision"] += 1; return
    deadline = float(session.get("deadline") or 0)
    if deadline <= 0 or time.time() < deadline: return
    if session.get("phase") == "memorize":
        session["phase"] = "trial"; session["phase_started_at"] = time.time(); session["deadline"] = time.time() + 15; session["revision"] += 1
    elif session.get("phase") == "trial":
        _po3_finish_member(session, False)


def _po3_public(session, viewer_id):
    if not session: return {"active": False}
    _po3_tick(session)
    if session.get("phase") == "finished" and int(viewer_id) in session.get("result_acks", []):
        return {"active": False, "finished": True, "session_id": session["id"]}
    is_current_player = int(viewer_id)==int(session["current_player_id"])
    challenge = dict(session.get("challenge") or {}) if is_current_player else {}
    challenge.pop("answer", None)
    challenge.pop("answer_order", None)
    return {
        "active": bool(session.get("active")), "session_id": session["id"], "revision": session["revision"],
        "phase": session["phase"], "owner_id": session["owner_id"], "current_player_id": session["current_player_id"],
        "is_owner": int(viewer_id)==int(session["owner_id"]), "is_current_player": is_current_player,
        "current_player_name": _po3_player_name(session["current_player_id"]),
        "queue": [{"id":pid,"name":_po3_player_name(pid)} for pid in session["queue"]],
        "choice": session.get("choice"), "choice_name": PO3_TRIAL_NAMES.get(session.get("choice")),
        "available_trials": [trial_id for trial_id in PO3_TRIAL_NAMES if trial_id not in session.get("chosen_trials", [])],
        "challenge": challenge, "round": session.get("round",0), "deadline": session.get("deadline") if is_current_player else None,
        "winners": [{"id":pid,"name":_po3_player_name(pid)} for pid in session["winners"]],
        "losers": [{"id":pid,"name":_po3_player_name(pid)} for pid in session["losers"]],
    }


def _po3_stale_request(session, expected_revision):
    return expected_revision not in (None, "") and int(expected_revision) != int(session.get("revision") or 0)


def po3_accept_access(user_id, expected_revision=None):
    session = _po3_session_for_user(user_id)
    if not session or int(user_id)!=int(session["owner_id"]): raise ValueError("Подтвердить доступ может только инициатор.")
    if _po3_stale_request(session, expected_revision): return _po3_public(session, user_id)
    if session["phase"] == "access": session["phase"]="dialog"; session["phase_started_at"] = time.time(); session["revision"]+=1
    return _po3_public(session, user_id)


def po3_begin_queue(user_id, expected_revision=None):
    session = _po3_session_for_user(user_id)
    if not session or int(user_id)!=int(session["owner_id"]): raise ValueError("Запустить очередь может только инициатор.")
    if _po3_stale_request(session, expected_revision): return _po3_public(session, user_id)
    if session["phase"] == "dialog": session["phase"]="select"; session["current_player_id"]=session["queue"][0]; session["phase_started_at"] = time.time(); session["revision"]+=1
    return _po3_public(session, user_id)


def po3_choose_trial(user_id, choice, expected_revision=None):
    session = _po3_session_for_user(user_id)
    if not session: raise ValueError("Сейчас не ваша очередь выбирать испытание.")
    if _po3_stale_request(session, expected_revision): return _po3_public(session, user_id)
    if session["phase"]!="select" or int(user_id)!=int(session["current_player_id"]): raise ValueError("Сейчас не ваша очередь выбирать испытание.")
    if int(choice) not in PO3_TRIAL_NAMES: raise ValueError("Неизвестное испытание.")
    if int(choice) in session.get("chosen_trials", []): raise ValueError("Это испытание уже выбрал другой игрок.")
    session.setdefault("chosen_trials", []).append(int(choice))
    _po3_begin_challenge(session, int(choice))
    return _po3_public(session, user_id)


def po3_answer(user_id, answer, expected_revision=None):
    session = _po3_session_for_user(user_id)
    if not session: raise ValueError("Сейчас не ваша очередь отвечать.")
    if _po3_stale_request(session, expected_revision): return _po3_public(session, user_id)
    if session["phase"]!="trial" or int(user_id)!=int(session["current_player_id"]): raise ValueError("Сейчас не ваша очередь отвечать.")
    _po3_tick(session)
    if session["phase"]!="trial": return _po3_public(session,user_id)
    challenge=session.get("challenge") or {}; choice=int(session.get("choice") or 0)
    if choice == 3:
        try:
            submitted_order = json.loads(str(answer))
        except (TypeError, ValueError, json.JSONDecodeError):
            submitted_order = []
        correct = isinstance(submitted_order, list) and [str(value) for value in submitted_order] == [str(value) for value in challenge.get("answer_order", [])]
    else:
        correct=str(answer)==str(challenge.get("answer"))
    if not correct:
        _po3_finish_member(session, False)
        return _po3_public(session, user_id)
    if choice == 1:
        session["round"] += 1
        if session["round"] >= 6: _po3_finish_member(session, True)
        else: session["challenge"]=_po3_random_anomaly_question(); session["deadline"]=time.time()+10; session["revision"]+=1
    elif choice == 2:
        session["round"] += 1
        if session["round"] >= 5: _po3_finish_member(session, True)
        else:
            idx,ans=session["math_order"][session["round"]]; opts=[ans,ans+7,ans-9,ans+18]; random.shuffle(opts)
            session["challenge"]={"prompt":"Выберите правильный ответ:","options":[str(v) for v in opts],"answer":str(ans),"image":f"/photo/PO3/math{idx}.png"}; session["revision"]+=1
    elif choice == 3:
        _po3_finish_member(session, True)
    else:
        session["round"] += 1
        if session["round"] >= 3: _po3_finish_member(session, True)
        else:
            session["challenge"]=_po3_memory_question(session); session["deadline"]=time.time()+(10 if session["challenge"].get("kind")=="symbols" else 15); session["phase"]="memorize" if session["challenge"].get("kind")=="symbols" else "trial"; session["revision"]+=1
    return _po3_public(session,user_id)


def po3_ack_results(user_id):
    session = _po3_session_for_user(user_id)
    if not session:
        return {"active": False, "finished": True}
    if session.get("phase") != "finished":
        raise ValueError("Результаты испытаний ещё не подведены.")
    uid = int(user_id)
    if uid not in session["result_acks"]:
        session["result_acks"].append(uid)
        session["revision"] += 1
    if all(int(pid) in session["result_acks"] for pid in session.get("queue", [])):
        session["active"] = False
    return {"active": False, "finished": True, "session_id": session["id"]}


def get_game_state(player_id):
    maybe_progress_countdown()
    _process_train_timer()
    _brass_transfer_if_owner_dead()
    with state_lock:
        assignments = lobby_state["game_assignments"].get(player_id, [])
        player_ids = [player["id"] for player in lobby_state["players"]]
        lobby_players = [dict(player) for player in lobby_state["players"]]
    assignments = _personalize_assignment_names(int(player_id), assignments)
    _sync_death_action_log(player_ids)
    try:
        core_state = core.get_game_state(DB_PATH)
    except sqlite3.OperationalError:
        core_state = {
            "status": "running" if runtime_game["started"] else "idle",
            "current_day": int(runtime_game["current_day"] or 0),
            "total_days": int(runtime_game["total_days"]),
            "turn_index": 0,
            "current_turn_user_id": None,
            "turn_order": [],
            "started_at": runtime_game["day_started_at"],
            "finished_at": None,
            "winner_user_id": runtime_game["winner_id"],
            "last_event_at": None,
        }
    if not player_ids and (core_state.get("status") == "finished" or not runtime_game["started"]):
        player_ids = [int(pid) for pid in runtime_game.get("final_player_ids") or []]
    alive_status = {}
    death_reasons = {}
    if player_ids:
        placeholders = ",".join("?" for _ in player_ids)
        with db_connect() as conn:
            rows = conn.execute(
                f"SELECT ID, COALESCE(IsDead, 0) AS IsDead, COALESCE(DEATHREASON, '') AS DEATHREASON FROM PLAYERS WHERE ID IN ({placeholders})",
                tuple(player_ids),
            ).fetchall()
        alive_status = {int(row["ID"]): int(row["IsDead"] or 0) == 0 for row in rows}
        death_reasons = {int(row["ID"]): _normalize_death_reason(row["DEATHREASON"]) for row in rows}
        if any(not alive for alive in alive_status.values()):
            _x125_mark("death")
        with db_connect() as conn:
            max_stat_row = conn.execute(
                f"SELECT 1 FROM PLAYERS WHERE ID IN ({placeholders}) AND MAX(COALESCE(STAT1,1), COALESCE(STAT2,1), COALESCE(STAT3,1), COALESCE(STAT4,1)) >= 5 LIMIT 1",
                tuple(player_ids),
            ).fetchone()
        if max_stat_row:
            _x125_mark("stat5")
    companion_id = _player_companion_id(int(player_id))
    with db_connect() as conn:
        artifact_row = conn.execute(
            "SELECT COALESCE(ART, 0) AS ART, COALESCE(KLIPOTA, 0) AS KLIPOTA FROM PLAYERS WHERE ID = ?",
            (int(player_id),),
        ).fetchone()
    artifact_id = int(artifact_row["ART"] or 0) if artifact_row else 0
    if assignments and artifact_id in (4, 5):
        anomaly_ids = [int(item.get("id") or 0) for item in assignments if int(item.get("id") or 0) > 0]
        metadata = {}
        if anomaly_ids:
            placeholders = ",".join("?" for _ in anomaly_ids)
            with db_connect() as conn:
                rows = conn.execute(
                    f"""SELECT ID, COALESCE(CLASS_ID, 0) AS CLASS_ID,
                               COALESCE(TYPE, 0) AS TYPE,
                               COALESCE(KLIPOTA, 0) AS KLIPOTA
                        FROM ANOMALY WHERE ID IN ({placeholders})""",
                    tuple(anomaly_ids),
                ).fetchall()
            metadata = {int(row["ID"]): row for row in rows}
        enriched = []
        for item in assignments:
            updated = dict(item)
            if artifact_id == 4:
                meta = metadata.get(int(item.get("id") or 0))
                if meta:
                    updated["artifact_hint"] = f"Клипота аномалии: +{int(meta['KLIPOTA'] or 0)}"
            elif artifact_id == 5:
                meta = metadata.get(int(item.get("id") or 0))
                if meta:
                    risk = (RISK_META.get(int(meta["CLASS_ID"] or 0)) or {}).get("label", "UNKNOWN")
                    anomaly_type = ANOMALY_TYPE_LABELS.get(int(meta["TYPE"] or 0), "Неизвестный")
                    updated["artifact_hint"] = f"{risk} · {anomaly_type}"
            enriched.append(updated)
        assignments = enriched
    if assignments and _player_has_effect(int(player_id), "skibidi"):
        assignments = [
            {
                **item,
                "description": _skibidi_text(
                    player_id,
                    int(item.get("id") or 0),
                    "selection",
                    int(core_state.get("current_day") or 0),
                ),
            }
            for item in assignments
        ]
    if assignments and companion_id == 8:
        anomaly_ids = [int(item.get("id") or 0) for item in assignments if int(item.get("id") or 0) > 0]
        damage_map = {}
        if anomaly_ids:
            placeholders = ",".join("?" for _ in anomaly_ids)
            with db_connect() as conn:
                rows = conn.execute(
                    f"SELECT ID, CLASS_ID, DMGTYPE FROM ANOMALY WHERE ID IN ({placeholders})",
                    tuple(anomaly_ids),
                ).fetchall()
            damage_map = {
                int(row["ID"]): _get_damage_display(int(row["CLASS_ID"] or 1), int(row["DMGTYPE"] or 0)).get("label", "UNKNOWN")
                for row in rows
            }
        assignments = [
            {
                **item,
                "damage_hint": damage_map.get(int(item.get("id") or 0), ""),
            }
            for item in assignments
        ]
    turn_order = [int(pid) for pid in core_state.get("turn_order", [])]
    turn_players = []
    for pid in turn_order:
        lobby_player = next((player for player in lobby_players if int(player["id"]) == pid), None)
        turn_players.append(
            {
                "id": pid,
                "name": (lobby_player or {}).get("name") or f"Игрок {pid}",
                "avatar_url": (lobby_player or {}).get("avatar_url"),
                "alive": alive_status.get(pid, True),
                "is_current": int(core_state.get("current_turn_user_id") or 0) == pid,
            }
        )
    future_days = []
    current_day = int(core_state.get("current_day") or runtime_game["current_day"] or 0)
    if current_day == 10:
        _x125_mark("day10")
    total_days = int(core_state.get("total_days") or runtime_game["total_days"] or 15)
    alive_turn_players = [player for player in turn_players if player["alive"]]
    current_turn_id = int(core_state.get("current_turn_user_id") or 0)
    current_turn_player = next((player for player in turn_players if int(player["id"]) == current_turn_id), None)
    with state_lock:
        camera_state = dict(camera_view_states.get(current_turn_id) or {"screen": "selection", "anomaly_id": None})
        # A player's last room/details screen belongs to their previous turn.
        # Compare the real turn identity; last_event_at changes on ordinary
        # actions such as opening a hint and caused false resets to selection.
        camera_is_current_turn = (
            int(camera_state.get("turn_index", -1) if camera_state.get("turn_index") is not None else -1) == int(core_state.get("turn_index") or 0)
            and int(camera_state.get("day_number", -1) if camera_state.get("day_number") is not None else -1) == current_day
            and int(camera_state.get("turn_user_id") or 0) == current_turn_id
        )
        if not camera_is_current_turn:
            camera_state = {
                "screen": "selection",
                "anomaly_id": None,
                "updated_at": time.time(),
                "turn_index": int(core_state.get("turn_index") or 0),
                "day_number": current_day,
                "turn_user_id": current_turn_id,
            }
            if current_turn_id > 0:
                camera_view_states[current_turn_id] = dict(camera_state)
        camera_assignments = [dict(item) for item in lobby_state["game_assignments"].get(current_turn_id, [])]
    camera_assignments = _personalize_assignment_names(current_turn_id, camera_assignments) if current_turn_id > 0 else []
    camera_view = {
        **camera_state,
        "player_id": current_turn_id or None,
        "player_name": (current_turn_player or {}).get("name") or (f"Игрок {current_turn_id}" if current_turn_id else "—"),
        "anomalies": camera_assignments,
    }
    for day_number in range(current_day + 1, total_days + 1):
        future_days.append(
            {
                "day": day_number,
                "players": alive_turn_players,
            }
        )
    final_results = {"exists": False, "winner_id": None, "winner_name": "", "standings": []}
    if core_state.get("status") == "finished" or not runtime_game["started"]:
        final_results = runtime_game.get("final_results") or final_results
        if (not final_results.get("standings")) and player_ids:
            final_results = get_final_results_payload(player_ids)
            runtime_game["final_results"] = final_results
        if int(player_id or 0):
            print(
                "[DEBUG get_game_state final]",
                json.dumps(
                    {
                        "user_id": int(player_id),
                        "core_status": core_state.get("status"),
                        "runtime_started": runtime_game.get("started"),
                        "player_ids": player_ids,
                        "runtime_final_player_ids": runtime_game.get("final_player_ids"),
                        "runtime_final_results": runtime_game.get("final_results"),
                        "final_results": final_results,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    return {
        "lobby": serialize_lobby(),
        "game": {
            "started": bool(runtime_game["started"]),
            "current_day": int(runtime_game["current_day"] or 0),
            "total_days": int(runtime_game["total_days"]),
            "day_started_at": runtime_game["day_started_at"],
            "winner_id": runtime_game["winner_id"] or (determine_winner_by_cp(player_ids) if player_ids else None),
        },
        "core": core_state,
        "final_results": final_results,
        "alastor_task": _build_alastor_task_prompt(int(player_id)),
        "d20_roll_pending": bool(
            int(_safe_global_value("d20", 0) or 0) == 1
            and current_day > int(_safe_global_value("d20_activated_day", 0) or 0)
            and int(core_state.get("current_turn_user_id") or 0) == int(player_id)
            and alive_status.get(int(player_id), True)
            and int(_safe_global_value(f"d20_{current_day}_{int(player_id)}", 0) or 0) != 1
        ),
        "crimson_bite": _build_crimson_bite_payload(
            int(player_id), core_state=core_state, alive_status=alive_status, lobby_players=lobby_players
        ),
        "train_ticket": get_train_ticket_payload(int(player_id)),
        "violin_button": get_violin_button_payload(int(player_id)),
        "brass_sphere_event": get_brass_sphere_event_payload(int(player_id)),
        "contract_summary": _build_contract_summary_payload(int(player_id)),
        "tenna_game": _tenna_public(_tenna_session_for_user(int(player_id)), int(player_id)),
        "po3_event": _po3_public(_po3_session_for_user(int(player_id)), int(player_id)),
        "x125_events": _x125_events_payload(),
        "x125_special_event": _x125_special_event_payload(),
        "klipota_event": _klipota_event_payload(int(player_id)),
        "voyager_warning": _voyager_warning_payload(int(player_id)),
        "clay_popup": _clay_popup_payload(int(player_id)),
        "target_notice": _target_notice_payload(int(player_id), core_state=core_state),
        "bloodbot_event": _bloodbot_event_for_player(int(player_id)),
        "utilizer_notice": _get_utilizer_notice(int(player_id)),
        "brainrot_music": _brainrot_music_payload(int(player_id)),
        "softlock_vote": _softlock_vote_payload(int(player_id)),
        "action_log": [dict(entry) for entry in game_action_log[-10:]],
        "turn_ui": {
            "current_day": current_day,
            "total_days": total_days,
            "current_turn_user_id": int(core_state.get("current_turn_user_id") or 0) or None,
            "players": turn_players,
            "future_days": future_days,
            "is_my_turn": int(core_state.get("current_turn_user_id") or 0) == int(player_id),
            "is_alive": alive_status.get(int(player_id), True),
            "death_reason": death_reasons.get(int(player_id), "") if not alive_status.get(int(player_id), True) else "",
        },
        "camera_view": camera_view,
        "anomalies": assignments,
    }


def resolve_crimson_bite(user_id, target_id=None):
    user_id = int(user_id)
    core_state = core.get_game_state(DB_PATH)
    current_day = int(core_state.get("current_day") or _current_day_number() or 0)
    if core_state.get("status") != "started" or int(core_state.get("current_turn_user_id") or 0) != user_id:
        raise ValueError("Укус можно совершить только в начале своего хода.")
    if not _player_has_effect(user_id, "CrimsonVirus"):
        raise ValueError("Игрок не заражён Багровым вирусом.")
    flag_key = _crimson_bite_flag(current_day, user_id)
    if int(_safe_global_value(flag_key, 0) or 0) == 1:
        raise ValueError("Голод в этом ходу уже утолён.")
    prompt = _build_crimson_bite_payload(user_id, core_state=core_state)
    targets = {int(item["id"]): item for item in prompt.get("targets", [])}
    core.set_global_value(DB_PATH, flag_key, 1)
    if not targets:
        damage = core.apply_damage(
            DB_PATH, user_id, hp_damage=10, sp_damage=10,
            reason="Голод Багрового вируса свёл с ума",
        )
        result = {
            "ok": True,
            "kind": "starvation",
            "message": "Голод сводит с ума... (-10 HP и -10 рассудка)",
            "damage": damage,
            "player_dead": bool(damage.get("is_dead")),
        }
        if result["player_dead"]:
            game_state = _advance_after_nonwork_death(user_id, "crimson_virus_starvation")
            result.update({
                "death_reason": "Голод Багрового вируса свёл с ума",
                "game_state": game_state,
                "final_results": game_state.get("final_results"),
            })
        else:
            result["game_state"] = get_game_state(user_id)
        return result
    if target_id is None:
        core.set_global_value(DB_PATH, flag_key, 0)
        raise ValueError("Выберите живую цель.")
    target_id = int(target_id)
    if target_id == user_id or target_id not in targets:
        core.set_global_value(DB_PATH, flag_key, 0)
        raise ValueError("Эта цель недоступна.")
    damage = core.apply_damage(
        DB_PATH, target_id, hp_damage=0, sp_damage=10,
        reason="Укус носителя Багрового вируса",
    )
    infection = _force_crimson_infection(target_id)
    target = targets[target_id]
    actor_name = _player_display_name(user_id)
    target_name = target.get("label") or f"Игрок {target_id}"
    _append_game_action_log(
        "effect",
        f"{actor_name} выбрал игрока {target_name} целью укуса Багрового вируса: −10 рассудка.",
        user_id,
    )
    _queue_target_notice(
        target_id,
        "Укус Багрового вируса",
        f"Игрок {actor_name} выбрал вас целью укуса. Вы потеряли 10 рассудка"
        + (" и были заражены Багровым вирусом." if bool(infection.get("newly_infected")) else "."),
        source_id=user_id,
    )
    return {
        "ok": True,
        "kind": "bite",
        "target_id": target_id,
        "target_name": target_name,
        "newly_infected": bool(infection.get("newly_infected")),
        "message": f"{target.get('label') or f'Игрок {target_id}'} получает -10 рассудка и заражается Багровым вирусом.",
        "damage": damage,
        "target_dead": bool(damage.get("is_dead")),
        "game_state": get_game_state(user_id),
    }


def roll_d20_curse(user_id):
    core_state = core.get_game_state(DB_PATH)
    current_day = int(core_state.get("current_day") or _current_day_number() or 0)
    if int(_safe_global_value("d20", 0) or 0) != 1:
        raise ValueError("Проклятие кубика не активно.")
    if current_day <= int(_safe_global_value("d20_activated_day", 0) or 0):
        raise ValueError("Первый бросок будет доступен со следующего дня.")
    if int(core_state.get("current_turn_user_id") or 0) != int(user_id):
        raise ValueError("Кубик можно бросить только в свой ход.")
    flag_key = f"d20_{current_day}_{int(user_id)}"
    if int(_safe_global_value(flag_key, 0) or 0) == 1:
        raise ValueError("В этом ходу кубик уже был брошен.")
    core.set_global_value(DB_PATH, flag_key, 1)
    forced_roll = int(_safe_global_value("forcedroll", 0) or 0)
    forced_roll_day = int(_safe_global_value("forcedroll_day", 0) or 0)
    use_forced_roll = 1 <= forced_roll <= 20 and (forced_roll_day <= 0 or current_day >= forced_roll_day)
    roll = forced_roll if use_forced_roll else random.randint(1, 20)
    if use_forced_roll:
        core.set_global_value(DB_PATH, "forcedroll", 0)
        core.set_global_value(DB_PATH, "forcedroll_day", 0)

    result = {"ok": True, "roll": int(roll), "player_dead": False}
    if roll == 1:
        with db_connect() as conn:
            row = conn.execute("SELECT COALESCE(HP, 0) AS HP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        hp = max(0, int(row["HP"] or 0) if row else 0)
        damage = core.apply_damage(DB_PATH, int(user_id), hp_damage=max(1, (hp + 1) // 2), reason="Проклятие двадцатигранного кубика")
        result.update({"damage": damage, "text": f"Выпало 1. Получен урон в размере 50% текущего HP."})
        if bool((damage or {}).get("is_dead")):
            game_state = _advance_after_nonwork_death(int(user_id), "d20_curse_death")
            result.update({"player_dead": True, "death_reason": "Погиб от проклятия двадцатигранного кубика", "game_state": game_state, "final_results": game_state.get("final_results")})
            _append_game_action_log("effect", f"{_player_display_name(user_id)} бросил D20: {result.get('text', '')}", int(user_id))
            return result
    elif 2 <= roll <= 5:
        with state_lock:
            pool = list(lobby_state.get("game_assignments", {}).get(int(user_id), []))
        if pool:
            rolled_pool = random.sample(pool, min(3, len(pool)))
            ids = [int(item.get("id") or 0) for item in rolled_pool]
            placeholders = ",".join("?" for _ in ids)
            with db_connect() as conn:
                rows = conn.execute(f"SELECT ID, COALESCE(CLASS_ID, 0) AS CLASS_ID FROM ANOMALY WHERE ID IN ({placeholders})", tuple(ids)).fetchall()
            class_by_id = {int(row["ID"]): int(row["CLASS_ID"] or 0) for row in rows}
            highest = max((class_by_id.get(item_id, 0) for item_id in ids), default=0)
            candidates = [item for item in rolled_pool if class_by_id.get(int(item.get("id") or 0), 0) == highest]
            chosen = random.choice(candidates) if candidates else random.choice(rolled_pool)
            with state_lock:
                lobby_state["game_assignments"][int(user_id)] = [chosen]
            result.update({"forced_anomaly": chosen, "text": f"Выпало {roll}. Кубик выбрал самую опасную аномалию: {chosen.get('name') or chosen.get('codename') or chosen.get('id')}."})
        else:
            result["text"] = f"Выпало {roll}. Подходящих аномалий для выбора не найдено."
    elif 6 <= roll <= 10:
        result["text"] = f"Выпало {roll}. Ничего не произошло."
    elif 11 <= roll <= 15:
        heal = int(roll) * 2
        with db_connect_write() as conn:
            row = conn.execute("SELECT COALESCE(HP, 0) AS HP, COALESCE(MAXHP, 0) AS MAXHP FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
            hp = int(row["HP"] or 0) if row else 0
            max_hp = int(row["MAXHP"] or 0) if row else 0
            restored = max(0, min(max_hp, hp + heal) - hp)
            conn.execute("UPDATE PLAYERS SET HP = MIN(COALESCE(MAXHP, 0), COALESCE(HP, 0) + ?) WHERE ID = ?", (heal, int(user_id)))
            conn.commit()
        result.update({"healed": restored, "text": f"Выпало {roll}. Восстановлено {restored} HP."})
    elif 16 <= roll <= 19:
        rt_reward = int(roll) - 15
        with db_connect_write() as conn:
            conn.execute("UPDATE PLAYERS SET RT = COALESCE(RT, 0) + ? WHERE ID = ?", (rt_reward, int(user_id)))
            conn.commit()
        result.update({"rt_reward": rt_reward, "text": f"Выпало {roll}. Получено {rt_reward} RT."})
    else:
        with db_connect_write() as conn:
            removed_effects = _clear_all_player_effects_conn(conn, int(user_id))
            cp_reward = len(removed_effects) * 1000
            conn.execute("UPDATE PLAYERS SET BONUS = COALESCE(BONUS, 0) + 10, CP = COALESCE(CP, 0) + ? WHERE ID = ?", (cp_reward, int(user_id)))
            sync_leaderboard_entry(int(user_id), conn=conn)
            conn.commit()
        result.update({
            "removed_effects": removed_effects,
            "cp_reward": cp_reward,
            "bonus_reward": 10,
            "text": f"Выпало 20. Постоянный бонус увеличен на 10%. Снято эффектов: {len(removed_effects)}. Получено {cp_reward} CP.",
        })
    _append_game_action_log("effect", f"{_player_display_name(user_id)} бросил D20: {result.get('text', '')}", int(user_id))
    result["game_state"] = get_game_state(int(user_id))
    return result


def get_test_anomalies():
    with db_connect() as conn:
        rows = conn.execute("SELECT ID, NAME, PDESCRIPTION, IsDone, codename FROM ANOMALY WHERE ID NOT IN (4, 13, 33) ORDER BY RANDOM() LIMIT 5").fetchall()
    result = []
    for row in rows:
        anomaly_id = row["ID"]
        result.append(
            {
                "id": anomaly_id,
                "name": row["NAME"] if row["IsDone"] == 1 else (row["codename"] or f"SC-UN-U-{anomaly_id}"),
                "real_name": row["NAME"],
                "description": row["PDESCRIPTION"] or "РћРїРёСЃР°РЅРёРµ РїРѕРєР° РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚.",
                "is_done": row["IsDone"],
            }
        )
    return result


def get_codex_payload(user_id):
    studied_ids = {
        int(anomaly_id)
        for anomaly_id in core.get_player_studied_anomalies(DB_PATH, int(user_id))
        if int(anomaly_id) not in DISABLED_ANOMALY_IDS
    }
    disabled_ids = sorted(int(anomaly_id) for anomaly_id in DISABLED_ANOMALY_IDS)
    disabled_placeholders = ",".join("?" for _ in disabled_ids)
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT ID, NAME, CLASS_ID, TYPE, DESCRIPTION, IsDone, PHOTO, codename
            FROM ANOMALY
            WHERE ID NOT IN ({disabled_placeholders})
            ORDER BY ID
            """,
            tuple(disabled_ids),
        ).fetchall()

    entries = []
    studied_count = len(studied_ids)
    total_count = len(rows)
    for row in rows:
        is_studied = int(row["ID"]) in studied_ids
        photo_ref = row["PHOTO"] or ""
        photo = f"/photo/anomaly/{photo_ref}.png" if is_studied and photo_ref else "/photo/web_ui/nophoto.png"
        entries.append(
            {
                "id": row["ID"],
                "name": row["NAME"] if is_studied else (row["codename"] or f"SC-UN-U-{row['ID']}"),
                "real_name": row["NAME"],
                "class_id": row["CLASS_ID"] if is_studied else None,
                "type_id": row["TYPE"] if is_studied else None,
                "description": row["DESCRIPTION"] if is_studied else None,
                "is_done": is_studied,
                "photo": photo,
            }
        )

    percent = round((studied_count / total_count) * 100) if total_count else 0
    return {"entries": entries, "done_count": studied_count, "total_count": total_count, "percent": percent}


def build_discord_avatar_url(user):
    avatar = user.get("avatar")
    user_id = user.get("id")
    if avatar and user_id:
        ext = "gif" if str(avatar).startswith("a_") else "png"
        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.{ext}?size=128"
    discriminator = user.get("discriminator")
    try:
        index = int(discriminator or 0) % 5
    except ValueError:
        index = 0
    return f"https://cdn.discordapp.com/embed/avatars/{index}.png"


def create_session(discord_user):
    sid = secrets.token_urlsafe(24)
    profile = {
        "id": discord_user.get("id"),
        "username": discord_user.get("username"),
        "global_name": discord_user.get("global_name"),
        "avatar": discord_user.get("avatar"),
        "avatar_url": build_discord_avatar_url(discord_user),
    }
    sessions[sid] = profile
    return sid, profile


def create_guest_session():
    while True:
        user_id = 8_000_000_000_000_000 + secrets.randbelow(999_999_999_999_999)
        with db_connect() as conn:
            exists = conn.execute("SELECT 1 FROM PLAYERS WHERE ID = ?", (int(user_id),)).fetchone()
        if not exists:
            break
    guest_name = f"Гость-{str(user_id)[-6:]}"
    profile = {
        "id": str(user_id),
        "username": guest_name,
        "global_name": guest_name,
        "avatar": None,
        "avatar_url": None,
        "is_guest": True,
    }
    ensure_player_registered(user_id, guest_name, None)
    sid = secrets.token_urlsafe(24)
    sessions[sid] = profile
    return sid, profile


def _oauth_enabled():
    return bool(DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET and DISCORD_REDIRECT_URI)


def _session_cookie_value(session_id, *, clear=False):
    cookie = cookies.SimpleCookie()
    cookie[SESSION_COOKIE] = "" if clear else str(session_id)
    cookie[SESSION_COOKIE]["path"] = "/"
    cookie[SESSION_COOKIE]["httponly"] = True
    cookie[SESSION_COOKIE]["samesite"] = "Lax"
    if DISCORD_REDIRECT_URI.lower().startswith("https://") or bool(os.getenv("RAILWAY_PROJECT_ID")):
        cookie[SESSION_COOKIE]["secure"] = True
    if clear:
        cookie[SESSION_COOKIE]["max-age"] = "0"
    return cookie.output(header="").strip()


def sync_discord_user_to_db(discord_user):
    user_id = int(discord_user["id"])
    username = discord_user.get("global_name") or discord_user.get("username") or f"Discord-{user_id}"
    avatar_url = build_discord_avatar_url(discord_user)

    with db_connect_write() as conn:
        player = conn.execute("SELECT ID, AVATAR_URL FROM PLAYERS WHERE ID = ?", (user_id,)).fetchone()
        if not player:
            conn.execute(
                """
                INSERT INTO PLAYERS
                (ID, NAME, HP, MAXHP, SP, MAXSP, INVSLOT1, SLOT1AMOUNT, INVSLOT2, SLOT2AMOUNT, COMPSLOT, RP, CP, RT, ART, STAT1, STAT2, STAT3, STAT4, PENALTY, KLIPOTA, BONUS, AVATAR_URL)
                VALUES (?, ?, 100, 100, 200, 200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, ?)
                """,
                (user_id, username, avatar_url),
            )
        else:
            if avatar_url:
                conn.execute("UPDATE PLAYERS SET NAME = ?, AVATAR_URL = ? WHERE ID = ?", (username, avatar_url, user_id))
            else:
                conn.execute("UPDATE PLAYERS SET NAME = ? WHERE ID = ?", (username, user_id))
        sync_leaderboard_entry(user_id, name=username, conn=conn)
        conn.commit()


def get_session_profile(handler):
    cookie_header = handler.headers.get("Cookie")
    if not cookie_header:
        return None
    jar = cookies.SimpleCookie()
    jar.load(cookie_header)
    morsel = jar.get(SESSION_COOKIE)
    if not morsel:
        return None
    return sessions.get(morsel.value)


def create_discord_login_url():
    if not _oauth_enabled():
        raise RuntimeError("Discord OAuth не настроен на сервере.")
    state = secrets.token_urlsafe(24)
    oauth_states[state] = time.time()
    params = urlencode(
        {
            "client_id": DISCORD_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": DISCORD_REDIRECT_URI,
            "scope": DISCORD_SCOPE,
            "state": state,
            "prompt": "consent",
        }
    )
    return f"{DISCORD_AUTH_URL}?{params}"


def exchange_discord_code(code):
    payload = urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": DISCORD_REDIRECT_URI,
        }
    ).encode("utf-8")
    request = Request(DISCORD_TOKEN_URL, data=payload, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    basic = base64.b64encode(f"{DISCORD_CLIENT_ID}:{DISCORD_CLIENT_SECRET}".encode("utf-8")).decode("ascii")
    request.add_header("Authorization", f"Basic {basic}")
    request.add_header("User-Agent", HTTP_USER_AGENT)
    request.add_header("Accept", "application/json")
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(body or str(exc))


def fetch_discord_user(access_token):
    request = Request(DISCORD_ME_URL)
    request.add_header("Authorization", f"Bearer {access_token}")
    request.add_header("User-Agent", HTTP_USER_AGENT)
    request.add_header("Accept", "application/json")
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/health":
            try:
                with db_connect() as conn:
                    conn.execute("SELECT 1").fetchone()
                self.respond_json({"ok": True})
            except sqlite3.Error as exc:
                self.respond_error(HTTPStatus.SERVICE_UNAVAILABLE, f"Database unavailable: {exc}")
            return

        if parsed.path == "/auth/discord/login":
            if not _oauth_enabled():
                self.respond_error(HTTPStatus.SERVICE_UNAVAILABLE, "Discord OAuth не настроен.")
                return
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", create_discord_login_url())
            self.end_headers()
            return
        if parsed.path == "/auth/discord/logout":
            profile = get_session_profile(self)
            if profile:
                stale = None
                for sid, stored in list(sessions.items()):
                    if stored == profile:
                        stale = sid
                        break
                if stale:
                    sessions.pop(stale, None)
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Set-Cookie", _session_cookie_value("", clear=True))
            self.send_header("Location", "/")
            self.end_headers()
            return
        if parsed.path == "/auth/discord/callback":
            code = query.get("code", [None])[0]
            state = query.get("state", [None])[0]
            if not code or not state or state not in oauth_states:
                self.respond_error(HTTPStatus.BAD_REQUEST, "Discord OAuth state invalid.")
                return
            oauth_states.pop(state, None)
            previous_profile = get_session_profile(self)
            try:
                token = exchange_discord_code(code)
                discord_user = fetch_discord_user(token["access_token"])
                sync_discord_user_to_db(discord_user)
                discord_player = ensure_player(
                    user_id=int(discord_user["id"]),
                    username=discord_user.get("global_name") or discord_user.get("username"),
                    avatar_url=build_discord_avatar_url(discord_user),
                )
                _replace_guest_lobby_identity(previous_profile, discord_player)
                sid, _profile = create_session(discord_user)
            except Exception as exc:
                self.respond_error(HTTPStatus.BAD_GATEWAY, f"Discord OAuth failed: {exc}")
                return

            self.send_response(HTTPStatus.FOUND)
            self.send_header("Set-Cookie", _session_cookie_value(sid))
            self.send_header("Location", "/")
            self.end_headers()
            return
        if parsed.path == "/api/bootstrap":
            user = ensure_player(user_id=int(query["user_id"][0]) if query.get("user_id") else None)
            self.respond_json(
                {
                    "user": user,
                    "arts": get_arts(),
                    "leaderboard": get_leaderboard_page(),
                    "lobby": serialize_lobby(),
                    "auth": {"discord_user": get_session_profile(self), "oauth_enabled": _oauth_enabled()},
                    "debug_enabled": debug_mode_enabled(),
                    "discord_integration": {
                        "supported": True,
                        "fields": ["id", "username", "avatar"],
                        "note": "Discord ????? ???????? id, username ? avatar ????? OAuth2 identify ??? ????? SDK ?????? Activity.",
                    },
                }
            )
            return
        if parsed.path == "/api/lobby":
            self.respond_json(serialize_lobby())
            return
        if parsed.path == "/api/leaderboard":
            page = int(query.get("page", ["1"])[0])
            per_page = int(query.get("per_page", ["10"])[0])
            self.respond_json(get_leaderboard_page(page=page, per_page=per_page))
            return
        if parsed.path == "/api/me":
            self.respond_json({"discord_user": get_session_profile(self), "oauth_enabled": _oauth_enabled(), "debug_enabled": debug_mode_enabled()})
            return
        if parsed.path == "/api/game":
            if not query.get("user_id"):
                self.respond_error(HTTPStatus.BAD_REQUEST, "????? user_id.")
                return
            with gameplay_action_lock:
                recovered = _recover_dead_current_turn(int(query["user_id"][0]))
                self.respond_json(recovered or get_game_state(int(query["user_id"][0])))
            return
        if parsed.path == "/api/game/x125-battle":
            battle = _safe_global_value("X125_BATTLE", {})
            self.respond_json({"battle": battle if isinstance(battle, dict) else {}})
            return
        if parsed.path == "/api/game/inventory":
            if not query.get("user_id"):
                self.respond_error(HTTPStatus.BAD_REQUEST, "Нужен user_id.")
                return
            try:
                self.respond_json(get_inventory_payload(int(query["user_id"][0])))
            except ValueError as exc:
                self.respond_error(HTTPStatus.BAD_REQUEST, str(exc))
            return
        if parsed.path == "/api/work-room":
            if not query.get("user_id") or not query.get("anomaly_id"):
                self.respond_error(HTTPStatus.BAD_REQUEST, "РќСѓР¶РЅС‹ user_id Рё anomaly_id.")
                return
            try:
                apply_initial = str((query.get("apply_initial") or ["0"])[0]).strip() in {"1", "true", "yes"}
                user_id = int(query["user_id"][0])
                anomaly_id = int(query["anomaly_id"][0])
                selection_position_raw = (query.get("selection_position") or [None])[0]
                observing = str((query.get("observe") or ["0"])[0]).strip().lower() in {"1", "true", "yes"}
                if apply_initial:
                    _assert_current_turn(user_id)
                if selection_position_raw not in (None, ""):
                    _assert_current_turn(user_id)
                    _record_alastor_anomaly_selection(user_id, anomaly_id, int(selection_position_raw))
                payload = {}
                if apply_initial and not observing:
                    _claim_day_anomaly(user_id, anomaly_id)
                    _capture_work_status_snapshot(user_id, anomaly_id)
                    payload["initial_effect_result"] = run_initial_effect(user_id, anomaly_id)
                payload["room"] = get_work_room_payload(user_id, anomaly_id)
                self.respond_json(
                    payload
                )
            except ValueError as exc:
                self.respond_error(HTTPStatus.BAD_REQUEST, str(exc))
            return
        if parsed.path == "/api/details":
            if not query.get("user_id") or not query.get("anomaly_id"):
                self.respond_error(HTTPStatus.BAD_REQUEST, "Нужны user_id и anomaly_id.")
                return
            try:
                self.respond_json({"details": get_details_payload(int(query["user_id"][0]), int(query["anomaly_id"][0]))})
            except ValueError as exc:
                self.respond_error(HTTPStatus.BAD_REQUEST, str(exc))
            return
        if parsed.path == "/api/test-anomalies":
            if not debug_mode_enabled():
                self.respond_error(HTTPStatus.NOT_FOUND, "Не найдено.")
                return
            self.respond_json({"entries": get_test_anomalies()})
            return
        if parsed.path == "/api/codex":
            user = ensure_player(user_id=int(query["user_id"][0]) if query.get("user_id") else None)
            self.respond_json(get_codex_payload(user["id"]))
            return
        if parsed.path.startswith("/photo/") or parsed.path.startswith("/sound/"):
            self.serve_static(parsed.path.lstrip("/"))
            return
        if parsed.path in {"/", "/index.html", "/styles.css", "/app.js", "/app_runtime.js", "/background.png", "/container.png", "/back.png", "/discord.png", "/codex.png", "/kodex_menu.png", "/containerback.png", "/back_leaderboard.png", "/anomaly_topleft.png", "/nophoto.png", "/online.png", "/solo.png", "/backgroundselect.png", "/cont.png", "/contfix.png", "/105_delirium.png", "/worksru.png"}:
            self.serve_static("index.html" if parsed.path == "/" else parsed.path.lstrip("/"))
            return
        self.respond_error(HTTPStatus.NOT_FOUND, "?? ???????.")

    def do_POST(self):
        with gameplay_action_lock:
            self._do_POST_locked()

    def _do_POST_locked(self):
        body = self.read_json()
        try:
            turn_owner_paths = {
                "/api/work", "/api/game/finish-preview", "/api/game/finish-turn",
                "/api/game/flee", "/api/game/d20-roll", "/api/game/crimson-bite",
                "/api/game/upgrade-stat",
            }
            if (self.path in turn_owner_paths or self.path.startswith("/api/details/")) and body.get("user_id") is not None:
                _assert_current_turn(int(body["user_id"]))
            if self.path == "/api/session":
                user = ensure_player(user_id=body.get("user_id"), username=body.get("username"), avatar_url=body.get("avatar_url"))
                self.respond_json({"user": user})
                return
            if self.path == "/api/game/camera-state":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(update_camera_view(
                    int(body["user_id"]), body.get("screen"), body.get("anomaly_id"),
                    body.get("revision"), body.get("vn_state"), body.get("details_scroll_ratio"),
                    body.get("mini_game_state")
                ))
                return
            if self.path == "/api/game/softlock-start":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(start_softlock_vote(int(body["user_id"])))
                return
            if self.path == "/api/game/softlock-vote":
                if body.get("user_id") is None or body.get("approve") is None:
                    raise ValueError("Нужны user_id и решение.")
                self.respond_json(vote_softlock(int(body["user_id"]), bool(body.get("approve"))))
                return
            if self.path == "/api/game/target-notice-ack":
                if body.get("user_id") is None or body.get("notice_id") is None:
                    raise ValueError("Нужны user_id и notice_id.")
                self.respond_json(consume_target_notice(int(body["user_id"]), int(body["notice_id"])))
                return
            if self.path == "/api/auth/guest":
                sid, profile = create_guest_session()
                self.respond_json(
                    {"user": profile, "oauth_enabled": _oauth_enabled()},
                    headers={"Set-Cookie": _session_cookie_value(sid)},
                )
                return
            if self.path == "/api/game/x125-battle-update":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(update_x125_battle(int(body["user_id"]), body.get("state") or {}))
                return
            if self.path == "/api/game/x125-battle-hit":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(damage_x125_battle(int(body["user_id"]), 7))
                return
            if self.path == "/api/game/x125-dead-owner-finish":
                self.respond_json(finish_x125_dead_owner_event())
                return
            if self.path == "/api/game/voyager-warning-ack":
                if body.get("user_id") is None or body.get("event_id") is None:
                    raise ValueError("Нужны user_id и event_id.")
                self.respond_json(acknowledge_voyager_warning(int(body["user_id"]), int(body["event_id"])))
                return
            if self.path == "/api/game/clay-popup-ack":
                if body.get("user_id") is None or body.get("event_id") is None:
                    raise ValueError("Нужны user_id и event_id.")
                self.respond_json(acknowledge_clay_popup(int(body["user_id"]), int(body["event_id"])))
                return
            if self.path == "/api/game/protocol-x":
                if body.get("user_id") is None or body.get("target_id") is None:
                    raise ValueError("Нужны user_id и target_id.")
                self.respond_json(use_protocol_x(int(body["user_id"]), int(body["target_id"])))
                return
            if self.path == "/api/lobby/join":
                player = ensure_player(user_id=body.get("user_id"), username=body.get("username"), avatar_url=body.get("avatar_url"))
                create_or_join_lobby(player)
                self.respond_json(serialize_lobby())
                return
            if self.path == "/api/lobby/create":
                create_empty_lobby()
                self.respond_json(serialize_lobby())
                return
            if self.path == "/api/lobby/artifact":
                if body.get("user_id") is None:
                    raise ValueError("РќСѓР¶РµРЅ user_id.")
                cycle_player_art(int(body["user_id"]), body.get("direction", "right"))
                self.respond_json({"lobby": serialize_lobby()})
                return
            if self.path == "/api/lobby/ready":
                if body.get("user_id") is None:
                    raise ValueError("РќСѓР¶РµРЅ user_id.")
                set_player_ready(int(body["user_id"]), body.get("ready", True))
                self.respond_json(serialize_lobby())
                return
            if self.path == "/api/lobby/leave":
                if body.get("user_id") is None:
                    raise ValueError("Р СњРЎС“Р В¶Р ВµР Р… user_id.")
                leave_lobby_slot(int(body["user_id"]))
                self.respond_json(serialize_lobby())
                return
            if self.path == "/api/lobby/chat":
                if body.get("user_id") is None:
                    raise ValueError("РќСѓР¶РµРЅ user_id.")
                add_chat_message(int(body["user_id"]), body.get("text"))
                self.respond_json(serialize_lobby())
                return
            if self.path == "/api/work":
                if body.get("user_id") is None or body.get("anomaly_id") is None or not body.get("work_type"):
                    raise ValueError("Нужны user_id, anomaly_id и work_type.")
                self.respond_json(
                    run_work_action(
                        int(body["user_id"]),
                        int(body["anomaly_id"]),
                        str(body["work_type"]),
                        body.get("chosen_class"),
                        body.get("chosen_type"),
                    )
                )
                return
            if self.path == "/api/details/base":
                if body.get("user_id") is None or body.get("anomaly_id") is None:
                    raise ValueError("Нужны user_id и anomaly_id.")
                self.respond_json(unlock_base_info(int(body["user_id"]), int(body["anomaly_id"])))
                return
            if self.path == "/api/details/description":
                if body.get("user_id") is None or body.get("anomaly_id") is None:
                    raise ValueError("Нужны user_id и anomaly_id.")
                self.respond_json(unlock_description_info(int(body["user_id"]), int(body["anomaly_id"])))
                return
            if self.path == "/api/details/hint":
                if body.get("user_id") is None or body.get("anomaly_id") is None:
                    raise ValueError("Нужны user_id и anomaly_id.")
                self.respond_json(unlock_next_hint(int(body["user_id"]), int(body["anomaly_id"])))
                return
            if self.path == "/api/details/curse137-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_curse137_preview(int(body["user_id"]), int(body.get("anomaly_id") or 137)))
                return
            if self.path == "/api/details/curse137-choice":
                if body.get("user_id") is None or not body.get("choice"):
                    raise ValueError("Нужны user_id и choice.")
                self.respond_json(resolve_curse137_choice(
                    int(body["user_id"]), body.get("choice"), int(body.get("anomaly_id") or 137)
                ))
                return
            if self.path == "/api/details/confirm-fatal":
                if body.get("user_id") is None or body.get("anomaly_id") is None:
                    raise ValueError("Нужны user_id и anomaly_id.")
                self.respond_json(
                    confirm_details_fatal_action(
                        int(body["user_id"]),
                        int(body["anomaly_id"]),
                        body.get("action_type"),
                    )
                )
                return
            if self.path == "/api/details/hidden-hint":
                if body.get("user_id") is None or body.get("anomaly_id") is None:
                    raise ValueError("Нужны user_id и anomaly_id.")
                self.respond_json(unlock_hidden_hint(int(body["user_id"]), int(body["anomaly_id"])))
                return
            if self.path == "/api/details/companion-accept":
                if body.get("user_id") is None or body.get("anomaly_id") is None:
                    raise ValueError("Нужны user_id и anomaly_id.")
                self.respond_json(accept_companion_offer(int(body["user_id"]), int(body["anomaly_id"])))
                return
            if self.path == "/api/details/companion-decline":
                if body.get("user_id") is None or body.get("anomaly_id") is None:
                    raise ValueError("Нужны user_id и anomaly_id.")
                self.respond_json(decline_companion_offer(int(body["user_id"]), int(body["anomaly_id"])))
                return
            if self.path == "/api/details/finish":
                if body.get("user_id") is None or body.get("anomaly_id") is None:
                    raise ValueError("Нужны user_id и anomaly_id.")
                self.respond_json(finish_research(int(body["user_id"]), int(body["anomaly_id"])))
                return
            if self.path == "/api/game/finish-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(prepare_finish_turn(int(body["user_id"])))
                return
            if self.path == "/api/game/finish-turn":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(finish_turn_for_user(int(body["user_id"])))
                return
            if self.path == "/api/game/train-ticket":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(reset_train_timer(int(body["user_id"])))
                return
            if self.path == "/api/game/violin-steal":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(steal_violin(int(body["user_id"])))
                return
            if self.path == "/api/game/train-pause":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(set_train_timer_paused(int(body["user_id"]), bool(body.get("paused"))))
                return
            if self.path == "/api/game/flee":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(flee_from_work(int(body["user_id"])))
                return
            if self.path == "/api/game/surrender":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                session_profile = get_session_profile(self)
                if not session_profile or int(session_profile.get("id") or 0) != int(body["user_id"]):
                    raise ValueError("Нельзя завершить игру за другого игрока.")
                self.respond_json(surrender_player(int(body["user_id"])))
                return
            if self.path == "/api/game/d20-roll":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(roll_d20_curse(int(body["user_id"])))
                return
            if self.path == "/api/game/crimson-bite":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                target_id = body.get("target_id")
                self.respond_json(resolve_crimson_bite(
                    int(body["user_id"]),
                    int(target_id) if target_id not in (None, "") else None,
                ))
                return
            if self.path == "/api/game/upgrade-stat":
                if body.get("user_id") is None or not body.get("stat_key"):
                    raise ValueError("Нужны user_id и stat_key.")
                self.respond_json(upgrade_player_stat(int(body["user_id"]), body.get("stat_key")))
                return
            if self.path == "/api/game/consume-ilvetal-notice":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                anomaly_id = body.get("anomaly_id")
                self.respond_json(
                    consume_ilvetal_notice(
                        int(body["user_id"]),
                        int(anomaly_id) if anomaly_id is not None else None,
                    )
                )
                return
            if self.path == "/api/game/consume-utilizer-notice":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(consume_utilizer_notice(int(body["user_id"])))
                return
            if self.path == "/api/game/consume-cheaptrick-notice":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                anomaly_id = body.get("anomaly_id")
                self.respond_json(
                    consume_cheaptrick_notice(
                        int(body["user_id"]),
                        int(anomaly_id) if anomaly_id is not None else None,
                    )
                )
                return
            if self.path == "/api/game/resolve-cheaptrick-fatal":
                if body.get("user_id") is None or body.get("anomaly_id") is None:
                    raise ValueError("Нужны user_id и anomaly_id.")
                self.respond_json(resolve_cheaptrick_fatal(int(body["user_id"]), int(body["anomaly_id"])))
                return
            if self.path == "/api/game/sovuh-zombie-action":
                if body.get("user_id") is None or body.get("anomaly_id") is None or not body.get("action"):
                    raise ValueError("Нужны user_id, anomaly_id и action.")
                self.respond_json(
                    resolve_sovuh_zombie_action(
                        int(body["user_id"]),
                        int(body["anomaly_id"]),
                        body.get("action"),
                    )
                )
                return
            if self.path == "/api/game/predator-action":
                if body.get("user_id") is None or body.get("anomaly_id") is None or not body.get("action"):
                    raise ValueError("Нужны user_id, anomaly_id и action.")
                self.respond_json(
                    resolve_predator_action(
                        int(body["user_id"]),
                        int(body["anomaly_id"]),
                        body.get("action"),
                        body.get("speech", ""),
                    )
                )
                return
            if self.path == "/api/game/puppy-action":
                if body.get("user_id") is None or body.get("anomaly_id") is None or not body.get("action"):
                    raise ValueError("Нужны user_id, anomaly_id и action.")
                self.respond_json(
                    resolve_puppy_action(
                        int(body["user_id"]),
                        int(body["anomaly_id"]),
                        body.get("action"),
                        body.get("touched", False),
                    )
                )
                return
            if self.path == "/api/game/contract-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(
                    get_contract_offer_preview(
                        int(body["user_id"]),
                        int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                    )
                )
                return
            if self.path == "/api/game/contract-apply":
                if body.get("user_id") is None or body.get("target_id") is None:
                    raise ValueError("Нужны user_id и target_id.")
                self.respond_json(apply_contract_target(int(body["user_id"]), int(body["target_id"])))
                return
            if self.path == "/api/game/contract-decline":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(decline_contract_offer(int(body["user_id"])))
                return
            if self.path == "/api/game/contract-respond":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(respond_contract_warning(int(body["user_id"]), bool(body.get("pay"))))
                return
            if self.path == "/api/game/contract-summary-ack":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(
                    consume_contract_summary(
                        int(body["user_id"]),
                        int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                    )
                )
                return
            if self.path == "/api/game/stat-conversion-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(
                    get_stat_conversion_preview(
                        int(body["user_id"]),
                        int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                    )
                )
                return
            if self.path == "/api/game/stat-conversion-apply":
                if body.get("user_id") is None or body.get("stat_key") is None:
                    raise ValueError("Нужны user_id и stat_key.")
                self.respond_json(apply_stat_conversion(int(body["user_id"]), body["stat_key"]))
                return
            if self.path == "/api/game/stat-conversion-decline":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(decline_stat_conversion(int(body["user_id"])))
                return
            if self.path == "/api/game/death-shield-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(
                    get_death_shield_offer_preview(
                        int(body["user_id"]),
                        int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                    )
                )
                return
            if self.path == "/api/game/death-shield-apply":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(apply_death_shield_offer(int(body["user_id"])))
                return
            if self.path == "/api/game/death-shield-decline":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(decline_death_shield_offer(int(body["user_id"])))
                return
            if self.path == "/api/game/altar-offering-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(
                    get_altar_offering_preview(
                        int(body["user_id"]),
                        int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                    )
                )
                return
            if self.path == "/api/game/altar-offering-apply":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(apply_altar_offering(int(body["user_id"])))
                return
            if self.path == "/api/game/devil-deal-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_devil_deal_preview(
                    int(body["user_id"]),
                    int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                ))
                return
            if self.path == "/api/game/devil-deal-resolve":
                if body.get("user_id") is None or body.get("accept") is None:
                    raise ValueError("Нужны user_id и accept.")
                self.respond_json(resolve_devil_deal(int(body["user_id"]), bool(body["accept"])))
                return
            if self.path == "/api/game/free-stat-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_free_stat_preview(
                    int(body["user_id"]),
                    int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                ))
                return
            if self.path == "/api/game/free-stat-apply":
                if body.get("user_id") is None or not body.get("stat_key"):
                    raise ValueError("Нужны user_id и stat_key.")
                self.respond_json(apply_free_stat_choice(int(body["user_id"]), body["stat_key"]))
                return
            if self.path == "/api/game/moon-eye-start":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(start_moon_eye_game(
                    int(body["user_id"]),
                    int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                ))
                return
            if self.path == "/api/game/emoji-glasses-start":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(start_emoji_glasses_game(
                    int(body["user_id"]),
                    int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                ))
                return
            if self.path == "/api/game/emoji-glasses-resolve":
                if body.get("user_id") is None or body.get("challenge_id") is None:
                    raise ValueError("Нужны user_id и challenge_id.")
                self.respond_json(resolve_emoji_glasses_game(
                    int(body["user_id"]), body["challenge_id"], bool(body.get("success"))
                ))
                return
            if self.path == "/api/game/sea-monster-start":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(start_sea_monster_game(
                    int(body["user_id"]),
                    int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                ))
                return
            if self.path == "/api/game/sea-monster-resolve":
                if body.get("user_id") is None or body.get("challenge_id") is None:
                    raise ValueError("Нужны user_id и challenge_id.")
                self.respond_json(resolve_sea_monster_round(
                    int(body["user_id"]), body["challenge_id"], bool(body.get("success"))
                ))
                return
            if self.path == "/api/game/moon-eye-resolve":
                if body.get("user_id") is None or body.get("challenge_id") is None or body.get("round_index") is None:
                    raise ValueError("Нужны user_id, challenge_id и round_index.")
                self.respond_json(resolve_moon_eye_game(
                    int(body["user_id"]), body["challenge_id"], int(body["round_index"]), body.get("answer")
                ))
                return
            if self.path == "/api/game/alastor-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(
                    get_alastor_deal_preview(
                        int(body["user_id"]),
                        int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                    )
                )
                return
            if self.path == "/api/game/alastor-apply":
                if body.get("user_id") is None or body.get("choice") is None:
                    raise ValueError("Нужны user_id и choice.")
                self.respond_json(apply_alastor_deal_choice(int(body["user_id"]), body["choice"]))
                return
            if self.path == "/api/game/alastor-task-ack":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(
                    resolve_alastor_task_prompt(
                        int(body["user_id"]),
                        int(body["anomaly_id"]) if body.get("anomaly_id") not in (None, "") else _current_work_anomaly_id(int(body["user_id"])),
                    )
                )
                return
            if self.path == "/api/game/alastor-final-ack":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(resolve_alastor_final_task(int(body["user_id"])))
                return
            if self.path == "/api/game/choose-bonus-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(
                    get_choose_bonus_preview(
                        int(body["user_id"]),
                        int(body["anomaly_id"]) if body.get("anomaly_id") is not None else None,
                    )
                )
                return
            if self.path == "/api/game/choose-bonus-apply":
                if body.get("user_id") is None or body.get("action_key") is None:
                    raise ValueError("Нужны user_id и action_key.")
                self.respond_json(apply_choose_bonus_action(int(body["user_id"]), body["action_key"]))
                return
            if self.path == "/api/game/use-item":
                if body.get("user_id") is None or body.get("item_id") is None:
                    raise ValueError("Нужны user_id и item_id.")
                self.respond_json(use_inventory_item(int(body["user_id"]), int(body["item_id"])))
                return
            if self.path == "/api/game/doomsday-vn-complete":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(complete_doomsday_vn(int(body["user_id"])))
                return
            if self.path == "/api/game/clay-transfer":
                if body.get("user_id") is None or body.get("target_id") is None:
                    raise ValueError("Нужны user_id и target_id.")
                self.respond_json(transfer_clay_statue(int(body["user_id"]), int(body["target_id"])))
                return
            if self.path == "/api/game/special-reset-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_reset_action_preview(int(body["user_id"])))
                return
            if self.path == "/api/game/special-reset-apply":
                if body.get("user_id") is None or body.get("target_id") is None:
                    raise ValueError("Нужны user_id и target_id.")
                self.respond_json(apply_reset_action(int(body["user_id"]), int(body["target_id"])))
                return
            if self.path == "/api/game/anomaly68-donation-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_anomaly68_donation_preview(int(body["user_id"])))
                return
            if self.path == "/api/game/pandora-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_pandora_box_preview(
                    int(body["user_id"]), int(body.get("anomaly_id") or 113)
                ))
                return
            if self.path == "/api/game/pandora-choose":
                if body.get("user_id") is None or body.get("item_id") is None:
                    raise ValueError("Нужны user_id и item_id.")
                self.respond_json(choose_pandora_box_item(
                    int(body["user_id"]), int(body["item_id"]), int(body.get("anomaly_id") or 113)
                ))
                return
            if self.path == "/api/game/portal116-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_portal116_preview(
                    int(body["user_id"]), int(body.get("anomaly_id") or 116)
                ))
                return
            if self.path == "/api/game/portal116-action":
                if body.get("user_id") is None or not body.get("action"):
                    raise ValueError("Нужны user_id и action.")
                self.respond_json(resolve_portal116_action(
                    int(body["user_id"]), body["action"], int(body.get("anomaly_id") or 116)
                ))
                return
            if self.path == "/api/game/rift135-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_global_rift_preview(
                    int(body["user_id"]), int(body.get("anomaly_id") or 135)
                ))
                return
            if self.path == "/api/game/rift135-action":
                if body.get("user_id") is None or not body.get("action") or body.get("slot") is None:
                    raise ValueError("Нужны user_id, action и slot.")
                self.respond_json(resolve_global_rift_action(
                    int(body["user_id"]), body["action"], int(body["slot"]),
                    int(body.get("anomaly_id") or 135),
                ))
                return
            if self.path == "/api/game/dice120-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_dice120_preview(
                    int(body["user_id"]), int(body.get("anomaly_id") or 120)
                ))
                return
            if self.path == "/api/game/dice120-choose":
                if body.get("user_id") is None or not body.get("choice"):
                    raise ValueError("Нужны user_id и choice.")
                self.respond_json(choose_dice120(
                    int(body["user_id"]), body["choice"], int(body.get("anomaly_id") or 120)
                ))
                return
            if self.path == "/api/game/pet122-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_pet122_preview(
                    int(body["user_id"]), int(body.get("anomaly_id") or 122)
                ))
                return
            if self.path == "/api/game/pet122-action":
                if body.get("user_id") is None or not body.get("action"):
                    raise ValueError("Нужны user_id и action.")
                self.respond_json(resolve_pet122_action(
                    int(body["user_id"]), body["action"], int(body.get("anomaly_id") or 122)
                ))
                return
            if self.path == "/api/game/gish125-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_gish125_feed_preview(
                    int(body["user_id"]), int(body.get("anomaly_id") or 125)
                ))
                return
            if self.path == "/api/game/gish125-feed":
                if body.get("user_id") is None or body.get("slot") is None:
                    raise ValueError("Нужны user_id и slot.")
                self.respond_json(feed_gish125_item(
                    int(body["user_id"]), int(body["slot"]), int(body.get("anomaly_id") or 125)
                ))
                return
            if self.path == "/api/game/bloodbot133-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_bloodbot133_preview(
                    int(body["user_id"]), int(body.get("anomaly_id") or 133)
                ))
                return
            if self.path == "/api/game/bloodbot133-donate":
                if body.get("user_id") is None or body.get("amount") is None:
                    raise ValueError("Нужны user_id и amount.")
                self.respond_json(donate_bloodbot133_hp(
                    int(body["user_id"]), int(body["amount"]), int(body.get("anomaly_id") or 133)
                ))
                return
            if self.path == "/api/game/anomaly68-donate":
                if body.get("user_id") is None or body.get("slot") is None:
                    raise ValueError("Нужны user_id и slot.")
                self.respond_json(donate_anomaly68_item(int(body["user_id"]), int(body["slot"])))
                return
            if self.path == "/api/game/instrument-preview":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json(get_instrument_choice_preview(int(body["user_id"]), int(body.get("anomaly_id") or 106)))
                return
            if self.path == "/api/game/instrument-choose":
                if body.get("user_id") is None or not body.get("choice"):
                    raise ValueError("Нужны user_id и choice.")
                self.respond_json(resolve_instrument_choice(int(body["user_id"]), int(body.get("anomaly_id") or 106), body["choice"]))
                return
            if self.path == "/api/game/tenna-start":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json({"tenna_game": start_tenna_game(int(body["user_id"]), int(body.get("anomaly_id") or 104))})
                return
            if self.path == "/api/game/tenna-intro-complete":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json({"tenna_game": tenna_intro_complete(int(body["user_id"]))})
                return
            if self.path == "/api/game/tenna-pick":
                if body.get("user_id") is None or body.get("category") is None or body.get("points") is None:
                    raise ValueError("Нужны user_id, category и points.")
                self.respond_json({"tenna_game": tenna_pick(int(body["user_id"]), body["category"], int(body["points"]))})
                return
            if self.path == "/api/game/tenna-answer":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json({"tenna_game": tenna_answer(int(body["user_id"]), body.get("answer", ""))})
                return
            if self.path == "/api/game/tenna-close":
                if body.get("user_id") is None:
                    raise ValueError("Нужен user_id.")
                self.respond_json({"tenna_game": tenna_close(int(body["user_id"]))})
                return
            if self.path == "/api/game/po3-access":
                if body.get("user_id") is None: raise ValueError("Нужен user_id.")
                self.respond_json({"po3_event": po3_accept_access(int(body["user_id"]), body.get("revision"))})
                return
            if self.path == "/api/game/po3-state":
                if body.get("user_id") is None: raise ValueError("Нужен user_id.")
                self.respond_json({"po3_event": _po3_public(_po3_session_for_user(int(body["user_id"])), int(body["user_id"]))})
                return
            if self.path == "/api/game/po3-begin":
                if body.get("user_id") is None: raise ValueError("Нужен user_id.")
                self.respond_json({"po3_event": po3_begin_queue(int(body["user_id"]), body.get("revision"))})
                return
            if self.path == "/api/game/po3-choose":
                if body.get("user_id") is None or body.get("choice") is None: raise ValueError("Нужны user_id и choice.")
                self.respond_json({"po3_event": po3_choose_trial(int(body["user_id"]), int(body["choice"]), body.get("revision"))})
                return
            if self.path == "/api/game/po3-answer":
                if body.get("user_id") is None or body.get("answer") is None: raise ValueError("Нужны user_id и answer.")
                self.respond_json({"po3_event": po3_answer(int(body["user_id"]), body["answer"], body.get("revision"))})
                return
            if self.path == "/api/game/po3-failure-continue":
                if body.get("user_id") is None: raise ValueError("Нужен user_id.")
                self.respond_json({"po3_event": po3_continue_after_failure(int(body["user_id"]), body.get("revision"))})
                return
            if self.path == "/api/game/po3-results-next":
                if body.get("user_id") is None: raise ValueError("Нужен user_id.")
                self.respond_json(po3_results_next(int(body["user_id"]), body.get("revision")))
                return
            if self.path == "/api/game/po3-ack":
                if body.get("user_id") is None: raise ValueError("Нужен user_id.")
                self.respond_json({"po3_event": po3_ack_results(int(body["user_id"]))})
                return
            if self.path == "/api/admin/action":
                if not debug_mode_enabled():
                    raise ValueError("Режим отладки отключён.")
                if body.get("user_id") is None or not body.get("action"):
                    raise ValueError("Нужны user_id и action.")
                self.respond_json(admin_apply_action(int(body["user_id"]), body.get("action"), body.get("value")))
                return
            self.respond_error(HTTPStatus.NOT_FOUND, "РќРµ РЅР°Р№РґРµРЅРѕ.")
        except ValueError as exc:
            self.respond_error(HTTPStatus.BAD_REQUEST, str(exc))

    def serve_static(self, filename):
        file_path = ROOT / unquote(filename)
        if not file_path.exists():
            self.respond_error(HTTPStatus.NOT_FOUND, "Р¤Р°Р№Р» РЅРµ РЅР°Р№РґРµРЅ.")
            return
        content_type = "text/html; charset=utf-8"
        if file_path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif file_path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        elif file_path.suffix == ".png":
            content_type = "image/png"
        elif file_path.suffix == ".webp":
            content_type = "image/webp"
        elif file_path.suffix.lower() in {".jpg", ".jpeg"}:
            content_type = "image/jpeg"
        elif file_path.suffix == ".mp3":
            content_type = "audio/mpeg"
        elif file_path.suffix == ".wav":
            content_type = "audio/wav"
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def respond_json(self, payload, status=HTTPStatus.OK, headers=None):
        # Discord snowflakes are larger than JavaScript's safe integer range.
        # Sending them as JSON numbers changes their last digits in a browser,
        # so legitimate actions can look as if another player sent them.
        def preserve_identifiers(value, parent_key=""):
            key = str(parent_key or "").lower()
            identifier_value = key == "id" or key.endswith("_id")
            identifier_list = key.endswith("_ids") or key in {
                "turn_order", "final_player_ids", "active_player_ids",
                "alive_ids", "dead_ids", "queue",
            }
            if isinstance(value, dict):
                return {name: preserve_identifiers(item, name) for name, item in value.items()}
            if isinstance(value, list):
                if identifier_list:
                    return [
                        str(item) if isinstance(item, int) and not isinstance(item, bool)
                        else preserve_identifiers(item)
                        for item in value
                    ]
                return [preserve_identifiers(item) for item in value]
            if identifier_value and isinstance(value, int) and not isinstance(value, bool):
                return str(value)
            return value

        raw = json.dumps(preserve_identifiers(payload), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        for key, value in (headers or {}).items():
            self.send_header(str(key), str(value))
        self.end_headers()
        self.wfile.write(raw)

    def respond_error(self, status, message):
        self.respond_json({"error": message}, status=status)

    def log_message(self, fmt, *args):
        return


def main():
    ensure_web_db()
    ensure_runtime_tables()
    # An interrupted VN/show no longer exists after a process restart. Resume
    # the persisted train deadline instead of leaving it paused indefinitely.
    paused_at = float(_safe_global_value("TrainPausedAt", 0) or 0)
    if paused_at > 0:
        deadline = float(_safe_global_value("TrainDeadlineAt", 0) or 0)
        if deadline > 0:
            core.set_global_value(DB_PATH, "TrainDeadlineAt", deadline + max(0, time.time() - paused_at))
        core.set_global_value(DB_PATH, "TrainPausedAt", 0)
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"Serving on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
