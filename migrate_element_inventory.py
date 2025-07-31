#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
元素庫存遷移腳本
修復現有用戶的元素庫存問題
"""

from app import app, db, User
import json

def migrate_element_inventory():
    """遷移元素庫存數據"""
    with app.app_context():
        # 獲取所有用戶
        users = User.query.all()
        
        for user in users:
            # 檢查元素庫存是否為None或空
            if user.element_inventory is None:
                user.element_inventory = {}
                print(f"修復用戶 {user.username} 的元素庫存")
            elif not isinstance(user.element_inventory, dict):
                user.element_inventory = {}
                print(f"修復用戶 {user.username} 的元素庫存格式")
        
        # 提交更改
        db.session.commit()
        print("元素庫存遷移完成！")

if __name__ == "__main__":
    migrate_element_inventory()