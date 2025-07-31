import psycopg2
from datetime import datetime
import json

def query_postgres_records():
    """查詢 PostgreSQL 中的監控記錄"""
    try:
        print("=== PostgreSQL 監控記錄查詢 ===\n")
        
        # 連接數據庫
        conn = psycopg2.connect(
            host="47.83.207.219",
            port="5432",
            database="user_pysdn_net",
            user="user_pysdn_net",
            password="password_cKcZrJ"
        )
        
        cursor = conn.cursor()
        
        # 1. 查詢發送方地址記錄
        print("📊 發送方地址記錄:")
        cursor.execute('''
            SELECT 
                chain_name,
                sender_address,
                receiver_address,
                token_address,
                transaction_hash,
                block_number,
                amount,
                created_at
            FROM sender_addresses 
            ORDER BY created_at DESC
            LIMIT 20
        ''')
        
        sender_records = cursor.fetchall()
        
        if sender_records:
            print(f"找到 {len(sender_records)} 條發送方記錄:\n")
            for i, record in enumerate(sender_records, 1):
                print(f"記錄 {i}:")
                print(f"  🔗 鏈: {record[0]}")
                print(f"  📤 發送方: {record[1]}")
                print(f"  📥 接收方: {record[2]}")
                print(f"  🪙 代幣: {record[3]}")
                print(f"  🔗 交易哈希: {record[4]}")
                print(f"  📦 區塊號: {record[5]}")
                print(f"  💰 金額: {record[6]}")
                print(f"  ⏰ 時間: {record[7]}")
                print()
        else:
            print("暫無發送方記錄\n")
        
        # 2. 查詢交易記錄
        print("📈 交易記錄統計:")
        cursor.execute('''
            SELECT COUNT(*) FROM transaction_records
        ''')
        
        transaction_count = cursor.fetchone()[0]
        print(f"總交易記錄數: {transaction_count}")
        
        # 3. 按鏈統計
        print("\n🔗 按鏈統計:")
        cursor.execute('''
            SELECT 
                chain_name,
                COUNT(*) as count
            FROM sender_addresses 
            GROUP BY chain_name
            ORDER BY count DESC
        ''')
        
        chain_stats = cursor.fetchall()
        for chain, count in chain_stats:
            print(f"  {chain}: {count} 條記錄")
        
        # 4. 按代幣統計
        print("\n🪙 按代幣統計:")
        cursor.execute('''
            SELECT 
                token_address,
                COUNT(*) as count
            FROM sender_addresses 
            GROUP BY token_address
            ORDER BY count DESC
        ''')
        
        token_stats = cursor.fetchall()
        for token, count in token_stats:
            print(f"  {token}: {count} 條記錄")
        
        # 5. 最近活動
        print("\n⏰ 最近活動:")
        cursor.execute('''
            SELECT 
                created_at,
                chain_name,
                sender_address,
                receiver_address,
                amount
            FROM sender_addresses 
            ORDER BY created_at DESC
            LIMIT 5
        ''')
        
        recent_records = cursor.fetchall()
        for record in recent_records:
            created_at, chain, sender, receiver, amount = record
            print(f"  {created_at} - {chain}: {sender} -> {receiver} ({amount})")
        
        # 6. 監控地址統計
        print("\n🎯 監控地址統計:")
        cursor.execute('''
            SELECT 
                receiver_address,
                COUNT(*) as count
            FROM sender_addresses 
            GROUP BY receiver_address
            ORDER BY count DESC
        ''')
        
        monitor_stats = cursor.fetchall()
        for address, count in monitor_stats:
            print(f"  {address}: 收到 {count} 次轉入")
        
        conn.close()
        print("\n✅ 查詢完成")
        
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")

def check_monitor_status():
    """檢查監控器狀態"""
    try:
        print("\n=== 監控器狀態檢查 ===")
        
        # 檢查配置文件
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        monitored_addresses = config.get('monitored_addresses', [])
        print(f"監控地址: {monitored_addresses}")
        
        # 檢查數據庫連接
        conn = psycopg2.connect(
            host="47.83.207.219",
            port="5432",
            database="user_pysdn_net",
            user="user_pysdn_net",
            password="password_cKcZrJ"
        )
        
        cursor = conn.cursor()
        
        # 檢查表是否存在
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('sender_addresses', 'transaction_records')
        """)
        
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        print(f"數據庫表: {table_names}")
        
        if 'sender_addresses' in table_names:
            cursor.execute("SELECT COUNT(*) FROM sender_addresses")
            count = cursor.fetchone()[0]
            print(f"發送方記錄數: {count}")
        
        if 'transaction_records' in table_names:
            cursor.execute("SELECT COUNT(*) FROM transaction_records")
            count = cursor.fetchone()[0]
            print(f"交易記錄數: {count}")
        
        conn.close()
        print("✅ 監控器狀態正常")
        
    except Exception as e:
        print(f"❌ 狀態檢查失敗: {e}")

if __name__ == "__main__":
    print("🔍 PostgreSQL 監控記錄查詢工具\n")
    
    query_postgres_records()
    check_monitor_status()
    
    print("\n📋 使用說明:")
    print("  1. 此腳本查詢 PostgreSQL 中的監控記錄")
    print("  2. 監控器正在後台運行，持續記錄新的轉入事件")
    print("  3. 所有記錄保存在 PostgreSQL 數據庫中")
    print("  4. 可以隨時運行此腳本查看最新記錄")