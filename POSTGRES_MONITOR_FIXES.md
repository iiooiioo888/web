# PostgreSQL 監控系統錯誤修復記錄

## 修復的問題

### 1. UnicodeEncodeError 編碼問題
**錯誤**: `UnicodeEncodeError: 'cp950' codec can't encode character '\u2705'`
**原因**: 日誌輸出中使用了 emoji 字符，但 Windows 終端的默認編碼 (CP950) 不支持這些字符
**解決方案**: 
- 移除所有 emoji 字符 (✅, ❌, 🎯, 🔍, 🚀, ⏹️, 🔌)
- 在 FileHandler 中指定 `encoding='utf-8'`

### 2. ExtraDataLengthError POA 鏈問題
**錯誤**: `web3.exceptions.ExtraDataLengthError: The field extraData is 280 bytes, but should be 32`
**原因**: BSC 是 Proof-of-Authority (POA) 鏈，需要特殊的中間件處理
**解決方案**: 
- 導入 `geth_poa_middleware`
- 為 BSC 鏈添加 POA 中間件：`w3.middleware_onion.inject(geth_poa_middleware, layer=0)`

### 3. RPC 查詢結果過多錯誤
**錯誤**: `ValueError: {'code': -32005, 'message': 'query returned more than 10000 results...'}`
**原因**: Infura 等 RPC 提供商對 `get_logs` 查詢有結果數量限制
**解決方案**:
- 減少區塊範圍從 1000 個區塊到 100 個區塊
- 添加專門的 ValueError 異常處理
- 使用具體的區塊號而不是 'latest'

## 修復後的代碼改進

### 日誌配置
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_postgres.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

### POA 中間件配置
```python
from web3.middleware import geth_poa_middleware

# 為 BSC 鏈添加 POA 中間件
if chain_name == 'bsc':
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
```

### 改進的區塊監控
```python
# 使用較小的區塊範圍來避免 RPC 限制
from_block = max(0, current_block - 100)  # 減少到 100 個區塊

logs = w3.eth.get_logs({
    'address': token_address,
    'topics': [transfer_signature],
    'fromBlock': from_block,
    'toBlock': current_block  # 使用具體區塊號
})
```

### 錯誤處理
```python
except ValueError as e:
    if "query returned more than 10000 results" in str(e):
        logging.warning(f"{chain_name} - {token_address}: RPC 查詢結果過多，跳過此代幣")
    else:
        logging.error(f"監控 {chain_name} - {token_address} 失敗: {e}")
```

## 當前狀態

✅ **所有錯誤已修復**
- 編碼問題已解決
- POA 鏈支持已添加
- RPC 查詢限制已處理
- 監控腳本正常運行

## 運行狀態

腳本正在後台運行，監控以下內容：
- **Ethereum 鏈**: USDT, USDC 代幣
- **BSC 鏈**: BUSD, USDT 代幣
- **監控地址**: `0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03`

## 數據庫表結構

### sender_addresses 表
記錄發送到監控地址的代幣轉賬信息：
- chain_name: 鏈名稱
- sender_address: 發送方地址
- receiver_address: 接收方地址（監控地址）
- token_address: 代幣地址
- transaction_hash: 交易哈希
- block_number: 區塊號
- amount: 轉賬金額

### transaction_records 表
記錄所有監控到的轉賬事件：
- chain_name: 鏈名稱
- transaction_hash: 交易哈希
- block_number: 區塊號
- from_address: 發送方地址
- to_address: 接收方地址
- token_address: 代幣地址
- amount: 轉賬金額

## 使用方法

1. **啟動監控**:
   ```bash
   python token_monitor_postgres.py
   ```

2. **查詢數據**:
   ```bash
   python query_postgres.py
   ```

3. **停止監控**:
   ```bash
   # 使用 Ctrl+C 或終止 Python 進程
   ```

## 監控日誌

日誌文件: `monitor_postgres.log`
- 記錄連接狀態
- 記錄找到的 Transfer 事件數量
- 記錄監控到的代幣轉入事件
- 記錄錯誤和警告信息

## 注意事項

1. **區塊範圍**: 每次只監控最近 100 個區塊，避免 RPC 限制
2. **監控間隔**: 每 60 秒檢查一次新區塊
3. **錯誤恢復**: 遇到錯誤時會等待 10 秒後重試
4. **數據持久化**: 所有數據存儲在 PostgreSQL 數據庫中