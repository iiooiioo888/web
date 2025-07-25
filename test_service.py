#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掛機挖礦服務測試腳本
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_service():
    """測試服務基本功能"""
    print("=" * 50)
    print("掛機挖礦服務測試")
    print("=" * 50)
    
    # 測試1: 檢查服務是否運行
    print("\n1. 測試服務連接...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ 服務運行正常")
        else:
            print(f"❌ 服務響應異常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 無法連接到服務: {e}")
        print("請確保服務已啟動: python run.py")
        return False
    
    # 測試2: 檢查註冊頁面
    print("\n2. 測試註冊頁面...")
    try:
        response = requests.get(f"{BASE_URL}/register", timeout=5)
        if response.status_code == 200:
            print("✅ 註冊頁面正常")
        else:
            print(f"❌ 註冊頁面異常: {response.status_code}")
    except Exception as e:
        print(f"❌ 註冊頁面測試失敗: {e}")
    
    # 測試3: 檢查登錄頁面
    print("\n3. 測試登錄頁面...")
    try:
        response = requests.get(f"{BASE_URL}/login", timeout=5)
        if response.status_code == 200:
            print("✅ 登錄頁面正常")
        else:
            print(f"❌ 登錄頁面異常: {response.status_code}")
    except Exception as e:
        print(f"❌ 登錄頁面測試失敗: {e}")
    
    # 測試4: 測試用戶註冊
    print("\n4. 測試用戶註冊...")
    test_user = {
        'username': f'testuser_{int(time.time())}',
        'email': f'test{int(time.time())}@example.com',
        'password': 'testpassword123'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", data=test_user, timeout=5)
        if response.status_code == 302:  # 重定向到登錄頁面
            print("✅ 用戶註冊功能正常")
        else:
            print(f"❌ 用戶註冊異常: {response.status_code}")
    except Exception as e:
        print(f"❌ 用戶註冊測試失敗: {e}")
    
    print("\n" + "=" * 50)
    print("基本功能測試完成")
    print("=" * 50)
    print("\n下一步:")
    print("1. 打開瀏覽器訪問: http://localhost:5000")
    print("2. 註冊新用戶帳號")
    print("3. 登錄並選擇礦場開始挖礦")
    print("4. 等待獎勵發放時間查看效果")
    
    return True

def test_database():
    """測試數據庫功能"""
    print("\n" + "=" * 50)
    print("數據庫功能測試")
    print("=" * 50)
    
    try:
        from app import app, db, User, Mine
        
        with app.app_context():
            # 檢查數據庫表是否存在
            print("\n1. 檢查數據庫表...")
            tables = db.engine.table_names()
            expected_tables = ['user', 'mine', 'mining_session', 'reward']
            
            for table in expected_tables:
                if table in tables:
                    print(f"✅ 表 {table} 存在")
                else:
                    print(f"❌ 表 {table} 不存在")
            
            # 檢查礦場數據
            print("\n2. 檢查礦場數據...")
            mines = Mine.query.all()
            if mines:
                print(f"✅ 找到 {len(mines)} 個礦場:")
                for mine in mines:
                    print(f"   - {mine.name} (倍率: {mine.base_reward_rate}x, 容量: {mine.max_capacity})")
            else:
                print("❌ 沒有找到礦場數據")
            
            # 檢查用戶數據
            print("\n3. 檢查用戶數據...")
            users = User.query.all()
            print(f"✅ 找到 {len(users)} 個用戶")
            
    except Exception as e:
        print(f"❌ 數據庫測試失敗: {e}")

if __name__ == '__main__':
    print("開始測試掛機挖礦服務...")
    
    # 基本功能測試
    if test_service():
        # 數據庫功能測試
        test_database()
    
    print("\n測試完成！") 