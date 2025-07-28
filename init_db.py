#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據庫初始化腳本
"""

from app import app, db, User, Mine, Refinery, Material
from datetime import datetime

def init_database():
    """初始化數據庫"""
    with app.app_context():
        print("開始初始化數據庫...")
        
        # 創建所有表
        db.create_all()
        
        # 創建默認礦場
        if not Mine.query.first():
            mines = [
                Mine(name="新手礦場", description="適合新手的基礎礦場", base_reward_rate=15.0, max_capacity=50, required_level=1),
                Mine(name="進階礦場", description="中等難度的礦場", base_reward_rate=25.0, max_capacity=30, required_level=5),
                Mine(name="專家礦場", description="高難度高回報礦場", base_reward_rate=40.0, max_capacity=20, required_level=10),
                Mine(name="傳說礦場", description="最高難度的傳說礦場", base_reward_rate=60.0, max_capacity=10, required_level=20)
            ]
            db.session.add_all(mines)
            db.session.commit()
            print("✅ 創建默認礦場完成")
        
        # 創建默認精煉廠
        if not Refinery.query.first():
            refineries = [
                Refinery(
                    name="基礎精煉廠", 
                    description="適合新手的基礎精煉廠", 
                    efficiency=1.0, 
                    cost_per_ore=0.0,
                    max_capacity=999999999,
                    refining_multiplier=1.0,
                    environment_multiplier=1.0,
                    correction_factor=1.0
                ),
                Refinery(
                    name="高效精煉廠", 
                    description="高效率的精煉廠", 
                    efficiency=1.5, 
                    cost_per_ore=0.0,
                    max_capacity=999999999,
                    refining_multiplier=1.2,
                    environment_multiplier=1.1,
                    correction_factor=1.05
                ),
                Refinery(
                    name="大師精煉廠", 
                    description="最高效率的精煉廠", 
                    efficiency=2.0, 
                    cost_per_ore=0.0,
                    max_capacity=999999999,
                    refining_multiplier=1.5,
                    environment_multiplier=1.3,
                    correction_factor=1.1
                )
            ]
            db.session.add_all(refineries)
            db.session.commit()
            print("✅ 創建默認精煉廠完成")
        
        # 創建默認材料
        if not Material.query.first():
            materials = [
                Material(name="鐵", description="基礎金屬材料", base_value=100.0, rarity="common"),
                Material(name="銅", description="導電性良好的金屬", base_value=150.0, rarity="common"),
                Material(name="石", description="基礎建築材料", base_value=50.0, rarity="common")
            ]
            db.session.add_all(materials)
            db.session.commit()
            print("✅ 創建默認材料完成")
        
        print("🎉 數據庫初始化完成！")

if __name__ == '__main__':
    init_database() 