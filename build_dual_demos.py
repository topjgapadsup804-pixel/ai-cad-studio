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
# 4. 英文版 Template (全可視 UI 與面板在地化)
# ==========================================
en_template = orig_template
en_template = en_template.replace('<html lang="zh-CN">', '<html lang="en">')
en_template = en_template.replace(
    '"PingFang SC","Microsoft YaHei"',
    '"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif',
)

en_replacements = [
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

for tmp in (tw_template_path, en_template_path):
    if os.path.exists(tmp):
        os.remove(tmp)

# ==========================================
# 6. 整合式頂部導覽列 + 登入系統 + Pro 授權解鎖模組
# ==========================================
nav_and_auth_css = """
<style>
.studio-global-nav {
  height: 40px;
  background: #090d16;
  border-bottom: 1px solid #1e293b;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;
  flex: none;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, "Noto Sans TC", sans-serif;
  font-size: 13px;
  color: #94a3b8;
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
  letter-spacing: 0.04em;
  color: #f8fafc;
  font-size: 13px;
}
.studio-global-nav .nav-brand b { color: #38bdf8; }
.studio-global-nav .nav-badge {
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 4px;
  padding: 1px 7px;
  font-size: 11px;
  font-weight: 600;
}
.studio-global-nav .nav-lang {
  display: flex;
  align-items: center;
  gap: 3px;
  background: #111726;
  border: 1px solid #1e293b;
  padding: 2px 4px;
  border-radius: 6px;
}
.studio-global-nav .lang-pill {
  color: #94a3b8;
  text-decoration: none;
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.15s ease;
}
.studio-global-nav .lang-pill:hover { color: #f1f5f9; background: rgba(255,255,255,0.08); }
.studio-global-nav .lang-pill.active { color: #0369a1; background: #38bdf8; font-weight: 700; }
.studio-global-nav .nav-btn {
  border: 1px solid #334155;
  background: #131c2e;
  color: #e2e8f0;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s ease;
}
.studio-global-nav .nav-btn:hover { border-color: #38bdf8; color: #38bdf8; }
.studio-global-nav .nav-btn-pro {
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  color: #fff;
  border: none;
}
.studio-global-nav .nav-btn-pro:hover { filter: brightness(1.08); color: #fff; }
.studio-global-nav .nav-btn-pro.unlocked {
  background: rgba(16, 185, 129, 0.16);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.45);
}
.studio-global-nav .nav-link-home {
  color: #38bdf8;
  text-decoration: none;
  font-weight: 600;
  font-size: 12px;
  padding: 3px 9px;
  border-radius: 6px;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.3);
}
.studio-global-nav .nav-link-home:hover { background: #38bdf8; color: #081018; }
.dp-pro-tag {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 5px;
  font-size: 10px;
  font-weight: 700;
  border-radius: 4px;
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  color: #fff;
  vertical-align: middle;
}
.dp-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(6, 10, 18, 0.78);
  backdrop-filter: blur(6px);
  z-index: 100000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, "Noto Sans TC", sans-serif;
}
.dp-modal-backdrop.open { display: flex; }
.dp-modal {
  width: 100%;
  max-width: 440px;
  background: #0f1623;
  border: 1px solid #263349;
  border-radius: 14px;
  color: #f1f5f9;
  box-shadow: 0 24px 60px rgba(0,0,0,0.6);
  overflow: hidden;
}
.dp-modal-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #1e293b;
}
.dp-modal-hdr h3 { margin: 0; font-size: 16px; font-weight: 700; }
.dp-modal-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}
.dp-modal-close:hover { color: #fff; }
.dp-tabs {
  display: flex;
  border-bottom: 1px solid #1e293b;
  background: #0b101b;
}
.dp-tabs button {
  flex: 1;
  padding: 11px 8px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.dp-tabs button.active { color: #38bdf8; border-bottom-color: #38bdf8; }
.dp-modal-body { padding: 20px; }
.dp-alert {
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 12.5px;
  margin-bottom: 14px;
  display: none;
}
.dp-alert.info { display: block; background: rgba(56,189,248,0.12); border: 1px solid rgba(56,189,248,0.35); color: #bae6fd; }
.dp-alert.err { display: block; background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.4); color: #fecaca; }
.dp-alert.ok { display: block; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.4); color: #a7f3d0; }
.dp-field { margin-bottom: 14px; }
.dp-field label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 5px; font-weight: 600; }
.dp-field input {
  width: 100%;
  box-sizing: border-box;
  background: #172133;
  border: 1px solid #2b3a55;
  color: #f8fafc;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
}
.dp-field input:focus { outline: none; border-color: #38bdf8; }
.dp-btn {
  width: 100%;
  padding: 11px 16px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-decoration: none;
  box-sizing: border-box;
}
.dp-btn-primary { background: #38bdf8; color: #081018; }
.dp-btn-primary:hover { background: #7dd3fc; }
.dp-btn-gold { background: linear-gradient(135deg, #f59e0b, #ea580c); color: #fff; margin-bottom: 12px; }
.dp-btn-gold:hover { filter: brightness(1.08); }
.dp-btn-ghost { background: #172133; color: #cbd5e1; border: 1px solid #2b3a55; margin-top: 8px; }
.dp-pro-list { list-style: none; padding: 0; margin: 0 0 16px; font-size: 13px; color: #cbd5e1; }
.dp-pro-list li { padding: 4px 0; }
.dp-pro-list li::before { content: "✓ "; color: #34d399; font-weight: 700; }
.dp-divider { border: none; border-top: 1px solid #1e293b; margin: 16px 0; }
.dp-oauth-group { display: grid; gap: 9px; margin-bottom: 14px; }
.dp-oauth-btn {
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #2b3a55;
  background: #141d2e;
  color: #f1f5f9;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.15s ease;
}
.dp-oauth-btn:hover { background: #1c2840; border-color: #38bdf8; }
.dp-oauth-btn.google { background: #ffffff; color: #1f2937; border-color: #e2e8f0; }
.dp-oauth-btn.google:hover { background: #f8fafc; border-color: #38bdf8; }
.dp-oauth-btn svg { width: 18px; height: 18px; flex: none; }
.dp-or {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 14px 0;
  color: #64748b;
  font-size: 12px;
}
.dp-or::before, .dp-or::after { content: ""; flex: 1; height: 1px; background: #1e293b; }
.dp-avatar {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  object-fit: cover;
}
.dp-acct-card { background: #141d2e; border: 1px solid #24324d; border-radius: 10px; padding: 14px; margin-bottom: 14px; font-size: 13px; }
.dp-acct-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
.dp-acct-row:last-child { border-bottom: none; }
@media (max-width: 720px) {
  .studio-global-nav .nav-badge, .studio-global-nav .nav-link-home { display: none; }
  .studio-global-nav { padding: 0 8px; }
}
</style>
"""


def build_nav_and_auth_html(lang: str) -> str:
    is_en = lang == "en"
    t = {
        "badge": "AI-CAD 3D Floor Plan Demo" if is_en else "AI-CAD 3D 空間互動提案",
        "home_url": "en.html" if is_en else "index.html",
        "home_txt": "Pricing ➔" if is_en else "服務報價 ➔",
        "upgrade_btn": "⚡ Upgrade Pro ($19)" if is_en else "⚡ 升級 Pro (NT$590)",
        "pro_active": "👑 PRO Active" if is_en else "👑 PRO 已啟用",
        "login_btn": "👤 Sign In" if is_en else "👤 登入 / 註冊",
        "modal_title": "DraftPro Account & Pro License" if is_en else "DraftPro 帳號登入與 Pro 授權",
        "tab_login": "Sign In" if is_en else "登入",
        "tab_signup": "Create Account" if is_en else "註冊帳號",
        "tab_pro": "Activate Pro" if is_en else "啟用 Pro 授權",
        "email_lbl": "Email Address" if is_en else "電子信箱 (Email)",
        "pwd_lbl": "Password (min 6 chars)" if is_en else "密碼（至少 6 碼）",
        "btn_login": "Sign In" if is_en else "立即登入",
        "btn_signup": "Create Free Account" if is_en else "免費註冊帳號",
        "pro_p1": "Export editable AutoCAD DXF (3-tier / 4-tier / MEP)" if is_en else "匯出可編輯 AutoCAD DXF（國標/裝修/水電圖）",
        "pro_p2": "Export watermark-free A3 Construction PDF Set" if is_en else "匯出無浮水印 A3 整套施工圖 PDF",
        "pro_p3": "Generate shareable client review link" if is_en else "產生客戶專用免安裝分享審圖檔",
        "pro_p4": "Commercial usage rights for client proposals" if is_en else "含商業專案提案使用授權",
        "buy_btn": "🛒 Buy Pro License Key — $19 USD" if is_en else "🛒 購買 Pro 永久授權碼 — NT$590 ($19 USD)",
        "key_lbl": "Already have a License Key?" if is_en else "已有 Pro 授權碼？立即輸入解鎖：",
        "key_ph": "DPRO-XXXX-XXXX-XXXX",
        "activate_btn": "Verify & Unlock Pro" if is_en else "驗證並立即解鎖 Pro",
        "logout_btn": "Sign Out" if is_en else "登出帳號",
        "acct_email": "Account" if is_en else "登入帳號",
        "acct_plan": "Current Plan" if is_en else "目前方案",
        "acct_key": "License Key" if is_en else "授權金鑰",
        "msg_need_login": "Please sign in or create a free account to export CAD/PDF files." if is_en else "請先登入或免費註冊帳號，以使用商業圖紙匯出功能。",
        "msg_need_pro": "AutoCAD DXF, A3 PDF sets, and Shareable Client Files require a Pro License." if is_en else "匯出 AutoCAD DXF、整套 A3 施工圖 PDF 與客戶分享檔需啟用 Pro 授權。",
        "msg_bad_cred": "Invalid email or password." if is_en else "信箱或密碼錯誤，請重新確認。",
        "msg_exists": "This email is already registered. Please sign in." if is_en else "此信箱已註冊，請直接切換至「登入」。",
        "msg_short_pwd": "Please enter a valid email and password (6+ characters)." if is_en else "請輸入有效的 Email 與至少 6 碼密碼。",
        "msg_signed_in": "Signed in successfully!" if is_en else "登入成功！",
        "msg_signed_up": "Account created! You are now signed in." if is_en else "註冊完成並已自動登入！",
        "msg_bad_key": "Invalid license key format or checksum. Purchase a key or contact topjgapadsup804@gmail.com." if is_en else "授權碼無效或校驗失敗。請點擊上方購買，或聯繫 topjgapadsup804@gmail.com 取得授權碼。",
        "msg_unlocked": "🎉 Pro License Activated! All CAD DXF & A3 PDF exports are now unlocked." if is_en else "🎉 Pro 授權已成功啟用！所有 CAD DXF、A3 PDF 與分享匯出功能已全面解鎖。",
        "oauth_google": "Continue with Google" if is_en else "使用 Google 帳號繼續",
        "oauth_github": "Continue with GitHub" if is_en else "使用 GitHub 帳號繼續",
        "oauth_apple": "Continue with Apple" if is_en else "使用 Apple 帳號繼續",
        "oauth_or": "or continue with email" if is_en else "或使用電子信箱",
        "msg_oauth_setup": "OAuth keys (Supabase or Google Client ID) are not configured yet. Add them in DRAFTPRO_CONFIG (see OAUTH_SETUP_GUIDE.md), or sign in with Email below right now." if is_en else "尚未填入 Google / Supabase OAuth 金鑰（請參閱 OAUTH_SETUP_GUIDE.md 填入 2 行設定即可啟用一鍵登入）；您目前可直接用下方 Email 註冊登入。",
        "msg_oauth_loading": "Redirecting to provider..." if is_en else "正在連線第三方登入驗證...",
        "buy_url": "mailto:topjgapadsup804@gmail.com?subject=%5BPro%20License%5D%20Purchase%20DraftPro%20Pro%20Key%20(%2419%20USD)&body=Hi%20DraftPro%20Studio%2C%0A%0AI%20would%20like%20to%20purchase%20a%20DraftPro%20Pro%20License%20Key%20(%2419%20USD).%0AMy%20account%20email%3A%20" if is_en else "mailto:topjgapadsup804@gmail.com?subject=%5B%E8%B3%BC%E8%B2%B7%E6%8E%88%E6%AC%8A%5D%20DraftPro%20Pro%20%E6%B0%B8%E4%B9%85%E6%8E%88%E6%AC%8A%E7%A2%BC%20(NT%24590)&body=%E4%BD%A0%E5%A5%BD%EF%BC%8C%E6%88%91%E6%83%B3%E8%B3%BC%E8%B2%B7%20DraftPro%20Pro%20%E6%8E%88%E6%AC%8A%E7%A2%BC%EF%BC%88NT%24590%20%2F%20%2419%20USD%EF%BC%89%E3%80%82%0A%E6%88%91%E7%9A%84%E7%99%BB%E5%85%A5%E4%BF%A1%E7%AE%B1%EF%BC%9A",
    }

    tw_active = "" if is_en else " active"
    en_active = " active" if is_en else ""

    return f"""
<nav class="studio-global-nav">
  <div class="nav-left">
    <span class="nav-brand">DRAFT<b>PRO</b> STUDIO</span>
    <span class="nav-badge">{t['badge']}</span>
  </div>
  <div class="nav-right">
    <div class="nav-lang">
      <a href="demo.html" class="lang-pill{tw_active}">🇹🇼 繁體中文</a>
      <a href="demo-en.html" class="lang-pill{en_active}">🌐 English</a>
    </div>
    <button type="button" class="nav-btn nav-btn-pro" id="dpProBtn">{t['upgrade_btn']}</button>
    <button type="button" class="nav-btn" id="dpAuthBtn">{t['login_btn']}</button>
    <a href="{t['home_url']}" class="nav-link-home">{t['home_txt']}</a>
  </div>
</nav>
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
          <div class="dp-acct-row"><span>{t['acct_key']}</span><code id="dpAcctKey" style="color:#38bdf8;">—</code></div>
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
      $("dpAcctPlan").textContent = user.pro ? "PRO" : "FREE";
      $("dpAcctPlan").style.color = user.pro ? "#34d399" : "#fbbf24";
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
      authBtn.textContent = "👤 " + user.email.split("@")[0];
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
      tag.textContent = (user && user.pro) ? "PRO ✓" : "PRO 🔒";
      tag.style.background = (user && user.pro) ? "#059669" : "";
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

  // Capture-phase paywall guard for PRO CAD/PDF exports
  document.addEventListener("click", e => {{
    const btn = e.target && e.target.closest && e.target.closest("#exportMenu [data-exp]");
    if (!btn) return;
    if (!window.DRAFTPRO_CONFIG.proExports.includes(btn.dataset.exp)) return;
    const user = getCurrentUser();
    if (!user) {{
      e.preventDefault();
      e.stopImmediatePropagation();
      openModal("login", "info", MSG.msg_need_login);
      return;
    }}
    if (!user.pro) {{
      e.preventDefault();
      e.stopImmediatePropagation();
      openModal("pro", "info", MSG.msg_need_pro);
      return;
    }}
  }}, true);

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
