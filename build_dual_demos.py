"""
雙語版本建置腳本（全新整合式版面結構，非浮動疊套）：
1. 頂部整合導覽列 (studio-global-nav) 做為 .app flex-direction: column 的首個子元素 (in-flow)。
2. 不使用任何 position: fixed / absolute 疊套遮擋面板或標籤。
3. 繁體版 (demo.html & demo-zh-tw.html) 全介面 100% 繁體中文與臺灣裝修圖說規範。
4. 簡體版 (demo-zh-cn.html) 100% 符合大陸 GB/T 規範。
"""
import copy
import json
import os
import re
import subprocess
import sys
from opencc import OpenCC

here = os.path.dirname(os.path.abspath(__file__))
skill_dir = r"C:\Users\jack5\.gemini\config\skills\house-plan-designer"
template_src = os.path.join(skill_dir, "assets", "template.html")
build_py = os.path.join(skill_dir, "scripts", "build.py")

# 讀取原始 template.html
with open(template_src, encoding="utf-8") as f:
    orig_template = f.read()

# 讀取基礎 spec.json
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
spec_tw["name"] = "DraftPro Studio · 30.2 坪標準三房兩廳兩衛（臺灣繁體標準）"
for r in spec_tw["rooms"]:
    if r["name"] in tw_room_names:
        r["name"] = tw_room_names[r["name"]]

with open(os.path.join(here, "spec_zh_tw.json"), "w", encoding="utf-8") as f:
    json.dump(spec_tw, f, ensure_ascii=False, indent=2)

# ==========================================
# 2. 簡體中文版 Spec (大陸 GB/T 規範)
# ==========================================
spec_cn = copy.deepcopy(base_spec)
spec_cn["name"] = "DraftPro Studio · 100㎡ 标准三室两厅两卫（大陆标准）"

with open(os.path.join(here, "spec_zh_cn.json"), "w", encoding="utf-8") as f:
    json.dump(spec_cn, f, ensure_ascii=False, indent=2)

# ==========================================
# 3. 繁體中文版 Template 生成 (OpenCC 全量轉換 + 專業詞彙精修)
# ==========================================
cc_tw = OpenCC("s2tw")
tw_template = cc_tw.convert(orig_template)

# 精修字體與臺灣專屬建築/裝修術語
tw_template = tw_template.replace('"PingFang SC","Microsoft YaHei"', '"PingFang TC","Microsoft JhengHei","Noto Sans TC","PingFang SC"')
tw_template = tw_template.replace("单价(元)", "單價(NTD)")
tw_template = tw_template.replace("合价(元)", "小計(NTD)")
tw_template = tw_template.replace("合价", "小計")
tw_template = tw_template.replace("项目", "工項")
tw_template = tw_template.replace("定制衣柜", "系統衣櫃")
tw_template = tw_template.replace("定制鞋柜", "系統鞋櫃")
tw_template = tw_template.replace("定制餐边柜", "系統餐邊櫃")
tw_template = tw_template.replace("定制柜", "系統櫃")
tw_template = tw_template.replace("拆改", "拆除隔間")
tw_template = tw_template.replace("导出 CAD", "匯出 CAD")
tw_template = tw_template.replace("导出 PDF", "匯出 PDF")
tw_template = tw_template.replace("保存方案", "儲存方案")
tw_template = tw_template.replace("燃气灶", "瓦斯爐")
tw_template = tw_template.replace("集成灶", "瓦斯爐/集成爐")
tw_template = tw_template.replace("油烟机", "抽油煙機")
tw_template = tw_template.replace("台盆", "面盆")
tw_template = tw_template.replace("花洒", "蓮蓬頭/花灑")
tw_template = tw_template.replace("淋浴房", "淋浴拉門")

# 存儲繁體模板
tw_template_path = os.path.join(here, "template_zh_tw.html")
with open(tw_template_path, "w", encoding="utf-8") as f:
    f.write(tw_template)

# ==========================================
# 4. 建置 HTML
# ==========================================
print("Building demo-zh-cn.html...")
subprocess.run([sys.executable, build_py, "spec_zh_cn.json", "-o", "demo-zh-cn.html"], cwd=here, check=True)

print("Building demo-zh-tw.html...")
subprocess.run([sys.executable, build_py, "spec_zh_tw.json", "-o", "demo-zh-tw.html", "--template", tw_template_path], cwd=here, check=True)

# 刪除臨時繁體模板
if os.path.exists(tw_template_path):
    os.remove(tw_template_path)

# ==========================================
# 5. 整合式頂部版面樣式 (In-flow Flex Item，非浮動疊套)
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
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Noto Sans TC", sans-serif;
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
      <span class="lang-txt">語言切換：</span>
      <a href="demo.html" class="lang-pill active">🇹🇼 臺灣繁體版</a>
      <a href="demo-zh-cn.html" class="lang-pill">🇨🇳 大陸簡體版</a>
    </div>
    <a href="index.html" class="nav-link-home">官網服務報價 ➔</a>
  </div>
</nav>
"""

cn_nav_html = """
<nav class="studio-global-nav">
  <div class="nav-left">
    <span class="nav-brand">DRAFT<b>PRO</b> STUDIO</span>
    <span class="nav-badge">AI-CAD 3D 空间交互提案</span>
  </div>
  <div class="nav-right">
    <div class="nav-lang">
      <span class="lang-txt">语言切换：</span>
      <a href="demo.html" class="lang-pill">🇹🇼 台湾繁体版</a>
      <a href="demo-zh-cn.html" class="lang-pill active">🇨🇳 大陆简体版</a>
    </div>
    <a href="index.html" class="nav-link-home">官网服务报价 ➔</a>
  </div>
</nav>
"""

def inject_in_flow_nav(file_path, nav_html, is_tw=False):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 注入 CSS 到 </head> 前
    html = html.replace("</head>", f"{nav_css}\n</head>")

    # 2. 將導覽列作為 .app 裡面的第一個正常文檔流元素，放置在 <header> 正前方（完全不疊套）
    if '<div class="app">' in html:
        html = html.replace('<div class="app">', f'<div class="app">\n{nav_html}')
    else:
        # fallback
        html = html.replace('<body>', f'<body>\n{nav_html}')

    # 3. 繁體版本語意與標題精修
    if is_tw:
        html = html.replace("装修设计器</title>", "3D 空間互動提案</title>")
        html = html.replace("夾角里的", "夾角裡的")
        html = html.replace("」里加", "」裡加")
        html = html.replace("3D 里", "3D 裡")
        html = html.replace("圖層里", "圖層裡")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

# 處理繁體版 demo-zh-tw.html 與 demo.html
inject_in_flow_nav(os.path.join(here, "demo-zh-tw.html"), tw_nav_html, is_tw=True)
open(os.path.join(here, "demo.html"), "w", encoding="utf-8").write(open(os.path.join(here, "demo-zh-tw.html"), encoding="utf-8").read())

# 處理簡體版 demo-zh-cn.html
inject_in_flow_nav(os.path.join(here, "demo-zh-cn.html"), cn_nav_html, is_tw=False)

print("Successfully injected integrated, in-flow navigation bars into both editions!")
