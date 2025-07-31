#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試元素庫存顯示問題
"""

from app import app, db, User, Material
import json

def debug_element_inventory():
    """調試元素庫存顯示問題"""
    with app.app_context():
        print("=== 調試元素庫存顯示問題 ===")
        
        # 檢查所有用戶
        users = User.query.all()
        print(f"總共有 {len(users)} 個用戶")
        
        for user in users:
            print(f"\n--- 用戶: {user.username} ---")
            print(f"元素庫存: {user.element_inventory}")
            print(f"元素庫存類型: {type(user.element_inventory)}")
            
            if user.element_inventory:
                print(f"元素庫存鍵值: {list(user.element_inventory.keys())}")
        
        # 檢查所有材料
        materials = Material.query.all()
        print(f"\n=== 材料數據 ===")
        print(f"總共有 {len(materials)} 種材料")
        
        for material in materials:
            print(f"符號: {material.symbol}, 名稱: {material.name}, 顏色: {material.color}")
        
        # 檢查材料數據格式
        materials_data = []
        for material in materials:
            materials_data.append({
                'id': material.id,
                'symbol': material.symbol,
                'name': material.name,
                'color': material.color,
                'rarity': material.rarity,
                'base_value': material.base_value
            })
        
        print(f"\n=== 材料JSON格式 ===")
        print(json.dumps(materials_data[:5], ensure_ascii=False, indent=2))
        
        # 測試元素庫存顯示邏輯
        print(f"\n=== 測試元素庫存顯示 ===")
        for user in users:
            if user.element_inventory:
                print(f"\n用戶 {user.username} 的元素庫存:")
                for symbol, amount in user.element_inventory.items():
                    material = Material.query.filter_by(symbol=symbol).first()
                    if material:
                        print(f"  {symbol} ({material.name}): {amount}")
                    else:
                        print(f"  {symbol}: {amount} (找不到對應材料)")

if __name__ == "__main__":
    debug_element_inventory()