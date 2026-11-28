"""
雙語版本建置腳本（繁體中文 TC + 英文 EN，無簡體中文）：
1. 頂部整合導覽列 (studio-global-nav) 做為 .app flex-direction: column 的首個子元素 (in-flow)，零遮擋。
2. 繁體中文版 (demo.html & demo-zh-tw.html)：100% 臺灣繁體中文與建築裝修術語（30.2 坪）。
3. 英文國際版 (demo-en.html)：100% 英文建築房間命名與核心操作介面（100㎡ / 1,076 sq ft）。
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

spec_tw = copy.deepcopy(base_spec)
spec_tw["name"] = "DraftPro Studio · 30.2 坪標準三房兩廳兩衛"
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
]
for src, dst in tw_terms:
    tw_template = tw_template.replace(src, dst)

tw_template_path = os.path.join(here, "template_zh_tw.html")
with open(tw_template_path, "w", encoding="utf-8") as f:
    f.write(tw_template)

# ==========================================
# 4. 英文版 Template (保留內部比對安全，翻譯所有可視 UI 與面板)
# ==========================================
en_template = orig_template
en_template = en_template.replace('<html lang="zh-CN">', '<html lang="en">')
en_template = en_template.replace(
    '"PingFang SC","Microsoft YaHei"',
    '"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif',
)

# 精準替換靜態 HTML 與主要動態面板字串（長字串優先，避免誤傷 JS 語法）
en_replacements = [
    # Header & Menus
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
    # 2D / 3D Overlays
    ("适应窗口 (F)", "Fit to View (F)"),
    (">布置</button>", ">Layout</button>"),
    (">顶面</button>", ">Ceiling</button>"),
    (">铺装</button>", ">Flooring</button>"),
    (">拆改</button>", ">Demo</button>"),
    ("正在准备 3D 场景…", "Preparing 3D Scene…"),
    (">鸟瞰</button>", ">Bird's-Eye</button>"),
    (">漫游</button>", ">Walkthrough</button>"),
    ("⚡ 管线", "⚡ MEP X-Ray"),
    ("🎨 风格", "🎨 Style"),
    ("🏠 智能中控", "🏠 Smart Home"),
    (">渲染出图</button>", ">Render HD</button>"),
    (">720° 全景</button>", ">720° Pano</button>"),
    ("重置视角", "Reset Camera"),
    ("▶ 日照演示（日出到深夜）", "▶ Sunlight Simulation"),
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
    # Left & Right Panel Dynamic JS Labels
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

# 刪除臨時模板
for tmp in (tw_template_path, en_template_path):
    if os.path.exists(tmp):
        os.remove(tmp)

# ==========================================
# 6. 整合式頂部版面 (In-flow Flex Item，零疊套遮擋)
# ==========================================
nav_css = """
<style>
.studio-global-nav {
  height: 38px;
  background: #090d16;
  border-bottom: 1px solid #1e293b;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex: none;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, "Noto Sans TC", sans-serif;
  font-size: 13px;
  color: #94a3b8;
  user-select: none;
  box-sizing: border-box;
}
.studio-global-nav .nav-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.studio-global-nav .nav-brand {
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #f8fafc;
  font-size: 13px;
}
.studio-global-nav .nav-brand b {
  color: #38bdf8;
}
.studio-global-nav .nav-badge {
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 4px;
  padding: 1px 7px;
  font-size: 11px;
  font-weight: 600;
}
.studio-global-nav .nav-right {
  display: flex;
  align-items: center;
  gap: 14px;
}
.studio-global-nav .nav-lang {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #111726;
  border: 1px solid #1e293b;
  padding: 2px 4px;
  border-radius: 6px;
}
.studio-global-nav .lang-txt {
  font-size: 11px;
  color: #64748b;
  margin-right: 2px;
  padding-left: 4px;
}
.studio-global-nav .lang-pill {
  color: #94a3b8;
  text-decoration: none;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.15s ease;
}
.studio-global-nav .lang-pill:hover {
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.08);
}
.studio-global-nav .lang-pill.active {
  color: #0369a1;
  background: #38bdf8;
  font-weight: 700;
}
.studio-global-nav .nav-link-home {
  color: #38bdf8;
  text-decoration: none;
  font-weight: 600;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.3);
  transition: all 0.15s ease;
}
.studio-global-nav .nav-link-home:hover {
  background: #38bdf8;
  color: #081018;
}
@media (max-width: 640px) {
  .studio-global-nav .nav-badge, .studio-global-nav .lang-txt { display: none; }
  .studio-global-nav { padding: 0 8px; }
}
</style>
"""

tw_nav_html = """
<nav class="studio-global-nav">
  <div class="nav-left">
    <span class="nav-brand">DRAFT<b>PRO</b> STUDIO</span>
    <span class="nav-badge">AI-CAD 3D 空間互動提案</span>
  </div>
  <div class="nav-right">
    <div class="nav-lang">
      <span class="lang-txt">語言：</span>
      <a href="demo.html" class="lang-pill active">🇹🇼 繁體中文</a>
      <a href="demo-en.html" class="lang-pill">🌐 English</a>
    </div>
    <a href="index.html" class="nav-link-home">官網服務報價 ➔</a>
  </div>
</nav>
"""

en_nav_html = """
<nav class="studio-global-nav">
  <div class="nav-left">
    <span class="nav-brand">DRAFT<b>PRO</b> STUDIO</span>
    <span class="nav-badge">AI-CAD 3D Floor Plan Demo</span>
  </div>
  <div class="nav-right">
    <div class="nav-lang">
      <span class="lang-txt">Lang:</span>
      <a href="demo.html" class="lang-pill">🇹🇼 繁體中文</a>
      <a href="demo-en.html" class="lang-pill active">🌐 English</a>
    </div>
    <a href="en.html" class="nav-link-home">Pricing &amp; Quote ➔</a>
  </div>
</nav>
"""

def inject_in_flow_nav(file_path, nav_html, lang="tw"):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("</head>", f"{nav_css}\n</head>")
    if '<div class="app">' in html:
        html = html.replace('<div class="app">', f'<div class="app">\n{nav_html}')
    else:
        html = html.replace("<body>", f"<body>\n{nav_html}")

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

inject_in_flow_nav(os.path.join(here, "demo-zh-tw.html"), tw_nav_html, lang="tw")
open(os.path.join(here, "demo.html"), "w", encoding="utf-8").write(
    open(os.path.join(here, "demo-zh-tw.html"), encoding="utf-8").read()
)
inject_in_flow_nav(os.path.join(here, "demo-en.html"), en_nav_html, lang="en")

print("Successfully built TC (demo.html / demo-zh-tw.html) and EN (demo-en.html) editions!")
