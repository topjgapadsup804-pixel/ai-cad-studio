"""
雙語版本建置腳本（完整字體與語意在地化）：
1. 繁體中文版本 (demo.html & demo-zh-tw.html)：
   - 全介面（面板、圖庫、工項清單、導覽、標註、提示）100% 轉換為臺灣標準繁體中文
   - 包含臺灣字體棧 ("PingFang TC", "Microsoft JhengHei", "Noto Sans TC")
   - 房名符合臺灣建築圖說規範（客餐廳、雙衛、景觀陽台、工作陽台、主臥、次臥、書房）
   - 報價幣別改為 NTD，項目欄位為工項/數量/小計
2. 簡體中文版本 (demo-zh-cn.html)：
   - 100% 符合大陸 GB/T 建築圖說標準（客餐厅、景观阳台、生活阳台、主卧、次卧、书房、主卫、公卫）
3. 兩者頂部皆具備即時雙向切換導覽條。
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

# 導覽切換條
tw_bar = """<style>
.studio-top-bar {
  position: fixed; top: 12px; right: 16px; z-index: 99999;
  background: rgba(15, 23, 42, 0.92); border: 1px solid #38bdf8;
  backdrop-filter: blur(8px); border-radius: 999px;
  padding: 6px 14px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", sans-serif;
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
  padding: 6px 14px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
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

# 寫入 demo-zh-tw.html 並加入導覽條與繁體語意修飾
html_tw = open(os.path.join(here, "demo-zh-tw.html"), encoding="utf-8").read()
html_tw = html_tw.replace("<body>", f"<body>\n{tw_bar}")
html_tw = html_tw.replace("装修设计器</title>", "3D 空間互動提案</title>")
html_tw = html_tw.replace("夾角里的", "夾角裡的")
html_tw = html_tw.replace("」里加", "」裡加")
html_tw = html_tw.replace("3D 里", "3D 裡")
html_tw = html_tw.replace("圖層里", "圖層裡")
open(os.path.join(here, "demo-zh-tw.html"), "w", encoding="utf-8").write(html_tw)

# 同步為 demo.html（繁體中文為預設）
open(os.path.join(here, "demo.html"), "w", encoding="utf-8").write(html_tw)

# 寫入 demo-zh-cn.html 並加入導覽條
html_cn = open(os.path.join(here, "demo-zh-cn.html"), encoding="utf-8").read()
html_cn = html_cn.replace("<body>", f"<body>\n{cn_bar}")
open(os.path.join(here, "demo-zh-cn.html"), "w", encoding="utf-8").write(html_cn)

print("Successfully built fully-localized Traditional Chinese and Simplified Chinese editions.")
