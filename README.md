# Minecraft Java Edition Update Notifier

一個使用 GitHub Actions 自動監控 Minecraft Java Edition 更新的通知系統，並透過 Groq LLM 產生摘要後發送至 Discord。

---

## 功能

- 自動檢查 Minecraft Java Edition 最新版本（Release / Snapshot）
- 偵測版本更新
- 抓取官方更新文章
- 過濾技術性內容，保留玩家有感資訊
- 使用 Groq LLM 生成更新摘要
- 發送 Discord Webhook 通知
- 使用 `state.json` 避免重複通知
- 完全無需常駐伺服器（GitHub Actions 運行）

---

## 系統架構

```text
GitHub Actions (定時觸發)
        ↓
取得 Minecraft 版本資訊
        ↓
判斷是否有更新
        ↓
抓取官方 Java 更新文章
        ↓
內容過濾（移除技術內容）
        ↓
Groq LLM 摘要
        ↓
Discord Webhook 發送
        ↓
更新 state.json