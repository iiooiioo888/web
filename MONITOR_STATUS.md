# 代幣監控系統狀態報告

## 🎯 當前配置

### 監控地址
- **主要監控地址**: `0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03`
- **額外監控地址**: `0xdAC17F958D2ee523a2206206994597C13D831ec7` (USDT 代幣合約)

### 監控鏈和代幣

#### Ethereum 主網
- **RPC**: `https://mainnet.infura.io/v3/50e39fa39f7e4745866f7c4f717651d4`
- **監控代幣**:
  - USDT: `0xdAC17F958D2ee523a2206206994597C13D831ec7`
  - USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`

#### BSC 主網
- **RPC**: `https://bsc-dataseed.binance.org/`
- **監控代幣**:
  - BUSD: `0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56`
  - USDT: `0x55d398326f99059fF775485246999027B3197955`

## ✅ 系統狀態

### 數據庫
- ✅ `sender_addresses` 表已創建
- ✅ 表結構正確
- ✅ 已有 1 條測試記錄

### 監控功能
- ✅ Web3 連接正常
- ✅ 事件監控邏輯正常
- ✅ 發送方地址記錄功能正常

### 日誌記錄
- ✅ 監控器正在運行
- ✅ 日誌文件: `monitor.log`
- ✅ 實時檢測區塊鏈事件

## 📊 當前記錄

### 測試記錄
- **鏈**: ethereum
- **發送方**: `0x1234567890abcdef1234567890abcdef12345678`
- **接收方**: `0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03`
- **代幣**: USDT (`0xdAC17F958D2ee523a2206206994597C13D831ec7`)
- **交易哈希**: `0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890`
- **區塊號**: 23022335
- **金額**: 1000000

## 🚀 使用方法

### 1. 查看監控狀態
```bash
python query_senders.py
```

### 2. 檢查配置
```bash
python test_monitor_config.py
```

### 3. 查看日誌
```bash
tail -f monitor.log
```

## 📋 監控邏輯

當以下地址收到任何代幣時，系統會自動記錄發送方地址：

1. **`0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03`** - 主要監控地址
2. **`0xdAC17F958D2ee523a2206206994597C13D831ec7`** - USDT 代幣合約

### 監控範圍
- **Ethereum**: USDT, USDC 轉賬事件
- **BSC**: BUSD, USDT 轉賬事件

## 🔧 技術細節

### 數據庫表結構
```sql
CREATE TABLE sender_addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_name TEXT NOT NULL,
    sender_address TEXT NOT NULL,
    receiver_address TEXT NOT NULL,
    token_address TEXT NOT NULL,
    transaction_hash TEXT NOT NULL,
    block_number INTEGER,
    amount TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 監控事件
- **事件簽名**: `Transfer(address,address,uint256)`
- **監控頻率**: 實時監控最新區塊
- **回溯範圍**: 1000 個區塊

## 🎉 系統已準備就緒！

監控器正在後台運行，持續監控區塊鏈上的代幣轉賬事件。當監控地址收到代幣時，會自動記錄發送方地址到數據庫中。