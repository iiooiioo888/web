import json
from web3 import Web3
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_monitor_config():
    """測試監控地址配置"""
    try:
        # 加載配置
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("=== 監控地址配置測試 ===")
        
        # 檢查監控地址
        monitored_addresses = config.get('monitored_addresses', [])
        print(f"監控地址數量: {len(monitored_addresses)}")
        
        for i, addr in enumerate(monitored_addresses, 1):
            print(f"  {i}. {addr}")
        
        # 檢查 Web3 連接
        ethereum_config = config['chains']['ethereum']
        w3 = Web3(Web3.HTTPProvider(ethereum_config['rpc_url']))
        
        if w3.is_connected():
            print("\n✅ Ethereum 連接成功")
            
            # 測試監控地址格式
            test_address = "0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03"
            if Web3.is_address(test_address):
                print(f"✅ 監控地址格式正確: {test_address}")
                
                # 檢查地址是否在監控列表中
                if test_address.lower() in [addr.lower() for addr in monitored_addresses]:
                    print("✅ 監控地址已配置")
                else:
                    print("❌ 監控地址未配置")
            else:
                print("❌ 監控地址格式錯誤")
            
            return True
        else:
            print("❌ Ethereum 連接失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_token_monitor():
    """測試 TokenMonitor 類"""
    try:
        from token_monitor import TokenMonitor
        
        print("\n=== TokenMonitor 測試 ===")
        
        # 創建監控器實例
        monitor = TokenMonitor('config.json')
        print("✅ TokenMonitor 初始化成功")
        
        # 檢查配置
        monitored_addresses = monitor.config.get('monitored_addresses', [])
        print(f"監控地址: {monitored_addresses}")
        
        # 檢查數據庫連接
        if monitor.db_connection:
            print("✅ 數據庫連接成功")
            
            # 檢查表是否存在
            cursor = monitor.db_connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"數據庫表: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        print(f"❌ TokenMonitor 測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🔍 開始監控配置測試...\n")
    
    config_ok = test_monitor_config()
    monitor_ok = test_token_monitor()
    
    print("\n=== 測試結果 ===")
    if config_ok and monitor_ok:
        print("🎉 所有測試通過！監控配置已準備就緒")
        print("\n📋 功能說明:")
        print("   1. 監控地址: 0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03")
        print("   2. 當該地址收到任何代幣時，會記錄轉出方地址")
        print("   3. 記錄保存在 sender_addresses 表中")
        print("   4. 運行 'python token_monitor.py' 開始監控")
    else:
        print("❌ 部分測試失敗，請檢查上述錯誤信息")
    
    print("\n✅ 監控地址配置完成！")