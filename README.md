# 掛機挖礦服務

一個基於Flask的掛機挖礦Web服務，用戶可以註冊登錄後選擇參與的礦場，服務器會記錄參與時間並在指定時間自動發放"原礦"獎勵。

## 功能特色

- 🔐 用戶註冊和登錄系統
- ⛏️ 多種礦場選擇（不同難度和獎勵倍率）
- ⏰ 自動定時獎勵發放（每1秒）
- 💰 原礦餘額管理
- 📊 挖礦狀態實時監控
- 📈 獎勵歷史記錄
- 🎨 現代化響應式界面

## 系統要求

- Python 3.7+
- pip

## 安裝步驟

1. **克隆或下載項目**
   ```bash
   cd web/
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **啟動服務**
   ```bash
   python run.py
   ```

4. **訪問服務**
   打開瀏覽器訪問：http://localhost:5000

## 使用說明

### 用戶註冊
1. 訪問首頁，點擊"註冊帳號"
2. 填寫用戶名、郵箱和密碼
3. 提交註冊信息

### 開始挖礦
1. 登錄後進入控制台
2. 選擇想要參與的礦場
3. 點擊"開始挖礦"按鈕
4. 系統會記錄挖礦開始時間

### 獎勵機制
- 每1秒自動發放獎勵
- 獎勵計算：挖礦時長 × 基礎獎勵率 × 礦場倍率
- 基礎獎勵率：每秒1個原礦（已加速）
- 獎勵時間：每1秒自動發放

### 礦場類型
- **新手礦場**：1.0x倍率，適合新手
- **進階礦場**：1.5x倍率，中等難度
- **專家礦場**：2.0x倍率，高難度高回報
- **傳說礦場**：3.0x倍率，最高難度

## 項目結構

```
web/
├── app.py              # 主應用程序
├── run.py              # 啟動腳本
├── requirements.txt    # Python依賴
├── README.md          # 項目說明
├── templates/         # HTML模板
│   ├── base.html      # 基礎模板
│   ├── index.html     # 首頁
│   ├── login.html     # 登錄頁面
│   ├── register.html  # 註冊頁面
│   └── dashboard.html # 控制台
└── mining_service.db  # SQLite數據庫（運行後生成）
```

## 數據庫模型

### User（用戶）
- id：用戶ID
- username：用戶名
- email：郵箱
- password_hash：密碼哈希
- created_at：註冊時間
- balance：原礦餘額

### Mine（礦場）
- id：礦場ID
- name：礦場名稱
- description：描述
- base_reward_rate：獎勵倍率
- max_capacity：最大容量
- current_players：當前玩家數
- is_active：是否開放

### MiningSession（挖礦會話）
- id：會話ID
- user_id：用戶ID
- mine_id：礦場ID
- start_time：開始時間
- end_time：結束時間
- is_active：是否活躍
- total_mining_time：總挖礦時間

### Reward（獎勵記錄）
- id：獎勵ID
- user_id：用戶ID
- mine_id：礦場ID
- amount：獎勵數量
- reward_time：發放時間
- reward_type：獎勵類型

## 技術棧

- **後端**：Flask + SQLAlchemy
- **前端**：Bootstrap 5 + jQuery
- **數據庫**：SQLite
- **定時任務**：schedule庫

## 注意事項

1. 首次運行會自動創建數據庫和默認礦場
2. 定時獎勵發放功能在後台運行，需要保持服務運行
3. 建議在生產環境中使用更安全的數據庫（如PostgreSQL）
4. 可以根據需要調整獎勵倍率和發放時間

## 開發說明

### 添加新礦場
在`app.py`的`init_database()`函數中添加新的礦場配置。

### 修改獎勵機制
在`distribute_rewards()`函數中調整獎勵計算邏輯。

### 自定義界面
修改`templates/`目錄下的HTML模板文件。

## 授權

本項目僅供學習和演示使用。 