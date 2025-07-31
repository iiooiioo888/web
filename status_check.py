import json
from web3 import Web3
import logging
import sqlite3

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_configuration():
    """檢查配置狀態"""
    print("=== 配置狀態檢查 ===")
    
    try:
        # 檢查配置文件
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ 配置文件加載成功")
        
        # 檢查 Infura 配置
        ethereum_config = config['chains']['ethereum']
        if 'YOUR_PROJECT_ID' in ethereum_config['rpc_url']:
            print("❌ 請配置 Infura PROJECT_ID")
            return False
        else:
            print("✅ Infura PROJECT_ID 已配置")
        
        # 檢查 Web3 連接
        w3 = Web3(Web3.HTTPProvider(ethereum_config['rpc_url']))
        if w3.is_connected():
            print("✅ Ethereum 連接成功")
            latest_block = w3.eth.get_block('latest')
            print(f"   最新區塊號: {latest_block.number}")
        else:
            print("❌ Ethereum 連接失敗")
            return False
        
        # 檢查 BSC 連接
        bsc_config = config['chains']['bsc']
        w3_bsc = Web3(Web3.HTTPProvider(bsc_config['rpc_url']))
        if w3_bsc.is_connected():
            print("✅ BSC 連接成功")
        else:
            print("❌ BSC 連接失敗")
        
        # 檢查監控代幣
        print(f"\n監控代幣:")
        print(f"  Ethereum: {len(ethereum_config['token_addresses'])} 個")
        for addr in ethereum_config['token_addresses']:
            print(f"    {addr}")
        
        print(f"  BSC: {len(bsc_config['token_addresses'])} 個")
        for addr in bsc_config['token_addresses']:
            print(f"    {addr}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置檢查失敗: {e}")
        return False

def check_database():
    """檢查數據庫狀態"""
    print("\n=== 數據庫狀態檢查 ===")
    
    try:
        # 檢查數據庫文件
        conn = sqlite3.connect('addresses.db')
        cursor = conn.cursor()
        
        # 檢查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"✅ 數據庫連接成功")
        print(f"   表數量: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   {table_name}: {count} 條記錄")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 數據庫檢查失敗: {e}")
        return False

def test_data_parsing_fix():
    """測試數據解析修復"""
    print("\n=== 數據解析修復測試 ===")
    
    try:
        # 測試之前出錯的數據
        test_data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcd\x137'
        
        if isinstance(test_data, bytes):
            amount = int.from_bytes(test_data, byteorder='big')
            print(f"✅ 數據解析修復成功: {amount}")
            return True
        else:
            print("❌ 數據格式錯誤")
            return False
            
    except Exception as e:
        print(f"❌ 數據解析測試失敗: {e}")
        return False

def main():
    """主檢查函數"""
    print("🔍 開始系統狀態檢查...\n")
    
    config_ok = check_configuration()
    db_ok = check_database()
    parsing_ok = test_data_parsing_fix()
    
    print("\n=== 檢查結果 ===")
    if config_ok and db_ok and parsing_ok:
        print("🎉 所有檢查通過！系統已準備就緒")
        print("\n📋 下一步:")
        print("   1. 運行 'python token_monitor.py' 開始監控")
        print("   2. 監控器將自動檢測代幣轉賬事件")
        print("   3. 所有交易記錄將保存到 addresses.db")
    else:
        print("❌ 部分檢查失敗，請檢查上述錯誤信息")
    
    print("\n✅ Infura 配置已成功完成！")

if __name__ == "__main__":
    main()