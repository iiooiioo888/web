#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復元素庫存數據格式
將中文名稱轉換為元素符號
"""

from app import app, db, User, Material
import json

def fix_element_inventory():
    """修復元素庫存數據格式"""
    with app.app_context():
        # 獲取所有用戶
        users = User.query.all()
        
        for user in users:
            if user.element_inventory and isinstance(user.element_inventory, dict):
                print(f"修復用戶 {user.username} 的元素庫存")
                
                # 創建新的庫存字典
                new_inventory = {}
                
                # 獲取所有材料
                materials = Material.query.all()
                material_map = {}
                for material in materials:
                    material_map[material.name] = material.symbol
                
                # 轉換舊的庫存格式
                for element_name, amount in user.element_inventory.items():
                    if element_name in material_map:
                        element_symbol = material_map[element_name]
                        new_inventory[element_symbol] = amount
                        print(f"  轉換: {element_name} -> {element_symbol}")
                    else:
                        print(f"  警告: 找不到材料 {element_name}")
                
                # 更新用戶的元素庫存
                user.element_inventory = new_inventory
        
        # 提交更改
        db.session.commit()
        print("元素庫存格式修復完成！")

if __name__ == "__main__":
    fix_element_inventory()