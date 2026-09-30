from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional


DEFAULT_TOTAL_DAYS = 15
EFFECT_SLOTS = 20
EFFECT_COLUMNS = [f"effect{i}" for i in range(1, EFFECT_SLOTS + 1)]
TYPE_MODIFIER_ITEM_ID = 4
CLAY_ITEM_ID = 5
DRUMS_ID = 30
DRUMS_EVER_FLAG = "DrumsEverHeld"
HEART_ID = 32
APPLE_FLAG = "apple_hp_boost"
TOK_EXTRA_MAX = "apple_extra_max"
TOK_EXTRA_CUR = "apple_extra_cur"
COMP11_TOK = "Comp11Left"
COMP13_TOKEN = "Comp13Applied"
TSD_FLAG = "TimeShiftDrug"
TSD_ACC_TOK = "TSD_ACC"
HOTDOG_FLAG = "LovecraftHotDog"
HOTDOG_PEND_PREFIX = "HotDogPending"
SALA_SHIELD_TOK = "SALA_SHIELD_CUR"
SALA_MULT_TOK = "SALA_MULT"
RING_RED_KING_FLAG = "RingRedKingOn"
HEART_ATTACK_DEATH_REASON = "Причина смерти: передозировка анксиолитиком и остановка сердца"
_POST_DAMAGE_HOOK: Optional[Callable[[Path | str, int, dict], Optional[dict]]] = None
_DAY_TRANSITION_HOOK: Optional[Callable[[Path | str, int, int], Optional[dict]]] = None


def set_post_damage_hook(callback: Optional[Callable[[Path | str, int, dict], Optional[dict]]]) -> None:
    global _POST_DAMAGE_HOOK
    _POST_DAMAGE_HOOK = callback


def set_day_transition_hook(callback: Optional[Callable[[Path | str, int, int], Optional[dict]]]) -> None:
    global _DAY_TRANSITION_HOOK
    _DAY_TRANSITION_HOOK = callback

KNOWN_GLOBAL_KEYS = sorted(
    {
        "A69_CNT", "A69_HP", "A69_SP", "ActiveWorker", "AlastorFledPlayer", "AlastorMood",
        "AlastorPrey", "AlastorTask", "AlephWasStudied", "BersWasMet", "BlockEverything",
        "CLAY_ABSORB", "CLAY_BYPASS", "CLAY_LAST_TRANSFER_DAY", "CRIMSON_DONE", "CRIMSON_PENDING",
        "CURSE_SUPPRESS", "CatGiveReward", "CatOnStoveEncountered", "CheapTrickNeedHost",
        "ChosenAnomalyNumber", "ClayAbsorbed", "ClayHolder", "ClayLastTransferDay", "CompTaken",
        "CompanionDoomActive", "CompanionDoomStartDay", "CompanionDoomVictim", "CurrentDay",
        "DeathsToday", "DogTouched", "ForcedPlayer", "GuessedRight", "ICICLE8_START_DAY",
        "LastWorkResult", "NoEscape", "NonAnomalyClass", "PisosCurseCount", "SiphIsSad",
        "SiphPunishment", "TSD_BYPASS", "TrainChannelId", "TrainPlayer", "UnderCurse2",
        "UnderCurse3", "WorkBase10", "WormActive", "WormStartDay", "WormVictim", "X125_ACTIVE",
        "alephsummoned", "altarismet", "babymonster", "bitecount", "check_work",
        "cinderplagueupgrade", "currentgoal", "d20", "first_work_anomalytype",
        "first_work_class", "first_work_type", "forcedroll", "idolcurse", "langustwasmet",
        "skipday", "xprotocol", "GameActive", "AlastorSuccessCount", "BLOODBOT_ACTIVE",
        "BLOODBOT_DEAD", "BLOODBOT_HP", "CURSE_DEATH_SEEN", "CURSE_EFFECT", "CURSE_ENABLED",
        "CURSE_OWNER_ID", "CURSE_REENTRANT", "CURSE_TRIGGER", "HIT_BIDDER", "HIT_EXEC_DAY",
        "HIT_PAYERS", "HIT_PENDING", "HIT_RESPONDED", "HIT_SUMMARY", "HIT_SUMMARY_SEEN",
        "HIT_TARGET", "HOTDOG_FLAG", "RIFT_STASH_ITEM_ID",
        "SYNTH_WARP", "VYJ_CNT", "ViolinDamage", "ViolinIsTaken", "ViolinOwnerPid",
        "ViolinOwnerStreak", "ViolinSteals", "ViolinTriggeredToday", "WORKBASE10_FLAG",
        "X125_DONE", "X125_EVENT_FIRED", "X125_EVENT_ID", "X125_EVENTS", "X125_RUN_ID",
        "X125_SPECIAL_EVENT_DAY", "X125_SPECIAL_EVENT_ID", "KLIPOTA_EVENT_ID", "KLIPOTA_EVENTS",
        "X125_OWNER_ID", "X125_ANOMALY_OWNER_ID", "X125_BATTLE", "X125_RUN_TOKEN",
        "CURSE_SUPPRESS", "ClayAbsorbed", "ClayHolder",
        "ClayLastTransferDay", "TrainDeadlineUserId", "TrainDeadlineAt", "TrainPausedAt",
        "TrainEventId", "TrainEventUserId", "TrainEventAt", "TrainEventDamage", "TrainEventDead",
        "BrassSphereOwner", "BrassSphereNeedsActivate", "BrassSphereEventId", "BrassSphereEventUserId",
    }
)


def _connect(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row: sqlite3.Row | None) -> Optional[dict]:
    return {key: row[key] for key in row.keys()} if row else None


def init_core_schema(db_path: Path | str) -> None:
    with _connect(db_path) as conn:
        columns = {str(row["name"]).strip().lower() for row in conn.execute("PRAGMA table_info(PLAYERS)").fetchall()}
        if "isdead" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN IsDead INTEGER NOT NULL DEFAULT 0")
            columns.add("isdead")
        if "deathreason" not in columns:
            conn.execute("ALTER TABLE PLAYERS ADD COLUMN DEATHREASON TEXT")
            columns.add("deathreason")
        for col in EFFECT_COLUMNS:
            if col.lower() not in columns:
                conn.execute(f"ALTER TABLE PLAYERS ADD COLUMN {col} TEXT")
                columns.add(col.lower())

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS PLAYER_STUDIED_ANOMALIES (
                user_id INTEGER NOT NULL,
                anomaly_id INTEGER NOT NULL,
                created_at REAL NOT NULL DEFAULT (strftime('%s','now')),
                PRIMARY KEY (user_id, anomaly_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS GAME_GLOBALS (
                key TEXT PRIMARY KEY,
                value_text TEXT,
                value_type TEXT NOT NULL DEFAULT 'str',
                updated_at REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS CORE_GAME_STATE (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                status TEXT NOT NULL DEFAULT 'idle',
                total_days INTEGER NOT NULL DEFAULT 15,
                current_day INTEGER NOT NULL DEFAULT 0,
                turn_index INTEGER NOT NULL DEFAULT 0,
                current_turn_user_id INTEGER,
                turn_order_json TEXT NOT NULL DEFAULT '[]',
                started_at REAL,
                finished_at REAL,
                winner_user_id INTEGER,
                last_event_at REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS CORE_TURN_EVENTS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id INTEGER,
                target_user_id INTEGER,
                day_number INTEGER,
                turn_index INTEGER,
                payload_json TEXT,
                created_at REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            INSERT INTO CORE_GAME_STATE (id, status, total_days, current_day, turn_index, current_turn_user_id, turn_order_json)
            VALUES (1, 'idle', ?, 0, 0, NULL, '[]')
            ON CONFLICT(id) DO NOTHING
            """,
            (DEFAULT_TOTAL_DAYS,),
        )
        conn.commit()


def set_global_value(db_path: Path | str, key: str, value: Any) -> None:
    if isinstance(value, bool):
        value_type = "bool"
        value_text = "1" if value else "0"
    elif isinstance(value, int):
        value_type = "int"
        value_text = str(value)
    elif isinstance(value, float):
        value_type = "float"
        value_text = repr(value)
    elif isinstance(value, (dict, list)):
        value_type = "json"
        value_text = json.dumps(value, ensure_ascii=False)
    elif value is None:
        value_type = "null"
        value_text = ""
    else:
        value_type = "str"
        value_text = str(value)

    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO GAME_GLOBALS (key, value_text, value_type, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value_text = excluded.value_text, value_type = excluded.value_type, updated_at = excluded.updated_at
            """,
            (key, value_text, value_type, time.time()),
        )
        conn.commit()


def get_global_value(db_path: Path | str, key: str, default: Any = None) -> Any:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT value_text, value_type FROM GAME_GLOBALS WHERE key = ?", (key,)).fetchone()
    if not row:
        return default
    value_text = row["value_text"]
    value_type = row["value_type"]
    if value_type == "bool":
        return value_text == "1"
    if value_type == "int":
        return int(value_text or 0)
    if value_type == "float":
        return float(value_text or 0)
    if value_type == "json":
        return json.loads(value_text or "null")
    if value_type == "null":
        return None
    return value_text


def list_globals(db_path: Path | str) -> dict:
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT key FROM GAME_GLOBALS ORDER BY key").fetchall()
    return {row["key"]: get_global_value(db_path, row["key"]) for row in rows}


def clear_globals(db_path: Path | str) -> None:
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM GAME_GLOBALS")
        conn.commit()


def record_turn_event(db_path: Path | str, event_type: str, *, user_id: int | None = None, target_user_id: int | None = None, day_number: int | None = None, turn_index: int | None = None, payload: dict | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO CORE_TURN_EVENTS (event_type, user_id, target_user_id, day_number, turn_index, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (event_type, user_id, target_user_id, day_number, turn_index, json.dumps(payload or {}, ensure_ascii=False), time.time()),
        )
        conn.execute("UPDATE CORE_GAME_STATE SET last_event_at = ? WHERE id = 1", (time.time(),))
        conn.commit()


def get_game_state(db_path: Path | str) -> dict:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM CORE_GAME_STATE WHERE id = 1").fetchone()
    data = _row_to_dict(row) or {}
    data["turn_order"] = json.loads(data.pop("turn_order_json", "[]") or "[]")
    return data


def reset_players_for_new_game(db_path: Path | str, player_ids: Iterable[int]) -> None:
    player_ids = [int(pid) for pid in player_ids]
    if not player_ids:
        return
    reset_sql = """
        UPDATE PLAYERS
        SET HP = 100,
            MAXHP = 100,
            SP = 200,
            MAXSP = 200,
            INVSLOT1 = 0,
            SLOT1AMOUNT = 0,
            INVSLOT2 = 0,
            SLOT2AMOUNT = 0,
            COMPSLOT = 0,
            RP = 0,
            CP = 0,
            RT = 0,
            STAT1 = 1,
            STAT2 = 1,
            STAT3 = 1,
            STAT4 = 1,
            PENALTY = 0,
            KLIPOTA = 0,
            BONUS = 0,
            IsDead = 0,
            DEATHREASON = NULL
    """
    for col in EFFECT_COLUMNS:
        reset_sql += f", {col} = NULL"
    placeholders = ",".join("?" for _ in player_ids)
    reset_sql += f" WHERE ID IN ({placeholders})"
    with _connect(db_path) as conn:
        conn.execute(reset_sql, tuple(player_ids))
        conn.commit()


def add_player_effect(db_path: Path | str, player_id: int, effect_name: str) -> dict:
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT COALESCE(COMPSLOT, 0) AS COMPSLOT, COALESCE(HP, 0) AS HP, {', '.join(EFFECT_COLUMNS)} FROM PLAYERS WHERE ID = ?",
            (int(player_id),),
        ).fetchone()
        if not row:
            return {"ok": False, "reason": "player_not_found"}
        values = [row[col] for col in EFFECT_COLUMNS]
        if effect_name in values:
            return {"ok": True, "slot": values.index(effect_name) + 1, "duplicate": True}
        if _safe_int(row["COMPSLOT"]) == 6:
            negative_effects = {
                "FleeIsDeath", "SparingCurse", "PisosCurse", "CinderPlague", "UnderCurse2",
                "UnderCurse3", "witness_curse", "BlockedPhoto", "BlockedDescription",
                "BlockedHint", "NoResult", "CrimsonVirus", "skibidi",
            }
            base_key = str(effect_name or "").split("=", 1)[0].strip()
            hp_cost = 20 if (base_key.isdigit() or base_key in negative_effects) else 0
            if hp_cost > 0:
                new_hp = max(0, _safe_int(row["HP"]) - hp_cost)
                conn.execute("UPDATE PLAYERS SET HP = ? WHERE ID = ?", (int(new_hp), int(player_id)))
                conn.commit()
                if new_hp <= 0:
                    set_player_dead(db_path, int(player_id), reason="Сотрудник погиб, пока Кот висельник поглощал чужеродное воздействие.")
                    return {"ok": True, "absorbed_by_companion": True, "hp_cost": hp_cost, "dead": True}
            return {"ok": True, "absorbed_by_companion": True, "hp_cost": hp_cost, "dead": False}
        try:
            empty_index = next(i for i, value in enumerate(values) if value in (None, "", "0"))
        except StopIteration:
            return {"ok": False, "reason": "no_free_slot"}
        conn.execute(f"UPDATE PLAYERS SET effect{empty_index + 1} = ? WHERE ID = ?", (effect_name, int(player_id)))
        conn.commit()
    return {"ok": True, "slot": empty_index + 1, "duplicate": False}


def remove_player_effect(db_path: Path | str, player_id: int, effect_name: str) -> bool:
    with _connect(db_path) as conn:
        row = conn.execute(f"SELECT {', '.join(EFFECT_COLUMNS)} FROM PLAYERS WHERE ID = ?", (int(player_id),)).fetchone()
        if not row:
            return False
        for idx, col in enumerate(EFFECT_COLUMNS, start=1):
            if row[col] == effect_name:
                conn.execute(f"UPDATE PLAYERS SET effect{idx} = NULL WHERE ID = ?", (int(player_id),))
                conn.commit()
                return True
    return False


def list_player_effects(db_path: Path | str, player_id: int) -> List[str]:
    with _connect(db_path) as conn:
        row = conn.execute(f"SELECT {', '.join(EFFECT_COLUMNS)} FROM PLAYERS WHERE ID = ?", (int(player_id),)).fetchone()
    if not row:
        return []
    return [row[col] for col in EFFECT_COLUMNS if row[col] not in (None, "", "0")]


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _has_item(conn: sqlite3.Connection, player_id: int, item_id: int) -> bool:
    row = conn.execute(
        """
        SELECT COALESCE(INVSLOT1, 0) AS INVSLOT1, COALESCE(SLOT1AMOUNT, 0) AS SLOT1AMOUNT,
               COALESCE(INVSLOT2, 0) AS INVSLOT2, COALESCE(SLOT2AMOUNT, 0) AS SLOT2AMOUNT
        FROM PLAYERS WHERE ID = ?
        """,
        (int(player_id),),
    ).fetchone()
    if not row:
        return False
    return (
        (_safe_int(row["INVSLOT1"]) == int(item_id) and _safe_int(row["SLOT1AMOUNT"], 1) > 0)
        or (_safe_int(row["INVSLOT2"]) == int(item_id) and _safe_int(row["SLOT2AMOUNT"], 1) > 0)
    )


def _remove_one_item(conn: sqlite3.Connection, player_id: int, item_id: int) -> bool:
    row = conn.execute(
        """
        SELECT COALESCE(INVSLOT1, 0) AS INVSLOT1, COALESCE(SLOT1AMOUNT, 0) AS SLOT1AMOUNT,
               COALESCE(INVSLOT2, 0) AS INVSLOT2, COALESCE(SLOT2AMOUNT, 0) AS SLOT2AMOUNT
        FROM PLAYERS WHERE ID = ?
        """,
        (int(player_id),),
    ).fetchone()
    if not row:
        return False
    if _safe_int(row["INVSLOT1"]) == int(item_id) and _safe_int(row["SLOT1AMOUNT"], 1) > 0:
        amount = _safe_int(row["SLOT1AMOUNT"], 1) - 1
        if amount > 0:
            conn.execute("UPDATE PLAYERS SET SLOT1AMOUNT = ? WHERE ID = ?", (amount, int(player_id)))
        else:
            conn.execute("UPDATE PLAYERS SET INVSLOT1 = 0, SLOT1AMOUNT = 0 WHERE ID = ?", (int(player_id),))
        return True
    if _safe_int(row["INVSLOT2"]) == int(item_id) and _safe_int(row["SLOT2AMOUNT"], 1) > 0:
        amount = _safe_int(row["SLOT2AMOUNT"], 1) - 1
        if amount > 0:
            conn.execute("UPDATE PLAYERS SET SLOT2AMOUNT = ? WHERE ID = ?", (amount, int(player_id)))
        else:
            conn.execute("UPDATE PLAYERS SET INVSLOT2 = 0, SLOT2AMOUNT = 0 WHERE ID = ?", (int(player_id),))
        return True
    return False


def _player_effects_from_row(row: sqlite3.Row) -> List[str]:
    return [str(row[col]) for col in EFFECT_COLUMNS if row[col] not in (None, "", "0")]


def _transfer_drums_on_heart_attack(conn: sqlite3.Connection, owner_id: int) -> dict:
    """Transfer the drums to the next living player who never held them."""
    owner_id = int(owner_id)
    slots = conn.execute(
        "SELECT COALESCE(INVSLOT1,1), COALESCE(SLOT1AMOUNT,0), COALESCE(INVSLOT2,1), COALESCE(SLOT2AMOUNT,0) FROM PLAYERS WHERE ID = ?",
        (owner_id,),
    ).fetchone()
    if not slots:
        return {"moved": False}
    slot = 1 if int(slots[0] or 0) == DRUMS_ID and int(slots[1] or 0) > 0 else (2 if int(slots[2] or 0) == DRUMS_ID and int(slots[3] or 0) > 0 else 0)
    if not slot:
        return {"moved": False}
    owner = conn.execute("SELECT * FROM PLAYERS WHERE ID = ?", (owner_id,)).fetchone()
    owner_effects = _player_effects_from_row(owner) if owner else []
    if DRUMS_EVER_FLAG not in owner_effects:
        owner_effects.append(DRUMS_EVER_FLAG)
        _save_effects(conn, owner_id, owner_effects)
    state = conn.execute("SELECT COALESCE(turn_order_json,'[]') FROM CORE_GAME_STATE WHERE id = 1").fetchone()
    try:
        order = [int(pid) for pid in json.loads(state[0] if state else "[]")]
    except Exception:
        order = []
    target_id = 0
    if owner_id in order:
        start = order.index(owner_id)
        for offset in range(1, len(order) + 1):
            candidate = int(order[(start + offset) % len(order)])
            if candidate == owner_id:
                continue
            candidate_row = conn.execute("SELECT * FROM PLAYERS WHERE ID = ?", (candidate,)).fetchone()
            if not candidate_row or int(candidate_row["IsDead"] or 0) == 1:
                continue
            if DRUMS_EVER_FLAG in _player_effects_from_row(candidate_row):
                continue
            target_id = candidate
            break
    if slot == 1:
        conn.execute("UPDATE PLAYERS SET INVSLOT1 = 1, SLOT1AMOUNT = 0 WHERE ID = ?", (owner_id,))
    else:
        conn.execute("UPDATE PLAYERS SET INVSLOT2 = 1, SLOT2AMOUNT = 0 WHERE ID = ?", (owner_id,))
    if not target_id:
        return {"moved": True, "burned": True, "from": owner_id}
    target = conn.execute(
        "SELECT COALESCE(INVSLOT1,1), COALESCE(SLOT1AMOUNT,0), COALESCE(INVSLOT2,1), COALESCE(SLOT2AMOUNT,0) FROM PLAYERS WHERE ID = ?",
        (target_id,),
    ).fetchone()
    target_slot = 1 if int(target[0] or 1) in (0, 1) or int(target[1] or 0) <= 0 else 2
    if target_slot == 1:
        conn.execute("UPDATE PLAYERS SET INVSLOT1 = ?, SLOT1AMOUNT = 1 WHERE ID = ?", (DRUMS_ID, target_id))
    else:
        conn.execute("UPDATE PLAYERS SET INVSLOT2 = ?, SLOT2AMOUNT = 1 WHERE ID = ?", (DRUMS_ID, target_id))
    target_row = conn.execute("SELECT * FROM PLAYERS WHERE ID = ?", (target_id,)).fetchone()
    target_effects = _player_effects_from_row(target_row) if target_row else []
    if DRUMS_EVER_FLAG not in target_effects:
        target_effects.append(DRUMS_EVER_FLAG)
        _save_effects(conn, target_id, target_effects)
    return {"moved": True, "from": owner_id, "to": target_id}


def _effect_has(effects: List[str], key: str) -> bool:
    for effect in effects:
        if effect == key or effect.startswith(f"{key}="):
            return True
    return False


def _effect_token_read(effects: List[str], key: str, default: Optional[int] = None) -> Optional[int]:
    prefix = f"{key}="
    for effect in effects:
        if effect.startswith(prefix):
            try:
                return int(effect.split("=", 1)[1])
            except (TypeError, ValueError):
                return default
    return default


def _effect_token_write(effects: List[str], key: str, value: int) -> None:
    prefix = f"{key}="
    effects[:] = [effect for effect in effects if not effect.startswith(prefix)]
    effects.append(f"{key}={int(value)}")


def _effect_remove_prefix(effects: List[str], key: str) -> None:
    prefix = f"{key}="
    effects[:] = [effect for effect in effects if effect != key and not effect.startswith(prefix)]


def _save_effects(conn: sqlite3.Connection, player_id: int, effects: List[str]) -> None:
    normalized = [str(effect) for effect in effects if str(effect).strip()]
    values = normalized[:EFFECT_SLOTS] + [None] * max(0, EFFECT_SLOTS - len(normalized))
    assignments = ", ".join(f"{col} = ?" for col in EFFECT_COLUMNS)
    conn.execute(f"UPDATE PLAYERS SET {assignments} WHERE ID = ?", (*values[:EFFECT_SLOTS], int(player_id)))


def set_player_dead(db_path: Path | str, player_id: int, *, reason: str = "") -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE PLAYERS SET HP = 0, IsDead = 1, DEATHREASON = ? WHERE ID = ?",
            (reason or None, int(player_id)),
        )
        conn.commit()
    try:
        deaths_today = int(get_global_value(db_path, "DeathsToday", 0) or 0)
        set_global_value(db_path, "DeathsToday", deaths_today + 1)
    except Exception:
        pass
    record_turn_event(db_path, "player_dead", user_id=int(player_id), payload={"reason": reason})


def apply_damage(
    db_path: Path | str,
    player_id: int,
    *,
    hp_damage: int = 0,
    sp_damage: int = 0,
    reason: str = "",
    bypass_death_shield: bool = False,
    source_anomaly_id: Optional[int] = None,
) -> dict:
    clay_absorbed = 0
    clay_total_absorbed = 0
    clay_overloaded = False
    with _connect(db_path) as conn:
        row = conn.execute(
            f"""
            SELECT COALESCE(HP,0) AS HP, COALESCE(SP,0) AS SP, COALESCE(MAXHP,100) AS MAXHP, COALESCE(MAXSP,200) AS MAXSP,
                   COALESCE(IsDead,0) AS IsDead, COALESCE(COMPSLOT,0) AS COMPSLOT,
                   COALESCE(INVSLOT1,0) AS INVSLOT1, COALESCE(SLOT1AMOUNT,0) AS SLOT1AMOUNT,
                   COALESCE(INVSLOT2,0) AS INVSLOT2, COALESCE(SLOT2AMOUNT,0) AS SLOT2AMOUNT,
                   {', '.join(EFFECT_COLUMNS)}
            FROM PLAYERS WHERE ID = ?
            """,
            (int(player_id),),
        ).fetchone()
        if not row:
            return {"ok": False, "reason": "player_not_found"}
        original_hp_damage = max(0, _safe_int(hp_damage))
        original_sp_damage = max(0, _safe_int(sp_damage))
        hp_damage = original_hp_damage
        sp_damage = original_sp_damage
        hp = _safe_int(row["HP"])
        sp = _safe_int(row["SP"])
        effects = _player_effects_from_row(row)

        current_anomaly_row = conn.execute(
            "SELECT anomaly_id FROM WORK WHERE user_id = ?",
            (int(player_id),),
        ).fetchone()
        current_anomaly_id = _safe_int(current_anomaly_row["anomaly_id"]) if current_anomaly_row and current_anomaly_row["anomaly_id"] is not None else None
        force_bypass = bool(get_global_value(db_path, "CLAY_BYPASS", 0))

        if not force_bypass and current_anomaly_id == 84:
            hp_damage = 0
            sp_damage = 0

        if _safe_int(row["COMPSLOT"]) == 11 and (hp_damage > 0 or sp_damage > 0):
            left = _effect_token_read(effects, COMP11_TOK, None)
            if isinstance(left, int) and left > 0:
                left = max(0, left - 1)
                hp_damage = 0
                sp_damage = 0
                _effect_token_write(effects, COMP11_TOK, left)
                _save_effects(conn, int(player_id), effects)
                if left == 0:
                    conn.execute("UPDATE PLAYERS SET COMPSLOT = 0 WHERE ID = ?", (int(player_id),))

        clay_holder = _safe_int(get_global_value(db_path, "ClayHolder", 0))
        has_clay_statue = clay_holder == int(player_id) or _has_item(conn, int(player_id), CLAY_ITEM_ID)
        if has_clay_statue and sp_damage > 0 and not force_bypass:
            absorbed = sp_damage
            clay_absorbed = int(absorbed)
            sp_damage = 0
            clay_absorb = _safe_int(get_global_value(db_path, "CLAY_ABSORB", 0))
            total_absorb = clay_absorb + absorbed
            clay_total_absorbed = int(total_absorb)
            set_global_value(db_path, "CLAY_ABSORB", total_absorb)
            if not get_global_value(db_path, "CLAY_LAST_TRANSFER_DAY", 0):
                state_row = conn.execute("SELECT current_day FROM CORE_GAME_STATE WHERE id = 1").fetchone()
                current_day = _safe_int(state_row["current_day"]) if state_row else 1
                set_global_value(db_path, "CLAY_LAST_TRANSFER_DAY", current_day)
            if total_absorb >= 200:
                clay_overloaded = True
                set_global_value(db_path, "CLAY_BYPASS", 1)
                try:
                    sp_damage = 100
                    _remove_one_item(conn, int(player_id), CLAY_ITEM_ID)
                    if clay_holder == int(player_id):
                        set_global_value(db_path, "ClayHolder", 0)
                    set_global_value(db_path, "CLAY_ABSORB", 0)
                finally:
                    set_global_value(db_path, "CLAY_BYPASS", 0)

        if _has_item(conn, int(player_id), TYPE_MODIFIER_ITEM_ID):
            anomaly_type_row = conn.execute(
                """
                SELECT a.TYPE
                FROM WORK w
                JOIN ANOMALY a ON a.ID = w.anomaly_id
                WHERE w.user_id = ?
                """,
                (int(player_id),),
            ).fetchone()
            anomaly_type = _safe_int(anomaly_type_row["TYPE"]) if anomaly_type_row else 0
            if anomaly_type in (2, 4):
                hp_damage = _safe_int(hp_damage * 0.5)
            else:
                hp_damage = _safe_int(hp_damage * 2)

        damage_happened = hp_damage > 0 or sp_damage > 0

        if _effect_has(effects, RING_RED_KING_FLAG) and hp_damage > 0:
            sp_damage += hp_damage
            hp_damage = 0

        has_drums = _has_item(conn, int(player_id), DRUMS_ID)
        if has_drums and (hp_damage > 0 or sp_damage > 0):
            sp_damage += hp_damage
            hp_damage = 0

        apple_active = APPLE_FLAG in effects
        apple_extra_cur = _safe_int(_effect_token_read(effects, TOK_EXTRA_CUR, 0), 0)
        if apple_active and apple_extra_cur > 0 and hp_damage > 0:
            absorbed = min(apple_extra_cur, hp_damage)
            hp_damage -= absorbed
            _effect_token_write(effects, TOK_EXTRA_CUR, apple_extra_cur - absorbed)
            _save_effects(conn, int(player_id), effects)

        sala_shield = _safe_int(_effect_token_read(effects, SALA_SHIELD_TOK, 0), 0)
        if sala_shield > 0 and (hp_damage > 0 or sp_damage > 0):
            remain = sala_shield
            if hp_damage > 0 and remain > 0:
                absorb_hp = min(hp_damage, remain)
                hp_damage -= absorb_hp
                remain -= absorb_hp
            if sp_damage > 0 and remain > 0:
                absorb_sp = min(sp_damage, remain)
                sp_damage -= absorb_sp
                remain -= absorb_sp
            _effect_token_write(effects, SALA_SHIELD_TOK, max(0, remain))
            _save_effects(conn, int(player_id), effects)

        has_heart = _has_item(conn, int(player_id), HEART_ID)
        if has_heart:
            total = int(hp_damage) + 2 * int(sp_damage)
            if total <= sp:
                sp_damage = total
                hp_damage = 0
            else:
                sp_damage = sp
                hp_damage = total - sp

        tsd_active = TSD_FLAG in effects
        tsd_bypass = bool(get_global_value(db_path, "TSD_BYPASS", 0))
        if tsd_active and not tsd_bypass:
            acc = _safe_int(_effect_token_read(effects, TSD_ACC_TOK, 0), 0)
            floor_val = 1 + (acc // 25)
            total_in = max(0, int(hp_damage)) + max(0, int(sp_damage))
            if total_in > 0:
                target = max(1, floor_val)
                if has_heart:
                    sp_take = min(sp, target)
                    hp_take = target - sp_take
                    sp_damage = sp_take
                    hp_damage = hp_take
                else:
                    if hp_damage > 0 and sp_damage > 0:
                        hp_part = round(target * (hp_damage / total_in))
                        sp_part = target - hp_part
                    elif hp_damage > 0:
                        hp_part, sp_part = target, 0
                    else:
                        hp_part, sp_part = 0, target
                    hp_damage = max(0, int(hp_part))
                    sp_damage = max(0, int(sp_part))

        hp = max(hp - int(hp_damage), 0)
        sp = max(sp - int(sp_damage), 0)

        was_dead = int(row["IsDead"] or 0) == 1
        laplace_rescued = bool(
            not was_dead
            and _safe_int(source_anomaly_id, 0) == 67
            and int(hp_damage) > 0
            and hp <= 0
        )
        if laplace_rescued:
            hp = max(1, _safe_int(row["MAXHP"], 100))
        elif _effect_has(effects, HOTDOG_FLAG) and hp <= 0:
            hp = 1
            _effect_remove_prefix(effects, HOTDOG_PEND_PREFIX)
            effects.append("HotDogPending=1")
            _save_effects(conn, int(player_id), effects)

        force_mad_death = _safe_int(get_global_value(db_path, "LAPLACE_FORCE_MAD_DEATH", 0), 0) == int(player_id)
        heart_attack_triggered = False
        heart_attack_dead = False
        drums_transfer = None
        if force_mad_death and sp <= 0:
            hp = 0
        elif (not has_heart) and sp == 0:
            if has_drums:
                drums_transfer = _transfer_drums_on_heart_attack(conn, int(player_id))
            if hp > 1:
                hp = 1
                sp = 50
                heart_attack_triggered = True
            elif hp == 1:
                hp = 0
                heart_attack_triggered = True
                heart_attack_dead = True

        shield_triggered = False
        if not was_dead and hp <= 0 and (not bypass_death_shield) and _effect_has(effects, "death_shield"):
            shield_triggered = True
            hp = 100
            sp = 200
            effects = []
            _save_effects(conn, int(player_id), effects)
            conn.execute(
                "UPDATE PLAYERS SET HP = ?, SP = ?, IsDead = 0, DEATHREASON = NULL WHERE ID = ?",
                (hp, sp, int(player_id)),
            )
            conn.commit()

        is_dead = was_dead or (hp <= 0 and not shield_triggered)
        if is_dead and not was_dead:
            death_reason = HEART_ATTACK_DEATH_REASON if heart_attack_dead else (reason or None)
            conn.execute(
                "UPDATE PLAYERS SET HP = ?, SP = ?, IsDead = 1, DEATHREASON = ? WHERE ID = ?",
                (hp, sp, death_reason, int(player_id)),
            )
        elif not shield_triggered:
            conn.execute(
                "UPDATE PLAYERS SET HP = ?, SP = ?, IsDead = ? WHERE ID = ?",
                (hp, sp, 1 if is_dead else 0, int(player_id)),
            )
        conn.commit()
    record_turn_event(
        db_path,
        "damage_applied",
        user_id=int(player_id),
        payload={
            "hp_damage_in": int(original_hp_damage),
            "sp_damage_in": int(original_sp_damage),
            "hp_damage_final": int(hp_damage),
            "sp_damage_final": int(sp_damage),
            "reason": reason,
            "is_dead": is_dead,
            "shield_triggered": shield_triggered,
            "heart_attack_triggered": heart_attack_triggered,
            "heart_attack_dead": heart_attack_dead,
            "damage_happened": damage_happened,
        },
    )
    if is_dead and not was_dead:
        record_turn_event(
            db_path,
            "player_dead",
            user_id=int(player_id),
            payload={"reason": HEART_ATTACK_DEATH_REASON if heart_attack_dead else reason},
        )
    result = {
        "ok": True,
        "hp": hp,
        "sp": sp,
        "is_dead": is_dead,
        "shield_triggered": shield_triggered,
        "heart_attack_triggered": heart_attack_triggered,
        "heart_attack_dead": heart_attack_dead,
        "drums_transfer": drums_transfer,
        "hp_damage_final": int(hp_damage),
        "sp_damage_final": int(sp_damage),
        "clay_absorbed": int(clay_absorbed),
        "clay_total_absorbed": int(clay_total_absorbed),
        "clay_overloaded": bool(clay_overloaded),
        "laplace_rescued": bool(laplace_rescued),
    }
    # Stress damage from every subsystem passes through this single point.
    # The web runtime registers the psychosis threshold handler here.
    if (int(hp_damage) > 0 or int(sp_damage) > 0 or bool(is_dead)) and _POST_DAMAGE_HOOK is not None:
        hook_result = _POST_DAMAGE_HOOK(db_path, int(player_id), result)
        if hook_result:
            result["psychosis"] = hook_result
            psychosis_damage = hook_result.get("damage") or {}
            if psychosis_damage:
                result["hp"] = psychosis_damage.get("hp", result["hp"])
                result["sp"] = psychosis_damage.get("sp", result["sp"])
                result["is_dead"] = bool(result["is_dead"] or psychosis_damage.get("is_dead"))
    return result


def determine_winner_by_cp(db_path: Path | str, player_ids: Iterable[int]) -> Optional[int]:
    player_ids = [int(pid) for pid in player_ids]
    if not player_ids:
        return None
    placeholders = ",".join("?" for _ in player_ids)
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT ID, COALESCE(CP, 0) AS CP FROM PLAYERS WHERE ID IN ({placeholders}) ORDER BY CP DESC, ID ASC LIMIT 1",
            tuple(player_ids),
        ).fetchone()
    return int(row["ID"]) if row else None


def _alive_players(db_path: Path | str, player_ids: Iterable[int]) -> List[int]:
    player_ids = [int(pid) for pid in player_ids]
    if not player_ids:
        return []
    placeholders = ",".join("?" for _ in player_ids)
    with _connect(db_path) as conn:
        rows = conn.execute(
            f"SELECT ID FROM PLAYERS WHERE ID IN ({placeholders}) AND COALESCE(IsDead, 0) = 0 ORDER BY ID",
            tuple(player_ids),
        ).fetchall()
    alive_set = {int(row["ID"]) for row in rows}
    return [pid for pid in player_ids if pid in alive_set]


def start_game(db_path: Path | str, player_ids: Iterable[int], *, total_days: int = DEFAULT_TOTAL_DAYS) -> dict:
    player_ids = [int(pid) for pid in player_ids]
    init_core_schema(db_path)
    # Содержимое межпространственного разлома переносится между партиями.
    rift_stash = get_global_value(db_path, "RIFT_STASH_ITEM_ID", 0)
    clear_globals(db_path)
    if _safe_int(rift_stash, 0) not in (0, 1):
        set_global_value(db_path, "RIFT_STASH_ITEM_ID", _safe_int(rift_stash, 0))
    reset_players_for_new_game(db_path, player_ids)
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM CORE_TURN_EVENTS")
        conn.execute(
            """
            UPDATE CORE_GAME_STATE
            SET status = 'started',
                total_days = ?,
                current_day = 1,
                turn_index = 0,
                current_turn_user_id = ?,
                turn_order_json = ?,
                started_at = ?,
                finished_at = NULL,
                winner_user_id = NULL,
                last_event_at = ?
            WHERE id = 1
            """,
            (int(total_days), player_ids[0] if player_ids else None, json.dumps(player_ids), time.time(), time.time()),
        )
        conn.commit()
    set_global_value(db_path, "CurrentDay", 1)
    set_global_value(db_path, "ActiveWorker", player_ids[0] if player_ids else 0)
    set_global_value(db_path, "DeathsToday", 0)
    record_turn_event(db_path, "game_started", user_id=player_ids[0] if player_ids else None, day_number=1, turn_index=0, payload={"turn_order": player_ids})
    return get_game_state(db_path)


def finish_game(db_path: Path | str, *, winner_user_id: int | None = None, reason: str = "") -> dict:
    state = get_game_state(db_path)
    turn_order = state.get("turn_order", [])
    if winner_user_id is None:
        winner_user_id = determine_winner_by_cp(db_path, turn_order)
    with _connect(db_path) as conn:
        conn.execute(
            """
            UPDATE CORE_GAME_STATE
            SET status = 'finished',
                winner_user_id = ?,
                finished_at = ?,
                last_event_at = ?
            WHERE id = 1
            """,
            (winner_user_id, time.time(), time.time()),
        )
        conn.commit()
    record_turn_event(db_path, "game_finished", user_id=winner_user_id, day_number=state.get("current_day"), turn_index=state.get("turn_index"), payload={"reason": reason})
    return get_game_state(db_path)


def process_turn_change_events(db_path: Path | str, *, previous_user_id: int | None, new_user_id: int | None, wrapped_day: bool) -> List[dict]:
    events = []
    if wrapped_day:
        current_day = int(get_global_value(db_path, "CurrentDay", 1) or 1)
        events.append({"type": "day_tick", "day": current_day})
        if get_global_value(db_path, "CompanionDoomActive", 0):
            events.append({"type": "companion_doom_tick"})
        if get_global_value(db_path, "WormActive", 0):
            events.append({"type": "worm_tick"})
        if get_global_value(db_path, "skipday", 0):
            events.append({"type": "skipday_flag"})
    if previous_user_id != new_user_id:
        events.append({"type": "turn_changed", "from": previous_user_id, "to": new_user_id})
    for event in events:
        record_turn_event(db_path, event["type"], user_id=new_user_id, target_user_id=previous_user_id, day_number=int(get_global_value(db_path, "CurrentDay", 1) or 1), payload=event)
    return events


def advance_turn(db_path: Path | str, *, reason: str = "manual") -> dict:
    state = get_game_state(db_path)
    if state.get("status") != "started":
        return {"ok": False, "reason": "game_not_started", "state": state}
    turn_order = [int(pid) for pid in state.get("turn_order", [])]
    if not turn_order:
        return {"ok": False, "reason": "empty_turn_order", "state": state}
    alive = _alive_players(db_path, turn_order)
    if not alive:
        return {"ok": True, "state": finish_game(db_path, winner_user_id=None, reason="no_alive_players"), "events": [{"type": "game_finished"}]}

    current_index = int(state.get("turn_index") or 0)
    next_index = current_index
    wrapped_day = False
    for _ in range(len(turn_order)):
        next_index = (next_index + 1) % len(turn_order)
        if next_index <= current_index:
            wrapped_day = True
        candidate = turn_order[next_index]
        if candidate in alive:
            break

    current_day = int(state.get("current_day") or 1)
    if wrapped_day:
        skip_day = int(get_global_value(db_path, "skipday", 0) or 0) == 1
        current_day += 2 if skip_day else 1
        set_global_value(db_path, "CurrentDay", current_day)
        if _DAY_TRANSITION_HOOK is not None:
            hook_result = _DAY_TRANSITION_HOOK(db_path, int(state.get("current_day") or 1), int(current_day))
            if hook_result:
                return {
                    "ok": True,
                    "state": hook_result.get("state") or get_game_state(db_path),
                    "events": [{"type": "laplace_time_loop", **dict(hook_result.get("event") or {})}],
                }
        if current_day > int(state.get("total_days") or DEFAULT_TOTAL_DAYS):
            if skip_day:
                set_global_value(db_path, "skipday", 0)
            return {"ok": True, "state": finish_game(db_path, reason="days_completed"), "events": [{"type": "game_finished"}]}

    new_user_id = turn_order[next_index]
    with _connect(db_path) as conn:
        conn.execute(
            """
            UPDATE CORE_GAME_STATE
            SET current_day = ?,
                turn_index = ?,
                current_turn_user_id = ?,
                last_event_at = ?
            WHERE id = 1
            """,
            (current_day, next_index, new_user_id, time.time()),
        )
        conn.commit()
    set_global_value(db_path, "ActiveWorker", new_user_id)
    events = process_turn_change_events(db_path, previous_user_id=state.get("current_turn_user_id"), new_user_id=new_user_id, wrapped_day=wrapped_day)
    if wrapped_day and int(get_global_value(db_path, "skipday", 0) or 0) == 1:
        set_global_value(db_path, "skipday", 0)
    record_turn_event(db_path, "turn_advanced", user_id=new_user_id, target_user_id=state.get("current_turn_user_id"), day_number=current_day, turn_index=next_index, payload={"reason": reason, "wrapped_day": wrapped_day})
    return {"ok": True, "state": get_game_state(db_path), "events": events}


def mark_anomaly_studied(db_path: Path | str, user_id: int, anomaly_id: int) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO PLAYER_STUDIED_ANOMALIES (user_id, anomaly_id, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, anomaly_id) DO NOTHING
            """,
            (int(user_id), int(anomaly_id), time.time()),
        )
        conn.commit()


def get_player_studied_anomalies(db_path: Path | str, user_id: int) -> List[int]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT anomaly_id FROM PLAYER_STUDIED_ANOMALIES WHERE user_id = ? ORDER BY anomaly_id",
            (int(user_id),),
        ).fetchall()
    return [int(row["anomaly_id"]) for row in rows]


__all__ = [
    "DEFAULT_TOTAL_DAYS",
    "EFFECT_COLUMNS",
    "KNOWN_GLOBAL_KEYS",
    "add_player_effect",
    "advance_turn",
    "apply_damage",
    "clear_globals",
    "determine_winner_by_cp",
    "finish_game",
    "get_game_state",
    "get_global_value",
    "get_player_studied_anomalies",
    "init_core_schema",
    "list_globals",
    "list_player_effects",
    "mark_anomaly_studied",
    "process_turn_change_events",
    "record_turn_event",
    "remove_player_effect",
    "reset_players_for_new_game",
    "set_global_value",
    "set_day_transition_hook",
    "set_player_dead",
    "start_game",
]
