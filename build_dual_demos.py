"""
雙語版本建置腳本（繁體中文 TC + 英文 EN，內建帳號登入 + Pro 授權解鎖 + CAD/PDF 匯出付費牆）：
1. 頂部整合導覽列 (studio-global-nav) 做為 .app flex-direction: column 的首個子元素 (in-flow)，零遮擋。
2. 完整登入/註冊系統（Email + WebCrypto SHA-256 密碼雜湊 + 帳號狀態管理）。
3. Pro 授權機制：
   - 支援 Gumroad / LemonSqueezy 即時線上驗證 API（填入 productId 即可自動啟用）
   - 支援離線校驗碼授權金鑰（DPRO-XXXX-XXXX-XXXX），業主收到匯款即可用 gen_license_key.py 1 秒發卡
   - 自動攔截高價值商業匯出（A3 PDF 施工圖、CAD DXF 國標/裝修/水電圖、客戶分享檔），未登入引導登入、免費版引導升級 Pro
4. 繁體中文版 (demo.html & demo-zh-tw.html) 與 英文國際版 (demo-en.html)。
"""
import copy
import json
import os
import subprocess
import sys
from opencc import OpenCC

here = os.path.dirname(os.path.abspath(__file__))
skill_dir = r"C:\Users\jack5\.gemini\config\skills\house-plan-designer"
template_src = os.path.join(skill_dir, "assets", "template.html")
build_py = os.path.join(skill_dir, "scripts", "build.py")

with open(template_src, encoding="utf-8") as f:
    orig_template = f.read()

base_spec = json.load(open(os.path.join(here, "spec.json"), encoding="utf-8"))

# ==========================================
# 1. 繁體中文版 Spec (臺灣建築圖說規範)
# ==========================================
tw_room_names = {
    "客餐厅": "客餐廳",
    "景观阳台": "景觀陽台",
    "生活阳台": "工作陽台",
    "主卧": "主臥",
    "次卧": "次臥",
    "书房": "書房",
    "厨房": "廚房",
    "主卫": "主衛",
    "公卫": "客衛",
}

# 2026 台灣室內裝修真實市場單價表（NTD，依連工帶料行情換算為引擎對應單位）
TW_NTD_PRICES = {
    "floor.oak": 1680,        # 超耐磨/橡木地板連工帶料 (~NT$5,550/坪)
    "floor.custom": 2050,     # 客製排磚地磚連工帶料 (~NT$6,800/坪)
    "floor.walnut": 2360,     # 胡桃實木複合地板 (~NT$7,800/坪)
    "floor.herring": 2880,    # 人字拼木地板 (~NT$9,500/坪)
    "floor.tile": 2050,       # 80x80 拋光石英磚 (~NT$6,800/坪)
    "floor.marble": 5450,     # 大理石石材連工帶料 (~NT$18,000/坪)
    "floor.cement": 3320,     # 磐多魔/微水泥無縫地坪 (~NT$11,000/坪)
    "floor.carpet": 1050,     # 方塊地毯 (~NT$3,500/坪)
    "floor.bath": 1960,       # 衛浴止滑地磚 (~NT$6,500/坪)
    "floor.terrazzo": 2420,   # 水磨石磚 (~NT$8,000/坪)
    "floor.deck": 2580,       # 戶外塑木地板 (~NT$8,500/坪)
    "wall.latexWhite": 580,   # 得利/虹牌乳膠漆批土刷漆 (~NT$1,900/坪)
    "wall.latexGrey": 620,    # 跳色乳膠漆批土刷漆 (~NT$2,050/坪)
    "wall.latexSage": 620,
    "wall.latexWarm": 620,
    "wall.wallpaper": 850,    # 防焰壁布/壁紙含底處理 (~NT$2,800/坪)
    "wall.wallTile": 2000,     # 衛浴/廚房壁磚鋪貼 (~NT$6,600/坪)
    "wall.woodPanel": 3800,   # 科定木皮板/木飾面造型牆 (~NT$12,500/坪)
    "wall.waterproof": 1350,  # 衛浴彈泥防水至1.8m高 (~NT$4,450/坪)
    "skirting.wood": 320,     # 木作/實木踢腳板 (NT$/m)
    "skirting.metal": 520,    # 鋁合金收邊踢腳板 (NT$/m)
    "ceil.paint": 480,        # 原頂批土乳膠漆 (~NT$1,600/坪)
    "ceil.flat": 1400,        # 日本麗仕矽酸鈣板平釘天花 (~NT$4,600/坪)
    "ceil.edge": 1680,        # 造型包樑/雙眼皮邊吊天花 (~NT$5,550/坪)
    "ceil.cove": 950,         # 間接照明層板燈槽 (NT$/m)
    "ceil.tray": 2150,        # 疊級造型天花板 (~NT$7,100/坪)
    "ceil.float": 2450,       # 懸浮造型天花含燈槽 (~NT$8,100/坪)
    "ceil.alu": 1550,         # 廚衛鋁扣板防潮天花 (~NT$5,100/坪)
    "ceil.wood": 3900,        # 實木格柵/木皮天花 (~NT$12,900/坪)
    "ceil.cornice": 280,      # 線板收邊 (NT$/m)
    "ceil.curtain": 1150,     # 木作窗簾盒 (NT$/m)
    "light.strip": 420,       # LED 鋁槽燈帶含變壓器 (NT$/m)
    "light.linear": 1250,     # 嵌入式線型燈 (NT$/m)
    "light.track": 2200,      # 磁吸軌道燈含燈具 (NT$/m)
    "demo.wall": 1100,        # 拆除隔間牆 (~NT$3,600/坪)
    "build.wall": 2450,       # 新砌輕質磚/輕鋼架隔間牆 (~NT$8,100/坪)
    "demo.waste": 14000,      # 廢棄物搬運清運車資 (NT$/車次)
    "door.door": 12500,       # 室內木作/實木貼皮門含門框五金 (NT$/樘)
    "door.double": 24000,     # 雙開門含框五金 (NT$/樘)
    "door.sliding": 18500,    # 鋁框玻璃連動拉門 (NT$/樘)
    "door.hole": 4800,        # 門洞木作包框收邊 (NT$/樘)
    "door.unequal": 32000,    # 玄關防火子母門含電子鎖安裝 (NT$/樘)
    "door.folding": 26000,    # 折疊門含五金軌道 (NT$/樘)
    "door.pocket": 22000,     # 隱藏式口袋滑門含預埋軌道 (NT$/樘)
    "win.rail": 2800,         # 陽台隱形鐵窗/欄杆 (NT$/m)
    "elec.socket": 1200,      # 強電插座/開關迴路配管配線 (NT$/位)
    "elec.light": 650,        # 燈具出線開孔安裝 (NT$/位)
    "elec.weak": 1350,        # 弱電網路 Cat.6 / 電視點位 (NT$/位)
    "elec.water": 2600,       # 冷熱給水不鏽鋼壓接管配置 (NT$/位)
    "elec.waste": 2200,       # PVC 排水管移位配置 (NT$/位)
    "elec.hvac": 1200,        # 冷氣洗孔/穿樑套管 (NT$/處)
    "elec.gas": 3500,         # 瓦斯管線配置申請 (NT$/處)
    "elec.panel": 9500,       # 士林/國際牌無熔絲開關分電盤更新 (NT$/組)
    "elec.weakbox": 4500,     # 弱電整合箱 (NT$/組)
    "cab.tall": 6200,         # E1-V313 系統高櫃/衣櫃 (~NT$580/才 投影計)
    "cab.base": 6800,         # 系統矮櫃/地櫃 (NT$/m)
    "cab.wall": 4800,         # 系統吊櫃 (NT$/m)
    "kit.base": 8500,         # 廚具下櫃桶身五金 (NT$/m)
    "kit.wall": 5500,         # 廚具吊櫃 (NT$/m)
    "kit.top": 6500,          # 石英石/賽麗石廚具檯面 (NT$/m)
    "kit.tall": 7200,         # 廚具電器高櫃 (NT$/㎡)
    "fee.manage": 8,          # 台灣室內裝修工程監工管理費 (%)
}

EN_USD_PRICES = {k: (v if k == "fee.manage" else max(8, round(v / 31.5))) for k, v in TW_NTD_PRICES.items()}

spec_tw = copy.deepcopy(base_spec)
spec_tw["name"] = "DraftPro Studio · 30.2 坪標準三房兩廳兩衛"
spec_tw["prices"] = TW_NTD_PRICES
for r in spec_tw["rooms"]:
    if r["name"] in tw_room_names:
        r["name"] = tw_room_names[r["name"]]

with open(os.path.join(here, "spec_zh_tw.json"), "w", encoding="utf-8") as f:
    json.dump(spec_tw, f, ensure_ascii=False, indent=2)

# ==========================================
# 2. 英文國際版 Spec (International English)
# ==========================================
en_room_names = {
    "客餐厅": "Living & Dining",
    "景观阳台": "Front Balcony",
    "生活阳台": "Utility Balcony",
    "主卧": "Master Bedroom",
    "次卧": "Bedroom 2",
    "书房": "Study",
    "厨房": "Kitchen",
    "主卫": "Master Bath",
    "公卫": "Guest Bath",
}

spec_en = copy.deepcopy(base_spec)
spec_en["name"] = "DraftPro Studio · 100㎡ (1,076 sq ft) 3BR/2BA Floor Plan"
spec_en["prices"] = EN_USD_PRICES
for r in spec_en["rooms"]:
    if r["name"] in en_room_names:
        r["name"] = en_room_names[r["name"]]

with open(os.path.join(here, "spec_en.json"), "w", encoding="utf-8") as f:
    json.dump(spec_en, f, ensure_ascii=False, indent=2)

# ==========================================
# 3. 繁體中文版 Template (OpenCC + 臺灣建築術語)
# ==========================================
cc_tw = OpenCC("s2tw")
tw_template = cc_tw.convert(orig_template)
tw_template = tw_template.replace(
    '"PingFang SC","Microsoft YaHei"',
    '"PingFang TC","Microsoft JhengHei","Noto Sans TC","PingFang SC"',
)
tw_terms = [
    ('location.search.includes("debug")&&(window.__designer=', '(window.__designer='),
    ('const Oo=t=>"¥"+Math.round(t).toLocaleString("en-US")', 'const Oo=t=>"NT$ "+Math.round(t).toLocaleString("en-US")'),
    ("元/㎡", "NTD/㎡"),
    ("單價（元）", "單價（NTD）"),
    ("合價（元）", "小計（NTD）"),
    ("单价（元）", "單價（NTD）"),
    ("合价（元）", "小計（NTD）"),
    ("单价(元)", "單價(NTD)"),
    ("合价(元)", "小計(NTD)"),
    ("合价", "小計"),
    ("项目", "工項"),
    ("定制衣柜", "系統衣櫃"),
    ("定制鞋柜", "系統鞋櫃"),
    ("定制餐边柜", "系統餐邊櫃"),
    ("定制柜", "系統櫃"),
    ("拆改", "拆除隔間"),
    ("导出 CAD", "匯出 CAD"),
    ("导出 PDF", "匯出 PDF"),
    ("保存方案", "儲存方案"),
    ("燃气灶", "瓦斯爐"),
    ("集成灶", "瓦斯爐/集成爐"),
    ("油烟机", "抽油煙機"),
    ("台盆", "面盆"),
    ("花洒", "蓮蓬頭/花灑"),
    ("淋浴房", "淋浴拉門"),
    ("⚡ 管線", "管線透視"),
    ("🎨 風格", "視覺風格"),
    ("🏠 智能中控", "空間中控"),
    ("▶ 日照演示", "日照模擬"),
]
for src, dst in tw_terms:
    tw_template = tw_template.replace(src, dst)

# 將 K2 預設單價表同步更新為台灣 NTD 行情（使「恢復預設單價」與新建空白圖紙皆預設為台灣 NTD）
import re as _re
for _k, _v in TW_NTD_PRICES.items():
    tw_template = _re.sub(
        rf'("{_re.escape(_k)}":\{{[^}}]*?price:)\d+(?:\.\d+)?',
        rf"\g<1>{_v}",
        tw_template,
        count=1,
    )

tw_template_path = os.path.join(here, "template_zh_tw.html")
with open(tw_template_path, "w", encoding="utf-8") as f:
    f.write(tw_template)

# ==========================================
# 4. 英文版 Template (全可視 UI 與面板在地化)
# ==========================================
en_template = orig_template
en_template = en_template.replace('<html lang="zh-CN">', '<html lang="en">')
en_template = en_template.replace(
    '"PingFang SC","Microsoft YaHei"',
    '"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif',
)

en_replacements = [
    ('location.search.includes("debug")&&(window.__designer=', '(window.__designer='),
    ('const Oo=t=>"¥"+Math.round(t).toLocaleString("en-US")', 'const Oo=t=>"$"+Math.round(t).toLocaleString("en-US")'),
    ("元/㎡", "USD/㎡"),
    ("单价（元）", "Unit ($)"),
    ("合价（元）", "Subtotal ($)"),
    ("单价(元)", "Unit ($)"),
    ("合价(元)", "Subtotal ($)"),
    ("导出 Excel (CSV)", "Export CSV"),
    ("恢复默认单价", "Reset Unit Rates"),
    ("户型装修设计器", "3D Floor Plan Designer"),
    ("方案管理：多方案切换与对比", "Manage & compare design schemes"),
    ("· 方案 ▾", "· Schemes ▾"),
    ("拆改设计阶段", "Renovation Phase"),
    ("原始结构阶段", "Existing Phase"),
    ("拆改设计", "Renovation"),
    ("原始结构", "Existing"),
    ("2D 平面 (1)", "2D Plan (1)"),
    ("分屏 (2)", "Split View (2)"),
    ("3D 空间 (3)", "3D View (3)"),
    (">分屏</button>", ">Split</button>"),
    ("选择 / 移动 (V)", "Select / Move (V)"),
    (">选择</button>", ">Select</button>"),
    ("画墙 (W)", "Draw Wall (W)"),
    (">画墙</button>", ">Wall</button>"),
    ("画房间 (B)", "Draw Room (B)"),
    (">房间</button>", ">Room</button>"),
    (">门窗</button>", ">Doors</button>"),
    ("水电点位 (E)", "MEP Points (E)"),
    (">水电</button>", ">MEP</button>"),
    (">管线</button>", ">Pipes</button>"),
    (">造型</button>", ">3D Form</button>"),
    ("批注留言 (C)", "Add Note (C)"),
    (">批注</button>", ">Note</button>"),
    ("测量 (M)", "Measure (M)"),
    (">测量</button>", ">Measure</button>"),
    ("拆墙 (D)", "Demolish Wall (D)"),
    (">拆墙</button>", ">Demolish</button>"),
    ("撤销 (Ctrl+Z)", "Undo (Ctrl+Z)"),
    ("重做 (Ctrl+Y)", "Redo (Ctrl+Y)"),
    ("算量报价", "Quantity Takeoff & Estimate"),
    (">报价</button>", ">Quote</button>"),
    ("保存到本地 (Ctrl+S)", "Save Locally (Ctrl+S)"),
    (">保存</button>", ">Save</button>"),
    ("导出图纸 ▾", "Export ▾"),
    ("整套施工图（A3 PDF）", "Full Construction Set (A3 PDF)"),
    ("CAD 平面布置图（DXF · 国标）", "CAD Floor Plan (DXF · Standard)"),
    ("（三道尺寸：门窗洞口 / 轴线 / 总尺寸）", " (3-tier dims: openings / axis / overall)"),
    ("CAD 平面布置图（DXF · 装修）", "CAD Floor Plan (DXF · Interior)"),
    ("（四道尺寸：多一道墙厚 + 净距）", " (4-tier dims: wall thickness + clear spans)"),
    ("CAD 水电点位图（DXF）", "CAD Electrical & Plumbing Plan (DXF)"),
    ("（插座 / 开关 / 灯 / 给排水，带离地高度）", " (outlets / switches / lights / plumbing)"),
    ("分享文件", "Shareable File"),
    ("（发给别人查看、留言、确认）", " (send for client review & comments)"),
    (">原始结构图</button>", ">Existing Structure Plan</button>"),
    (">拆改图（新砌 / 拆除）</button>", ">Demolition & New Wall Plan</button>"),
    (">平面布置图</button>", ">Furniture Layout Plan</button>"),
    (">地面铺装图</button>", ">Flooring Finish Plan</button>"),
    (">顶面布置图</button>", ">Reflected Ceiling Plan (RCP)</button>"),
    (">水电点位图</button>", ">MEP Electrical & Plumbing Plan</button>"),
    (">当前 3D 画面</button>", ">Current 3D Snapshot</button>"),
    (">彩平图（高清 PNG）</button>", ">Colored Floor Plan (HD PNG)</button>"),
    ("导出方案文件 (.json)", "Export Project (.json)"),
    ("导入方案文件…", "Import Project…"),
    ("清除全部测量", "Clear All Measurements"),
    ("恢复所有拆除的墙", "Restore Demolished Walls"),
    ("适应窗口 (F)", "Fit to View (F)"),
    (">布置</button>", ">Layout</button>"),
    (">顶面</button>", ">Ceiling</button>"),
    (">铺装</button>", ">Flooring</button>"),
    (">拆改</button>", ">Demo</button>"),
    ("正在准备 3D 场景…", "Preparing 3D Scene…"),
    (">鸟瞰</button>", ">Bird's-Eye</button>"),
    (">漫游</button>", ">Walkthrough</button>"),
    ("⚡ 管线", "MEP X-Ray"),
    ("🎨 风格", "Visual Style"),
    ("🏠 智能中控", "Scene Control"),
    (">渲染出图</button>", ">Render HD</button>"),
    (">720° 全景</button>", ">720° Pano</button>"),
    ("重置视角", "Reset Camera"),
    ("▶ 日照演示（日出到深夜）", "Sun Study (Dawn–Dusk)"),
    ("打开全部室内灯光（夜晚自动打开）", "Turn on all interior lights"),
    ("实时画面（几秒）", "Real-time (Fast)"),
    ("光线追踪（约 1~3 分钟，最真实）", "Path Tracing (1–3 min, Photorealistic)"),
    (">写实</button>", ">Realistic</button>"),
    (">沙盘效果图</button>", ">Diorama</button>"),
    (">彩平图</button>", ">Color Plan</button>"),
    (">流畅</button>", ">Fast</button>"),
    (">均衡</button>", ">Balanced</button>"),
    (">高画质</button>", ">High</button>"),
    ("灯带辉光", "LED Bloom"),
    ("地面房间名", "Room Labels"),
    ("圆润家具", "Soft Edges"),
    ("微缩景深（鸟瞰）", "Tilt-Shift DOF"),
    ("沙盘俯视视角", "Isometric View"),
    ("漫游视角", "Walkthrough Camera"),
    ("第一人称", "First-Person"),
    ("近跟随", "Near Follow"),
    ("远跟随", "Far Follow"),
    ("W A S D 移动 · 拖动鼠标转向 · 点标记或按空格操作开关 / 灯 / 门 · T 显示标记 · R / F 视高 · Esc 退出", "WASD Move · Drag to Look · Space to toggle Lights/Doors · T Markers · R/F Eye Height · Esc Exit"),
    ("点选家具/墙/门窗拖动 · 点蓝色尺寸可输入 · 空白处拖动平移 · 滚轮缩放", "Drag items/walls · Click blue dims to edit · Scroll to zoom"),
    (">户型<", ">Plan<"),
    (">水电<", ">MEP<"),
    (">家具<", ">Furniture<"),
    (">属性<", ">Properties<"),
    (">检查", ">Check"),
    (">批注", ">Notes"),
    ("单层户型。别墅、自建房、复式可以加楼层：每层单独编辑，2D 平铺、3D 叠成整栋。", "Single-story plan. Add floors for duplexes or multi-story homes."),
    ("复制本层为二层", "Duplicate to Floor 2"),
    ("加空白楼层", "Add Blank Floor"),
    ("楼层", "Floors"),
    ("设计阶段", "Design Phase"),
    ("原有墙体已锁定位置。新画的墙记为", "Existing walls are locked. New walls marked as "),
    ("，拆掉的墙记为", ", removed as "),
    ("，可导出拆改图。", "."),
    ("<b>新砌</b>", "<b>New</b>"),
    ("<b>拆除</b>", "<b>Demolished</b>"),
    (">新砌<", ">New<"),
    (">拆除<", ">Demolished<"),
    ("墙体", "Walls"),
    ("墙厚 (mm)", "Thickness (mm)"),
    ("非承重墙", "Partition Wall"),
    ("承重墙", "Bearing Wall"),
    ("点选后到墙上单击放置", "Select then click on a wall"),
    ("隐形推拉门", "Pocket Door"),
    ("单开门", "Single Door"),
    ("双开门", "Double Door"),
    ("子母门", "Entry Door"),
    ("推拉门", "Sliding Door"),
    ("折叠门", "Folding Door"),
    ("门洞 / 哑口", "Cased Opening"),
    ("平开窗", "Casement Win"),
    ("推拉窗", "Sliding Win"),
    ("套内净面积（自动计算）", "Net Interior Area (Auto)"),
    ("套内净面积", "Net Area"),
    ("新砌墙 / 拆除墙", "New / Demolished Walls"),
    ("门窗 / 家具", "Openings / Furniture"),
    ("跟着方案实时变，导出图纸也带", "Live & exported"),
    ("尺寸标注", "Dimensions"),
    ("外墙门窗分段尺寸", "Exterior Opening Dims"),
    ("每段墙净长", "Interior Wall Segments"),
    ("房间开间 × 进深", "Room Width × Depth"),
    ("层高", "Ceiling Height"),
    ("快捷键", "Shortcuts"),
    ("适应窗口", "Fit View"),
    ("2D / 分屏 / 3D", "2D / Split / 3D"),
    ("缩放 ", "Zoom "),
    ("未保存", "Unsaved"),
    ("已保存", "Saved"),
    ("个空间", " rooms"),
    ("件家具", " items"),
    ("<h4>房间</h4>", "<h4>Rooms</h4>"),
    ("<h4>门窗</h4>", "<h4>Doors & Windows</h4>"),
    ("<h4>类型</h4>", "<h4>Type</h4>"),
    ("画房间", "Room"),
    ("画墙", "Wall"),
    ("拆墙", "Demo"),
    ("测量", "Measure"),
    ("门窗", "Doors "),
    ("房间", "Rooms"),
    ("类型", "Type"),
    ("撤销", "Undo"),
    ("重做", "Redo"),
    ("保存", "Save"),
    ("选择", "Select"),
    ('"北"', '"N"'),
]

for src, dst in en_replacements:
    en_template = en_template.replace(src, dst)

for _k, _v in EN_USD_PRICES.items():
    en_template = _re.sub(
        rf'("{_re.escape(_k)}":\{{[^}}]*?price:)\d+(?:\.\d+)?',
        rf"\g<1>{_v}",
        en_template,
        count=1,
    )

en_template_path = os.path.join(here, "template_en.html")
with open(en_template_path, "w", encoding="utf-8") as f:
    f.write(en_template)

# ==========================================
# 5. 建置 HTML (TC + EN)
# ==========================================
print("Building demo-en.html...")
subprocess.run(
    [sys.executable, build_py, "spec_en.json", "-o", "demo-en.html", "--template", en_template_path],
    cwd=here,
    check=True,
)

print("Building demo-zh-tw.html...")
subprocess.run(
    [sys.executable, build_py, "spec_zh_tw.json", "-o", "demo-zh-tw.html", "--template", tw_template_path],
    cwd=here,
    check=True,
)

for tmp in (tw_template_path, en_template_path):
    if os.path.exists(tmp):
        os.remove(tmp)

# ==========================================
# 6. 建築圖紙暖白風（Architectural Paper）頂部導覽列 + OAuth 登入 + Pro 授權模組
# ==========================================
nav_and_auth_css = """
<style>
:root {
  --bg: #F6F4EF !important;
  --panel: #FDFCFA !important;
  --line: #DFDAD0 !important;
  --text: #18181B !important;
  --muted: #6E6A63 !important;
  --accent: #18181B !important;
  --accent-soft: #ECE8DF !important;
  --danger: #9A4A2B !important;
  --new: #9A4A2B !important;
}
header { background: #FAF8F4 !important; border-bottom: 1px solid #DFDAD0 !important; }
.logo { border-radius: 3px !important; background: #18181B !important; }
.phase { border-radius: 2px !important; background: #ECE8DF !important; color: #57534E !important; }
.phase.renovate { background: #F5E9E2 !important; color: #9A4A2B !important; }
.btn, .seg, .seg button, .iconbtn, .dropdown { border-radius: 3px !important; }
.btn.primary { background: #18181B !important; border-color: #18181B !important; color: #FAF8F5 !important; }
.btn.primary:hover { background: #2E2D2A !important; }

.studio-global-nav {
  height: 36px;
  background: #EFECE4;
  border-bottom: 1px solid #D5CFC2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;
  flex: none;
  font-family: "Inter", "Noto Sans TC", -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 12px;
  color: #57534E;
  user-select: none;
  box-sizing: border-box;
}
.studio-global-nav .nav-left, .studio-global-nav .nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.studio-global-nav .nav-brand {
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #18181B;
  font-size: 12px;
}
.studio-global-nav .nav-brand b { color: #9A4A2B; font-weight: 700; }
.studio-global-nav .nav-spec {
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  color: #6E6A63;
  border-left: 1px solid #CFC8BA;
  padding-left: 10px;
  font-size: 11px;
  letter-spacing: 0.03em;
}
.studio-global-nav .nav-lang {
  display: inline-flex;
  align-items: center;
  border: 1px solid #CFC8BA;
  background: #FAF8F4;
  border-radius: 3px;
  overflow: hidden;
}
.studio-global-nav .lang-pill {
  color: #57534E;
  text-decoration: none;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  transition: background 0.12s ease, color 0.12s ease;
}
.studio-global-nav .lang-pill:hover { color: #18181B; background: #EFECE4; }
.studio-global-nav .lang-pill.active { color: #FAF8F5; background: #18181B; }
.studio-global-nav .nav-btn {
  border: 1px solid #CFC8BA;
  background: #FAF8F4;
  color: #18181B;
  border-radius: 3px;
  padding: 3px 10px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: border-color 0.12s ease, background 0.12s ease;
}
.studio-global-nav .nav-btn:hover { border-color: #18181B; background: #fff; }
.studio-global-nav .nav-btn-pro {
  background: #9A4A2B;
  color: #FAF8F5;
  border: 1px solid #843D22;
}
.studio-global-nav .nav-btn-pro:hover { background: #843D22; color: #fff; border-color: #6E311A; }
.studio-global-nav .nav-btn-pro.unlocked {
  background: #234236;
  color: #FAF8F5;
  border: 1px solid #1B332A;
}
.studio-global-nav .nav-link-home {
  color: #18181B;
  text-decoration: none;
  font-weight: 600;
  font-size: 11.5px;
  padding: 3px 10px;
  border-radius: 3px;
  border: 1px solid #CFC8BA;
  background: transparent;
}
.studio-global-nav .nav-link-home:hover { background: #FAF8F4; border-color: #18181B; }
.dp-pro-tag {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 5px;
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 0.04em;
  border-radius: 2px;
  background: #9A4A2B;
  color: #FAF8F5;
  vertical-align: middle;
}
.dp-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(24, 24, 27, 0.48);
  z-index: 100000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 16px;
  font-family: "Inter", "Noto Sans TC", -apple-system, BlinkMacSystemFont, sans-serif;
}
.dp-modal-backdrop.open { display: flex; }
.dp-modal {
  width: 100%;
  max-width: 420px;
  background: #FDFCFA;
  border: 1px solid #C7C0B2;
  border-radius: 4px;
  color: #18181B;
  box-shadow: 0 20px 50px rgba(24, 24, 27, 0.18);
  overflow: hidden;
}
.dp-modal-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: #F6F4EF;
  border-bottom: 1px solid #DFDAD0;
}
.dp-modal-hdr h3 { margin: 0; font-size: 14.5px; font-weight: 700; letter-spacing: 0.01em; color: #18181B; }
.dp-modal-close {
  background: transparent;
  border: none;
  color: #6E6A63;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}
.dp-modal-close:hover { color: #18181B; }
.dp-tabs {
  display: flex;
  border-bottom: 1px solid #DFDAD0;
  background: #F6F4EF;
}
.dp-tabs button {
  flex: 1;
  padding: 10px 8px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #6E6A63;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}
.dp-tabs button.active { color: #18181B; border-bottom-color: #18181B; background: #FDFCFA; }
.dp-modal-body { padding: 20px; }
.dp-alert {
  padding: 9px 12px;
  border-radius: 3px;
  font-size: 12px;
  line-height: 1.5;
  margin-bottom: 14px;
  display: none;
}
.dp-alert.info { display: block; background: #F4EFE6; border: 1px solid #D8CEBE; color: #44403C; }
.dp-alert.err { display: block; background: #FBEAE5; border: 1px solid #E2B4A6; color: #7F2D15; }
.dp-alert.ok { display: block; background: #E9F2EE; border: 1px solid #B5D1C4; color: #1B3B2E; }
.dp-field { margin-bottom: 13px; }
.dp-field label { display: block; font-size: 11.5px; color: #57534E; margin-bottom: 5px; font-weight: 600; }
.dp-field input {
  width: 100%;
  box-sizing: border-box;
  background: #FFFFFF;
  border: 1px solid #CFC8BA;
  color: #18181B;
  border-radius: 3px;
  padding: 9px 11px;
  font-size: 13.5px;
}
.dp-field input:focus { outline: none; border-color: #18181B; }
.dp-btn {
  width: 100%;
  padding: 10px 14px;
  border-radius: 3px;
  border: 1px solid transparent;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-decoration: none;
  box-sizing: border-box;
}
.dp-btn-primary { background: #18181B; color: #FAF8F5; border-color: #18181B; }
.dp-btn-primary:hover { background: #2E2D2A; }
.dp-btn-gold { background: #9A4A2B; color: #FAF8F5; border-color: #843D22; margin-bottom: 12px; }
.dp-btn-gold:hover { background: #843D22; }
.dp-btn-ghost { background: #F6F4EF; color: #44403C; border: 1px solid #CFC8BA; margin-top: 8px; }
.dp-btn-ghost:hover { border-color: #18181B; color: #18181B; }
.dp-pro-list { list-style: none; padding: 0; margin: 0 0 16px; font-size: 12.5px; color: #292524; }
.dp-pro-list li { padding: 5px 0; border-bottom: 1px solid #EFECE4; display: flex; gap: 8px; }
.dp-pro-list li::before { content: "—"; color: #9A4A2B; font-weight: 700; }
.dp-divider { border: none; border-top: 1px solid #E5E0D5; margin: 16px 0; }
.dp-oauth-group { display: grid; gap: 8px; margin-bottom: 14px; }
.dp-oauth-btn {
  width: 100%;
  padding: 9px 12px;
  border-radius: 3px;
  border: 1px solid #CFC8BA;
  background: #FFFFFF;
  color: #18181B;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  transition: border-color 0.12s ease, background 0.12s ease;
}
.dp-oauth-btn:hover { background: #F6F4EF; border-color: #18181B; }
.dp-oauth-btn svg { width: 16px; height: 16px; flex: none; }
.dp-or {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 13px 0;
  color: #78716C;
  font-size: 11.5px;
}
.dp-or::before, .dp-or::after { content: ""; flex: 1; height: 1px; background: #E5E0D5; }
.dp-acct-card { background: #F6F4EF; border: 1px solid #DFDAD0; border-radius: 3px; padding: 12px 14px; margin-bottom: 14px; font-size: 12.5px; }
.dp-acct-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #E5E0D5; }
.dp-acct-row:last-child { border-bottom: none; }
.dp-luban-pop {
  position: fixed;
  top: 42px;
  left: 248px;
  width: 336px;
  background: #FDFCFA;
  border: 1px solid #C7C0B2;
  border-radius: 4px;
  box-shadow: 0 14px 36px rgba(24,24,27,0.16);
  z-index: 95000;
  display: none;
  font-family: "Inter", "Noto Sans TC", -apple-system, sans-serif;
  color: #18181B;
  font-size: 12px;
}
.dp-luban-pop.open { display: block; }
.dp-luban-hdr {
  display: flex; align-items: center; justify-content: space-between;
  padding: 9px 12px; background: #F6F4EF; border-bottom: 1px solid #DFDAD0;
  font-weight: 700; font-size: 12.5px;
}
.dp-luban-body { padding: 12px; }
.dp-luban-target {
  font-size: 11px; color: #57534E; background: #F4F1EA; border: 1px solid #E2DDD2;
  padding: 5px 8px; border-radius: 2px; margin-bottom: 9px;
  display: flex; justify-content: space-between; align-items: center;
}
.dp-luban-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
.dp-luban-grid label { display: block; font-size: 10.5px; color: #6E6A63; margin-bottom: 3px; font-weight: 600; }
.dp-luban-grid input {
  width: 100%; padding: 6px 8px; border: 1px solid #CFC8BA; border-radius: 2px;
  background: #fff; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12.5px;
}
.dp-luban-row {
  padding: 8px 10px; border: 1px solid #E5E0D5; border-radius: 3px; margin-bottom: 8px; background: #FAF8F4;
}
.dp-luban-row-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.dp-badge-ji {
  background: #9A2B2B; color: #FFF8F6; padding: 1px 7px; border-radius: 2px; font-weight: 700; font-size: 11px;
}
.dp-badge-xiong {
  background: #27272A; color: #F4F4F5; padding: 1px 7px; border-radius: 2px; font-weight: 600; font-size: 11px;
}
.dp-sugg-row { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
.dp-sugg-btn {
  flex: 1; padding: 4px 7px; font-size: 11px; font-weight: 600; border-radius: 2px;
  border: 1px solid #C99A8E; background: #FDF6F4; color: #8A2424; cursor: pointer;
}
.dp-sugg-btn:hover { background: #9A2B2B; color: #fff; border-color: #9A2B2B; }
@media (max-width: 860px) {
  .studio-global-nav .nav-spec, .studio-global-nav .nav-link-home, .studio-global-nav .hide-sm { display: none; }
  .studio-global-nav { padding: 0 8px; }
}
</style>
"""


def build_nav_and_auth_html(lang: str) -> str:
    is_en = lang == "en"
    t = {
        "spec": "DWG 2018 · A3 1:50" if is_en else "DWG 2018 · A3 1:50",
        "btn_blank": "+ Blank Plan" if is_en else "+ 新建空白圖紙",
        "btn_trace": "Trace Underlay" if is_en else "匯入底圖描圖",
        "btn_luban": "ft-in Scale" if is_en else "文公尺・台尺",
        "luban_title": "Imperial / Metric Scale Inspector" if is_en else "台灣文公尺（魯班尺）與台尺檢核",
        "home_url": "en.html" if is_en else "index.html",
        "home_txt": "Studio & Fees" if is_en else "事務所報價",
        "upgrade_btn": "Lifetime Pro · $19" if is_en else "終身 Pro · NT$590",
        "pro_active": "PRO Active" if is_en else "PRO 已授權",
        "login_btn": "Sign In" if is_en else "登入 / 註冊",
        "modal_title": "Account & Lifetime Pro License" if is_en else "帳號登入與終身 Pro 買斷授權",
        "tab_login": "Sign In" if is_en else "登入",
        "tab_signup": "Register" if is_en else "建立帳號",
        "tab_pro": "Lifetime Pro" if is_en else "終身 Pro 買斷",
        "email_lbl": "Email" if is_en else "電子信箱",
        "pwd_lbl": "Password (min 6 characters)" if is_en else "密碼（至少 6 碼）",
        "btn_login": "Sign In" if is_en else "登入",
        "btn_signup": "Create Account" if is_en else "建立免費帳號",
        "pro_p1": "One-time payment ($19 USD) — lifetime access, zero monthly fees" if is_en else "一次買斷終身授權（NT$590 免月費，無每期自動扣款）",
        "pro_p2": "Editable AutoCAD DXF (Standard / Interior 4-tier / MEP) + A3 PDF Set" if is_en else "解鎖可編輯 AutoCAD DXF（三道／四道尺寸／水電）與整套 A3 施工圖冊 PDF",
        "pro_p3": "Itemized Renovation Cost Estimate CSV export" if is_en else "解鎖 2026 台灣真實裝修行情工程估價單 Excel (CSV) 匯出",
        "pro_p4": "Photorealistic Path-Tracing Render & 720° VR Panorama export" if is_en else "解鎖光線追蹤寫實渲染（Path Tracing）與 720° 全景圖出圖",
        "buy_btn": "Buy Lifetime Pro Key — $19 USD (One-Time)" if is_en else "購買終身 Pro 買斷金鑰 — NT$590（一次付清免月費）",
        "key_lbl": "Enter License Key" if is_en else "輸入授權金鑰解鎖",
        "key_ph": "DPRO-XXXX-XXXX-XXXX",
        "activate_btn": "Verify & Activate" if is_en else "驗證並啟用終身授權",
        "logout_btn": "Sign Out" if is_en else "登出帳號",
        "acct_email": "Account" if is_en else "帳號",
        "acct_plan": "License Tier" if is_en else "授權等級",
        "acct_key": "License Key" if is_en else "金鑰編號",
        "msg_need_login": "Sign in or create a free account before exporting commercial CAD/PDF/CSV deliverables." if is_en else "匯出商業施工圖、報價單 CSV 或高階渲染前，請先登入或免費建立帳號。",
        "msg_need_pro": "DXF, A3 PDF sets, Cost CSV, Path Tracing, and 720° Panorama require the $19 Lifetime Pro license (zero monthly subscription)." if is_en else "AutoCAD DXF、A3 施工圖冊、台灣行情估價單 CSV、光線追蹤寫實渲染與 720° 全景需啟用終身 Pro 授權（NT$590 一次買斷免月費）。",
        "msg_bad_cred": "Incorrect email or password." if is_en else "信箱或密碼不正確。",
        "msg_exists": "Email already registered. Switch to Sign In." if is_en else "此信箱已註冊，請切換至「登入」。",
        "msg_short_pwd": "Enter a valid email and at least 6 characters for password." if is_en else "請填寫有效信箱與至少 6 位字元密碼。",
        "msg_signed_in": "Signed in." if is_en else "已登入。",
        "msg_signed_up": "Account created and signed in." if is_en else "帳號已建立並自動登入。",
        "msg_bad_key": "Invalid license key. Purchase a license above or contact topjgapadsup804@gmail.com." if is_en else "金鑰格式或校驗不符。請點擊上方購買，或來信 topjgapadsup804@gmail.com。",
        "msg_unlocked": "Pro License activated. All CAD DXF and A3 PDF exports are now unlocked." if is_en else "Pro 授權已啟用，所有 DXF 與 A3 PDF 施工圖匯出功能已解鎖。",
        "oauth_google": "Continue with Google" if is_en else "透過 Google 繼續",
        "oauth_github": "Continue with GitHub" if is_en else "透過 GitHub 繼續",
        "oauth_apple": "Continue with Apple" if is_en else "透過 Apple 繼續",
        "oauth_or": "or with email" if is_en else "或使用信箱",
        "msg_oauth_setup": "OAuth client keys are not yet configured in DRAFTPRO_CONFIG (see OAUTH_SETUP_GUIDE.md). Please sign in with Email below." if is_en else "尚未設定第三方 OAuth 金鑰（設定方式見 OAUTH_SETUP_GUIDE.md），請先使用下方信箱登入。",
        "msg_oauth_loading": "Connecting to provider..." if is_en else "正在連線驗證服務...",
        "buy_url": "mailto:topjgapadsup804@gmail.com?subject=%5BPro%20License%5D%20DraftPro%20Pro%20Key%20(%2419%20USD)&body=Hello%2C%0A%0AI%20would%20like%20to%20purchase%20a%20DraftPro%20Pro%20License%20Key%20(%2419%20USD).%0AAccount%20email%3A%20" if is_en else "mailto:topjgapadsup804@gmail.com?subject=%5BPro%20%E6%8E%88%E6%AC%8A%E7%94%B3%E8%B3%BC%5D%20DraftPro%20%E6%B0%B8%E4%B9%85%E6%8E%88%E6%AC%8A%E9%87%91%E9%91%B0%20(NT%24590)&body=%E6%82%A8%E5%A5%BD%EF%BC%8C%E6%88%91%E6%AC%B2%E7%94%B3%E8%B3%BC%20DraftPro%20Pro%20%E6%8E%88%E6%AC%8A%E9%87%91%E9%91%B0%EF%BC%88NT%24590%20%2F%20%2419%20USD%EF%BC%89%E3%80%82%0A%E8%A8%BB%E5%86%8A%E4%BF%A1%E7%AE%B1%EF%BC%9A",
    }

    tw_active = "" if is_en else " active"
    en_active = " active" if is_en else ""

    return f"""
<nav class="studio-global-nav">
  <div class="nav-left">
    <span class="nav-brand">DRAFT<b>PRO</b></span>
    <span class="nav-spec">{t['spec']}</span>
    <button type="button" class="nav-btn" id="dpNewBlankBtn" title="Free blank canvas — no login required">{t['btn_blank']}</button>
    <button type="button" class="nav-btn hide-sm" id="dpTraceBtn">{t['btn_trace']}</button>
    <button type="button" class="nav-btn" id="dpLubanBtn">{t['btn_luban']}</button>
  </div>
  <div class="nav-right">
    <div class="nav-lang">
      <a href="demo.html" class="lang-pill{tw_active}">繁體</a>
      <a href="demo-en.html" class="lang-pill{en_active}">EN</a>
    </div>
    <button type="button" class="nav-btn nav-btn-pro" id="dpProBtn">{t['upgrade_btn']}</button>
    <button type="button" class="nav-btn" id="dpAuthBtn">{t['login_btn']}</button>
    <a href="{t['home_url']}" class="nav-link-home">{t['home_txt']}</a>
  </div>
</nav>
<div class="dp-luban-pop" id="dpLubanPop">
  <div class="dp-luban-hdr">
    <span>{t['luban_title']}</span>
    <button type="button" class="dp-modal-close" id="dpLubanClose" style="font-size:16px;">×</button>
  </div>
  <div class="dp-luban-body">
    <div class="dp-luban-target" id="dpLubanTarget">{'Select any door/window/cabinet or enter mm' if is_en else '點選畫布門窗／櫃體自動帶入，或直接輸入尺寸'}</div>
    <div class="dp-luban-grid">
      <div>
        <label>{'Millimeters (mm)' if is_en else '公釐 (mm)'}</label>
        <input type="number" id="dpMmIn" value="900" min="50" max="20000" step="5" />
      </div>
      <div>
        <label>{'Centimeters (cm)' if is_en else '公分 (cm)'}</label>
        <input type="number" id="dpCmIn" value="90" min="5" max="2000" step="0.5" />
      </div>
    </div>
    <div id="dpLubanResult"></div>
  </div>
</div>
<div class="dp-modal-backdrop" id="dpModal">
  <div class="dp-modal" role="dialog" aria-modal="true">
    <div class="dp-modal-hdr">
      <h3>{t['modal_title']}</h3>
      <button type="button" class="dp-modal-close" id="dpModalClose">×</button>
    </div>
    <div class="dp-tabs" id="dpTabs">
      <button type="button" data-dptab="login" class="active">{t['tab_login']}</button>
      <button type="button" data-dptab="signup">{t['tab_signup']}</button>
      <button type="button" data-dptab="pro">{t['tab_pro']}</button>
    </div>
    <div class="dp-modal-body">
      <div class="dp-alert" id="dpAlert"></div>

      <div id="dpPaneAccount" style="display:none;">
        <div class="dp-acct-card">
          <div class="dp-acct-row"><span>{t['acct_email']}</span><b id="dpAcctEmail"></b></div>
          <div class="dp-acct-row"><span>{t['acct_plan']}</span><b id="dpAcctPlan"></b></div>
          <div class="dp-acct-row"><span>{t['acct_key']}</span><code id="dpAcctKey" style="color:#9A4A2B;font-weight:600;">—</code></div>
        </div>
        <button type="button" class="dp-btn dp-btn-gold" id="dpGoProFromAcct">{t['tab_pro']}</button>
        <button type="button" class="dp-btn dp-btn-ghost" id="dpLogoutBtn">{t['logout_btn']}</button>
      </div>

      <div id="dpOAuthBlock">
        <div class="dp-oauth-group">
          <button type="button" class="dp-oauth-btn google" data-oauth="google">
            <svg viewBox="0 0 24 24"><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/><path fill="#4285F4" d="M23.49 12.27c0-.79-.07-1.54-.19-2.27H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58l3.7 2.87c2.16-2 3.72-4.94 3.72-8.69z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.7-2.87c-.98.66-2.23 1.06-3.58 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/></svg>
            {t['oauth_google']}
          </button>
          <button type="button" class="dp-oauth-btn" data-oauth="github">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1.5C6.2 1.5 1.5 6.2 1.5 12c0 4.64 3.01 8.58 7.18 9.97.53.1.72-.23.72-.51v-1.8c-2.92.63-3.54-1.41-3.54-1.41-.48-1.21-1.17-1.53-1.17-1.53-.96-.65.07-.64.07-.64 1.06.07 1.62 1.09 1.62 1.09.94 1.61 2.47 1.15 3.07.88.1-.68.37-1.15.67-1.41-2.33-.26-4.78-1.17-4.78-5.19 0-1.15.41-2.09 1.08-2.82-.11-.27-.47-1.34.1-2.79 0 0 .88-.28 2.89 1.08a10.03 10.03 0 0 1 5.26 0c2-1.36 2.88-1.08 2.88-1.08.58 1.45.22 2.52.11 2.79.67.73 1.08 1.67 1.08 2.82 0 4.03-2.46 4.92-4.8 5.18.38.33.72.97.72 1.96v2.9c0 .28.19.62.73.51A10.51 10.51 0 0 0 22.5 12c0-5.8-4.7-10.5-10.5-10.5z"/></svg>
            {t['oauth_github']}
          </button>
          <button type="button" class="dp-oauth-btn" data-oauth="apple">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.365 1.43c0 1.14-.493 2.27-1.177 3.08-.744.9-1.99 1.57-2.987 1.57-.12 0-.23-.02-.3-.03-.01-.06-.04-.22-.04-.39 0-1.15.572-2.27 1.206-2.98.804-.94 2.142-1.64 3.248-1.68.03.13.05.28.05.43zm4.565 15.71c-.03.07-.463 1.58-1.518 3.12-.945 1.34-1.94 2.71-3.43 2.71-1.517 0-1.9-.88-3.63-.88-1.698 0-2.302.91-3.67.91-1.377 0-2.332-1.26-3.428-2.8-1.287-1.82-2.323-4.63-2.323-7.28 0-4.28 2.797-6.55 5.552-6.55 1.448 0 2.675.95 3.6.95.865 0 2.222-1.01 3.902-1.01.613 0 2.886.06 4.374 2.19-.13.09-2.383 1.37-2.383 4.19 0 3.26 2.854 4.42 2.955 4.45z"/></svg>
            {t['oauth_apple']}
          </button>
        </div>
        <div class="dp-or">{t['oauth_or']}</div>
      </div>

      <form id="dpPaneLogin">
        <div class="dp-field">
          <label for="dpLoginEmail">{t['email_lbl']}</label>
          <input id="dpLoginEmail" type="email" required placeholder="you@studio.com" />
        </div>
        <div class="dp-field">
          <label for="dpLoginPwd">{t['pwd_lbl']}</label>
          <input id="dpLoginPwd" type="password" required minlength="6" placeholder="••••••••" />
        </div>
        <button type="submit" class="dp-btn dp-btn-primary">{t['btn_login']}</button>
      </form>

      <form id="dpPaneSignup" style="display:none;">
        <div class="dp-field">
          <label for="dpSignupEmail">{t['email_lbl']}</label>
          <input id="dpSignupEmail" type="email" required placeholder="you@studio.com" />
        </div>
        <div class="dp-field">
          <label for="dpSignupPwd">{t['pwd_lbl']}</label>
          <input id="dpSignupPwd" type="password" required minlength="6" placeholder="••••••••" />
        </div>
        <button type="submit" class="dp-btn dp-btn-primary">{t['btn_signup']}</button>
      </form>

      <form id="dpPanePro" style="display:none;">
        <ul class="dp-pro-list">
          <li>{t['pro_p1']}</li>
          <li>{t['pro_p2']}</li>
          <li>{t['pro_p3']}</li>
          <li>{t['pro_p4']}</li>
        </ul>
        <a id="dpBuyLink" href="{t['buy_url']}" class="dp-btn dp-btn-gold">{t['buy_btn']}</a>
        <hr class="dp-divider" />
        <div class="dp-field">
          <label for="dpKeyInput">{t['key_lbl']}</label>
          <input id="dpKeyInput" type="text" placeholder="{t['key_ph']}" style="text-transform:uppercase;letter-spacing:0.06em;" />
        </div>
        <button type="submit" class="dp-btn dp-btn-primary">{t['activate_btn']}</button>
      </form>
    </div>
  </div>
</div>
<script>
(function() {{
  // Owner Configuration:
  // 1) Set supabaseUrl + supabaseAnonKey for instant Google + GitHub + Apple OAuth (see OAUTH_SETUP_GUIDE.md)
  // 2) Or set googleClientId for direct Google One-Tap / Sign In with Google
  // 3) Set gumroadProductId + checkoutUrl for automated Pro license verification
  window.DRAFTPRO_CONFIG = {{
    supabaseUrl: "",
    supabaseAnonKey: "",
    googleClientId: "",
    gumroadProductId: "",
    checkoutUrl: {json.dumps(t['buy_url'])},
    proExports: ["pdf", "dxf", "dxf-deco", "dxf-mep", "share"]
  }};

  const SALT = "DRAFTPRO-STUDIO-2026-PRO-V1";
  const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const USERS_KEY = "draftpro_users_v1";
  const SESSION_KEY = "draftpro_session_v1";
  const MSG = {json.dumps({k: v for k, v in t.items() if k.startswith('msg_') or k in ('pro_active', 'upgrade_btn', 'login_btn')}, ensure_ascii=False)};

  const $ = id => document.getElementById(id);

  async function sha256Hex(str) {{
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("").toUpperCase();
  }}

  async function verifyOfflineKey(key) {{
    const m = /^DPRO-([A-Z2-9]{{4}})-([A-Z2-9]{{4}})-([A-Z2-9]{{4}})$/.exec(key.trim().toUpperCase());
    if (!m) return false;
    const hex = await sha256Hex(m[1] + "-" + m[2] + "-" + SALT);
    let chk = "";
    for (let i = 0; i < 4; i++) {{
      chk += ALPHABET[parseInt(hex.slice(i * 2, i * 2 + 2), 16) % ALPHABET.length];
    }}
    return chk === m[3];
  }}

  async function verifyLicenseKey(key) {{
    const clean = key.trim().toUpperCase();
    if (await verifyOfflineKey(clean)) return true;
    const gid = window.DRAFTPRO_CONFIG.gumroadProductId;
    if (gid) {{
      try {{
        const res = await fetch("https://api.gumroad.com/v2/licenses/verify", {{
          method: "POST",
          headers: {{ "Content-Type": "application/x-www-form-urlencoded" }},
          body: "product_id=" + encodeURIComponent(gid) + "&license_key=" + encodeURIComponent(clean)
        }});
        const data = await res.json();
        return !!(data && data.success && !data.purchase?.refunded);
      }} catch (e) {{
        return false;
      }}
    }}
    return false;
  }}

  function getUsers() {{
    try {{ return JSON.parse(localStorage.getItem(USERS_KEY) || "{{}}"); }} catch {{ return {{}}; }}
  }}
  function saveUsers(u) {{ localStorage.setItem(USERS_KEY, JSON.stringify(u)); }}
  function getSession() {{
    try {{ return JSON.parse(localStorage.getItem(SESSION_KEY) || "null"); }} catch {{ return null; }}
  }}
  function setSession(s) {{
    if (s) localStorage.setItem(SESSION_KEY, JSON.stringify(s));
    else localStorage.removeItem(SESSION_KEY);
    refreshUI();
  }}

  function getCurrentUser() {{
    const s = getSession();
    if (!s || !s.email) return null;
    const users = getUsers();
    return users[s.email] ? {{ email: s.email, ...users[s.email] }} : null;
  }}

  function setAlert(type, text) {{
    const el = $("dpAlert");
    el.className = "dp-alert" + (type ? " " + type : "");
    el.textContent = text || "";
  }}

  function switchTab(tab) {{
    const user = getCurrentUser();
    const showAccount = user && (tab === "account" || tab === "login" || tab === "signup");
    $("dpTabs").style.display = showAccount ? "none" : "flex";
    $("dpOAuthBlock").style.display = (!showAccount && (tab === "login" || tab === "signup")) ? "block" : "none";
    $("dpPaneAccount").style.display = showAccount ? "block" : "none";
    $("dpPaneLogin").style.display = !showAccount && tab === "login" ? "block" : "none";
    $("dpPaneSignup").style.display = !showAccount && tab === "signup" ? "block" : "none";
    $("dpPanePro").style.display = tab === "pro" ? "block" : "none";
    if (tab === "pro") {{
      $("dpTabs").style.display = user ? "none" : "flex";
      $("dpPaneAccount").style.display = "none";
      $("dpOAuthBlock").style.display = "none";
    }}
    document.querySelectorAll("#dpTabs button").forEach(b => {{
      b.classList.toggle("active", b.dataset.dptab === tab);
    }});
    if (user) {{
      $("dpAcctEmail").textContent = user.email;
      $("dpAcctPlan").textContent = user.pro ? "PRO" : "STANDARD";
      $("dpAcctPlan").style.color = user.pro ? "#234236" : "#57534E";
      $("dpAcctKey").textContent = user.licenseKey || "—";
      $("dpGoProFromAcct").style.display = user.pro ? "none" : "inline-flex";
    }}
  }}

  function openModal(tab, alertType, alertMsg) {{
    setAlert(alertType, alertMsg);
    switchTab(tab);
    $("dpModal").classList.add("open");
  }}
  function closeModal() {{ $("dpModal").classList.remove("open"); }}

  function refreshUI() {{
    const user = getCurrentUser();
    const authBtn = $("dpAuthBtn");
    const proBtn = $("dpProBtn");
    if (user) {{
      authBtn.textContent = user.email.split("@")[0];
      if (user.pro) {{
        proBtn.textContent = MSG.pro_active;
        proBtn.classList.add("unlocked");
      }} else {{
        proBtn.textContent = MSG.upgrade_btn;
        proBtn.classList.remove("unlocked");
      }}
    }} else {{
      authBtn.textContent = MSG.login_btn;
      proBtn.textContent = MSG.upgrade_btn;
      proBtn.classList.remove("unlocked");
    }}
    // Tag PRO items in export dropdown
    document.querySelectorAll("#exportMenu [data-exp]").forEach(btn => {{
      const isProExp = window.DRAFTPRO_CONFIG.proExports.includes(btn.dataset.exp);
      if (!isProExp) return;
      let tag = btn.querySelector(".dp-pro-tag");
      if (!tag) {{
        tag = document.createElement("span");
        tag.className = "dp-pro-tag";
        btn.appendChild(tag);
      }}
      tag.textContent = "PRO";
      tag.style.background = (user && user.pro) ? "#234236" : "#9A4A2B";
    }});
  }}

  $("dpAuthBtn").addEventListener("click", () => {{
    const user = getCurrentUser();
    openModal(user ? "account" : "login");
  }});
  $("dpProBtn").addEventListener("click", () => {{
    const user = getCurrentUser();
    openModal(user && user.pro ? "account" : "pro");
  }});
  $("dpGoProFromAcct").addEventListener("click", () => switchTab("pro"));
  $("dpModalClose").addEventListener("click", closeModal);
  $("dpModal").addEventListener("click", e => {{ if (e.target === $("dpModal")) closeModal(); }});
  document.querySelectorAll("#dpTabs button").forEach(b => {{
    b.addEventListener("click", () => {{ setAlert("", ""); switchTab(b.dataset.dptab); }});
  }});

  $("dpPaneSignup").addEventListener("submit", async e => {{
    e.preventDefault();
    const email = $("dpSignupEmail").value.trim().toLowerCase();
    const pwd = $("dpSignupPwd").value;
    if (!email || pwd.length < 6) return setAlert("err", MSG.msg_short_pwd);
    const users = getUsers();
    if (users[email]) return setAlert("err", MSG.msg_exists);
    users[email] = {{ pwdHash: await sha256Hex(email + ":" + pwd + ":" + SALT), pro: false, licenseKey: null, createdAt: Date.now() }};
    saveUsers(users);
    setSession({{ email }});
    setAlert("ok", MSG.msg_signed_up);
    switchTab("account");
  }});

  $("dpPaneLogin").addEventListener("submit", async e => {{
    e.preventDefault();
    const email = $("dpLoginEmail").value.trim().toLowerCase();
    const pwd = $("dpLoginPwd").value;
    const users = getUsers();
    const hash = await sha256Hex(email + ":" + pwd + ":" + SALT);
    if (!users[email] || users[email].pwdHash !== hash) return setAlert("err", MSG.msg_bad_cred);
    setSession({{ email }});
    setAlert("ok", MSG.msg_signed_in);
    switchTab("account");
  }});

  $("dpLogoutBtn").addEventListener("click", () => {{
    setSession(null);
    setAlert("", "");
    switchTab("login");
  }});

  $("dpPanePro").addEventListener("submit", async e => {{
    e.preventDefault();
    const key = $("dpKeyInput").value.trim().toUpperCase();
    const ok = await verifyLicenseKey(key);
    if (!ok) return setAlert("err", MSG.msg_bad_key);
    let user = getCurrentUser();
    const users = getUsers();
    if (!user) {{
      // Auto-create a quick licensed profile if activating directly before signing in
      const email = "pro-user@draftpro.local";
      users[email] = users[email] || {{ pwdHash: "", pro: true, licenseKey: key, createdAt: Date.now() }};
      users[email].pro = true;
      users[email].licenseKey = key;
      saveUsers(users);
      setSession({{ email }});
    }} else {{
      users[user.email].pro = true;
      users[user.email].licenseKey = key;
      saveUsers(users);
      refreshUI();
    }}
    setAlert("ok", MSG.msg_unlocked);
    switchTab("account");
  }});

  // Capture-phase paywall guard for PRO deliverables (DXF, A3 PDF, Share, Cost CSV, Path Tracing, 720 Pano)
  function requireProAccess(e) {{
    const user = getCurrentUser();
    if (!user) {{
      e.preventDefault();
      e.stopImmediatePropagation();
      openModal("login", "info", MSG.msg_need_login);
      return false;
    }}
    if (!user.pro) {{
      e.preventDefault();
      e.stopImmediatePropagation();
      openModal("pro", "info", MSG.msg_need_pro);
      return false;
    }}
    return true;
  }}

  document.addEventListener("click", e => {{
    const tEl = e.target && e.target.closest ? e.target : null;
    if (!tEl) return;
    const expBtn = tEl.closest("#exportMenu [data-exp]");
    if (expBtn && window.DRAFTPRO_CONFIG.proExports.includes(expBtn.dataset.exp)) {{
      requireProAccess(e);
      return;
    }}
    if (tEl.closest("#qCsv") || tEl.closest("#panoBtn")) {{
      requireProAccess(e);
      return;
    }}
    if (tEl.closest("#renderBtn")) {{
      const rm = document.getElementById("rendMode");
      if (rm && rm.value === "pt") {{
        requireProAccess(e);
        return;
      }}
    }}
  }}, true);

  // ==========================================
  // Quick Actions: Blank Plan (No Login), Underlay Trace, Lu Ban Ruler & Dual Area Units
  // ==========================================
  const IS_EN = { "true" if is_en else "false" };

  $("dpNewBlankBtn").addEventListener("click", () => {{
    const planTab = document.querySelector('#leftPanel .tabs [data-tab="plan"]');
    if (planTab) planTab.click();
    setTimeout(() => {{
      const np = document.getElementById("newPlan");
      if (np) np.click();
    }}, 60);
  }});

  $("dpTraceBtn").addEventListener("click", () => {{
    const planTab = document.querySelector('#leftPanel .tabs [data-tab="plan"]');
    if (planTab) planTab.click();
    setTimeout(() => {{
      const D = window.__designer;
      if (D && D.app && D.app.underlay) {{
        D.setTool("calibrate");
      }} else {{
        const uf = document.getElementById("ulFile");
        if (uf) uf.click();
      }}
    }}, 60);
  }});

  // Lu Ban Ruler (門公尺 429.6mm / 丁蘭尺 388.8mm) + Taiwanese Foot (台尺 303.03mm) / Imperial ft-in
  const MENGONG_CYCLE = 429.6;
  const MENGONG = [
    {{ w: "財", good: true, subs: ["財德","寶庫","六合","迎福"] }},
    {{ w: "病", good: false, subs: ["退財","公事","牢執","孤寡"] }},
    {{ w: "離", good: false, subs: ["長庫","劫財","官鬼","失脫"] }},
    {{ w: "義", good: true, subs: ["添丁","益利","貴子","大吉"] }},
    {{ w: "官", good: true, subs: ["順科","橫財","進益","富貴"] }},
    {{ w: "劫", good: false, subs: ["死別","退口","離鄉","財失"] }},
    {{ w: "害", good: false, subs: ["災至","死絕","病臨","口舌"] }},
    {{ w: "本", good: true, subs: ["財至","登科","進寶","興旺"] }}
  ];
  const DINGLAN_CYCLE = 388.8;
  const DINGLAN = [
    {{ w: "丁", good: true, sub: "福星・及第" }},
    {{ w: "害", good: false, sub: "口舌・病臨" }},
    {{ w: "旺", good: true, sub: "天德・納福" }},
    {{ w: "苦", good: false, sub: "失脫・劫財" }},
    {{ w: "義", good: true, sub: "大吉・益利" }},
    {{ w: "官", good: true, sub: "富貴・順科" }},
    {{ w: "死", good: false, sub: "退丁・失財" }},
    {{ w: "興", good: true, sub: "登科・興旺" }},
    {{ w: "失", good: false, sub: "孤寡・退財" }},
    {{ w: "財", good: true, sub: "六合・進寶" }}
  ];

  function evalMengong(mm) {{
    const pos = ((mm % MENGONG_CYCLE) + MENGONG_CYCLE) % MENGONG_CYCLE;
    const seg = MENGONG_CYCLE / 8;
    const idx = Math.min(7, Math.floor(pos / seg));
    const subIdx = Math.min(3, Math.floor((pos - idx * seg) / (seg / 4)));
    return {{ ...MENGONG[idx], sub: MENGONG[idx].subs[subIdx] }};
  }}

  function evalDinglan(mm) {{
    const pos = ((mm % DINGLAN_CYCLE) + DINGLAN_CYCLE) % DINGLAN_CYCLE;
    const seg = DINGLAN_CYCLE / 10;
    const idx = Math.min(9, Math.floor(pos / seg));
    return DINGLAN[idx];
  }}

  function nearestGoodMengong(mm) {{
    const out = [];
    for (let d = 5; d <= 260 && out.length < 2; d += 5) {{
      for (const cand of [Math.round((mm - d) / 10) * 10, Math.round((mm + d) / 10) * 10]) {{
        if (cand < 120 || out.some(x => x.mm === cand)) continue;
        const r = evalMengong(cand);
        if (r.good) out.push({{ mm: cand, label: `${{cand}}mm（${{r.w}}・${{r.sub}}）` }});
        if (out.length >= 2) break;
      }}
    }}
    return out;
  }}

  function toTaichi(mm) {{
    const totalFen = mm / 3.030303;
    const chi = Math.floor(totalFen / 100);
    const cun = Math.floor((totalFen - chi * 100) / 10);
    const fen = Math.round(totalFen - chi * 100 - cun * 10);
    return `${{chi}} 尺 ${{cun}} 寸 ${{fen}} 分`;
  }}

  function toFtIn(mm) {{
    const totalIn = mm / 25.4;
    const ft = Math.floor(totalIn / 12);
    const inch = (totalIn - ft * 12).toFixed(1);
    return `${{ft}}' - ${{inch}}"`;
  }}

  let _lastSelKey = "";
  function applyDimensionToSelected(newMm) {{
    const D = window.__designer;
    if (!D || !D.app || !D.app.sel) return;
    const sel = D.app.sel;
    if (sel.kind === "opening") {{
      const op = D.app.plan.openings.find(o => o.id === sel.id);
      if (op) {{
        const w = D.app.plan.walls.find(x => x.id === op.wall);
        const a = w && D.app.plan.nodes.find(n => n.id === w.a);
        const b = w && D.app.plan.nodes.find(n => n.id === w.b);
        const wallLen = (a && b) ? Math.hypot(b.x - a.x, b.y - a.y) : 99999;
        const half = newMm / 2;
        if (op.pos - half >= 60 && op.pos + half <= wallLen - 60) {{
          op.width = Math.round(newMm);
          D.commit();
          D.requestDraw();
          renderLuban(newMm);
        }}
      }}
    }} else if (sel.kind === "furn") {{
      const fn = D.app.plan.furniture.find(f => f.id === sel.id);
      if (fn) {{
        fn.w = Math.round(newMm);
        D.commit();
        D.requestDraw();
        renderLuban(newMm);
      }}
    }}
  }}

  function renderLuban(mmVal) {{
    const mm = Math.max(10, Number(mmVal) || 900);
    $("dpMmIn").value = Math.round(mm);
    $("dpCmIn").value = +(mm / 10).toFixed(1);
    const box = $("dpLubanResult");
    if (IS_EN) {{
      const sqSample = ((mm / 1000) * (mm / 1000) * 10.7639).toFixed(1);
      box.innerHTML = `
        <div class="dp-luban-row">
          <div class="dp-luban-row-top"><b>Imperial Architectural</b><span style="font-family:monospace;font-weight:700;">${{toFtIn(mm)}}</span></div>
          <div style="color:#57534E;">Inches: <b>${{(mm / 25.4).toFixed(2)}} in</b> · Meters: <b>${{(mm / 1000).toFixed(3)}} m</b></div>
        </div>
        <div class="dp-luban-row" style="margin-bottom:0;">
          <div class="dp-luban-row-top"><b>Standard Door / Clearances</b></div>
          <div class="dp-sugg-row">
            <button type="button" class="dp-sugg-btn" data-setmm="762">30" (762mm)</button>
            <button type="button" class="dp-sugg-btn" data-setmm="813">32" (813mm)</button>
            <button type="button" class="dp-sugg-btn" data-setmm="914">36" ADA (914mm)</button>
          </div>
        </div>`;
    }} else {{
      const mg = evalMengong(mm);
      const dl = evalDinglan(mm);
      const suggs = nearestGoodMengong(mm);
      box.innerHTML = `
        <div class="dp-luban-row">
          <div class="dp-luban-row-top"><span>台灣營建台尺</span><b style="font-family:monospace;font-size:13px;">${{toTaichi(mm)}}</b></div>
          <div style="color:#6E6A63;font-size:11px;">1 台尺 = 30.303 cm｜目前 = ${{(mm / 303.0303).toFixed(2)}} 台尺</div>
        </div>
        <div class="dp-luban-row">
          <div class="dp-luban-row-top">
            <b>門公尺（陽宅門窗・魯班尺）</b>
            <span class="${{mg.good ? 'dp-badge-ji' : 'dp-badge-xiong'}}">${{mg.w}}・${{mg.sub}}（${{mg.good ? '紅字吉' : '黑字凶'}}）</span>
          </div>
          ${{!mg.good && suggs.length ? `<div style="font-size:11px;color:#57534E;margin-top:3px;">一鍵改為鄰近紅字吉數：</div><div class="dp-sugg-row">${{suggs.map(s => `<button type="button" class="dp-sugg-btn" data-setmm="${{s.mm}}">${{s.label}}</button>`).join("")}}</div>` : `<div style="font-size:11px;color:#234236;">符合傳統陽宅門窗紅字吉數。</div>`}}
        </div>
        <div class="dp-luban-row" style="margin-bottom:0;">
          <div class="dp-luban-row-top">
            <b>丁蘭尺（系統櫃／書桌／神明桌）</b>
            <span class="${{dl.good ? 'dp-badge-ji' : 'dp-badge-xiong'}}">${{dl.w}}・${{dl.sub}}（${{dl.good ? '紅字吉' : '黑字凶'}}）</span>
          </div>
        </div>`;
    }}
    box.querySelectorAll("[data-setmm]").forEach(b => {{
      b.addEventListener("click", () => applyDimensionToSelected(Number(b.dataset.setmm)));
    }});
  }}

  $("dpLubanBtn").addEventListener("click", () => {{
    $("dpLubanPop").classList.toggle("open");
    if ($("dpLubanPop").classList.contains("open")) renderLuban($("dpMmIn").value);
  }});
  $("dpLubanClose").addEventListener("click", () => $("dpLubanPop").classList.remove("open"));
  $("dpMmIn").addEventListener("input", () => renderLuban($("dpMmIn").value));
  $("dpCmIn").addEventListener("input", () => renderLuban(Number($("dpCmIn").value) * 10));

  // Sync selection -> Lu Ban Ruler & Dual-Unit Area (m² + 坪 / sq ft)
  function syncDesignerHUD() {{
    const D = window.__designer;
    if (D && D.app && D.app.sel) {{
      const sel = D.app.sel;
      const key = (sel.kind || "") + ":" + (sel.id || "");
      if (key !== _lastSelKey) {{
        _lastSelKey = key;
        if (sel.kind === "opening") {{
          const op = D.app.plan.openings.find(o => o.id === sel.id);
          if (op) {{
            const w = Math.round(op.width);
            $("dpLubanTarget").textContent = IS_EN ? `Selected Opening Width: ${{w}} mm` : `已選取門窗洞口寬度：${{w}} mm（可一鍵套用紅字）`;
            renderLuban(w);
          }}
        }} else if (sel.kind === "furn") {{
          const fn = D.app.plan.furniture.find(f => f.id === sel.id);
          if (fn) {{
            $("dpLubanTarget").textContent = IS_EN ? `Selected: ${{fn.name}} (W ${{fn.w}} mm)` : `已選取「${{fn.name}}」寬度：${{fn.w}} mm`;
            renderLuban(fn.w);
          }}
        }} else {{
          $("dpLubanTarget").textContent = IS_EN ? "Select any door/window/cabinet or enter mm" : "點選畫布門窗／櫃體自動帶入，或直接輸入尺寸";
        }}
      }}
    }}

    // Append 坪 (TC) or sq ft (EN) to status bar & right inspector area readouts
    const stArea = document.getElementById("stArea");
    if (stArea && stArea.textContent && !stArea.textContent.includes("坪") && !stArea.textContent.includes("sq ft")) {{
      stArea.textContent = stArea.textContent.replace(/(\d+(?:\.\d+)?)\s*(?:m²|㎡)/, (_, m2) => {{
        return IS_EN ? `${{m2}} m² (${{Math.round(Number(m2) * 10.7639).toLocaleString("en-US")}} sq ft)` : `${{m2}} m²（${{(Number(m2) * 0.3025).toFixed(1)}} 坪）`;
      }});
    }}
    const insp = document.getElementById("inspector");
    if (insp) {{
      insp.querySelectorAll("b, span, td, div").forEach(el => {{
        if (el.children.length === 0 && el.textContent && /^\d+(?:\.\d+)?\s*(?:m²|㎡)$/.test(el.textContent.trim())) {{
          const m2 = parseFloat(el.textContent);
          if (!isNaN(m2)) {{
            el.textContent = IS_EN ? `${{m2.toFixed(2)}} m² (${{Math.round(m2 * 10.7639)}} sf)` : `${{m2.toFixed(2)}} m² · ${{(m2 * 0.3025).toFixed(1)}} 坪`;
          }}
        }}
      }});
    }}
  }}
  setInterval(syncDesignerHUD, 350);
  renderLuban(900);

  let _sbClient = null;
  function loadScript(src) {{
    return new Promise((resolve, reject) => {{
      if (document.querySelector(`script[src="${{src}}"]`)) return resolve();
      const s = document.createElement("script");
      s.src = src; s.async = true; s.onload = resolve; s.onerror = reject;
      document.head.appendChild(s);
    }});
  }}

  async function getSupabase() {{
    const cfg = window.DRAFTPRO_CONFIG;
    if (!cfg.supabaseUrl || !cfg.supabaseAnonKey) return null;
    if (_sbClient) return _sbClient;
    await loadScript("https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js");
    _sbClient = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey);
    return _sbClient;
  }}

  function upsertOAuthUser(email, provider, avatar) {{
    const users = getUsers();
    users[email] = users[email] || {{ pwdHash: "", pro: false, licenseKey: null, createdAt: Date.now() }};
    users[email].provider = provider;
    if (avatar) users[email].avatar = avatar;
    saveUsers(users);
    setSession({{ email, provider, avatar }});
  }}

  async function restoreOAuthSession() {{
    const sb = await getSupabase();
    if (!sb) return;
    const {{ data }} = await sb.auth.getSession();
    const u = data && data.session && data.session.user;
    if (u && u.email) {{
      upsertOAuthUser(u.email.toLowerCase(), u.app_metadata?.provider || "oauth", u.user_metadata?.avatar_url || "");
    }}
  }}

  document.querySelectorAll("[data-oauth]").forEach(btn => {{
    btn.addEventListener("click", async () => {{
      const provider = btn.dataset.oauth;
      const cfg = window.DRAFTPRO_CONFIG;
      // 1. Supabase OAuth (Google / GitHub / Apple)
      if (cfg.supabaseUrl && cfg.supabaseAnonKey) {{
        setAlert("info", MSG.msg_oauth_loading);
        const sb = await getSupabase();
        const {{ error }} = await sb.auth.signInWithOAuth({{
          provider,
          options: {{ redirectTo: window.location.origin + window.location.pathname }}
        }});
        if (error) setAlert("err", error.message);
        return;
      }}
      // 2. Direct Google Identity Services (GIS)
      if (provider === "google" && cfg.googleClientId) {{
        setAlert("info", MSG.msg_oauth_loading);
        await loadScript("https://accounts.google.com/gsi/client");
        window.google.accounts.id.initialize({{
          client_id: cfg.googleClientId,
          callback: resp => {{
            try {{
              const payload = JSON.parse(atob(resp.credential.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
              if (payload.email) {{
                upsertOAuthUser(payload.email.toLowerCase(), "google", payload.picture || "");
                setAlert("ok", MSG.msg_signed_in);
                switchTab("account");
              }}
            }} catch (err) {{
              setAlert("err", "Google token parse error");
            }}
          }}
        }});
        window.google.accounts.id.prompt();
        return;
      }}
      // 3. Not configured yet -> clear guidance
      setAlert("info", MSG.msg_oauth_setup);
    }});
  }});

  window.addEventListener("DOMContentLoaded", () => {{ refreshUI(); restoreOAuthSession(); }});
  setTimeout(refreshUI, 300);
}})();
</script>
"""


def inject_in_flow_nav(file_path, lang="tw"):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("</head>", f"{nav_and_auth_css}\n</head>")
    nav_block = build_nav_and_auth_html(lang)
    if '<div class="app">' in html:
        html = html.replace('<div class="app">', f'<div class="app">\n{nav_block}')
    else:
        html = html.replace("<body>", f"<body>\n{nav_block}")

    if lang == "tw":
        html = html.replace("装修设计器</title>", "3D 空間互動提案</title>")
        html = html.replace("夾角里的", "夾角裡的")
        html = html.replace("」里加", "」裡加")
        html = html.replace("3D 里", "3D 裡")
        html = html.replace("圖層里", "圖層裡")
    elif lang == "en":
        html = html.replace(" · 装修设计器</title>", " · Interactive 3D Floor Plan</title>")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)


inject_in_flow_nav(os.path.join(here, "demo-zh-tw.html"), lang="tw")
open(os.path.join(here, "demo.html"), "w", encoding="utf-8").write(
    open(os.path.join(here, "demo-zh-tw.html"), encoding="utf-8").read()
)
inject_in_flow_nav(os.path.join(here, "demo-en.html"), lang="en")

print("Successfully built TC + EN editions with Login + Pro License Gate!")
