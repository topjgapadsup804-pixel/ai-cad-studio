# DraftPro Studio — AI-CAD 施工圖 × 戶型轉 3D 空間互動提案

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Live_Demo-GitHub_Pages-brightgreen)](https://topjgapadsup804-pixel.github.io/ai-cad-studio/)
[![QA Specs](https://img.shields.io/badge/Architectural_QA-100%25_Passed-success)](check/)

專為室內設計工作室、統包工程行與房仲代銷打造的快速製圖與 3D 空間互動提案系統。  
將手繪草圖、舊圖面或格局圖，在 48 小時內轉換為符合建築製圖規範之標準 AutoCAD DWG、A3 施工圖 PDF，以及免裝軟體、用手機或瀏覽器即可自由漫遊與切換水電圖層的 3D 空間網頁。

---

## 🌐 線上即時展示 (Live Interactive Demos)

- 🏠 **[服務官網與即時估價試算器 (繁體中文 / TWD)](https://topjgapadsup804-pixel.github.io/ai-cad-studio/)**
- 🌐 **[International Service & Instant USD Quote (English)](https://topjgapadsup804-pixel.github.io/ai-cad-studio/en.html)**
- 📝 **[線上填寫製圖詢價單 / Submit Floor Plan Order Form](https://github.com/topjgapadsup804-pixel/ai-cad-studio/issues/new?template=order-quote.yml)**
- 🇹🇼 **[3D 互動戶型 Demo（臺灣繁體中文版）](https://topjgapadsup804-pixel.github.io/ai-cad-studio/demo.html)**
  - 30.2 坪標準三房兩廳兩衛（客餐廳、雙陽台、主臥、次臥、書房、雙衛浴）
  - 完整 2D 平面配置圖層、天花吊頂、地坪鋪貼、水電管線與 3D 自由漫遊
- 🌐 **[3D Interactive Floor Plan Demo (English — 100㎡ / 1,076 sq ft)](https://topjgapadsup804-pixel.github.io/ai-cad-studio/demo-en.html)**
  - International 3BR/2BA interactive 2D CAD + 3D walkthrough, MEP X-Ray, and DXF/PDF export.

---

## 📐 建築圖說標準檢驗 (QA Compliance)

本專案產出之圖面與模型，嚴格遵循建築圖說檢驗規範，並經自動化 QA 工具全數校驗通過：
- **承重牆與隔間牆真實厚度**：外牆與主要承重剪力牆 240mm / 200mm，分室輕質隔間牆 120mm。
- **門窗開口規範**：大門子母門開向正確且避開鞋櫃，主臥/次臥門軸留置開關實牆垛，窗洞設有標準窗臺高與窗頂高。
- **家具人體工學動線**：
  - 客廳主通道保留 $\ge 1,800\text{ mm}$ 淨通行寬度。
  - 書房、主臥、次臥皆具備獨立工作桌與衣櫃深度，無穿牆或重疊。
  - 衛浴與廚房落水頭（地漏）、排煙管道間、給排水管路全數避開樑柱與結構牆。
- **校驗結果**：`check.mjs` 與 `elecaudit.mjs` 檢驗結果 **0 錯誤、0 警告、0 衝突**。

---

## 💼 商業服務方案 (Commercial Packages)

| 服務項目 | 定價 | 適用場景 | 交付內容 | 交期 |
| :--- | :--- | :--- | :--- | :--- |
| **單圖快出** | **NT$ 3,500 / $120 USD 起** | 急件放樣、舊圖整理、樓梯詳圖 | 可編輯 DWG 檔 + A3 PDF | 48 小時 |
| **3D 互動設計包** | **NT$ 9,800 / $300 USD / 戶** | 業主提案、統包解說、代銷展示 | 2D 配置圖 + 專屬獨立 3D 互動網頁 + 估價表 | 72 小時 |
| **工作室包月外包** | **NT$ 28,000 / $890 USD / 月** | 設計公司長期製圖支援 | 每月 10 張施工圖 + 2 戶 3D 網頁 + 圖框同步 | 優先排程 (24h) |

> 完整變現規劃與合作細節，請參閱 **[MONETIZATION_STRATEGY.md](MONETIZATION_STRATEGY.md)**。

---

## 📩 業務預約與聯繫合作

- **接案專用信箱**：[`topjgapadsup804@gmail.com`](mailto:topjgapadsup804@gmail.com)
- **GitHub 需求提交**：歡迎透過 [Issues](https://github.com/topjgapadsup804-pixel/ai-cad-studio/issues) 發起專案洽詢。
- **海外案源委託**：支援 Upwork、Tasker 104、Pro360 接案與 USD / TWD 結算。

---

## 📄 授權條款 (License)

本儲存庫基礎代碼採用 **MIT License** 開源。  
商用戶型繪製、客製化白標商業專案提案與統包製圖服務，請直接聯繫官方信箱預約檔期。
