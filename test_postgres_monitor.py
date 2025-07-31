import json
import psycopg2
from datetime import datetime
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_postgres_connection():
    """測試 PostgreSQL 連接"""
    try:
        print("=== PostgreSQL 連接測試 ===")
        
        # 測試連接
        conn = psycopg2.connect(
            host="47.83.207.219",
            port="5432",
            database="user_pysdn_net",
            user="user_pysdn_net",
            password="password_cKcZrJ"
        )
        
        print("✅ PostgreSQL 連接成功")
        
        # 檢查表是否存在
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('sender_addresses', 'monitored_addresses', 'transaction_records')
        """)
        
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        print(f"數據庫表: {table_names}")
        
        # 檢查 sender_addresses 表結構
        if 'sender_addresses' in table_names:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'sender_addresses'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("sender_addresses 表結構:")
            for col in columns:
                print(f"  {col[0]} ({col[1]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL 連接失敗: {e}")
        return False

def test_monitor_initialization():
    """測試監控器初始化"""
    try:
        print("\n=== 監控器初始化測試 ===")
        
        from token_monitor_postgres import TokenMonitorPostgres
        monitor = TokenMonitorPostgres('config.json')
        
        print("✅ 監控器初始化成功")
        
        # 檢查配置
        monitored_addresses = monitor.config.get('monitored_addresses', [])
        print(f"監控地址: {monitored_addresses}")
        
        # 檢查 Web3 連接
        for chain_name, w3 in monitor.web3_instances.items():
            if w3.is_connected():
                print(f"✅ {chain_name} Web3 連接正常")
            else:
                print(f"❌ {chain_name} Web3 連接失敗")
        
        # 測試記錄功能
        test_data = {
            'chain_name': 'ethereum',
            'from_address': '0x1234567890abcdef1234567890abcdef12345678',
            'to_address': '0xf7b330c1d69bc1dcc5ab66f71b1c5119b40cfd03',
            'token_address': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
            'transaction_hash': '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
            'block_number': 23022335,
            'amount': '1000000'
        }
        
        monitor.record_sender_address(**test_data)
        print("✅ 測試記錄發送方地址成功")
        
        # 查詢記錄
        cursor = monitor.db_connection.cursor()
        cursor.execute('''
            SELECT * FROM sender_addresses 
            WHERE sender_address = %s
        ''', (test_data['from_address'],))
        
        records = cursor.fetchall()
        if records:
            print(f"✅ 找到 {len(records)} 條測試記錄")
        else:
            print("❌ 未找到測試記錄")
        
        monitor.close()
        return True
        
    except Exception as e:
        print(f"❌ 監控器初始化失敗: {e}")
        return False

def query_postgres_records():
    """查詢 PostgreSQL 記錄"""
    try:
        print("\n=== PostgreSQL 記錄查詢 ===")
        
        conn = psycopg2.connect(
            host="47.83.207.219",
            port="5432",
            database="user_pysdn_net",
            user="user_pysdn_net",
            password="password_cKcZrJ"
        )
        
        cursor = conn.cursor()
        
        # 查詢發送方地址記錄
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
            LIMIT 10
        ''')
        
        records = cursor.fetchall()
        
        if records:
            print(f"📊 找到 {len(records)} 條發送方記錄:")
            for i, record in enumerate(records, 1):
                print(f"記錄 {i}:")
                print(f"  鏈: {record[0]}")
                print(f"  發送方: {record[1]}")
                print(f"  接收方: {record[2]}")
                print(f"  代幣: {record[3]}")
                print(f"  交易哈希: {record[4]}")
                print(f"  區塊號: {record[5]}")
                print(f"  金額: {record[6]}")
                print(f"  時間: {record[7]}")
        else:
            print("📊 暫無發送方記錄")
        
        # 查詢交易記錄
        cursor.execute('''
            SELECT COUNT(*) FROM transaction_records
        ''')
        
        transaction_count = cursor.fetchone()[0]
        print(f"📈 總交易記錄數: {transaction_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 查詢記錄失敗: {e}")
        return False

if __name__ == "__main__":
    print("🔧 PostgreSQL 監控器測試\n")
    
    conn_ok = test_postgres_connection()
    monitor_ok = test_monitor_initialization()
    query_ok = query_postgres_records()
    
    print("\n=== 測試結果 ===")
    if conn_ok and monitor_ok and query_ok:
        print("🎉 所有測試通過！PostgreSQL 監控器已準備就緒")
        print("\n📋 使用方法:")
        print("   1. 運行 'python token_monitor_postgres.py' 開始監控")
        print("   2. 使用此腳本查看記錄")
        print("   3. 所有記錄保存在 PostgreSQL 數據庫中")
    else:
        print("❌ 部分測試失敗，請檢查上述錯誤信息")