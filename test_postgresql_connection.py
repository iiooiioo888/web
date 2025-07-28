#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 PostgreSQL 連接
"""

import psycopg2
from psycopg2 import OperationalError

def test_postgresql_connection():
    """測試 PostgreSQL 連接"""
    # 嘗試不同的數據庫名稱
    databases_to_try = ['postgres', 'mining_service', 'user_pysdn_net']
    
    connection_params = {
        'host': '47.83.207.219',
        'port': 5432,
        'user': 'user_pysdn_net',
        'password': 'password_cKcZrJ'
    }
    
    for db_name in databases_to_try:
        print(f"\n嘗試連接到數據庫: {db_name}")
        connection_params['database'] = db_name
        
        try:
            conn = psycopg2.connect(**connection_params)
            cursor = conn.cursor()
            
            # 測試查詢
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            print(f"✅ 成功連接到數據庫: {db_name}")
            print(f"PostgreSQL 版本: {version[0]}")
            
            # 檢查當前數據庫
            cursor.execute("SELECT current_database();")
            current_db = cursor.fetchone()
            print(f"當前數據庫: {current_db[0]}")
            
            # 檢查現有數據庫
            cursor.execute("SELECT datname FROM pg_database;")
            databases = cursor.fetchall()
            print("可用的數據庫:")
            for db in databases:
                print(f"  - {db[0]}")
            
            cursor.close()
            conn.close()
            
            return db_name
            
        except OperationalError as e:
            print(f"❌ 無法連接到 {db_name}: {str(e)}")
            continue
        
        except Exception as e:
            print(f"❌ 未知錯誤: {str(e)}")
            continue
    
    print("\n❌ 無法連接到任何數據庫")
    return None

if __name__ == '__main__':
    test_postgresql_connection()