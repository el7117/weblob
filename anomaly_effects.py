from __future__ import annotations

import sqlite3
import time
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import core
import dictionary as effect_dictionary


@dataclass
class HintEffectContext:
    player_id: int
    anomaly_id: int
    effect_name: str
    hint_slot: Optional[int] = None
    db_path: Optional[Path] = None
    runtime_state: Optional[dict] = None


def _result(status: str, title: str, description: str, **extra: Any) -> dict:
    payload = {"status": status, "title": title, "description": description}
    payload.update(extra)
    return payload


def _connect(db_path: Optional[Path], write: bool = False) -> sqlite3.Connection:
    if db_path is None:
        db_path = Path(__file__).resolve().parent / "WEB_GAME.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    if write:
        conn.execute("PRAGMA foreign_keys=OFF")
    return conn


def _runtime(ctx: HintEffectContext) -> dict:
    state = ctx.runtime_state or {}
    state.setdefault("globals", {})
    state.setdefault("player_effects", {})
    state.setdefault("pending_events", [])
    ctx.runtime_state = state
    return state


def _player_effects(ctx: HintEffectContext) -> list:
    return _runtime(ctx)["player_effects"].setdefault(int(ctx.player_id), [])


PLAYER_EFFECT_ICONS = {
    "curse": "/photo/work_room/badresult.png",
    "bless": "/photo/work_room/goodresult.png",
    "neutral": "/photo/work_room/neutralresult.png",
}


def _get_effect_meta(effect_key: str) -> dict:
    raw_key = str(effect_key or "").strip()
    base_key = effect_dictionary.base_key(raw_key).strip()
    catalogs = (
        ("curse", effect_dictionary.CURSES_CATALOG),
        ("bless", effect_dictionary.BLESS_CATALOG),
        ("neutral", effect_dictionary.NEUTRAL_CATALOG),
    )
    kind = "neutral"
    info = None
    for candidate_kind, catalog in catalogs:
        info = catalog.get(base_key)
        if info:
            kind = candidate_kind
            break
    if not info:
        info = effect_dictionary.PSYCHOSIS_EFFECTS_S.get(base_key)
    name = str((info or {}).get("name") or base_key or raw_key or "Неизвестный эффект")
    description = str((info or {}).get("desc") or "Описание эффекта пока отсутствует.")
    return {
        "key": base_key,
        "raw_key": raw_key,
        "name": name,
        "description": description,
        "kind": kind,
        "icon": PLAYER_EFFECT_ICONS[kind],
        "dictionary_found": bool(info),
    }


def _effect_is_implemented(_ctx: HintEffectContext, _effect_key: str) -> str:
    """Confirm that this stored effect has an active consumer in the web game."""
    return "OK"


PLAYER_EFFECT_HANDLERS: Dict[str, Callable[[HintEffectContext, str], str]] = {
    # Each entry below is backed by an active check in server.py/core.py.
    "SparingCurse": _effect_is_implemented,
    "PisosCurse": _effect_is_implemented,
    "FleeIsDeath": _effect_is_implemented,
    "BlockedPhoto": _effect_is_implemented,
    "BlockedDescription": _effect_is_implemented,
    "witness_curse": _effect_is_implemented,
    "CinderPlague": _effect_is_implemented,
    "UnderCurse2": _effect_is_implemented,
    "UnderCurse3": _effect_is_implemented,
    "CrimsonVirus": _effect_is_implemented,
    "skibidi": _effect_is_implemented,
    "TimeShiftDrug": _effect_is_implemented,
    "NoResult": _effect_is_implemented,
    "NoResultPermanent": _effect_is_implemented,
    "VoyagerCurse": _effect_is_implemented,
    "TimeDebt69": _effect_is_implemented,
    "DevilsDeal": _effect_is_implemented,
    "WormEggs": _effect_is_implemented,
    # Stored companion/runtime tokens with active consumers in server.py/core.py.
    "comp9_next": _effect_is_implemented,
    "Comp11Left": _effect_is_implemented,
    "Comp13Applied": _effect_is_implemented,
    "SALA_MULT": _effect_is_implemented,
    "IlvitalWeakening": _effect_is_implemented,
    "death_shield": _effect_is_implemented,
    # Psychosis ids are consumed by damage/work rules in the web runtime.
    **{str(effect_id): _effect_is_implemented for effect_id in range(1001, 1011)},
}


def _add_player_effect(ctx: HintEffectContext, effect_key: str) -> dict:
    meta = _get_effect_meta(effect_key)
    handler = PLAYER_EFFECT_HANDLERS.get(meta["key"])
    implemented = bool(handler and handler(ctx, str(effect_key)) == "OK")
    description = meta["description"]
    if not implemented:
        description = f"{description}\n\nЭффекта сейчас нет!"
    common = {
        "effect": str(effect_key),
        "effect_key": meta["key"],
        "effect_kind": meta["kind"],
        "dictionary_found": meta["dictionary_found"],
        "effect_script_available": implemented,
        "modal": {
            "intro": meta["name"],
            "effect": description,
            "icon": meta["icon"],
            "iconAlt": meta["name"],
        },
    }
    if ctx.db_path:
        result = core.add_player_effect(ctx.db_path, ctx.player_id, effect_key)
        if result.get("ok"):
            if result.get("absorbed_by_companion"):
                hp_cost = int(result.get("hp_cost") or 0)
                absorbed = f"Кот-висельник поглотил эффект и взамен забрал {hp_cost} HP."
                return _result(
                    "blocked",
                    meta["name"],
                    absorbed,
                    **{
                        **common,
                        "effect_script_available": implemented,
                        "modal": {**common["modal"], "effect": absorbed},
                    },
                    reason="absorbed_by_companion",
                    hp_cost=hp_cost,
                    dead=bool(result.get("dead")),
                )
            return _result(
                "implemented" if implemented else "recorded",
                meta["name"],
                description,
                **common,
                slot=result.get("slot"),
                duplicate=bool(result.get("duplicate")),
            )
        blocked_text = "Не удалось записать эффект: свободные слоты эффектов закончились." if result.get("reason") == "no_free_slot" else "Не удалось записать эффект игроку."
        return _result(
            "blocked",
            meta["name"],
            blocked_text,
            **{**common, "modal": {**common["modal"], "effect": blocked_text}},
            reason=result.get("reason"),
        )
    effects = _player_effects(ctx)
    duplicate = effect_key in effects
    if effect_key not in effects:
        effects.append(effect_key)
    return _result(
        "implemented" if implemented else "recorded",
        meta["name"],
        description,
        **common,
        duplicate=duplicate,
    )


def _combine_player_effect_results(results: list[dict]) -> dict:
    if not results:
        return _result("blocked", "Эффект не записан", "Не удалось определить эффект.")
    if len(results) == 1:
        return results[0]
    names = [str(item.get("title") or item.get("effect_key") or "Эффект") for item in results]
    descriptions = [str((item.get("modal") or {}).get("effect") or item.get("description") or "") for item in results]
    blocked = any(item.get("status") == "blocked" for item in results)
    implemented = all(bool(item.get("effect_script_available")) for item in results)
    description = "\n\n".join(text for text in descriptions if text)
    return _result(
        "blocked" if blocked else ("implemented" if implemented else "recorded"),
        ", ".join(names),
        description,
        effects=results,
        effect_script_available=implemented,
        modal={
            "intro": ", ".join(names),
            "effect": description,
            "icon": "/photo/work_room/badresult.png",
            "iconAlt": ", ".join(names),
        },
    )


def apply_player_effect(
    effect_key: str,
    *,
    player_id: int,
    anomaly_id: int = 0,
    db_path: Optional[Path] = None,
    runtime_state: Optional[dict] = None,
) -> dict:
    """Public central entry point for every write to a player's effect slots."""
    return _add_player_effect(
        HintEffectContext(
            player_id=int(player_id),
            anomaly_id=int(anomaly_id or 0),
            effect_name=str(effect_key),
            db_path=db_path,
            runtime_state=runtime_state,
        ),
        str(effect_key),
    )


def _set_global(ctx: HintEffectContext, key: str, value: Any) -> None:
    if ctx.db_path:
        core.set_global_value(ctx.db_path, key, value)
        return
    _runtime(ctx)["globals"][key] = value


def _get_global(ctx: HintEffectContext, key: str, default: Any = 0) -> Any:
    if ctx.db_path:
        return core.get_global_value(ctx.db_path, key, default)
    return _runtime(ctx)["globals"].get(key, default)


EVENT_UI_COPY = {
    "puppy_encounter": ("Симпатяга Убивака", "Существо внимательно смотрит на сотрудника. Встреча завершена без враждебности."),
    "portal_mushroom_dialog": ("Лесной портал", "Портал открылся и стабилизировался. Его координаты сохранены."),
    "global_rift_dialog": ("Межпространственный разлом", "Разлом открыл общий тайник между измерениями."),
    "pandora_box_dialog": ("Ящик Пандоры", "Ящик отреагировал на присутствие сотрудника и снова закрылся."),
    "instrument_choice_dialog": ("Мясной рок", "Аномалия услышала выбранный сотрудником ритм."),
    "forest_tape_dialog": ("Запись из леса", "Плёнка воспроизведена. Наблюдение занесено в протокол."),
    "po3_trials": ("Испытание PO3", "Испытание зарегистрировано веб-системой."),
    "curse_anomaly_dialog": ("Предложение проклятия", "Аномалия предложила сделку. Событие зарегистрировано."),
    "tenna_game": ("Шоу Тенны", "Раунд шоу завершён."),
    "sovuh_zombie_game": ("Сова-зомби", "Мини-игра завершена, сотрудник вернулся к исследованию."),
    "dice_pick_dialog": ("Набор игральных кубиков", "Кубик выбран, результат зафиксирован."),
    "pet_anomaly_prompt": ("Кот Вельмондт", "Контакт с аномалией завершён."),
    "feedable_anomaly_prompt": ("Гиш", "Попытка взаимодействия с аномалией завершена."),
    "sea_monster_game": ("Морской дьявол", "Приготовьтесь отразить пять атак Левиафана."),
}


def _queue_event(ctx: HintEffectContext, event_type: str, **payload: Any) -> dict:
    event = {"type": event_type, "player_id": int(ctx.player_id), "anomaly_id": int(ctx.anomaly_id), **payload}
    _runtime(ctx)["pending_events"].append(event)
    title, description = EVENT_UI_COPY.get(event_type, ("Событие аномалии", f"Событие `{ctx.effect_name}` готово к обработке."))
    return _result("pending_ui", title, description, event=event)


def _build_codename_from_row(row: sqlite3.Row | dict | None) -> str:
    if not row:
        return "SC-UN-U-0"
    try:
        ready = str((row["codename"] if isinstance(row, sqlite3.Row) or isinstance(row, dict) else "") or "").strip()
        if ready:
            return ready
    except Exception:
        pass
    type_map = {1: "NA", 2: "DA", 3: "CO", 4: "AB", 5: "HU"}
    class_map = {1: "Z", 2: "T", 3: "H", 4: "W", 5: "A"}
    type_id = int((row["TYPE"] if isinstance(row, (sqlite3.Row, dict)) else 0) or 0)
    class_id = int((row["CLASS_ID"] if isinstance(row, (sqlite3.Row, dict)) else 0) or 0)
    anomaly_id = int((row["ID"] if isinstance(row, (sqlite3.Row, dict)) else 0) or 0)
    item_id = int((row["item_id"] if isinstance(row, (sqlite3.Row, dict)) else 0) or 0)
    hidden_hint = str((row["HINTHIDDEN"] if isinstance(row, (sqlite3.Row, dict)) else "") or "").strip()
    prefix = "IA" if item_id > 0 else ("SH" if hidden_hint else "SC")
    return f"{prefix}-{type_map.get(type_id, 'UN')}-{class_map.get(class_id, 'U')}-{anomaly_id}"


def _update_player(ctx: HintEffectContext, sql: str, params: tuple) -> None:
    with _connect(ctx.db_path, write=True) as conn:
        conn.execute(sql, params)
        conn.commit()


def _get_player_row(ctx: HintEffectContext):
    with _connect(ctx.db_path) as conn:
        return conn.execute("SELECT * FROM PLAYERS WHERE ID = ?", (int(ctx.player_id),)).fetchone()


def _ensure_work_row(ctx: HintEffectContext) -> None:
    with _connect(ctx.db_path, write=True) as conn:
        row = conn.execute(
            "SELECT anomaly_id FROM WORK WHERE user_id = ?",
            (int(ctx.player_id),),
        ).fetchone()
        if not row:
            conn.execute(
                """
                INSERT INTO WORK (user_id, anomaly_id, photounlocked, descriptionunlocked, hintunlocked, hintcount)
                VALUES (?, ?, 0, 0, 0, 0)
                """,
                (int(ctx.player_id), int(ctx.anomaly_id)),
            )
        elif int(row["anomaly_id"] or 0) != int(ctx.anomaly_id):
            conn.execute(
                "UPDATE WORK SET anomaly_id = ?, photounlocked = 0, descriptionunlocked = 0, hintunlocked = 0, IsCompleted = 0 WHERE user_id = ?",
                (int(ctx.anomaly_id), int(ctx.player_id)),
            )
        conn.commit()


def _assign_companion(ctx: HintEffectContext, companion_id: int) -> dict:
    _update_player(ctx, "UPDATE PLAYERS SET COMPSLOT = ? WHERE ID = ?", (int(companion_id), int(ctx.player_id)))
    return _result("implemented", "Компаньон получен", f"Игрок получил компаньона `{companion_id}`.", companion_id=companion_id)


def _inventory_add(ctx: HintEffectContext, item_id: int, amount: int = 1) -> dict:
    item_name = f"Предмет {int(item_id)}"
    with _connect(ctx.db_path) as conn:
        item_row = conn.execute("SELECT NAME, COALESCE(AMOUNT, 1) AS AMOUNT FROM ITEMS WHERE ID = ?", (int(item_id),)).fetchone()
        if item_row and item_row["NAME"]:
            item_name = str(item_row["NAME"])
        # These stackable anomaly rewards use their configured pack size.
        # Explicit non-default grants remain untouched.
        if int(item_id) in (3, 10, 21) and int(amount) == 1 and item_row:
            amount = max(1, int(item_row["AMOUNT"] or 1))

    with _connect(ctx.db_path, write=True) as conn:
        row = conn.execute(
            """
            SELECT INVSLOT1, SLOT1AMOUNT, INVSLOT2, SLOT2AMOUNT
            FROM PLAYERS WHERE ID = ?
            """,
            (int(ctx.player_id),),
        ).fetchone()
        if not row:
            return _result("error", "Игрок не найден", "Не удалось открыть инвентарь игрока.")

        slots = [
            ["INVSLOT1", "SLOT1AMOUNT", int(row["INVSLOT1"] or 0), int(row["SLOT1AMOUNT"] or 0)],
            ["INVSLOT2", "SLOT2AMOUNT", int(row["INVSLOT2"] or 0), int(row["SLOT2AMOUNT"] or 0)],
        ]
        target = None
        for slot in slots:
            if slot[2] == int(item_id):
                target = slot
                break
        if target is None:
            for slot in slots:
                if slot[2] in (0, 1) or slot[3] <= 0:
                    target = slot
                    break
        if target is None:
            description = f"Предмет «{item_name}» не выдан: инвентарь переполнен, свободных слотов нет."
            return _result(
                "blocked", "Инвентарь заполнен", description,
                item_id=int(item_id), item_name=item_name, amount=0,
                modal={
                    "intro": "Предмет не выдан",
                    "effect": description,
                    "icon": "/photo/work_room/giveitem.png",
                    "iconAlt": "Инвентарь заполнен",
                },
            )

        slot_id_col, slot_amount_col = target[0], target[1]
        conn.execute(
            f"UPDATE PLAYERS SET {slot_id_col} = ?, {slot_amount_col} = COALESCE({slot_amount_col}, 0) + ? WHERE ID = ?",
            (int(item_id), int(amount), int(ctx.player_id)),
        )
        conn.commit()
    return _result(
        "implemented",
        "Предмет выдан",
        f"Игрок получил предмет `{item_name}` x{amount}.",
        item_id=item_id,
        item_name=item_name,
        amount=amount,
        modal={
            "intro": "Новый предмет!",
            "effect": f"Аномалия передала предмет {item_name} ({int(amount)}).",
            "icon": "/photo/work_room/giveitem.png",
            "iconAlt": "Новый предмет",
        },
    )

def _stub(ctx: HintEffectContext, reason: str, **extra: Any) -> dict:
    return _result("stub", "Нужна отдельная веб-сцена", f"Эффект `{ctx.effect_name}` пока оставлен заглушкой: {reason}.", **extra)


# ============================================================
# ЭФФЕКТ ПРИ ОТКРЫТИИ ПОДСКАЗОК
# ============================================================
#
# --- ID 1: Sparing --- hint4effect -> apply_sparing_curse
# --- ID 2: berserk17 --- hint1effect -> berserk17meet
# --- ID 6: Кот Писос --- hint1effect -> apply_pisos_curse
# --- ID 7: Плита призыва --- hint1effect -> check_cat_reward
# --- ID 8: Undercards --- hint1effect -> fleeIsDeath; hint2effect -> UnderCurse2;
# hint3effect -> UnderCurse3; hint5effect -> UnderCurse4; hint6effect -> UnderCurse5;
# hint7effect -> UnderCurse6; hint8effect -> UnderCurse7
# --- ID 9, 53, 75, 78, 87, 91, 94, 95, 97, 99, 103, 114, 117, 118, 119, 127, 130 ---
# используется give_item_command
# --- ID 12: Моль --- hint5effect -> MothInstaKill
# --- ID 13: Халикоптер --- hint2effect -> attack
# --- ID 15, 16, 17, 18, 23, 45, 54, 55, 85, 86, 115, 124, 126 ---
# используются эффекты-компаньоны
# --- ID 19 --- open_contract_kill_offer
# --- ID 21 --- offer_stat_conversion
# --- ID 25 --- langustwasmet
# --- ID 31 --- choose_bonus
# --- ID 32 --- sovuh_zombie
# --- ID 35 --- prompt_death_shield
# --- ID 36, 38 --- alephsummoned
# --- ID 37 --- altar_unlock
# --- ID 39 --- moon_game
# --- ID 41 --- deviloffer
# --- ID 43 --- d20curse
# --- ID 44 --- hint_with_emoji_check
# --- ID 46 --- cinder_idol1..5
# --- ID 47 --- hungry_bag1..3
# --- ID 49 --- free_stat
# --- ID 58 --- start_train_timer
# --- ID 61 --- SeaMonster
# --- ID 62 --- spread_cinder_plague, cinderplagueupgrade
# --- ID 64 --- stat_checks
# --- ID 65 --- CinderPlague
# --- ID 66 --- start_puppy_encounter
# --- ID 70 --- memetic_rabbit_scene
# --- ID 71 --- fleeIsDeath, izbushka1..3
# --- ID 76 --- infect_worm_eggs
# --- ID 77 --- witness_curse
# --- ID 79 --- start_companion_doom
# --- ID 81 --- crimson_infect
# --- ID 83 --- NonAnomaly
# --- ID 92 --- steal_cp1/2, steal_stat4_level
# --- ID 100 --- frogbonus
# --- ID 102 --- cookie_anomaly_give
# --- ID 104 --- start_tenna_game
# --- ID 106 --- start_instrument_anomaly
# --- ID 107 --- start_forest_tape_dialog
# --- ID 108 --- skibidi
# --- ID 109 --- dmg20, dmg35, grant_vicious_heart
# --- ID 110 --- violin_force_give_to
# --- ID 113 --- start_pandora_box
# --- ID 116 --- anomaly_portal_mushroom
# --- ID 120 --- dice_anomaly
# --- ID 122 --- pet_anomaly_prompt
# --- ID 123 --- x125_meet_sleeping
# --- ID 125 --- feedable_anomaly
# --- ID 128 --- start_nubert_dialog
# --- ID 129 --- grant_legend_rt
# --- ID 132 --- give_utilizer
# --- ID 134 --- grant_or_use_timeshift_drug
# --- ID 135 --- interdimensional_rift_global
# --- ID 136 --- start_po3_trials
# --- ID 137 --- start_curse_anomaly_dialog


HINT_EFFECTS_BY_ANOMALY: Dict[int, dict] = {
    1: {"hint4effect": "apply_sparing_curse"},
    2: {"hint1effect": "berserk17meet"},
    6: {"hint1effect": "apply_pisos_curse"},
    7: {"hint1effect": "check_cat_reward"},
    8: {"hint1effect": "fleeIsDeath", "hint2effect": "UnderCurse2", "hint3effect": "UnderCurse3", "hint5effect": "UnderCurse4", "hint6effect": "UnderCurse5", "hint7effect": "UnderCurse6", "hint8effect": "UnderCurse7"},
    9: {"hint2effect": "give_item_command"},
    12: {"hint5effect": "MothInstaKill"},
    13: {"hint2effect": "attack"},
    15: {"hint2effect": "bulbasaur"},
    16: {"hint2effect": "kurem"},
    17: {"hint2effect": "ilvetal"},
    18: {"hint2effect": "check_berserk", "hint3effect": "genesect"},
    19: {"hint2effect": "open_contract_kill_offer"},
    21: {"hint1effect": "offer_stat_conversion"},
    23: {"hint1effect": "cheaptrick"},
    25: {"hint1effect": "langustwasmet"},
    31: {"hint1effect": "choose_bonus"},
    32: {"hint1effect": "sovuh_zombie"},
    35: {"hint1effect": "prompt_death_shield"},
    36: {"hint1effect": "skipday", "hint2effect": "alephsummoned"},
    37: {"hint1effect": "altar_unlock"},
    38: {"hint3effect": "alephsummoned"},
    39: {"hint1effect": "moon_game"},
    41: {"hint2effect": "deviloffer"},
    43: {"hint1effect": "d20curse"},
    44: {"hint1effect": "hint_with_emoji_check"},
    45: {"hint1effect": "hanged_cat"},
    46: {"hint1effect": "cinder_idol1", "hint2effect": "cinder_idol2", "hint3effect": "cinder_idol3", "hint4effect": "cinder_idol4", "hint5effect": "cinder_idol5"},
    47: {"hint1effect": "hungry_bag", "hint2effect": "hungry_bag2", "hint3effect": "hungry_bag3"},
    49: {"hint2effect": "free_stat"},
    53: {"hint2effect": "give_item_command"},
    54: {"hint1effect": "shnublik"},
    55: {"hint1effect": "lil_zema"},
    58: {"hint1effect": "start_train_timer"},
    61: {"hint4effect": "SeaMonster"},
    62: {"hint1effect": "spread_cinder_plague", "hint3effect": "cinderplagueupgrade"},
    64: {"hint4effect": "stat_checks"},
    65: {"hint1effect": "CinderPlague"},
    66: {},
    70: {"hint1effect": "memetic_rabbit_scene"},
    71: {"hint1effect": "fleeIsDeath", "hint2effect": "izbushka1", "hint3effect": "izbushka2", "hint4effect": "izbushka3", "hint5effect": "izbushka4"},
    75: {"hint1effect": "give_item_command"},
    76: {"hint1effect": "infect_worm_eggs"},
    77: {"hint1effect": "witness_curse"},
    78: {"hint1effect": "give_item_command"},
    79: {"hint1effect": "start_companion_doom"},
    81: {"hint1effect": "crimson_infect"},
    83: {"hint1effect": "NonAnomaly"},
    85: {"hint1effect": "stupidreptile"},
    86: {"hint1effect": "stonefox"},
    87: {"hint1effect": "give_item_command"},
    91: {"hint2effect": "give_item_command"},
    92: {"hint1effect": "steal_cp1", "hint2effect": "steal_cp1", "hint3effect": "steal_cp2", "hint4effect": "steal_stat4_level"},
    94: {"hint1effect": "give_item_command"},
    95: {"hint1effect": "give_item_command"},
    97: {"hint1effect": "give_item_command"},
    99: {"hint1effect": "give_item_command"},
    100: {"hint1effect": "frogbonus"},
    102: {"hint1effect": "cookie_anomaly_give"},
    103: {"hint1effect": "give_item_command"},
    104: {"hint1effect": "start_tenna_game"},
    106: {"hint1effect": "start_instrument_anomaly"},
    107: {"hint1effect": "start_forest_tape_dialog"},
    108: {"hint1effect": "skibidi"},
    109: {"hint2effect": "dmg20", "hint4effect": "dmg35", "hint7effect": "grant_vicious_heart"},
    110: {"hint2effect": "violin_force_give_to"},
    112: {"hint2effect": "salamander"},
    113: {"hint1effect": "start_pandora_box"},
    114: {"hint1effect": "give_item_command"},
    115: {"hint1effect": "fairy"},
    116: {"hint1effect": "anomaly_portal_mushroom"},
    117: {"hint1effect": "give_item_command"},
    118: {"hint1effect": "give_item_command"},
    119: {"hint1effect": "give_item_command"},
    120: {"hint1effect": "dice_anomaly"},
    122: {"hint1effect": "pet_anomaly_prompt"},
    123: {"hint1effect": "x125_meet_sleeping"},
    124: {"hint1effect": "sprigatito"},
    125: {"hint1effect": "feedable_anomaly"},
    126: {"hint1effect": "xqc"},
    127: {"hint1effect": "give_item_command"},
    128: {"hint1effect": "start_nubert_dialog"},
    129: {"hint3effect": "grant_legend_rt"},
    130: {"hint1effect": "give_item_command"},
    132: {"hint2effect": "give_utilizer"},
    134: {"hint1effect": "grant_or_use_timeshift_drug"},
    135: {"hint2effect": "interdimensional_rift_global"},
    136: {"hint1effect": "start_po3_trials"},
    137: {"hint1effect": "start_curse_anomaly_dialog"},
}


def effect_apply_sparing_curse(ctx: HintEffectContext) -> dict:
    return _add_player_effect(ctx, "SparingCurse")


def effect_apply_pisos_curse(ctx: HintEffectContext) -> dict:
    return _add_player_effect(ctx, "PisosCurse")


def effect_catonstoveencountered(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "CatOnStoveEncountered", 1)
    _set_global(ctx, "CatGiveReward", 0)
    return _result(
        "implemented",
        "Эффект активирован",
        "Следующая выполненная работа будет проверена для кошачьего бонуса.",
    )


def effect_start_battle_with_flee_is_death(ctx: HintEffectContext) -> dict:
    return _add_player_effect(ctx, "FleeIsDeath")


def effect_start_battle_with_heli(ctx: HintEffectContext) -> dict:
    return _combine_player_effect_results(
        [
            _add_player_effect(ctx, "BlockedPhoto"),
            _add_player_effect(ctx, "BlockedDescription"),
        ]
    )


def effect_flee_is_death(ctx: HintEffectContext) -> dict:
    return _add_player_effect(ctx, "FleeIsDeath")


def effect_witness_curse(ctx: HintEffectContext) -> dict:
    return _add_player_effect(ctx, "witness_curse")


def effect_skibidi(ctx: HintEffectContext) -> dict:
    result = _add_player_effect(ctx, "skibidi")
    if not bool(result.get("duplicate")):
        _set_global(ctx, f"SkibidiActivatedDay_{int(ctx.player_id)}", int(_get_global(ctx, "CurrentDay", 1) or 1))
    return result


def effect_cinder_plague(ctx: HintEffectContext) -> dict:
    return _add_player_effect(ctx, "CinderPlague")


def effect_under_curse2(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "UnderCurse2", 1)
    return _add_player_effect(ctx, "UnderCurse2")


def effect_under_curse3(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "UnderCurse3", 1)
    return _add_player_effect(ctx, "UnderCurse3")


def effect_under_curse4(ctx: HintEffectContext) -> dict:
    row = _get_player_row(ctx)
    if not row:
        return _result("error", "Игрок не найден", "Не удалось проверить здоровье игрока.")
    hp = int(row["HP"] or 0)
    max_hp = max(1, int(row["MAXHP"] or 1))
    if hp / max_hp <= 0.5:
        _update_player(ctx, "UPDATE PLAYERS SET CP = COALESCE(CP, 0) + 2000 WHERE ID = ?", (int(ctx.player_id),))
        return _result("implemented", "Бонус выдан", "HP ниже 50%, игрок получил +2000 CP.")
    return _result("implemented", "Условие не выполнено", "HP выше 50%, эффект ничего не изменил.")


def effect_under_curse5(ctx: HintEffectContext) -> dict:
    _ensure_work_row(ctx)
    with _connect(ctx.db_path, write=True) as conn:
        row = conn.execute(
            "SELECT photounlocked, descriptionunlocked FROM WORK WHERE user_id = ? AND anomaly_id = ?",
            (int(ctx.player_id), int(ctx.anomaly_id)),
        ).fetchone()
        photo = int(row["photounlocked"] or 0) if row else 0
        desc = int(row["descriptionunlocked"] or 0) if row else 0
        conn.execute(
            "UPDATE WORK SET photounlocked = 1, descriptionunlocked = 1 WHERE user_id = ? AND anomaly_id = ?",
            (int(ctx.player_id), int(ctx.anomaly_id)),
        )
        if photo == 1 and desc == 1:
            conn.execute("UPDATE PLAYERS SET RP = COALESCE(RP, 0) + 20 WHERE ID = ?", (int(ctx.player_id),))
        conn.commit()
    return _result("implemented", "Подсказки раскрыты", "Фото и описание открыты, а при полном открытии выдан RP.")


def effect_under_curse6(ctx: HintEffectContext) -> dict:
    if int(_get_global(ctx, "AlephWasStudied", 0) or 0) == 0:
        _update_player(ctx, "UPDATE PLAYERS SET HP = MAXHP WHERE ID = ?", (int(ctx.player_id),))
        return _result("implemented", "HP восстановлено", "Aleph ещё не изучен, HP установлено в MAXHP.")
    return _result("implemented", "Условие не выполнено", "Aleph уже изучен, эффект не сработал.")


def effect_under_curse7(ctx: HintEffectContext) -> dict:
    _update_player(ctx, "UPDATE PLAYERS SET BONUS = COALESCE(BONUS, 0) + 15 WHERE ID = ?", (int(ctx.player_id),))
    _set_global(ctx, "UnderCurse2", 0)
    _set_global(ctx, "UnderCurse3", 0)
    return _result("implemented", "Бонус обновлён", "Игрок получил +15 BONUS, прогресс проклятия сброшен.")


def effect_berserk17meet(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "BersWasMet", 1)
    return _result("implemented", "Глобальный флаг обновлён", "BersWasMet установлен в 1.")


def effect_non_anomaly(ctx: HintEffectContext) -> dict:
    first_work_class = int(_get_global(ctx, "first_work_class", 3) or 3)
    first_work_type = int(_get_global(ctx, "first_work_anomalytype", 3) or 3)
    cls = first_work_class if first_work_class in (1, 2, 3, 4, 5) else 3
    anomaly_type = first_work_type if first_work_type in (1, 2, 3, 4, 5) else 3
    _set_global(ctx, "NonAnomalyClass", cls)
    _set_global(ctx, "NonAnomalyType", anomaly_type)
    return _result(
        "implemented", "Параметры приняты",
        f"Аномалия приняла класс {cls} и тип {anomaly_type} из первой работы.",
        class_id=cls, type_id=anomaly_type,
    )


def effect_dmg20(ctx: HintEffectContext) -> dict:
    damage = None
    if ctx.db_path:
        damage = core.apply_damage(
            ctx.db_path,
            int(ctx.player_id),
            hp_damage=20,
            sp_damage=0,
            reason=f"hint_effect:{ctx.effect_name}",
        )
    else:
        _update_player(ctx, "UPDATE PLAYERS SET HP = MAX(0, COALESCE(HP, 0) - 20) WHERE ID = ?", (int(ctx.player_id),))
    return _result(
        "implemented",
        "Нанесён урон",
        "Игрок получил 20 урона.",
        damage=damage,
        player_dead=bool((damage or {}).get("is_dead")),
    )


def effect_dmg35(ctx: HintEffectContext) -> dict:
    damage = None
    if ctx.db_path:
        damage = core.apply_damage(
            ctx.db_path,
            int(ctx.player_id),
            hp_damage=35,
            sp_damage=0,
            reason=f"hint_effect:{ctx.effect_name}",
        )
    else:
        _update_player(ctx, "UPDATE PLAYERS SET HP = MAX(0, COALESCE(HP, 0) - 35) WHERE ID = ?", (int(ctx.player_id),))
    return _result(
        "implemented",
        "Нанесён урон",
        "Игрок получил 35 урона.",
        damage=damage,
        player_dead=bool((damage or {}).get("is_dead")),
    )


def effect_steal_cp1(ctx: HintEffectContext) -> dict:
    _update_player(ctx, "UPDATE PLAYERS SET CP = MAX(0, COALESCE(CP, 0) - 50) WHERE ID = ?", (int(ctx.player_id),))
    return _result("implemented", "CP уменьшены", "Игрок потерял 50 CP.")


def effect_steal_cp2(ctx: HintEffectContext) -> dict:
    _update_player(ctx, "UPDATE PLAYERS SET CP = MAX(0, COALESCE(CP, 0) - 200) WHERE ID = ?", (int(ctx.player_id),))
    return _result("implemented", "CP уменьшены", "Игрок потерял 200 CP.")


def effect_steal_stat4(ctx: HintEffectContext) -> dict:
    _update_player(ctx, "UPDATE PLAYERS SET STAT4 = CASE WHEN COALESCE(STAT4, 0) > 1 THEN STAT4 - 1 ELSE STAT4 END WHERE ID = ?", (int(ctx.player_id),))
    return _result("implemented", "STAT4 проверен", "Если STAT4 был выше 1, он уменьшен на 1.")


def effect_check_berserk(ctx: HintEffectContext) -> dict:
    if int(_get_global(ctx, "BersWasMet", 0) or 0) == 1:
        return _result("implemented", "Доступ разрешён", "Объект уже был встречен ранее.")
    berserk_codename = "SC-UN-U-2"
    if ctx.db_path:
        with _connect(ctx.db_path, write=True) as conn:
            conn.execute(
                "UPDATE WORK SET BerserkGateFailed = 1 WHERE user_id = ? AND anomaly_id = ?",
                (int(ctx.player_id), int(ctx.anomaly_id)),
            )
            try:
                row = conn.execute(
                    "SELECT ID, TYPE, CLASS_ID, COALESCE(item_id, 0) AS item_id, COALESCE(HINTHIDDEN, '') AS HINTHIDDEN FROM ANOMALY WHERE ID = 2"
                ).fetchone()
                berserk_codename = _build_codename_from_row(row)
            except Exception:
                pass
            conn.commit()
    return _result(
        "implemented",
        "Проверка не пройдена",
        f"Без активного сигнала от {berserk_codename} дальнейшее исследование невозможно.",
        modal={
            "intro": "Проверка не пройдена",
            "effect": f"Без активного сигнала от {berserk_codename} дальнейшее исследование невозможно.",
            "icon": "/photo/work_room/neutralresult.png",
            "iconAlt": "Проверка не пройдена",
        },
        research_locked=True,
        berserk_codename=berserk_codename,
    )


def effect_skip_day(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "skipday", 1)
    return _result("implemented", "Время искажено", "При следующей смене дня один день будет пропущен.")


def effect_cinderplague_upgrade(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "cinderplagueupgrade", 1)
    return _result("implemented", "Улучшение активировано", "Флаг cinderplagueupgrade установлен.")


def effect_d20curse(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "d20", 1)
    _set_global(ctx, "d20_activated_day", int(_get_global(ctx, "CurrentDay", 0) or 0))
    return _result("implemented", "Куб проклятия активирован", "Глобальный флаг d20 установлен в 1.")


def effect_give_item_command(ctx: HintEffectContext) -> dict:
    with _connect(ctx.db_path) as conn:
        row = conn.execute("SELECT item_id FROM ANOMALY WHERE ID = ?", (int(ctx.anomaly_id),)).fetchone()
    if not row or row["item_id"] is None:
        return _stub(ctx, "у аномалии не найден item_id для выдачи предмета")
    return _inventory_add(ctx, int(row["item_id"]), 1)


def effect_cookie_anomaly_give(ctx: HintEffectContext) -> dict:
    first = _inventory_add(ctx, 11, 1)
    second = _inventory_add(ctx, 12, 1)
    first_ok = str(first.get("status") or "") == "implemented"
    second_ok = str(second.get("status") or "") == "implemented"
    if first_ok and second_ok:
        description = "Вы получили две печеньки: материальную и антиматериальную."
    elif first_ok:
        description = "Вы получили материальную печеньку. Для антиматериальной не нашлось свободного слота."
    elif second_ok:
        description = "Вы получили антиматериальную печеньку. Для материальной не нашлось свободного слота."
    else:
        description = "Инвентарь переполнен — печеньки не выданы."
    return _result(
        "implemented" if (first_ok or second_ok) else "blocked",
        "Печеньки выданы" if (first_ok or second_ok) else "Печеньки не выданы",
        description,
        first=first,
        second=second,
        modal={
            "intro": "Новые предметы" if (first_ok or second_ok) else "Предметы не выданы",
            "effect": description,
            "icon": "/photo/work_room/giveitem.png",
            "iconAlt": "Материальное и антиматериальное печенье",
        },
    )


def effect_give_utilizer(ctx: HintEffectContext) -> dict:
    # В таблице ITEMS утилизатор имеет ID 26. ID 52 отсутствует, поэтому
    # прежняя реализация записывала в слот невидимый для инвентаря предмет.
    return _inventory_add(ctx, 26, 1)


def effect_grant_legend_rt(ctx: HintEffectContext) -> dict:
    # Original bot rule: only the real legendaryfox receives the token.
    if int(ctx.player_id) != 368079488216465440:
        return _result(
            "blocked",
            "Мифический лис",
            "Ты недостаточно легендарен...",
            modal={
                "intro": "Мифический лис",
                "effect": "Ты недостаточно легендарен...",
                "icon": "/photo/work_room/neutralresult.png",
                "iconAlt": "Мифический лис",
            },
        )
    _update_player(ctx, "UPDATE PLAYERS SET RT = COALESCE(RT, 0) + 1 WHERE ID = ?", (int(ctx.player_id),))
    return _result(
        "implemented",
        "YOU ARE TRUE LEGEND",
        "Получен 1 токен прокачки.",
        modal={
            "intro": "YOU ARE TRUE LEGEND",
            "effect": "Получен 1 токен прокачки.",
            "icon": "/photo/work_room/success.png",
            "iconAlt": "Истинная легенда",
        },
    )


def effect_grant_vicious_heart(ctx: HintEffectContext) -> dict:
    return _inventory_add(ctx, 32, 1)


def effect_violin_force_give_to(ctx: HintEffectContext) -> dict:
    result = _inventory_add(ctx, 33, 1)
    if str(result.get("status") or "") == "blocked":
        with _connect(ctx.db_path, write=True) as conn:
            conn.execute(
                "UPDATE PLAYERS SET INVSLOT1 = 33, SLOT1AMOUNT = 1 WHERE ID = ?",
                (int(ctx.player_id),),
            )
            conn.commit()
        result = _result(
            "implemented",
            "Скрипка получена",
            "Скрипка Безмолвного Дирижёра заменила предмет в первом слоте.",
            item_id=33,
            amount=1,
            replaced_slot=1,
            modal={
                "intro": "Скрипка получена",
                "effect": "Скрипка Безмолвного Дирижёра заменила предмет в первом слоте.",
                "icon": "/photo/work_room/giveitem.png",
                "iconAlt": "Скрипка Безмолвного Дирижёра",
            },
        )
    if str(result.get("status") or "") != "blocked":
        _set_global(ctx, "ViolinIsTaken", 1)
        _set_global(ctx, "ViolinOwnerPid", int(ctx.player_id))
        if int(_get_global(ctx, "ViolinDamage", 0) or 0) <= 0:
            _set_global(ctx, "ViolinDamage", 40)
            _set_global(ctx, "ViolinSteals", 0)
        _set_global(ctx, "ViolinOwnerStreak", 1)
        _set_global(ctx, "ViolinTriggeredToday", 0)
    return result


def effect_grant_or_use_timeshift_drug(ctx: HintEffectContext) -> dict:
    row = _get_player_row(ctx)
    if not row:
        return _result("error", "Игрок не найден", "Не удалось проверить HP игрока.")
    hp = int(row["HP"] or 0)
    max_hp = int(row["MAXHP"] or 0)
    if max_hp and hp < max_hp:
        result = _add_player_effect(ctx, core.TSD_FLAG)
        if str(result.get("status") or "") != "blocked":
            # Автоматическое применение должно раскрывать предмет точно так же,
            # как его ручное использование из инвентаря.
            with _connect(ctx.db_path, write=True) as conn:
                conn.execute(
                    "UPDATE ITEMS SET IsUsed = 1 WHERE ID = ? AND COALESCE(IsUsed, 0) <> 1",
                    (34,),
                )
                conn.commit()
        return result
    return _inventory_add(ctx, 34, 1)


def effect_prompt_death_shield(ctx: HintEffectContext) -> dict:
    return _queue_event(ctx, "death_shield_offer")


def effect_spread_cinder_plague(ctx: HintEffectContext) -> dict:
    players = list(dict.fromkeys(int(pid) for pid in _runtime(ctx).get("active_player_ids", []) if pid is not None))
    if not players:
        return _stub(ctx, "в runtime_state пока не передан список активных игроков")
    if ctx.db_path:
        candidates = [pid for pid in players if int(pid) != int(ctx.player_id)]
        if candidates:
            placeholders = ",".join("?" for _ in candidates)
            with _connect(ctx.db_path) as conn:
                alive_rows = conn.execute(
                    f"SELECT ID FROM PLAYERS WHERE ID IN ({placeholders}) AND COALESCE(IsDead, 0) = 0 AND COALESCE(HP, 0) > 0",
                    tuple(candidates),
                ).fetchall()
            alive_ids = {int(row["ID"]) for row in alive_rows}
            players = [pid for pid in players if pid in alive_ids or int(pid) == int(ctx.player_id)]
    infected = []
    results = []
    for player_id in players:
        if int(player_id) == int(ctx.player_id):
            continue
        payload = HintEffectContext(player_id=int(player_id), anomaly_id=ctx.anomaly_id, effect_name="CinderPlague", db_path=ctx.db_path, runtime_state=ctx.runtime_state)
        effect_result = _add_player_effect(payload, "CinderPlague")
        results.append(effect_result)
        if effect_result.get("status") != "blocked" and not bool(effect_result.get("duplicate")):
            infected.append(int(player_id))
    meta = _get_effect_meta("CinderPlague")
    description = f"{meta['description']}\n\nЗаражено игроков: {len(infected)}."
    return _result(
        "implemented",
        meta["name"],
        description,
        targets=infected,
        effects=results,
        effect_script_available=True,
        modal={
            "intro": meta["name"],
            "effect": description,
            "icon": meta["icon"],
            "iconAlt": meta["name"],
        },
    )


def effect_memetic_rabbit_scene(ctx: HintEffectContext) -> dict:
    row = _get_player_row(ctx)
    if not row:
        return _result("error", "Игрок не найден", "Не удалось проверить артефакт игрока.")
    if int(row["ART"] or 0) == 3:
        description = (
            "Перед вами кролик. Судя по всему, он излучает сильную меметическую ауру, "
            "которую блокирует ваш артефакт."
        )
        return _result(
            "implemented", "Защита артефакта", description,
            protected=True,
            modal={
                "intro": "Перед вами кролик",
                "effect": description,
                "icon": "/photo/work_room/neutralresult.png",
                "iconAlt": "Меметический кролик",
            },
        )
    description = "ВЫ ВИДИТЕ ПЕРЕД СОБОЙ УЖАСНЕЙШЕЕ СУЩЕСТВО.\nВ панике вы убегаете (+75 стресса)."
    damage = core.apply_damage(
        ctx.db_path,
        int(ctx.player_id),
        sp_damage=75,
        reason="Воздействие меметического кролика",
    ) if ctx.db_path else None
    return _result(
        "implemented", "Паника", description,
        protected=False,
        damage=damage,
        player_dead=bool((damage or {}).get("is_dead")),
        modal={
            "intro": "Меметическое воздействие",
            "effect": description,
            "icon": "/photo/work_room/badresult.png",
            "iconAlt": "Меметический кролик",
        },
    )


def effect_infect_worm_eggs(ctx: HintEffectContext) -> dict:
    row = _get_player_row(ctx)
    if not row:
        return _result("error", "Игрок не найден", "Не удалось проверить ART игрока.")
    if int(row["ART"] or 0) in (2, 5):
        return _result("implemented", "Защита артефакта", "Артефакт защитил игрока от заражения.")
    if int(_get_global(ctx, "WormActive", 0) or 0) == 1:
        return _result("implemented", "Заражение уже активно", "Колония паразитов уже развивается внутри носителя.")
    current_day = int(_get_global(ctx, "CurrentDay", 1) or 1)
    _set_global(ctx, "WormActive", 1)
    _set_global(ctx, "WormStartDay", current_day)
    _set_global(ctx, "WormVictim", int(ctx.player_id))
    status = _add_player_effect(ctx, "WormEggs")
    description = "Игрок стал носителем яиц червей. Инкубационный период начался."
    return _result(
        "implemented", "Заражение паразитом", description,
        effect="WormEggs", effect_key="WormEggs", effect_script_available=True,
        duplicate=bool(status.get("duplicate")), slot=status.get("slot"),
        modal={"intro": "Заражение паразитом", "effect": description, "icon": "/photo/work_room/badresult.png", "iconAlt": "Яйца паразитов"},
    )


def effect_start_companion_doom(ctx: HintEffectContext) -> dict:
    row = _get_player_row(ctx)
    if not row:
        return _result("error", "Игрок не найден", "Не удалось проверить наличие компаньона.")
    if int(row["COMPSLOT"] or 0) == 0:
        return _result("implemented", "Нет компаньона", "У игрока сейчас нет компаньона, эффект пропущен.")
    if int(_get_global(ctx, "CompanionDoomActive", 0) or 0) == 1:
        return _result("implemented", "Проклятие уже активно", "Один из компаньонов уже поражён Ульем.")
    current_day = int(_get_global(ctx, "CurrentDay", 1) or 1)
    _set_global(ctx, "CompanionDoomActive", 1)
    _set_global(ctx, "CompanionDoomVictim", int(ctx.player_id))
    _set_global(ctx, "CompanionDoomStartDay", current_day)
    _set_global(ctx, "CompanionDoomLastTickDay", 0)
    description = "Аномалия поразила вашего компаньона. Через 3 дня он погибнет — спасти его невозможно."
    return _result(
        "implemented", "Компаньон заражён", description,
        modal={"intro": "Компаньон заражён", "effect": description, "icon": "/photo/work_room/badresult.png", "iconAlt": "Улей заразил компаньона"},
    )


def effect_crimson_infect(ctx: HintEffectContext) -> dict:
    # Нулевой пациент получает вирус непосредственно от аномалии, поэтому здесь
    # сохраняется стандартная защита Кота-висельника. Передача через укус идёт
    # отдельным принудительным обработчиком на сервере и эту защиту обходит.
    result = _add_player_effect(ctx, "CrimsonVirus")
    if (
        str(result.get("reason") or "") != "absorbed_by_companion"
        and not bool(result.get("duplicate"))
        and str(result.get("status") or "") in {"implemented", "recorded"}
    ):
        current_day = int(_get_global(ctx, "CurrentDay", 1) or 1)
        _set_global(ctx, f"CrimsonInfectedDay_{int(ctx.player_id)}", current_day)
    return result


def effect_start_train_timer(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "TrainDeadlineUserId", int(ctx.player_id))
    _set_global(ctx, "TrainDeadlineAt", time.time() + 180)
    _set_global(ctx, "TrainPausedAt", 0)
    return _result("implemented", "Таймер поезда запущен", "Для игрока сохранён дедлайн через 180 секунд.")


def effect_free_stat(ctx: HintEffectContext) -> dict:
    return _queue_event(ctx, "free_stat_offer")


def effect_attack(ctx: HintEffectContext) -> dict:
    damage = core.apply_damage(ctx.db_path, int(ctx.player_id), hp_damage=20, reason="Атака Халикоптера") if ctx.db_path else None
    return _result("implemented", "Атака Халикоптера", "Сотрудник получил 20 красного урона.", damage=damage)
def effect_choose_bonus(ctx: HintEffectContext) -> dict:
    _ensure_work_row(ctx)
    if ctx.db_path:
        with _connect(ctx.db_path, write=True) as conn:
            conn.execute(
                "UPDATE WORK SET PendingChooseBonus = 1, ChooseBonusDamage = COALESCE(ChooseBonusDamage, 5) WHERE user_id = ? AND anomaly_id = ?",
                (int(ctx.player_id), int(ctx.anomaly_id)),
            )
            conn.commit()
    return _queue_event(ctx, "choose_bonus_offer")
def effect_moon_game(ctx: HintEffectContext) -> dict:
    return _queue_event(ctx, "moon_eye_game")
def effect_check_cat_reward(ctx: HintEffectContext) -> dict:
    if int(_get_global(ctx, "CatGiveReward", 0) or 0) == 1:
        _update_player(ctx, "UPDATE PLAYERS SET BONUS = COALESCE(BONUS, 0) + 5 WHERE ID = ?", (int(ctx.player_id),))
        _set_global(ctx, "CatGiveReward", 0)
        return _result(
            "implemented",
            "Бонус получен",
            "Аномалия наградила вас постоянным бонусом в 5% к шансу успешной работы.",
            modal={
                "intro": "Успех!",
                "effect": "Аномалия наградила вас постоянным бонусом в 5% к шансу успешной работы.",
                "icon": "/photo/work_room/goodresult.png",
                "iconAlt": "Успешный результат",
            },
            reward={"bonus": 5},
        )
    return _result(
        "implemented",
        "Бонус не получен",
        "К сожалению, первая работа не соответствует запросу аномалии и бонуса нет.",
        modal={
            "intro": "Провал",
            "effect": "К сожалению, первая работа не соответствует запросу аномалии и бонуса нет.",
            "icon": "/photo/work_room/neutralresult.png",
            "iconAlt": "Нейтральный результат",
        },
        reward={"bonus": 0},
    )
def effect_moth_insta_kill(ctx: HintEffectContext) -> dict:
    damage = core.apply_damage(ctx.db_path, int(ctx.player_id), hp_damage=9999, bypass_death_shield=True, reason="Моль настигла сотрудника") if ctx.db_path else None
    return _result("implemented", "Моль настигла вас", "Сотрудник погиб.", damage=damage, player_dead=True)


def effect_sea_monster(ctx: HintEffectContext) -> dict:
    return _queue_event(ctx, "sea_monster_game")


def effect_stat_checks(ctx: HintEffectContext) -> dict:
    row = _get_player_row(ctx)
    if not row:
        return _result("missing", "Проверка характеристик", "Игрок не найден.")
    chances = {1: 20, 2: 40, 3: 60, 4: 80, 5: 100}
    labels = ("Выносливость", "Удача", "Гибкость ума", "Адаптация")
    checks = []
    for index, label in enumerate(labels, start=1):
        level = max(1, min(5, int(row[f"STAT{index}"] or 1)))
        chance = chances[level]
        roll = random.randint(1, 100)
        success = roll <= chance
        checks.append({
            "stat": f"STAT{index}", "label": label, "level": level,
            "chance": chance, "roll": roll, "success": success,
            "fill": 100 if success else max(5, min(96, int((chance / max(roll, 1)) * 100))),
        })
    failed = sum(1 for check in checks if not check["success"])
    sp_damage = failed * 30
    sp_before = int(row["SP"] or 0)
    damage = core.apply_damage(
        ctx.db_path, int(ctx.player_id), sp_damage=sp_damage,
        reason="Проверка характеристик",
    ) if ctx.db_path and sp_damage else None
    psychosis = (damage or {}).get("psychosis")
    extra_damage = None
    if ctx.db_path and sp_damage and sp_before - sp_damage <= 0 and not bool((damage or {}).get("is_dead")):
        extra_damage = core.apply_damage(
            ctx.db_path, int(ctx.player_id), hp_damage=100,
            reason="Проверка характеристик",
        )
    final_damage = extra_damage or damage
    if final_damage is not None and psychosis and not final_damage.get("psychosis"):
        final_damage["psychosis"] = psychosis
    passed = 4 - failed
    return _result(
        "implemented", "Проверка характеристик",
        f"Пройдено проверок: {passed}/4. Получено {sp_damage} урона рассудку.",
        damage=final_damage,
        event={
            "type": "stat_checks", "anomaly_id": int(ctx.anomaly_id),
            "checks": checks, "passed": passed, "failed": failed,
            "sp_damage": sp_damage, "extra_hp_damage": 100 if extra_damage else 0,
        },
        player_dead=bool((final_damage or {}).get("is_dead")),
    )
def effect_time_debt69(ctx: HintEffectContext) -> dict:
    return _add_player_effect(ctx, "TimeDebt69")
def effect_start_puppy_encounter(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "puppy_encounter")
def effect_start_nubert_dialog(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "nubert_dialog")
def effect_anomaly_portal_mushroom(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "portal_mushroom_dialog")
def effect_interdimensional_rift_global(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "global_rift_dialog")
def effect_open_contract_kill_offer(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "kill_contract_offer")
def effect_start_pandora_box(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "pandora_box_dialog")
def effect_start_instrument_anomaly(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "instrument_choice_dialog")
def effect_start_forest_tape_dialog(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "forest_tape_dialog", asset="/photo/special/anjela.png")
def effect_start_po3_trials(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "po3_trials")
def effect_start_curse_anomaly_dialog(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "curse_anomaly_dialog")
def effect_start_tenna_game(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "tenna_game")
def effect_sovuh_zombie(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "sovuh_zombie_game")
def effect_dice_anomaly(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "dice_pick_dialog")
def effect_pet_anomaly_prompt(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "pet_anomaly_prompt")
def effect_feedable_anomaly(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "feedable_anomaly_prompt")
def effect_offer_stat_conversion(ctx: HintEffectContext) -> dict: return _queue_event(ctx, "stat_conversion_offer")
def effect_bulbasaur(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 1)
def effect_ilvetal(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 2)
def effect_kurem(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 3)
def effect_cheaptrick(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 4)
def effect_genesect(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 5)
def effect_hanged_cat(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 6)
def effect_stupidreptile(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "bitecount", 3)
    return _assign_companion(ctx, 7)
def effect_stonefox(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 8)
def effect_xqc(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 9)
def effect_sprigatito(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 10)
def effect_fairy(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 11)
def effect_shnublik(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 12)
def effect_lil_zema(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 13)
def effect_salamander(ctx: HintEffectContext) -> dict: return _assign_companion(ctx, 14)
def effect_langustwasmet(ctx: HintEffectContext) -> dict:
    _ensure_work_row(ctx)
    if ctx.db_path:
        with _connect(ctx.db_path, write=True) as conn:
            conn.execute(
                """UPDATE WORK
                   SET LangustTracking = 1, LangustAffection = 0
                   WHERE user_id = ? AND anomaly_id = ?""",
                (int(ctx.player_id), int(ctx.anomaly_id)),
            )
            conn.commit()
    return _result("implemented", "Наблюдение началось", "Аномалия запомнит следующую выбранную работу.")


def effect_langustartifact(ctx: HintEffectContext) -> dict:
    _ensure_work_row(ctx)
    affection = False
    if ctx.db_path:
        with _connect(ctx.db_path, write=True) as conn:
            row = conn.execute(
                """SELECT COALESCE(LangustAffection, 0) AS affection
                   FROM WORK WHERE user_id = ? AND anomaly_id = ?""",
                (int(ctx.player_id), int(ctx.anomaly_id)),
            ).fetchone()
            affection = bool(row and int(row["affection"] or 0) == 1)
            if affection:
                conn.execute("UPDATE PLAYERS SET ART = 5 WHERE ID = ?", (int(ctx.player_id),))
            conn.execute(
                """UPDATE WORK SET LangustTracking = 0, LangustAffection = 0
                   WHERE user_id = ? AND anomaly_id = ?""",
                (int(ctx.player_id), int(ctx.anomaly_id)),
            )
            conn.commit()
    if affection:
        return _result(
            "implemented",
            "Артефакт изменён",
            "Работа «Привязанность» удовлетворила аномалию. Ваш артефакт заменён на Печать тьмы.",
            artifact_id=5,
            modal={
                "intro": "Артефакт изменён",
                "effect": "Работа «Привязанность» удовлетворила аномалию. Ваш артефакт заменён на Печать тьмы.",
                "icon": "/photo/work_room/goodresult.png",
                "iconAlt": "Артефакт изменён",
            },
        )
    return _result(
        "implemented",
        "Условие не выполнено",
        "Первая работа после подсказки не была «Привязанностью». Артефакт не изменён.",
    )
def effect_x125_meet_sleeping(ctx: HintEffectContext) -> dict:
    run_id = int(_get_global(ctx, "X125_RUN_ID", 0) or 0) + 1
    _set_global(ctx, "X125_ACTIVE", 1)
    _set_global(ctx, "X125_DONE", "")
    _set_global(ctx, "X125_EVENT_FIRED", 0)
    _set_global(ctx, "X125_EVENT_ID", 0)
    _set_global(ctx, "X125_EVENTS", [])
    _set_global(ctx, "X125_SPECIAL_EVENT_DAY", 0)
    _set_global(ctx, "X125_SPECIAL_EVENT_ID", 0)
    _set_global(ctx, "X125_RUN_ID", run_id)
    _set_global(ctx, "X125_RUN_TOKEN", int(time.time() * 1000))
    selected_owner = int(_get_global(ctx, "X125_ANOMALY_OWNER_ID", 0) or 0)
    _set_global(ctx, "X125_OWNER_ID", selected_owner if selected_owner > 0 else int(ctx.player_id))
    _set_global(ctx, "X125_BATTLE", {})
    return _result("implemented", "Х-125 спит", "Кажется, аномалия продолжает спать.")
def effect_alephsummoned(ctx: HintEffectContext) -> dict:
    current_day = 1
    if ctx.db_path:
        current_day = int(core.get_game_state(ctx.db_path).get("current_day") or 1)
    skip_pending = int(_get_global(ctx, "skipday", 0) or 0) == 1
    target_day = current_day + (2 if skip_pending else 1)
    _set_global(ctx, "alephsummoned", target_day)
    return _result(
        "implemented",
        "ALEPH призван",
        f"В пуле дня {target_day} гарантированно появится аномалия класса ALEPH.",
    )
def effect_altar_unlock(ctx: HintEffectContext) -> dict:
    return _queue_event(ctx, "altar_offering")


def effect_siph_is_sad(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "SiphIsSad", 1)
    _set_global(ctx, "SiphPunishment", 0)
    return _result("implemented", "Сиф опечален", "Штраф Сифа будет нарастать при работах на подавление.")


def effect_altar_is_met(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "altarismet", 1)
    return _result("implemented", "Алтарь угля встречен", "Защитный флаг Алтаря угля активирован.")


def effect_apply_noresult(ctx: HintEffectContext) -> dict:
    return _add_player_effect(ctx, "NoResult")


def effect_apply_voyager_curse(ctx: HintEffectContext) -> dict:
    result = _add_player_effect(ctx, "VoyagerCurse")
    player_id = int(ctx.player_id)
    _set_global(ctx, f"VoyagerCount_{player_id}", 3)
    _set_global(ctx, f"VoyagerBan_{player_id}", "")
    _set_global(ctx, f"VoyagerBanDay_{player_id}", 0)
    _set_global(ctx, f"VoyagerSolo_{player_id}", {})
    return result


def effect_baby_monster(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "babymonster", 1)
    return _result("implemented", "Дитя пробудилось", "Открытие информации об аномалиях теперь снижает шанс успешной работы.")


def effect_give_brass_sphere(ctx: HintEffectContext) -> dict:
    item_id = 35
    item_name = "Металлический шар из латуни"
    if not ctx.db_path:
        return _inventory_add(ctx, item_id, 1)
    with _connect(ctx.db_path, write=True) as conn:
        row = conn.execute("SELECT ID FROM PLAYERS WHERE ID = ?", (int(ctx.player_id),)).fetchone()
        if not row:
            return _result("error", "Игрок не найден", "Не удалось выдать латунный шар.")
        conn.execute(
            """
            UPDATE PLAYERS
            SET INVSLOT1 = ?, SLOT1AMOUNT = 1, INVSLOT2 = 1, SLOT2AMOUNT = 0
            WHERE ID = ?
            """,
            (item_id, int(ctx.player_id)),
        )
        effects = list(core.list_player_effects(ctx.db_path, int(ctx.player_id)))
        effects = [effect for effect in effects if str(effect) != "metalcrusher"]
        effects.append("metalcrusher")
        core._save_effects(conn, int(ctx.player_id), effects)
        conn.commit()
    _set_global(ctx, "BrassSphereOwner", int(ctx.player_id))
    _set_global(ctx, "BrassSphereNeedsActivate", 1)
    return _result(
        "implemented",
        "Новый предмет!",
        "Вы получили Металлический шар из латуни. Остальные предметы уничтожены. Шар необходимо активировать до конца дня.",
        item_id=item_id,
        item_name=item_name,
        amount=1,
        modal={
            "intro": "Новый предмет!",
            "effect": "Вы получили Металлический шар из латуни. Остальные предметы уничтожены. Шар необходимо активировать до конца дня.",
            "icon": "/photo/work_room/giveitem.png",
            "iconAlt": "Латунный шар",
        },
    )


def effect_remember_first_work(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "check_work", 1)
    if int(ctx.anomaly_id) in (71, 83, 100):
        _set_global(ctx, "first_work_type", "")
        _set_global(ctx, "first_work_class", 0)
        _set_global(ctx, "first_work_anomalytype", 0)
    if int(ctx.anomaly_id) == 71:
        _set_global(ctx, "LastWorkResult", -1)
        _set_global(ctx, "GuessedRight", 0)
    if int(ctx.anomaly_id) == 83:
        _set_global(ctx, "NonAnomalyClass", 0)
        _set_global(ctx, "NonAnomalyType", 0)
    return _result("implemented", "Наблюдение началось", "Следующая первая работа будет сохранена системой.")


def effect_set_train_player(ctx: HintEffectContext) -> dict:
    _set_global(ctx, "TrainPlayer", int(ctx.player_id))
    _set_global(ctx, "TrainStartedAt", int(time.time()))
    return _result("implemented", "Пассажир выбран", "Игрок назначен целью события Адского экспресса.")


def effect_start_battle_with_heli2(ctx: HintEffectContext) -> dict:
    if int(ctx.anomaly_id) == 61:
        return _queue_event(ctx, "sea_monster_game")
    return _combine_player_effect_results(
        [
            _add_player_effect(ctx, "BlockedPhoto"),
            _add_player_effect(ctx, "BlockedDescription"),
            _add_player_effect(ctx, "NoResult"),
        ]
    )


def effect_frogbonus(ctx: HintEffectContext) -> dict:
    work_type = str(_get_global(ctx, "first_work_type", "") or "").strip().lower()
    work_names = {
        "intuition": "Интуиция",
        "insight": "Понимание",
        "affection": "Привязанность",
        "suppression": "Подавление",
    }
    if work_type not in work_names:
        return _result("blocked", "Бонус лягушки", "Первая работа не определена — бонус не выдан.")
    work_name = work_names[work_type]
    if not ctx.db_path:
        return _stub(ctx, "для бонуса лягушки требуется база игроков")
    with _connect(ctx.db_path, write=True) as conn:
        row = conn.execute(
            """
            SELECT COALESCE(CP,0) AS CP, COALESCE(BONUS,0) AS BONUS,
                   COALESCE(STAT1,1) AS STAT1, COALESCE(STAT2,1) AS STAT2,
                   COALESCE(STAT3,1) AS STAT3, COALESCE(STAT4,1) AS STAT4,
                   COALESCE(HP,0) AS HP, COALESCE(MAXHP,100) AS MAXHP
            FROM PLAYERS WHERE ID = ?
            """,
            (int(ctx.player_id),),
        ).fetchone()
        if not row:
            return _result("error", "Бонус лягушки", "Игрок не найден.")
        if work_type == "intuition":
            new_bonus = int(row["BONUS"] or 0) + 5
            conn.execute("UPDATE PLAYERS SET BONUS = ? WHERE ID = ?", (new_bonus, int(ctx.player_id)))
            conn.commit()
            return _result("implemented", "Бонус лягушки", f"{work_name}: бонус исследований +5% (итого {new_bonus}%).")
        if work_type == "affection":
            new_cp = int(row["CP"] or 0) + 250
            conn.execute("UPDATE PLAYERS SET CP = ? WHERE ID = ?", (new_cp, int(ctx.player_id)))
            conn.commit()
            return _result("implemented", "Бонус лягушки", f"{work_name}: получено +250 CP (теперь {new_cp}).")
        if work_type == "suppression":
            return _result("implemented", "Бонус лягушки", f"{work_name}: бонусов нет.")

        stat_columns = ("STAT1", "STAT2", "STAT3", "STAT4")
        stats = {column: int(row[column] or 1) for column in stat_columns}
        target = min(stat_columns, key=lambda column: (stats[column], stat_columns.index(column)))
        if stats[target] >= 5:
            return _result("implemented", "Бонус лягушки", f"{work_name}: все характеристики уже достигли уровня 5.")
        stats[target] += 1
        pretty = {"STAT1": "Выносливость", "STAT2": "Удача", "STAT3": "Самоконтроль", "STAT4": "Адаптация"}
        if target == "STAT1":
            new_max_hp = int(row["MAXHP"] or 100) + 50
            new_hp = min(int(row["HP"] or 0) + 50, new_max_hp)
            conn.execute(
                "UPDATE PLAYERS SET STAT1=?, STAT2=?, STAT3=?, STAT4=?, MAXHP=?, HP=? WHERE ID=?",
                (stats["STAT1"], stats["STAT2"], stats["STAT3"], stats["STAT4"], new_max_hp, new_hp, int(ctx.player_id)),
            )
            conn.commit()
            return _result(
                "implemented", "Бонус лягушки",
                f"{work_name}: {pretty[target]} +1 (теперь {stats[target]}). MAXHP и HP увеличены на 50.",
                stat=target, new_level=stats[target], hp=new_hp, max_hp=new_max_hp,
            )
        conn.execute(
            "UPDATE PLAYERS SET STAT1=?, STAT2=?, STAT3=?, STAT4=? WHERE ID=?",
            (stats["STAT1"], stats["STAT2"], stats["STAT3"], stats["STAT4"], int(ctx.player_id)),
        )
        conn.commit()
        return _result(
            "implemented", "Бонус лягушки",
            f"{work_name}: {pretty[target]} +1 (теперь {stats[target]}).",
            stat=target, new_level=stats[target],
        )


def effect_deviloffer(ctx: HintEffectContext) -> dict:
    return _queue_event(ctx, "devil_deal_offer")


def effect_hint_with_emoji_check(ctx: HintEffectContext) -> dict:
    return _queue_event(ctx, "emoji_glasses_game")
def effect_hungry_bag(ctx: HintEffectContext) -> dict:
    if str(_get_global(ctx, "first_work_anomalytype", "")) != "3":
        if ctx.db_path:
            damage = core.apply_damage(ctx.db_path, int(ctx.player_id), hp_damage=5, sp_damage=0, reason="Голодный рюкзак: неверный тип первой работы")
        else:
            _update_player(ctx, "UPDATE PLAYERS SET HP = MAX(0, COALESCE(HP, 0) - 5) WHERE ID = ?", (int(ctx.player_id),))
            damage = None
        return _result("implemented", "Голодный рюкзак атакует", "Первая работа не была типа «Конструкт». Получено 5 урона.", damage=damage)
    return _result("implemented", "Условие не выполнено", "Первая работа была по типу 3, штраф не применён.")
def effect_hungry_bag2(ctx: HintEffectContext) -> dict:
    _ensure_work_row(ctx)
    with _connect(ctx.db_path) as conn:
        row = conn.execute("SELECT COALESCE(photounlocked, 0) AS photounlocked FROM WORK WHERE user_id = ? AND anomaly_id = ?", (int(ctx.player_id), int(ctx.anomaly_id))).fetchone()
    if row and int(row["photounlocked"] or 0) == 0:
        if ctx.db_path:
            damage = core.apply_damage(ctx.db_path, int(ctx.player_id), hp_damage=5, sp_damage=0, reason="Голодный рюкзак: фото не открыто")
        else:
            _update_player(ctx, "UPDATE PLAYERS SET HP = MAX(0, COALESCE(HP, 0) - 5) WHERE ID = ?", (int(ctx.player_id),))
            damage = None
        return _result("implemented", "Голодный рюкзак атакует", "Фото не было открыто до подсказки. Получено 5 урона.", damage=damage)
    return _result("implemented", "Условие не выполнено", "Фото уже открыто, штраф не применён.")
def effect_hungry_bag3(ctx: HintEffectContext) -> dict:
    _ensure_work_row(ctx)
    with _connect(ctx.db_path) as conn:
        row = conn.execute("SELECT COALESCE(descriptionunlocked, 0) AS descriptionunlocked FROM WORK WHERE user_id = ? AND anomaly_id = ?", (int(ctx.player_id), int(ctx.anomaly_id))).fetchone()
    if row and int(row["descriptionunlocked"] or 0) == 0:
        damage = core.apply_damage(ctx.db_path, int(ctx.player_id), hp_damage=5, reason="Голодный рюкзак: описание не открыто") if ctx.db_path else None
        return _result("implemented", "Голодный рюкзак атакует", "Описание не было открыто до подсказки. Получено 5 урона.", damage=damage)
    return _result("implemented", "Условие не выполнено", "Описание уже открыто, штраф не применён.")


def effect_izbushka_stage(ctx: HintEffectContext, stage: int) -> dict:
    work_names = {
        "intuition": "Интуиция",
        "insight": "Понимание",
        "affection": "Привязанность",
        "suppression": "Подавление",
    }
    stage = int(stage)
    if stage == 1:
        key = str(_get_global(ctx, "first_work_type", "") or "").strip()
        prediction = work_names.get(key, key or "неизвестна")
        text = f"1) Твоя первая работа была… {prediction}."
    elif stage == 2:
        _ensure_work_row(ctx)
        with _connect(ctx.db_path) as conn:
            row = conn.execute(
                "SELECT COALESCE(photounlocked, 0) AS photounlocked FROM WORK WHERE user_id = ? AND anomaly_id = ?",
                (int(ctx.player_id), int(ctx.anomaly_id)),
            ).fetchone()
        opened = bool(row and int(row["photounlocked"] or 0) >= 1)
        text = "2) Ты открыл фото до этой подсказки." if opened else "2) Ты не открыл фото до этой подсказки."
    elif stage == 3:
        try:
            actual = int(_get_global(ctx, "LastWorkResult", -1))
        except (TypeError, ValueError):
            actual = -1
        guess = random.randint(0, 10)
        guessed = actual >= 0 and guess == actual
        _set_global(ctx, "GuessedRight", 1 if guessed else 0)
        text = f"3) Твоя последняя работа принесла тебе {guess} Очков исследований."
    else:
        guessed = int(_get_global(ctx, "GuessedRight", 0) or 0) == 1
        if not guessed:
            return _result(
                "implemented", "Игра окончена", "На третьем предсказании старуха ошиблась. Вы пережили игру.",
                modal={"intro": "Игра окончена", "effect": "На третьем предсказании старуха ошиблась. Вы пережили игру.", "icon": "/photo/work_room/goodresult.png", "iconAlt": "Предсказание не сбылось"},
            )
        damage = core.apply_damage(ctx.db_path, int(ctx.player_id), hp_damage=500, reason="Стал частью Старой избушки плоти") if ctx.db_path else None
        return _result(
            "implemented", "Три верных предсказания", "Старуха угадала все три действия. Теперь вы станете частью этого дома…",
            damage=damage,
            modal={"intro": "Три верных предсказания", "effect": "Старуха угадала все три действия. Теперь вы станете частью этого дома…", "icon": "/photo/work_room/badresult.png", "iconAlt": "Игра проиграна"},
        )
    return _result(
        "implemented", f"Предсказание {stage}/3", text,
        modal={"intro": f"Предсказание {stage}/3", "effect": text, "icon": "/photo/work_room/neutralresult.png", "iconAlt": "Предсказание старухи"},
    )


def effect_cinder_idol1(ctx: HintEffectContext) -> dict:
    if int(_get_global(ctx, "altarismet", 0) or 0) == 1:
        return _result("implemented", "Эффект подавлен", "Алтарь угля защитил игроков от ярости Пепельного идола.")
    players = list(_runtime(ctx).get("active_player_ids", []))
    if not players:
        return _stub(ctx, "нет состава активной партии для массового урона")
    damage_results = []
    dead_ids = []
    for pid in players:
        damage = core.apply_damage(ctx.db_path, int(pid), hp_damage=666666, reason="Ярость Пепельного идола")
        damage_results.append({"player_id": int(pid), "damage": damage})
        if bool((damage or {}).get("is_dead")):
            dead_ids.append(int(pid))
    return _result(
        "implemented",
        "Ярость идола",
        "Всем активным игрокам нанесено 666666 урона.",
        targets=players,
        damage_results=damage_results,
        player_dead_ids=dead_ids,
    )


def effect_cinder_idol2(ctx: HintEffectContext) -> dict:
    if int(_get_global(ctx, "AlephWasStudied", 0) or 0) == 1:
        return _result("implemented", "Условие не выполнено", "Aleph уже изучен, штраф не выдан.")
    players = list(_runtime(ctx).get("active_player_ids", []))
    if not players:
        return _stub(ctx, "нет состава активной партии для массового штрафа BONUS")
    with _connect(ctx.db_path, write=True) as conn:
        conn.executemany("UPDATE PLAYERS SET BONUS = COALESCE(BONUS, 0) - 10 WHERE ID = ?", [(int(pid),) for pid in players])
        conn.commit()
    return _result("implemented", "Штраф BONUS", "Всем активным игрокам выдан BONUS -10.", targets=players)


def effect_cinder_idol3(ctx: HintEffectContext) -> dict:
    _ensure_work_row(ctx)
    with _connect(ctx.db_path) as conn:
        row = conn.execute("SELECT COALESCE(photounlocked, 0) AS photounlocked FROM WORK WHERE user_id = ? AND anomaly_id = ?", (int(ctx.player_id), int(ctx.anomaly_id))).fetchone()
    if row and int(row["photounlocked"] or 0) == 1:
        return _result("implemented", "Условие не выполнено", "Фото уже открыто, штраф не применяется.")
    players = list(_runtime(ctx).get("active_player_ids", []))
    if not players:
        return _stub(ctx, "нет состава активной партии для массового штрафа по HP")
    penalties = []
    with _connect(ctx.db_path, write=True) as conn:
        for pid in players:
            prow = conn.execute("SELECT COALESCE(MAXHP, 0) AS maxhp, COALESCE(HP, 0) AS hp FROM PLAYERS WHERE ID = ?", (int(pid),)).fetchone()
            if not prow:
                continue
            penalty = max(0, int(prow["maxhp"] or 0) - int(prow["hp"] or 0)) * 200
            penalties.append({"player_id": int(pid), "cp_loss": penalty})
            conn.execute("UPDATE PLAYERS SET CP = MAX(0, COALESCE(CP, 0) - ?) WHERE ID = ?", (penalty, int(pid)))
        conn.commit()
    return _result("implemented", "Штраф CP", "Всем активным игрокам начислен штраф за недостающее здоровье.", penalties=penalties)


def effect_cinder_idol4(ctx: HintEffectContext) -> dict:
    triggered = bool(_runtime(ctx).get("player_triggered_effects", {}).get(int(ctx.player_id), False))
    if not triggered:
        return _result("implemented", "Условие не выполнено", "У инициатора не было психоза, эффект не сработал.")
    players = list(_runtime(ctx).get("active_player_ids", []))
    if not players:
        return _stub(ctx, "нет состава активной партии для массового изменения SP")
    with _connect(ctx.db_path, write=True) as conn:
        conn.executemany("UPDATE PLAYERS SET SP = 50 WHERE ID = ?", [(int(pid),) for pid in players])
        conn.commit()
    return _result("implemented", "SP изменён", "Всем активным игрокам установлено SP = 50.", targets=players)


def effect_cinder_idol5(ctx: HintEffectContext) -> dict:
    if int(_get_global(ctx, "xprotocol", 0) or 0) != 1:
        return _result("implemented", "Эффект не сработал", "Протокол X ещё не использовался в этой игре.")
    _set_global(ctx, "idolcurse", 1)
    return _result("implemented", "Последнее проклятие идола", "Награды CP за классы аномалий начисляются в обратном порядке.")


HINT_EFFECT_HANDLERS: Dict[str, Callable[[HintEffectContext], dict]] = {
    "CinderPlague": effect_cinder_plague,
    "MothInstaKill": effect_moth_insta_kill,
    "NonAnomaly": effect_non_anomaly,
    "SeaMonster": effect_sea_monster,
    "UnderCurse2": effect_under_curse2,
    "UnderCurse3": effect_under_curse3,
    "UnderCurse4": effect_under_curse4,
    "UnderCurse5": effect_under_curse5,
    "UnderCurse6": effect_under_curse6,
    "UnderCurse7": effect_under_curse7,
    "SiphIsSad": effect_siph_is_sad,
    "altarismet": effect_altar_is_met,
    "apply_noresult_effect": effect_apply_noresult,
    "apply_voyager_curse": effect_apply_voyager_curse,
    "babymonster": effect_baby_monster,
    "give_brass_sphere": effect_give_brass_sphere,
    "remember_first_work": effect_remember_first_work,
    "set_train_player_global": effect_set_train_player,
    "start_battle_with_heli2": effect_start_battle_with_heli2,
    "alephsummoned": effect_alephsummoned,
    "altar_unlock": effect_altar_unlock,
    "anomaly_portal_mushroom": effect_anomaly_portal_mushroom,
    "apply_pisos_curse": effect_apply_pisos_curse,
    "apply_sparing_curse": effect_apply_sparing_curse,
    "attack": effect_attack,
    "berserk17meet": effect_berserk17meet,
    "bulbasaur": effect_bulbasaur,
    "catonstoveencountered": effect_catonstoveencountered,
    "cheaptrick": effect_cheaptrick,
    "check_berserk": effect_check_berserk,
    "check_cat_reward": effect_check_cat_reward,
    "choose_bonus": effect_choose_bonus,
    "cinder_idol1": effect_cinder_idol1,
    "cinder_idol2": effect_cinder_idol2,
    "cinder_idol3": effect_cinder_idol3,
    "cinder_idol4": effect_cinder_idol4,
    "cinder_idol5": effect_cinder_idol5,
    "cinderplagueupgrade": effect_cinderplague_upgrade,
    "cookie_anomaly_give": effect_cookie_anomaly_give,
    "crimson_infect": effect_crimson_infect,
    "d20curse": effect_d20curse,
    "deviloffer": effect_deviloffer,
    "dice_anomaly": effect_dice_anomaly,
    "dmg20": effect_dmg20,
    "dmg35": effect_dmg35,
    "fairy": effect_fairy,
    "feedable_anomaly": effect_feedable_anomaly,
    "fleeIsDeath": effect_flee_is_death,
    "free_stat": effect_free_stat,
    "frogbonus": effect_frogbonus,
    "genesect": effect_genesect,
    "give_item_command": effect_give_item_command,
    "give_utilizer": effect_give_utilizer,
    "grant_legend_rt": effect_grant_legend_rt,
    "grant_or_use_timeshift_drug": effect_grant_or_use_timeshift_drug,
    "grant_vicious_heart": effect_grant_vicious_heart,
    "hanged_cat": effect_hanged_cat,
    "hint_with_emoji_check": effect_hint_with_emoji_check,
    "hungry_bag": effect_hungry_bag,
    "hungry_bag2": effect_hungry_bag2,
    "hungry_bag3": effect_hungry_bag3,
    "ilvetal": effect_ilvetal,
    "infect_worm_eggs": effect_infect_worm_eggs,
    "interdimensional_rift_global": effect_interdimensional_rift_global,
    "izbushka1": lambda ctx: effect_izbushka_stage(ctx, 1),
    "izbushka2": lambda ctx: effect_izbushka_stage(ctx, 2),
    "izbushka3": lambda ctx: effect_izbushka_stage(ctx, 3),
    "izbushka4": lambda ctx: effect_izbushka_stage(ctx, 4),
    "kurem": effect_kurem,
    "langustwasmet": effect_langustwasmet,
    "langustartifact": effect_langustartifact,
    "lil_zema": effect_lil_zema,
    "memetic_rabbit_scene": effect_memetic_rabbit_scene,
    "moon_game": effect_moon_game,
    "offer_stat_conversion": effect_offer_stat_conversion,
    "open_contract_kill_offer": effect_open_contract_kill_offer,
    "pet_anomaly_prompt": effect_pet_anomaly_prompt,
    "prompt_death_shield": effect_prompt_death_shield,
    "salamander": effect_salamander,
    "shnublik": effect_shnublik,
    "skibidi": effect_skibidi,
    "skipday": effect_skip_day,
    "sovuh_zombie": effect_sovuh_zombie,
    "spread_cinder_plague": effect_spread_cinder_plague,
    "sprigatito": effect_sprigatito,
    "start_battle_with_flee_is_death": effect_start_battle_with_flee_is_death,
    "start_battle_with_heli": effect_start_battle_with_heli,
    "start_companion_doom": effect_start_companion_doom,
    "start_curse_anomaly_dialog": effect_start_curse_anomaly_dialog,
    "start_forest_tape_dialog": effect_start_forest_tape_dialog,
    "start_instrument_anomaly": effect_start_instrument_anomaly,
    "start_nubert_dialog": effect_start_nubert_dialog,
    "start_pandora_box": effect_start_pandora_box,
    "start_po3_trials": effect_start_po3_trials,
    "start_puppy_encounter": effect_start_puppy_encounter,
    "start_tenna_game": effect_start_tenna_game,
    "start_train_timer": effect_start_train_timer,
    "stat_checks": effect_stat_checks,
    "TimeDebt69": effect_time_debt69,
    "steal_cp1": effect_steal_cp1,
    "steal_cp2": effect_steal_cp2,
    "steal_stat4_level": effect_steal_stat4,
    "stonefox": effect_stonefox,
    "stupidreptile": effect_stupidreptile,
    "violin_force_give_to": effect_violin_force_give_to,
    "witness_curse": effect_witness_curse,
    "x125_meet_sleeping": effect_x125_meet_sleeping,
    "xqc": effect_xqc,
}


def execute_hint_effect(effect_name: str, *, player_id: int, anomaly_id: int, hint_slot: Optional[int] = None, db_path: Optional[Path] = None, runtime_state: Optional[dict] = None) -> dict:
    handler = HINT_EFFECT_HANDLERS.get(effect_name)
    if handler is None:
        return _result("missing", "Эффект не найден", f"Для `{effect_name}` пока нет обработчика в anomaly_effects.py.")
    ctx = HintEffectContext(player_id=int(player_id), anomaly_id=int(anomaly_id), effect_name=effect_name, hint_slot=hint_slot, db_path=db_path, runtime_state=runtime_state)
    return handler(ctx)


__all__ = [
    "HINT_EFFECTS_BY_ANOMALY",
    "HINT_EFFECT_HANDLERS",
    "PLAYER_EFFECT_HANDLERS",
    "HintEffectContext",
    "apply_player_effect",
    "execute_hint_effect",
]
