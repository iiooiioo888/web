# 代幣監控系統配置說明

## 🎯 功能概述

本系統監控指定地址 `0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03`，當該地址收到任何代幣轉入時，自動記錄轉出方（發送方）的地址。

## 📋 配置詳情

### 監控地址
- **地址**: `0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03`
- **功能**: 當此地址收到任何代幣時，記錄發送方地址

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

## 🗄️ 數據庫結構

### sender_addresses 表
記錄所有發送方地址信息：
- `chain_name`: 區塊鏈名稱
- `sender_address`: 發送方地址
- `receiver_address`: 接收方地址（監控地址）
- `token_address`: 代幣合約地址
- `transaction_hash`: 交易哈希
- `block_number`: 區塊號
- `amount`: 轉賬金額
- `timestamp`: 記錄時間

## 🚀 使用方法

### 1. 開始監控
```bash
python token_monitor.py
```

### 2. 查看發送方記錄
```bash
python query_senders.py
```

### 3. 檢查配置狀態
```bash
python test_monitor_config.py
```

## 📊 監控邏輯

1. **實時監控**: 系統會持續監控 Ethereum 和 BSC 鏈上的代幣轉賬事件
2. **地址匹配**: 當檢測到轉入地址為 `0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03` 時
3. **記錄發送方**: 自動記錄轉出方地址到 `sender_addresses` 表
4. **詳細信息**: 同時記錄交易哈希、區塊號、金額等完整信息

## 🔧 配置文件

### config.json
```json
{
    "chains": {
        "ethereum": {
            "rpc_url": "https://mainnet.infura.io/v3/50e39fa39f7e4745866f7c4f717651d4",
            "chain_id": 1,
            "token_addresses": [
                "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
            ]
        },
        "bsc": {
            "rpc_url": "https://bsc-dataseed.binance.org/",
            "chain_id": 56,
            "token_addresses": [
                "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
                "0x55d398326f99059fF775485246999027B3197955"
            ]
        }
    },
    "monitored_addresses": [
        "0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03"
    ],
    "database": "addresses.db"
}
```

## 📝 日誌輸出

當監控地址收到代幣時，系統會輸出詳細信息：
```
🎯 監控地址收到代幣！
  接收地址: 0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03
  發送地址: 0x1234567890abcdef...
  代幣地址: 0xdAC17F958D2ee523a2206206994597C13D831ec7
  交易哈希: 0xabcdef123456...
  區塊號: 23022335
  金額: 1000000
```

## ✅ 配置完成狀態

- ✅ Infura PROJECT_ID 已配置
- ✅ 監控地址已設置
- ✅ Web3 連接正常
- ✅ 數據庫結構已準備
- ✅ 監控邏輯已實現

## 🎉 系統已準備就緒！

現在可以運行 `python token_monitor.py` 開始監控了！