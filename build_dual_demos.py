"""
產生繁體中文與簡體中文雙版本戶型 3D 互動設計器：
1. demo-zh-tw.html & demo.html：臺灣繁體中文建築圖說規範（坪數、客餐廳、景觀陽台、工作陽台、主臥、主衛、客衛、書房、次臥、廚房）
2. demo-zh-cn.html：簡體中文建築圖說規範（平米、客餐厅、景观阳台、生活阳台、主卧、主卫、公卫、书房、次卧、厨房）
並在介面頂部加入便捷語言切換導覽條。
"""
import copy
import json
import os
import re
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
skill_dir = r"C:\Users\jack5\.gemini\config\skills\house-plan-designer"
build_py = os.path.join(skill_dir, "scripts", "build.py")

# 讀取基礎 spec.json
base_spec = json.load(open(os.path.join(here, "spec.json"), encoding="utf-8"))

# 繁體版本 Room 映射
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

# 1. 產生 spec_zh_tw.json
spec_tw = copy.deepcopy(base_spec)
spec_tw["name"] = "DraftPro Studio · 30.2 坪標準三房兩廳兩衛（繁體中文版）"
for r in spec_tw["rooms"]:
    if r["name"] in tw_room_names:
        r["name"] = tw_room_names[r["name"]]

with open(os.path.join(here, "spec_zh_tw.json"), "w", encoding="utf-8") as f:
    json.dump(spec_tw, f, ensure_ascii=False, indent=2)

# 2. 產生 spec_zh_cn.json
spec_cn = copy.deepcopy(base_spec)
spec_cn["name"] = "DraftPro Studio · 100㎡ 标准三室两厅两卫（简体中文版）"
with open(os.path.join(here, "spec_zh_cn.json"), "w", encoding="utf-8") as f:
    json.dump(spec_cn, f, ensure_ascii=False, indent=2)

# 3. 使用 build.py 建置 HTML
print("Building demo-zh-cn.html...")
subprocess.run([sys.executable, build_py, "spec_zh_cn.json", "-o", "demo-zh-cn.html"], cwd=here, check=True)

print("Building demo-zh-tw.html...")
subprocess.run([sys.executable, build_py, "spec_zh_tw.json", "-o", "demo-zh-tw.html"], cwd=here, check=True)

# 4. 繁體中文 UI 詞庫替換
tw_replacements = [
    (r"户型装修设计器", r"戶型裝修設計器"),
    (r"装修设计器", r"3D 空間互動提案設計器"),
    (r"“我的造型”", r"「我的造型」"),
    (r"从模型库删除", r"從模型庫刪除"),
    (r"点击放到视图中心", r"點擊放到視圖中心"),
    (r"点击添加到视图中心", r"點擊添加到視圖中心"),
    (r"拖到平面 / 3D 里", r"拖到平面 / 3D 空間內"),
    (r"已替换为：", r"已替換為："),
    (r"画场地", r"繪製場地"),
    (r"画吊顶造型", r"繪製天花吊頂造型"),
    (r"顶面图层", r"天花圖層"),
    (r"工程直接费", r"工程直接費"),
    (r"管理费", r"管理費"),
    (r"合计", r"合計"),
    (r"合价\(元\)", r"小計(NTD)"),
    (r"单价\(元\)", r"單價(NTD)"),
    (r"明细", r"明細"),
    (r"项目", r"工項"),
    (r"分类", r"類別"),
    (r"单位", r"單位"),
    (r"数量", r"數量"),
    (r"家具软装", r"家具軟裝"),
    (r"定制柜", r"系統櫃"),
    (r"拆改", r"拆除隔間"),
    (r"水电", r"水電管線"),
    (r"地面", r"地坪鋪貼"),
    (r"墙面", r"牆面配置"),
    (r"顶面", r"天花吊頂"),
    (r"原始结构", r"原始結構圖"),
    (r"方案图", r"平面配置圖"),
]

# 導覽條 HTML
tw_bar = """<style>
.studio-top-bar {
  position: fixed; top: 12px; right: 16px; z-index: 99999;
  background: rgba(15, 23, 42, 0.92); border: 1px solid #38bdf8;
  backdrop-filter: blur(8px); border-radius: 999px;
  padding: 6px 14px; font-family: -apple-system, sans-serif;
  display: flex; gap: 10px; align-items: center; font-size: 13px; color: #f1f5f9;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.studio-top-bar a { color: #94a3b8; text-decoration: none; font-weight: 500; transition: color 0.15s; }
.studio-top-bar a:hover { color: #38bdf8; }
.studio-top-bar a.active { color: #38bdf8; font-weight: 700; }
.studio-top-bar .sep { color: #475569; }
</style>
<div class="studio-top-bar">
  <span style="color:#38bdf8;font-weight:700;">DraftPro 3D</span>
  <span class="sep">|</span>
  <a href="demo.html" class="active">🇹🇼 繁體版</a>
  <a href="demo-zh-cn.html">🇨🇳 简体版</a>
  <span class="sep">|</span>
  <a href="index.html" style="color:#e2e8f0;">首頁服務報價 ➔</a>
</div>
"""

cn_bar = """<style>
.studio-top-bar {
  position: fixed; top: 12px; right: 16px; z-index: 99999;
  background: rgba(15, 23, 42, 0.92); border: 1px solid #38bdf8;
  backdrop-filter: blur(8px); border-radius: 999px;
  padding: 6px 14px; font-family: -apple-system, sans-serif;
  display: flex; gap: 10px; align-items: center; font-size: 13px; color: #f1f5f9;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.studio-top-bar a { color: #94a3b8; text-decoration: none; font-weight: 500; transition: color 0.15s; }
.studio-top-bar a:hover { color: #38bdf8; }
.studio-top-bar a.active { color: #38bdf8; font-weight: 700; }
.studio-top-bar .sep { color: #475569; }
</style>
<div class="studio-top-bar">
  <span style="color:#38bdf8;font-weight:700;">DraftPro 3D</span>
  <span class="sep">|</span>
  <a href="demo.html">🇹🇼 繁体版</a>
  <a href="demo-zh-cn.html" class="active">🇨🇳 简体版</a>
  <span class="sep">|</span>
  <a href="index.html" style="color:#e2e8f0;">首页服务报价 ➔</a>
</div>
"""

# 處理 demo-zh-tw.html
html_tw = open(os.path.join(here, "demo-zh-tw.html"), encoding="utf-8").read()
for pat, rep in tw_replacements:
    html_tw = re.sub(pat, rep, html_tw)
html_tw = html_tw.replace("<body>", f"<body>\n{tw_bar}")
open(os.path.join(here, "demo-zh-tw.html"), "w", encoding="utf-8").write(html_tw)

# 同步至 demo.html（繁體為預設）
open(os.path.join(here, "demo.html"), "w", encoding="utf-8").write(html_tw)

# 處理 demo-zh-cn.html
html_cn = open(os.path.join(here, "demo-zh-cn.html"), encoding="utf-8").read()
html_cn = html_cn.replace("<body>", f"<body>\n{cn_bar}")
open(os.path.join(here, "demo-zh-cn.html"), "w", encoding="utf-8").write(html_cn)

print("Both demo-zh-tw.html, demo.html, and demo-zh-cn.html built successfully with language bars.")
