import json
from web3 import Web3
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_web3_connections():
    """測試 Web3 連接"""
    try:
        # 加載配置
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("=== Web3 連接測試 ===")
        
        for chain_name, chain_config in config['chains'].items():
            print(f"\n測試 {chain_name} 連接...")
            
            try:
                # 創建 Web3 實例
                w3 = Web3(Web3.HTTPProvider(chain_config['rpc_url']))
                
                # 測試連接
                if w3.is_connected():
                    print(f"✓ {chain_name} 連接成功")
                    
                    # 獲取最新區塊
                    latest_block = w3.eth.get_block('latest')
                    print(f"  最新區塊號: {latest_block['number']}")
                    print(f"  區塊時間戳: {latest_block['timestamp']}")
                    
                    # 測試代幣地址
                    for token_address in chain_config['token_addresses']:
                        try:
                            # 檢查地址格式
                            checksum_address = Web3.to_checksum_address(token_address)
                            print(f"  ✓ 代幣地址 {token_address} 格式正確")
                        except Exception as e:
                            print(f"  ✗ 代幣地址 {token_address} 格式錯誤: {e}")
                    
                else:
                    print(f"✗ {chain_name} 連接失敗")
                    
            except Exception as e:
                print(f"✗ {chain_name} 連接出錯: {e}")
        
        print("\n=== 測試完成 ===")
        return True
        
    except Exception as e:
        print(f"測試失敗: {e}")
        return False

if __name__ == "__main__":
    test_web3_connections()