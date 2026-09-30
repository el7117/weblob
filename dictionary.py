from typing import Dict, List, Set, Optional, TypedDict

class CurseInfo(TypedDict):
    name: str
    desc: str

class BlessInfo(TypedDict):
    name: str
    desc: str

class NeutralInfo(TypedDict):
    name: str
    desc: str

class EffectInfo(TypedDict):
    name: str
    desc: str

# Основной словарь (ключи int)
PSYCHOSIS_EFFECTS: Dict[int, EffectInfo] = {
    1001: {"name": "[Психоз]Никтофобия",     "desc": "Получает +10 урона от тёмных"},
    1002: {"name": "[Психоз]Биофобия",       "desc": "Получает +10 урона от природных"},
    1003: {"name": "[Психоз]Теофобия",       "desc": "Получает +10 урона от абстрактных"},
    1004: {"name": "[Психоз]Антропофобия",   "desc": "Получает +10 урона от гуманоидов"},
    1005: {"name": "[Психоз]Технофобия",     "desc": "Получает +10 урона от конструктов"},
    1006: {"name": "[Психоз]Ничего",         "desc": "Абсолютно ничего не произошло"},
    1007: {"name": "[Психоз]Прозрение",      "desc": "Единоразово снижает текущий стресс на 50"},
    1008: {"name": "[Психоз]Мазохизм",       "desc": "Единоразово получает 20 красного урона"},
    1009: {"name": "[Психоз]Паника",         "desc": "Невозможно провести работу на ПРИВЯЗАННОСТЬ"},
    1010: {"name": "[Психоз]Ярость",         "desc": "Невозможно провести работу на ПОНИМАНИЕ"},
}

# Строковое представление ключей (если в JSON эффекты как "1006")
PSYCHOSIS_EFFECTS_S: Dict[str, EffectInfo] = {str(k): v for k, v in PSYCHOSIS_EFFECTS.items()}


CURSES_CATALOG: Dict[str, CurseInfo] = {
    "SparingCurse": {
        "name": "Проклятье Спаринга",
        "desc": "Пока кто-то не изучит Алефа, прокачать навыки выше 3 не получится",
    },
    "FleeIsDeath": {
        "name": "Бегство — смерть",
        "desc": "Любая попытка сбежать приводит к мгновенной гибели.",
    },
    "IlvitalWeakening": {
        "name": "Печать Ильветалля",
        "desc": "Дает бонус к характеристикам... но не навсегда",
    },
    "PisosCurse": {
        "name": "Проклятье Романа",
        "desc": "Каждый раз при использовании привязанности добавляется минимальный штраф изучения 5%, который нельзя сбросить.",
    },
    "CinderPlague": {
        "name": "Пепельная чума",
        "desc": "Даёт +10% шанса работ на Aleph и −10% на WAW. Может прогрессировать.",
    },
    "UnderCurse2": {
        "name": "Проклятье Undercards 2",
        "desc": "Любая работа не на подавление снижает максимальное и текущее здоровье на 5.",
    },
    "UnderCurse3": {
        "name": "Проклятье Undercards 3",
        "desc": "Количество очков исследований после работы с этой аномалией всегда на 2 меньше (не влияет на порог урона).",
    },
    "MothInstantDeath": {
        "name": "Моль тебя убьет",
        "desc": "От моли не сбежать...",
    },
    "DevilsDeal": {
        "name": "Метка дьявола",
        "desc": "Дар в обмен на здоровье. Такова цена сделки.",
    },
    "witness_curse": {
        "name": "Проклятье свидетеля",
        "desc": "При психозе положительный/нейтральный эффект не сможет выпасть.",
    },
    "VoyagerCurse": {
        "name": "Преследование Вояжера",
        "desc": "Никто еще не выживал после встречи с ним...",
    },
    "RingRedKingOn": {
        "name": "Кольцо красного короля активно",
        "desc": "Весь урон обращен в черный.",
    },
    "PANACEA_DOOM_IN": {
        "name": "Побочный эффект панацеи",
        "desc": "Скоро станет известно...",
    },
    "WormEggs": {
        "name": "Заражение паразитом",
        "desc": "Летальный исход наступит по истечению инкубационного периода.",
    },
    "CrimsonVirus": {
        "name": "Багровый вирус",
        "desc": "Жажда крови неутолима.",
    },
    "PO3_LOSER": {
        "name": "Не прошёл испытание PO-3",
        "desc": "С позором провалил испытание.",
    },
    "skibidi": {
        "name": "СКИБИДИ",
        "desc": "СКИБИДИ ДОБ ДОБ ЙЕС ЙЕС (весь текст теперь такой...)",
    },
    "BlockedPhoto": {
        "name": "Блокировка базовой информации",
        "desc": "До конца текущего исследования нельзя открыть базовую информацию об аномалии.",
    },
    "BlockedDescription": {
        "name": "Блокировка описания",
        "desc": "До конца текущего исследования нельзя открыть полное описание аномалии.",
    },
    "crimson_infect": {
        "name": "Багровый вирус",
        "desc": "Жажда крови неутолима.",
    },
    "NoResult": {
        "name": "Подавление результата",
        "desc": "Результаты работ остаются неизвестными. Проклятие снимется, если завершить исследование аномалии; побег сохранит его до конца игры.",
    },
    "NoResultPermanent": {
        "name": "Подавление результата",
        "desc": "После побега результаты всех работ останутся неизвестными до конца игры.",
    },
    "metalcrusher": {
        "name": "Латунный шар активирован",
        "desc": "Если не использовать его до конца дня - убьет владельца",
    },
}

BLESS_CATALOG: Dict[str, BlessInfo] = {
    "Comp13Applied": {
        "name": "Бонус Зёмы",
        "desc": "Зёма даёт +5% исследований, будучи компаньоном.",
    },
    "SALA_SHIELD_CUR": {
        "name": "Щит Саламандры",
        "desc": "Принимает урон на себя, пока это возможно.",
    },
    "SALA_MULT": {
        "name": "Усиленная саламандра",
        "desc": "Саламандра вдвое эффективнее.",
    },
    "death_shield": {
        "name": "Универсальный щит от смерти",
        "desc": "Взамен за 50% СО даёт одноразовый щит от смерти.",
    },
}

NEUTRAL_CATALOG: Dict[str, NeutralInfo] = {  # ← было BlessInfo
    "TimeDebt69": {
        "name": "Отсроченный урон",
        "desc": "Каждая проведённая работа приближает расплату. Урон от неудачных работ накапливается и будет нанесён одновременно после двенадцатой работы.",
    },
    "TimeShiftDrug": {
        "name": "ПВС",
        "desc": "Снижает входящий урон до 1, но каждое исследование наносит накопительный урон, который бьёт HP+SP в конце дня.",
    },
    "TSD_ACC": {
        "name": "Накопленный урон ПВС",
        "desc": "Каждые 25 накопленного урона понижает эффективность снижения на 1.",
    },
    "cookie_m_eaten": {
        "name": "Материальное печенье",
        "desc": "Очень вкусное шоколадное печенье.",
    },
    "cookie_a_eaten": {
        "name": "Антиматериальное печенье",
        "desc": "Неописуемый вкус... Пустоты?",
    },
    "timeshift_drug_active": {
        "name": "Активный ПВС",
        "desc": "Препарат временного сдвига активирован аномалией.",
    },
}

HIDE_EFFECTS = {
    "TSD_ACC", "HOTDOG_PEND", "comp9_next", "A69_HP", "A69_SP", "A69_CNT",
    "CLAY_ABSORB", "SALA_SHIELD", "TOK_EXTRA_CUR", "RING_RED_KING_ON", "VYJ_CNT", "BRASS_NEEDS_ACTIVATE",
    "crimson_last_bite_day", "VYJ_ACTIVE", "GuitarTurnsLeft", "BlockedPhoto", "BlockedDescription", "SALA_MULT", "Comp11Left", "sue_saved", "ART1COUNT", "LovecraftHotDog"
}

def base_key(s: object) -> str:
    """'TSD_ACC=10' → 'TSD_ACC'; число/None → ''"""
    t = "" if s is None else str(s)
    return t.split("=", 1)[0] if "=" in t else t

def render_effect_lines(effects: List[object]) -> List[str]:
    """
    Преобразует список эффектов из JSON в человекочитаемые строки:
    - психозы как int / '1007' → берутся из PSYCHOSIS_EFFECTS
    - строковые ключи → CURSES_CATALOG / BLESS_CATALOG / NEUTRAL_CATALOG
    - всё лишнее из HIDE_EFFECTS скрываем
    """
    seen: Set[str] = set()
    lines: List[str] = []

    for raw in (effects or []):
        # 1) Психозы (в JSON могут быть числами или строками-числами)
        if isinstance(raw, int) or (isinstance(raw, str) and raw.strip().isdigit()):
            pid = int(raw)
            info = PSYCHOSIS_EFFECTS.get(pid)
            key_seen = f"psychosis:{pid}"
            if info and key_seen not in seen:
                lines.append(f"• **{info['name']}** — {info['desc']}")
                seen.add(key_seen)
            continue  # к строковым токенам не переходим

        # 2) Строковые эффекты (возможен формат "TOKEN=123")
        if not isinstance(raw, str):
            continue
        key = raw.split("=", 1)[0].strip()
        if not key or key.lower() in {hidden.lower() for hidden in HIDE_EFFECTS} or key in seen:
            continue
        seen.add(key)

        info = CURSES_CATALOG.get(key) or BLESS_CATALOG.get(key) or NEUTRAL_CATALOG.get(key)
        if info:
            lines.append(f"• **{info['name']}** — {info['desc']}")
        else:
            lines.append(f"• `{key}`")

    return lines

__all__ = [
    "CURSES_CATALOG",
    "BLESS_CATALOG",
    "NEUTRAL_CATALOG",
    "HIDE_EFFECTS",
    "base_key",
    "render_effect_lines",
]

