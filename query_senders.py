import sqlite3
import json
from datetime import datetime

def query_sender_addresses():
    """查詢已記錄的發送方地址"""
    try:
        # 連接數據庫
        conn = sqlite3.connect('addresses.db')
        cursor = conn.cursor()
        
        print("=== 發送方地址記錄查詢 ===")
        
        # 檢查 sender_addresses 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sender_addresses'")
        if not cursor.fetchone():
            print("❌ sender_addresses 表不存在")
            print("   請先運行監控器來創建表")
            return
        
        # 查詢所有發送方記錄
        cursor.execute('''
            SELECT 
                chain_name,
                sender_address,
                receiver_address,
                token_address,
                transaction_hash,
                block_number,
                amount,
                timestamp
            FROM sender_addresses 
            ORDER BY timestamp DESC
        ''')
        
        records = cursor.fetchall()
        
        if not records:
            print("📭 目前沒有發送方地址記錄")
            print("   當監控地址收到代幣時，會自動記錄發送方地址")
        else:
            print(f"📊 找到 {len(records)} 條發送方記錄:")
            print()
            
            for i, record in enumerate(records, 1):
                chain_name, sender_addr, receiver_addr, token_addr, tx_hash, block_num, amount, timestamp = record
                
                print(f"記錄 {i}:")
                print(f"  鏈: {chain_name}")
                print(f"  發送方: {sender_addr}")
                print(f"  接收方: {receiver_addr}")
                print(f"  代幣: {token_addr}")
                print(f"  交易哈希: {tx_hash}")
                print(f"  區塊號: {block_num}")
                print(f"  金額: {amount}")
                print(f"  時間: {timestamp}")
                print()
        
        # 統計信息
        cursor.execute('''
            SELECT 
                chain_name,
                COUNT(DISTINCT sender_address) as unique_senders,
                COUNT(*) as total_transactions
            FROM sender_addresses 
            GROUP BY chain_name
        ''')
        
        stats = cursor.fetchall()
        if stats:
            print("📈 統計信息:")
            for chain, unique_senders, total_tx in stats:
                print(f"  {chain}: {unique_senders} 個唯一發送方，{total_tx} 筆交易")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")

def show_monitor_config():
    """顯示監控配置"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("\n=== 監控配置 ===")
        monitored_addresses = config.get('monitored_addresses', [])
        print(f"監控地址: {monitored_addresses}")
        
        print("\n監控代幣:")
        for chain_name, chain_config in config['chains'].items():
            print(f"  {chain_name}: {len(chain_config['token_addresses'])} 個代幣")
            for token in chain_config['token_addresses']:
                print(f"    {token}")
        
    except Exception as e:
        print(f"❌ 讀取配置失敗: {e}")

if __name__ == "__main__":
    print("🔍 發送方地址查詢工具\n")
    
    show_monitor_config()
    query_sender_addresses()
    
    print("\n💡 使用說明:")
    print("   1. 運行 'python token_monitor.py' 開始監控")
    print("   2. 當監控地址收到代幣時，會自動記錄發送方地址")
    print("   3. 使用此腳本查看已記錄的發送方地址")
    print("   4. 所有記錄保存在 addresses.db 的 sender_addresses 表中")