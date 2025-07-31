#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試元素庫存功能
"""

from app import app, db, User, Material
import json

def test_element_inventory():
    """測試元素庫存功能"""
    with app.app_context():
        # 獲取所有用戶
        users = User.query.all()
        print(f"總共有 {len(users)} 個用戶")
        
        for user in users:
            print(f"\n用戶: {user.username}")
            print(f"元素庫存: {user.element_inventory}")
            
            # 檢查元素庫存格式
            if user.element_inventory is None:
                print("❌ 元素庫存為None")
            elif not isinstance(user.element_inventory, dict):
                print(f"❌ 元素庫存格式錯誤: {type(user.element_inventory)}")
            else:
                print(f"✅ 元素庫存格式正確，有 {len(user.element_inventory)} 種元素")
        
        # 獲取所有材料
        materials = Material.query.all()
        print(f"\n總共有 {len(materials)} 種材料")
        
        for material in materials:
            print(f"材料: {material.symbol} ({material.name}) - {material.rarity} - {material.color}")

if __name__ == "__main__":
    test_element_inventory()