import json
import time
from token_monitor import TokenMonitor
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_monitor():
    """測試監控器"""
    try:
        print("=== 監控器測試 ===")
        
        # 創建監控器實例
        monitor = TokenMonitor('config.json')
        
        print("✓ 監控器初始化成功")
        print(f"✓ 數據庫: {monitor.config['database']}")
        
        # 檢查 Web3 連接
        for chain_name, w3 in monitor.web3_instances.items():
            if w3.is_connected():
                print(f"✓ {chain_name} Web3 連接正常")
            else:
                print(f"✗ {chain_name} Web3 連接失敗")
        
        # 測試添加監控地址
        test_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        test_token = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        
        if monitor.add_monitored_address('ethereum', test_address, test_token):
            print(f"✓ 成功添加監控地址: {test_address}")
        else:
            print(f"✗ 添加監控地址失敗: {test_address}")
        
        # 獲取監控地址列表
        addresses = monitor.get_monitored_addresses()
        print(f"✓ 當前監控地址數量: {len(addresses)}")
        
        # 測試短時間監控（5秒）
        print("\n開始短時間監控測試（5秒）...")
        monitor.start_monitoring()
        
        print("✓ 監控器測試完成")
        return True
        
    except Exception as e:
        print(f"✗ 監控器測試失敗: {e}")
        return False

if __name__ == "__main__":
    test_monitor()