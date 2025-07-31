import json
from web3 import Web3
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_infura_config():
    """測試 Infura 配置"""
    try:
        # 加載配置
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("=== Infura 配置測試 ===")
        
        # 測試 Ethereum 連接
        ethereum_config = config['chains']['ethereum']
        print(f"Ethereum RPC URL: {ethereum_config['rpc_url']}")
        
        # 檢查 PROJECT_ID 是否已配置
        if 'YOUR_PROJECT_ID' in ethereum_config['rpc_url']:
            print("❌ 錯誤: 請先配置 Infura PROJECT_ID")
            return False
        
        # 測試 Web3 連接
        w3 = Web3(Web3.HTTPProvider(ethereum_config['rpc_url']))
        
        if w3.is_connected():
            print("✅ Ethereum 連接成功")
            
            # 獲取最新區塊
            latest_block = w3.eth.get_block('latest')
            print(f"最新區塊號: {latest_block.number}")
            print(f"區塊時間戳: {latest_block.timestamp}")
            
            # 測試代幣地址
            print(f"\n監控的代幣地址:")
            for token_addr in ethereum_config['token_addresses']:
                print(f"  {token_addr}")
            
            return True
        else:
            print("❌ Ethereum 連接失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_infura_config()
    if success:
        print("\n🎉 Infura 配置測試成功！")
    else:
        print("\n💥 Infura 配置測試失敗！")