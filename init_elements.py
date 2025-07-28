#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
元素週期表初始化腳本
"""
from app import app, db, User, Mine, Refinery, Material
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_elements_database():
    """初始化元素週期表數據庫"""
    with app.app_context():
        print("開始初始化元素週期表數據庫...")
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
                Refinery(name="基礎精煉廠", description="適合新手的基礎精煉廠", efficiency=1.0, cost_per_ore=0.0, max_capacity=999999999, refining_multiplier=1.0, environment_multiplier=1.0, correction_factor=1.0),
                Refinery(name="高效精煉廠", description="高效率的精煉廠", efficiency=1.5, cost_per_ore=0.0, max_capacity=999999999, refining_multiplier=1.2, environment_multiplier=1.1, correction_factor=1.05),
                Refinery(name="大師精煉廠", description="最高效率的精煉廠", efficiency=2.0, cost_per_ore=0.0, max_capacity=999999999, refining_multiplier=1.5, environment_multiplier=1.3, correction_factor=1.1)
            ]
            db.session.add_all(refineries)
            db.session.commit()
            print("✅ 創建默認精煉廠完成")
        
        # 創建元素週期表
        if not Material.query.first():
            elements = [
                # 常見元素
                Material(symbol="H", name="氫", description="最輕的元素", base_value=10.0, rarity="common", color="#e74c3c"),
                Material(symbol="He", name="氦", description="惰性氣體", base_value=15.0, rarity="common", color="#3498db"),
                Material(symbol="Li", name="鋰", description="鹼金屬", base_value=20.0, rarity="common", color="#f39c12"),
                Material(symbol="Be", name="鈹", description="鹼土金屬", base_value=25.0, rarity="common", color="#2ecc71"),
                Material(symbol="B", name="硼", description="類金屬", base_value=30.0, rarity="common", color="#9b59b6"),
                Material(symbol="C", name="碳", description="生命基礎", base_value=35.0, rarity="common", color="#34495e"),
                Material(symbol="N", name="氮", description="空氣主要成分", base_value=40.0, rarity="common", color="#1abc9c"),
                Material(symbol="O", name="氧", description="生命必需", base_value=45.0, rarity="common", color="#e67e22"),
                Material(symbol="F", name="氟", description="最活潑元素", base_value=50.0, rarity="common", color="#d35400"),
                Material(symbol="Ne", name="氖", description="惰性氣體", base_value=55.0, rarity="common", color="#8e44ad"),
                Material(symbol="Na", name="鈉", description="鹼金屬", base_value=60.0, rarity="common", color="#f1c40f"),
                Material(symbol="Mg", name="鎂", description="鹼土金屬", base_value=65.0, rarity="common", color="#27ae60"),
                Material(symbol="Al", name="鋁", description="輕金屬", base_value=70.0, rarity="common", color="#7f8c8d"),
                Material(symbol="Si", name="矽", description="半導體材料", base_value=75.0, rarity="common", color="#bdc3c7"),
                Material(symbol="P", name="磷", description="生命元素", base_value=80.0, rarity="common", color="#c0392b"),
                Material(symbol="S", name="硫", description="黃色固體", base_value=85.0, rarity="common", color="#f39c12"),
                Material(symbol="Cl", name="氯", description="鹵素", base_value=90.0, rarity="common", color="#16a085"),
                Material(symbol="Ar", name="氬", description="惰性氣體", base_value=95.0, rarity="common", color="#3498db"),
                
                # 稀有元素
                Material(symbol="K", name="鉀", description="鹼金屬", base_value=150.0, rarity="rare", color="#e67e22"),
                Material(symbol="Ca", name="鈣", description="鹼土金屬", base_value=160.0, rarity="rare", color="#9b59b6"),
                Material(symbol="Sc", name="鈧", description="稀土元素", base_value=170.0, rarity="rare", color="#34495e"),
                Material(symbol="Ti", name="鈦", description="輕質金屬", base_value=180.0, rarity="rare", color="#2c3e50"),
                Material(symbol="V", name="釩", description="過渡金屬", base_value=190.0, rarity="rare", color="#8e44ad"),
                Material(symbol="Cr", name="鉻", description="過渡金屬", base_value=200.0, rarity="rare", color="#e74c3c"),
                Material(symbol="Mn", name="錳", description="過渡金屬", base_value=210.0, rarity="rare", color="#f39c12"),
                Material(symbol="Fe", name="鐵", description="過渡金屬", base_value=220.0, rarity="rare", color="#7f8c8d"),
                Material(symbol="Co", name="鈷", description="過渡金屬", base_value=230.0, rarity="rare", color="#3498db"),
                Material(symbol="Ni", name="鎳", description="過渡金屬", base_value=240.0, rarity="rare", color="#27ae60"),
                Material(symbol="Cu", name="銅", description="過渡金屬", base_value=250.0, rarity="rare", color="#d35400"),
                Material(symbol="Zn", name="鋅", description="過渡金屬", base_value=260.0, rarity="rare", color="#1abc9c"),
                Material(symbol="Ga", name="鎵", description="後過渡金屬", base_value=270.0, rarity="rare", color="#c0392b"),
                Material(symbol="Ge", name="鍺", description="類金屬", base_value=280.0, rarity="rare", color="#f1c40f"),
                Material(symbol="As", name="砷", description="類金屬", base_value=290.0, rarity="rare", color="#2ecc71"),
                Material(symbol="Se", name="硒", description="非金屬", base_value=300.0, rarity="rare", color="#95a5a6"),
                Material(symbol="Br", name="溴", description="鹵素", base_value=310.0, rarity="rare", color="#e74c3c"),
                Material(symbol="Kr", name="氪", description="惰性氣體", base_value=320.0, rarity="rare", color="#3498db"),
                Material(symbol="Ag", name="銀", description="貴金屬", base_value=330.0, rarity="rare", color="#bdc3c7"),
                Material(symbol="Cd", name="鎘", description="過渡金屬", base_value=340.0, rarity="rare", color="#8e44ad"),
                Material(symbol="In", name="銦", description="後過渡金屬", base_value=350.0, rarity="rare", color="#f39c12"),
                Material(symbol="Sn", name="錫", description="後過渡金屬", base_value=360.0, rarity="rare", color="#7f8c8d"),
                Material(symbol="Sb", name="銻", description="類金屬", base_value=370.0, rarity="rare", color="#34495e"),
                Material(symbol="Te", name="碲", description="類金屬", base_value=380.0, rarity="rare", color="#16a085"),
                Material(symbol="I", name="碘", description="鹵素", base_value=390.0, rarity="rare", color="#c0392b"),
                Material(symbol="Xe", name="氙", description="惰性氣體", base_value=400.0, rarity="rare", color="#3498db"),
                Material(symbol="Cs", name="銫", description="鹼金屬", base_value=410.0, rarity="rare", color="#f1c40f"),
                Material(symbol="Ba", name="鋇", description="鹼土金屬", base_value=420.0, rarity="rare", color="#27ae60"),
                Material(symbol="Au", name="金", description="貴金屬", base_value=430.0, rarity="rare", color="#f1c40f"),
                Material(symbol="Hg", name="汞", description="液態金屬", base_value=440.0, rarity="rare", color="#bdc3c7"),
                Material(symbol="Tl", name="鉈", description="後過渡金屬", base_value=450.0, rarity="rare", color="#7f8c8d"),
                Material(symbol="Pb", name="鉛", description="後過渡金屬", base_value=460.0, rarity="rare", color="#34495e"),
                Material(symbol="Bi", name="鉍", description="後過渡金屬", base_value=470.0, rarity="rare", color="#8e44ad"),
                Material(symbol="Po", name="釙", description="放射性元素", base_value=480.0, rarity="rare", color="#e74c3c"),
                Material(symbol="At", name="砈", description="放射性元素", base_value=490.0, rarity="rare", color="#d35400"),
                Material(symbol="Rn", name="氡", description="放射性氣體", base_value=500.0, rarity="rare", color="#3498db"),
                
                # 極稀有元素
                Material(symbol="Fr", name="鈁", description="放射性鹼金屬", base_value=1000.0, rarity="very-rare", color="#e74c3c"),
                Material(symbol="Ra", name="鐳", description="放射性鹼土金屬", base_value=1100.0, rarity="very-rare", color="#f39c12"),
                Material(symbol="Ac", name="錒", description="放射性元素", base_value=1200.0, rarity="very-rare", color="#8e44ad"),
                Material(symbol="Th", name="釷", description="放射性元素", base_value=1300.0, rarity="very-rare", color="#34495e"),
                Material(symbol="Pa", name="鏷", description="放射性元素", base_value=1400.0, rarity="very-rare", color="#2c3e50"),
                Material(symbol="U", name="鈾", description="放射性元素", base_value=1500.0, rarity="very-rare", color="#7f8c8d"),
                Material(symbol="Np", name="錼", description="放射性元素", base_value=1600.0, rarity="very-rare", color="#1abc9c"),
                Material(symbol="Pu", name="鈈", description="放射性元素", base_value=1700.0, rarity="very-rare", color="#c0392b"),
                Material(symbol="Am", name="鋂", description="放射性元素", base_value=1800.0, rarity="very-rare", color="#f39c12"),
                Material(symbol="Cm", name="鋦", description="放射性元素", base_value=1900.0, rarity="very-rare", color="#9b59b6")
            ]
            db.session.add_all(elements)
            db.session.commit()
            print("✅ 創建元素週期表完成")
        
        # 創建測試用戶
        if not User.query.filter_by(username='admin').first():
            test_user = User(
                username='admin', 
                email='admin@example.com', 
                password_hash=generate_password_hash('password'), 
                balance=100000.0,
                element_inventory={}
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ 創建測試用戶 'admin' 完成")
        
        print("🎉 元素週期表數據庫初始化完成！")

if __name__ == '__main__':
    init_elements_database() 