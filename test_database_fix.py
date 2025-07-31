import sqlite3
import json
from datetime import datetime

def test_database_fix():
    """測試數據庫修復"""
    try:
        print("=== 數據庫修復測試 ===")
        
        # 重新初始化數據庫
        from token_monitor import TokenMonitor
        monitor = TokenMonitor('config.json')
        
        # 檢查表是否存在
        cursor = monitor.db_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        print(f"數據庫表: {table_names}")
        
        # 檢查 sender_addresses 表是否存在
        if 'sender_addresses' in table_names:
            print("✅ sender_addresses 表已創建")
            
            # 檢查表結構
            cursor.execute("PRAGMA table_info(sender_addresses)")
            columns = cursor.fetchall()
            print("表結構:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        else:
            print("❌ sender_addresses 表未創建")
        
        # 檢查監控配置
        monitored_addresses = monitor.config.get('monitored_addresses', [])
        print(f"\n監控地址: {monitored_addresses}")
        
        # 檢查代幣配置
        print("\n監控代幣:")
        for chain_name, chain_config in monitor.config['chains'].items():
            print(f"  {chain_name}: {len(chain_config['token_addresses'])} 個代幣")
            for token in chain_config['token_addresses']:
                print(f"    {token}")
        
        monitor.close()
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_monitor_functionality():
    """測試監控功能"""
    try:
        print("\n=== 監控功能測試 ===")
        
        from token_monitor import TokenMonitor
        monitor = TokenMonitor('config.json')
        
        # 測試記錄發送方地址功能
        test_data = {
            'chain_name': 'ethereum',
            'from_address': '0x1234567890abcdef1234567890abcdef12345678',
            'to_address': '0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03',
            'token_address': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
            'transaction_hash': '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
            'block_number': 23022335,
            'amount': '1000000'
        }
        
        # 測試記錄功能
        monitor.record_sender_address(**test_data)
        print("✅ 測試記錄發送方地址成功")
        
        # 查詢記錄
        cursor = monitor.db_connection.cursor()
        cursor.execute('''
            SELECT * FROM sender_addresses 
            WHERE sender_address = ?
        ''', (test_data['from_address'],))
        
        records = cursor.fetchall()
        if records:
            print(f"✅ 找到 {len(records)} 條測試記錄")
        else:
            print("❌ 未找到測試記錄")
        
        monitor.close()
        return True
        
    except Exception as e:
        print(f"❌ 功能測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🔧 數據庫修復和功能測試\n")
    
    db_ok = test_database_fix()
    func_ok = test_monitor_functionality()
    
    print("\n=== 測試結果 ===")
    if db_ok and func_ok:
        print("🎉 所有測試通過！數據庫修復成功")
        print("\n📋 下一步:")
        print("   1. 運行 'python token_monitor.py' 開始監控")
        print("   2. 使用 'python query_senders.py' 查看記錄")
    else:
        print("❌ 部分測試失敗，請檢查上述錯誤信息")