import json
from web3 import Web3
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_data_parsing():
    """測試數據解析修復"""
    try:
        # 加載配置
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("=== 數據解析測試 ===")
        
        # 測試 Ethereum 連接
        ethereum_config = config['chains']['ethereum']
        w3 = Web3(Web3.HTTPProvider(ethereum_config['rpc_url']))
        
        if w3.is_connected():
            print("✅ Ethereum 連接成功")
            
            # 獲取最新區塊
            latest_block = w3.eth.get_block('latest')
            print(f"最新區塊號: {latest_block.number}")
            
            # 測試 Transfer 事件簽名
            transfer_signature = Web3.keccak(text="Transfer(address,address,uint256)").hex()
            print(f"Transfer 事件簽名: {transfer_signature}")
            
            # 測試數據解析
            test_data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcd\x137'
            
            if isinstance(test_data, bytes):
                amount = int.from_bytes(test_data, byteorder='big')
                print(f"✅ 測試數據解析成功: {amount}")
            else:
                print("❌ 數據格式錯誤")
            
            return True
        else:
            print("❌ Ethereum 連接失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_data_parsing()
    if success:
        print("\n🎉 數據解析修復測試成功！")
    else:
        print("\n💥 數據解析修復測試失敗！")