# Google / GitHub / Apple 第三方帳號登入啟用指南（3 分鐘免費串接）

DraftPro Studio 前端（`demo.html` / `demo-en.html`）已內建 **Supabase OAuth** 與 **Google Identity Services (GIS)** 完整串接程式，支援 **Google、GitHub、Apple** 一鍵登入與真實頭像顯示。

因為 OAuth 必須綁定您自己的開發者金鑰，請依以下 3 步驟啟用（全程免費額度 50,000 MAU）：

---

## 方式一：透過 Supabase 一次開通 Google + GitHub + Apple（最推薦）

1. 前往 [https://supabase.com](https://supabase.com) 免費建立一個專案（例如 `draftpro-studio`）。
2. 在左側選單進入 **Authentication → URL Configuration**：
   - **Site URL**：`https://topjgapadsup804-pixel.github.io/ai-cad-studio/`
   - **Redirect URLs** 新增：
     - `https://topjgapadsup804-pixel.github.io/ai-cad-studio/demo.html`
     - `https://topjgapadsup804-pixel.github.io/ai-cad-studio/demo-en.html`
3. 在 **Authentication → Providers** 開啟：
   - **Google**（填入 Google Cloud Console 取得的 Client ID 與 Secret）
   - **GitHub**（填入 GitHub OAuth App 的 Client ID 與 Secret）
   - **Apple**（選用，需 Apple Developer 帳號）
4. 到 **Project Settings → API** 複製 **Project URL** 與 **anon public key**，貼入 `build_dual_demos.py` 的 `window.DRAFTPRO_CONFIG`：
   ```js
   window.DRAFTPRO_CONFIG = {
     supabaseUrl: "https://YOUR_PROJECT.supabase.co",
     supabaseAnonKey: "YOUR_ANON_PUBLIC_KEY",
     googleClientId: "",
     gumroadProductId: "",
     ...
   };
   ```
5. 重新執行 `python build_dual_demos.py` 並推送，即刻啟用真實第三方登入！

---

## 方式二：僅串接 Google 一鍵登入（免 Supabase）

1. 前往 [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials) 建立 **OAuth 2.0 Client ID（Web application）**。
2. **Authorized JavaScript origins** 填入：
   - `https://topjgapadsup804-pixel.github.io`
3. 將取得的 `YOUR_CLIENT_ID.apps.googleusercontent.com` 貼入 `build_dual_demos.py` 的 `googleClientId` 欄位並重新建置即可。
