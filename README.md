# Minecraft Update Notifier

一個使用 GitHub Actions 自動監控 Minecraft 更新的通知系統，透過 Groq LLM 產生摘要後發送至 Discord。

---

## 功能

- 自動檢查 Minecraft Java Edition 最新版本（Release / Snapshot）
- 偵測版本更新後，從官方新聞 API 抓取最新遊戲更新文章
- 支援 Java Snapshot / Release、Bedrock Preview、Bedrock Changelog 等更新文章
- 跳過 Marketplace、Deep Dives 等非更新類文章
- 過濾技術性內容，保留玩家有感資訊
- 使用 Groq LLM 生成更新摘要（繁體中文、分類呈現）
- 發送 Discord Webhook 通知
- 使用 `state.json` 避免重複通知
- 完全無需常駐伺服器（GitHub Actions 運行）

---

## 系統架構

```text
GitHub Actions (每天 UTC 3:00 定時觸發)
        ↓
  取得 Java 版最新版本號
        ↓
  比對 state.json — 版本相同則結束
        ↓
  版本有變 → 從官方 API 抓取最新遊戲更新文章
        ↓
  解析文章內容（changelog / 新增方塊 / 機制變更）
        ↓
  關鍵字過濾（保留 Added / New / Introduced 行）
        ↓
  Groq LLM 摘要（繁體中文、分類整理）
        ↓
  Discord Webhook 發送通知
        ↓
  更新 state.json（記錄最新版本）
```

---

## 檔案結構

| 檔案 | 說明 |
|---|---|
| `src/main.py` | 進入點，串接整個流程 |
| `src/version.py` | 從 Mojang API 取得 Java 版最新 Release / Snapshot 編號 |
| `src/article.py` | 從官方 JSON API 抓取新聞列表，過濾出遊戲更新文章，解析 HTML 內文 |
| `src/filter.py` | 關鍵字過濾（保留玩家有感內容，移除技術細節） |
| `src/summarize.py` | 呼叫 Groq API 產生繁體中文摘要 |
| `src/discord.py` | 發送 Discord Webhook |
| `src/state.py` | 讀寫 `state.json`，避免重複通知 |
| `state.json` | 記錄最後處理的版本編號 |
| `.github/workflows/check-update.yml` | GitHub Actions 排程設定 |

---

## 部署方式

### 1. Fork 或 Clone 此 Repository

### 2. 在 GitHub Secrets 設定環境變數

前往 GitHub Repository → Settings → Secrets and variables → Actions → 新增：

| Name | Value |
|---|---|
| `GROQ_API_KEY` | 你的 Groq API Key |
| `DISCORD_WEBHOOK_URL` | 你的 Discord Webhook URL |

### 3. 啟用 GitHub Actions

Workflow 已設定為每日 UTC 3:00 自動執行，也可手動觸發。

---

## 本地開發

```bash
# 安裝依賴
poetry install --no-root

# 執行
poetry run python src/main.py
```

---

## state.json

用於避免重複通知。儲存最後處理的版本資訊：

```json
{
  "release": "26.2",
  "snapshot": "26.3-snapshot-1"
}
```

比對時兩者皆相同則跳過該次執行。

---

## 技術棧

- Python 3.11+
- httpx（HTTP 請求）
- BeautifulSoup 4（HTML 解析）
- Groq API（LLM 摘要生成）
- GitHub Actions（排程自動化）
- Discord Webhook（通知發送）
