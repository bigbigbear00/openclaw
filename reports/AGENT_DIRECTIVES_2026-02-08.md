Agent Delivery Directives — 2026-02-08

Copy each section and forward to the corresponding Agent group or individual. Each agent must ACK by appending a JSON ACK to their inbox.jsonl as shown.

---

1) nba-expert (球弟)

球弟，重要流程更新，請立即遵守並回執：
- 所有正式 boxscore / 數據產物必須寫入：/Users/apple/clawd/claw_comm/nba-expert/artifacts
- 每場記錄必須包含字段：game, score, boxscore_url（權威來源：NBA/ESPN/Basketball-Reference 至少一條）、top_players（name/pts/reb/ast）、highlight
- 產物寫入後系統會自動運行 QA；僅 QA=PASS 才能被標記 DELIVERED 與 publish_ready
- 若抓取失敗請寫 FAILED_FETCH 並附原因，不得偽造數據或寫佔位文本

請在收到本消息後向 /Users/apple/clawd/claw_comm/nba-expert/inbox.jsonl 追加一條 ACK（格式示例）：
{"id":"ack-<timestamp>","timestamp":"<ISO>","from":"agent:nba-expert","to":"agent:main:main","type":"ack","subject":"ack","body":"ack","status":"done"}

---

2) writer-editor (簡寧)

簡寧，重要流程更新，請立即遵守並回執：
- writer-editor 的輸出必須結構化 claims；每條 claim 必須帶 source_url（可追溯），未驗證條目必須進入 Rumor 區
- 生成 final 報告前必須確保依賴的 boxscore.json 存在且 QA=PASS；若依賴缺失寫 BLOCKED_WAITING_DEP（body 必列缺失路徑）
- DONE 僅在 QA PASS 且 verification_summary 明確後允許

請在收到本消息後在 /Users/apple/clawd/claw_comm/writer-editor/inbox.jsonl 寫一條 ACK（同上格式）。

---

3) news-analyst (探哥)

探哥，重要流程更新，請立即遵守並回執：
- 所有正式產物請寫入標準 artifacts：/Users/apple/clawd/claw_comm/news-analyst/artifacts（若你目前使用其他路徑，請改為此路徑；若有歷史原因需要保留，請回覆說明）
- 產物必須附帶可追溯 source_url；摘要需在 verification_summary 中標注已驗證/未驗證項
- 寫入後系統會自動 QA，QA=PASS 才能 DELIVERED

請在收到本消息後向 /Users/apple/clawd/claw_comm/news-analyst/inbox.jsonl 追加 ACK（同上格式），並說明你的 artifacts 當前路徑是否已為標準路徑。

---

4) ctf-director (小鑽)

小鑽，重要流程更新，請立即遵守並回執：
- 采集與匯總產物請寫入：/Users/apple/clawd/claw_comm/ctf-director/artifacts
- 采集產物需包含源條目（原始 URL / API 回應）並寫入采集日誌；自動化結果需附 verification_summary
- 若抓取腳本或 cron 出現錯誤請寫 FAILED_FETCH 並把日誌路徑帶上以便排查

請在收到本消息後在 /Users/apple/clawd/claw_comm/ctf-director/inbox.jsonl 寫 ACK（同上格式）。

---

5) library-keeper (小雅)

小雅，重要流程更新，請立即遵守並回執：
- 資料、知識與最終稿請寫入：/Users/apple/clawd/claw_comm/library-keeper/artifacts（並保持 metadata/source_url 完整）
- 幫助審校 verification_summary / sources；若發現未驗證項，請把清單寫入 verification_todo，並把路徑回報 main

請在收到本消息後在 /Users/apple/clawd/claw_comm/library-keeper/inbox.jsonl 寫 ACK（同上格式）。

---

6) designer (畫畫)

設計組，請注意流程更新並回執：
- 所有最終設計產物（發布級圖片/素材）請寫入：/Users/apple/clawd/claw_comm/designer/artifacts，並在 meta 中寫明來源/資產授權（如 stock link / license）
- 不要把佔位圖或佔位文本當作最終 artifact；系統會 QA 檢測“Artifact for/placeholder”並拒絕

請在收到本消息後在 /Users/apple/clawd/claw_comm/designer/inbox.jsonl 寫 ACK（同上格式）。

---

7) vn-realestate (阿南)

阿南，重要流程更新請回執：
- 本地調研產物請寫入：/Users/apple/clawd/claw_comm/vn-realestate/artifacts，並附來源（現場照片、官方登記頁、聯絡方式）
- 若存在數據敏感或需脫敏的項目，請在 artifact metadata 標註並通知 main 以便合規處理

請收到後在 /Users/apple/clawd/claw_comm/vn-realestate/inbox.jsonl 寫 ACK（同上格式）。

---

8) main / ops (哆啦Ai熊 & 負責人)

主控/Ops，已下發給全部 agent 的正式流程更新通知，要求：
- 確保 inbox 路徑與 artifacts 路徑一致性；對不一致者由 owner 負責手動修正或請 sysadmin 建 symlink
- 繼續監控 QA/FAILED/BLOCKED 的報警；任何 FAILED 兩次須發 WAITING_APPROVAL 並通知老板

請 main 在 /Users/apple/clawd/claw_comm/main/inbox.jsonl 寫 ACK（同上格式）。

---

Notes:
- If you want I can send these messages to agent Telegram groups for you (need chat IDs). As instructed, you will forward them manually; this file is prepared for copy-paste.

Generated at: 2026-02-08T10:19:00Z
