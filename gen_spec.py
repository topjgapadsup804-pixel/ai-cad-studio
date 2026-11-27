"""
30.2 坪標準三房兩廳兩衛雙陽台（11,600 × 9,600 mm 軸線，外包 11,840 × 9,840 mm）
建築平面、立體空間與水電管線模型生成腳本。
"""
import json
import math
import sys


def H(y, x0, x1, t, bearing=False, ops=(), flush=None):
    w = {"a": [x0, y], "b": [x1, y], "t": t, "bearing": bearing}
    if flush:
        w["flush"] = flush
    if ops:
        w["openings"] = list(ops)
    return w


def V(x, y0, y1, t, bearing=False, ops=(), flush=None):
    w = {"a": [x, y0], "b": [x, y1], "t": t, "bearing": bearing}
    if flush:
        w["flush"] = flush
    if ops:
        w["openings"] = list(ops)
    return w


def F(key, x, y, rot=0, **kw):
    d = {"key": key, "at": [x, y], "rot": rot}
    d.update(kw)
    return d


EX = 240
SW = 200
PT = 120

walls = [
    # 1. 北外牆（書房外牆 + 玄關入戶牆 + 生活陽台外沿齊平欄板）
    H(0, 0, 3800, EX, True, [
        {"type": "window", "from": 950, "to": 2750, "sill": 900, "head": 2400}
    ]),
    H(0, 3800, 8200, EX, True, [
        {"type": "unequal", "from": 5450, "to": 6550, "hinge": "from", "into": [5950, 900], "entry": True}
    ]),
    H(0, 8200, 11600, PT, False, [
        {"type": "hole", "from": 8500, "to": 11300, "sill": 1100}
    ], flush="N"),

    # 2. 南外牆（主臥外牆 + 景觀陽台外沿齊平欄板 + 次臥外牆）
    H(9600, 0, 3800, EX, True, [
        {"type": "window", "from": 800, "to": 3000, "sill": 500, "head": 2400}
    ]),
    H(9600, 3800, 8200, PT, False, [
        {"type": "hole", "from": 4100, "to": 7900, "sill": 1100}
    ], flush="S"),
    H(9600, 8200, 11600, EX, True, [
        {"type": "window", "from": 9000, "to": 10800, "sill": 900, "head": 2400}
    ]),

    # 3. 西外牆（主衛設高窗明衛）
    V(0, 0, 9600, EX, True, [
        {"type": "highWindow", "from": 3650, "to": 4450, "sill": 1500, "head": 2100}
    ]),

    # 4. 東外牆（生活陽台 + 廚房採光窗 + 次臥）
    V(11600, 0, 1650, EX, True),
    V(11600, 1650, 9600, EX, True, [
        {"type": "window", "from": 2300, "to": 3700, "sill": 950, "head": 2400}
    ]),

    # 5. 西翼縱向承重剪力牆 x=3800（書房門、公衛門、主臥門）
    V(3800, 0, 9600, SW, True, [
        {"type": "door", "from": 2050, "to": 2950, "hinge": "to", "into": [3200, 2500]},
        {"type": "door", "from": 3700, "to": 4450, "hinge": "from", "into": [3200, 3900]},
        {"type": "door", "from": 5300, "to": 6200, "hinge": "from", "into": [3200, 5750]}
    ]),

    # 6. 東翼縱向承重剪力牆 x=8200（廚房玻璃推拉門、次臥門）
    V(8200, 0, 9600, SW, True, [
        {"type": "sliding", "from": 2200, "to": 3600},
        {"type": "door", "from": 4680, "to": 5550, "hinge": "from", "into": [8800, 5100]}
    ]),

    # 7. 西翼橫隔牆：書房/雙衛 y=3100、主公衛分界 x=1850、雙衛/主臥 y=5100（主衛推拉門）
    H(3100, 0, 3800, PT, False),
    V(1850, 3100, 5100, PT, False),
    H(5100, 0, 3800, PT, False, [
        {"type": "sliding", "from": 900, "to": 1680}
    ]),

    # 8. 客廳與景觀陽台分界牆 y=8000（東側預留 1,250mm 沙發牆垛，推拉門 4650..6850）
    H(8000, 3800, 8200, EX, True, [
        {"type": "sliding", "from": 4650, "to": 6850}
    ]),

    # 9. 東翼橫隔牆：生活陽台/廚房 y=1650（門軸在西端，把手側留實牆裝開關）、廚房/次臥 y=4550
    H(1650, 8200, 11600, EX, True, [
        {"type": "door", "from": 9450, "to": 10250, "hinge": "from", "into": [9850, 1100]}
    ]),
    H(4550, 8200, 11600, PT, False),
]

rooms = [
    {
        "at": [6000, 5800],
        "name": "客餐厅",
        "mat": "marble",
        "wallMat": "latexWarm",
        "ceil": {"type": "tray", "drop": 220, "edgeW": 420, "drop2": 130, "edgeW2": 280, "cove": True, "curtain": 200},
        "tile": {"w": 800, "h": 800, "gap": 2, "pattern": "grid", "tex": "marble", "color": "#ebe7df", "grout": "#c9c3b8"}
    },
    {
        "at": [6000, 8800],
        "name": "景观阳台",
        "mat": "deck"
    },
    {
        "at": [1900, 7400],
        "name": "主卧",
        "mat": "herring",
        "wallMat": "latexWarm",
        "ceil": {"type": "edge", "drop": 180, "edgeW": 380, "cove": True, "curtain": 200}
    },
    {
        "at": [950, 4200],
        "name": "主卫",
        "mat": "bath",
        "wallMat": "wallTile",
        "ceil": {"type": "alu", "drop": 300}
    },
    {
        "at": [2800, 4200],
        "name": "公卫",
        "mat": "bath",
        "wallMat": "wallTile",
        "ceil": {"type": "alu", "drop": 300}
    },
    {
        "at": [1900, 1600],
        "name": "书房",
        "mat": "oak",
        "wallMat": "latexSage",
        "ceil": {"type": "flat", "drop": 120, "curtain": 200, "cornice": True}
    },
    {
        "at": [9800, 7200],
        "name": "次卧",
        "mat": "oak",
        "wallMat": "latexWarm",
        "ceil": {"type": "edge", "drop": 180, "edgeW": 350, "cove": True, "curtain": 200}
    },
    {
        "at": [9800, 3000],
        "name": "厨房",
        "mat": "bath",
        "wallMat": "wallTile",
        "ceil": {"type": "alu", "drop": 300}
    },
    {
        "at": [9800, 850],
        "name": "生活阳台",
        "mat": "bath"
    },
]

furniture = [
    # --- 玄關（x: 3900..8100, y: 120..1900）---
    F("cabShoe", 4090, 1050, 270, w=1300, d=380),
    F("sideboard", 7380, 320, 0, w=1200, d=400),
    F("entryBench", 7925, 1220, 90, w=880, d=350),
    F("doormat", 6000, 480, 0, w=900, d=600),

    # --- 餐廳（x: 3900..8100, y: 1900..4400）---
    F("diningTable6", 5800, 2900, 0, w=1800, d=900),
    F("chair", 5400, 2340, 0),
    F("chair", 6200, 2340, 0),
    F("chair", 5400, 3460, 180),
    F("chair", 6200, 3460, 180),

    # --- 客廳（x: 3900..8100, y: 5400..7880）---
    # 沙發收進東側 1,250mm 牆垛內，茶几與電視櫃之間留出 1,800mm 主動線淨寬
    F("wallPanel", 8070, 6750, 90, w=2150, d=60, opt={"style": "slat"}),
    F("sofa", 7650, 6750, 90, w=2050, d=900),
    F("rug", 6450, 6750, 90, w=2200, d=1600),
    F("ovalCoffee", 6450, 6750, 90, w=1150, d=600),
    F("armchair", 6450, 5480, 0, w=740, d=740),
    F("tvCabinet", 4100, 6950, 270, w=1500, d=400),
    F("wallTV", 3930, 6950, 270, w=1350, d=60),
    F("acWall", 8000, 4100, 90),
    F("plant", 7820, 3920, 0, w=450, d=450),
    F("curtain", 5750, 7800, 180, w=2500, d=160),

    # --- 景觀陽台（x: 3900..8100, y: 8120..9600）---
    F("lounge", 4550, 8880, 270, w=700, d=750),
    F("sideTable", 5250, 8880, 0, w=450, d=450),
    F("plantShelf", 7450, 8980, 90, w=900, d=350),

    # --- 主臥（x: 120..3700, y: 5160..9480）---
    F("wallPanel", 150, 7450, 270, w=2800, d=60, opt={"style": "soft"}),
    F("bed18", 1230, 7450, 270, w=1800, d=2100),
    F("nightstand", 390, 6250, 270, w=500, d=420),
    F("nightstand", 390, 8650, 270, w=500, d=420),
    F("rug", 1650, 7450, 270, w=2300, d=1800),
    F("cabWardrobe", 3400, 7550, 90, w=2400, d=600),
    F("acWall", 250, 5650, 270),
    F("curtain", 1900, 9400, 180, w=2500, d=160),

    # --- 主衛（x: 120..1790, y: 3160..5040）---
    F("shower", 1340, 3610, 0, w=900, d=900),
    F("smartToilet", 520, 3510, 0, w=400, d=700),
    F("waterHeater", 520, 3385, 0, w=700, d=420),
    F("vanity", 490, 4800, 180, w=720, d=480),
    F("bathHeater", 950, 4150, 0),

    # --- 公衛（x: 1910..3700, y: 3160..5040）---
    F("shower", 2360, 3610, 0, w=900, d=900),
    F("toilet", 2260, 4620, 270, w=400, d=700),
    F("waterHeater", 2135, 4620, 270, w=700, d=420),
    F("vanity", 3220, 4790, 180, w=800, d=500),
    F("bathHeater", 2850, 4150, 0),

    # --- 書房（x: 120..3700, y: 120..3040）---
    F("bed12", 1120, 2320, 270, w=1200, d=2000),
    F("wardrobe3", 3400, 1050, 90, w=1450, d=600),
    F("desk", 1850, 770, 0, w=1200, d=600),
    F("officeChair", 1850, 1380, 180),
    F("bookshelf", 300, 950, 270, w=900, d=350),
    F("acWall", 250, 2320, 270),
    F("curtain", 1850, 200, 0, w=2100, d=160),

    # --- 廚房（x: 8300..11480, y: 1770..4490）---
    F("counter", 9500, 4190, 180, w=2200, d=600),
    F("fridgeDouble", 11020, 4120, 180, w=880, d=720),
    F("gasHeater", 9000, 1860, 0),

    # --- 生活陽台（x: 8300..11480, y: 0..1530）---
    F("laundryCabinet", 8625, 820, 270, w=1350, d=650),
    F("clothesRack", 10100, 750, 0, w=2000, d=450),
    F("acOutdoor", 11250, 480, 90, w=800, d=320),

    # --- 次臥（x: 8300..11480, y: 4610..9480）---
    F("wallPanel", 11450, 7350, 90, w=2400, d=60, opt={"style": "flat"}),
    F("bed15", 10455, 7350, 90, w=1500, d=2050),
    F("nightstand", 11240, 6250, 90, w=500, d=420),
    F("nightstand", 11240, 8450, 90, w=500, d=420),
    F("cabWardrobe", 8600, 7350, 270, w=2100, d=600),
    F("desk", 10650, 4910, 0, w=1200, d=600),
    F("officeChair", 10650, 5520, 180),
    F("acWall", 11350, 5500, 90),
    F("curtain", 9900, 9400, 180, w=2100, d=160),
]

structs = [
    # 廚房排煙道（東北角）與給排水管道間（西北角）
    {"kind": "flue", "at": [11280, 1950], "w": 400, "d": 350},
    {"kind": "shaft", "at": [8450, 1910], "w": 300, "d": 280},
    # 地漏：主衛、公衛、景觀陽台、生活陽台
    {"kind": "drain", "at": [1340, 3610]},
    {"kind": "drain", "at": [1050, 4750]},
    {"kind": "drain", "at": [2360, 3610]},
    {"kind": "drain", "at": [2800, 4300]},
    {"kind": "drain", "at": [7850, 9300]},
    {"kind": "drain", "at": [9150, 1380]},
]

for f in furniture:
    if f["key"] in ("toilet", "smartToilet", "wallToilet"):
        a = math.radians(f["rot"])
        sx = round((f["at"][0] + 45 * math.sin(a)) / 5) * 5
        sy = round((f["at"][1] - 45 * math.cos(a)) / 5) * 5
        structs.append({"kind": "sewer", "at": [sx, sy]})

spec = {
    "name": "DraftPro Studio · 30.2坪標準三房兩廳兩衛",
    "height": 2850,
    "phase": "renovate",
    "north": 0,
    "site": {"city": "上海", "month": 11},
    "style": "modern",
    "walls": walls,
    "rooms": rooms,
    "structs": structs,
    "furniture": furniture,
    "autoElec": True,
}

out_path = sys.argv[1] if len(sys.argv) > 1 else "spec.json"
with open(out_path, "w", encoding="utf-8") as fp:
    json.dump(spec, fp, ensure_ascii=False, indent=2)
print("Generated", out_path, "walls=", len(walls), "furniture=", len(furniture))
