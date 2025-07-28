#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試均等機率材料選擇
"""

import random
from app import app, db, Material

def test_equal_probability():
    """測試均等機率材料選擇"""
    with app.app_context():
        materials = Material.query.filter_by(is_active=True).all()
        print('可用材料:')
        for material in materials:
            print(f'  {material.name}: rarity = {material.rarity}')
        
        print('\n測試均等機率選擇 (100次):')
        results = {'鐵': 0, '銅': 0, '石': 0}
        
        for i in range(100):
            # 均等機率隨機選擇
            selected_material = random.choice(materials)
            results[selected_material.name] += 1
            
            if i < 10:  # 只顯示前10次結果
                print(f'測試 {i+1}: 選擇了 {selected_material.name}')
        
        print('\n最終統計:')
        for name, count in results.items():
            percentage = count / 100 * 100
            print(f'{name}: {count} 次 ({percentage:.1f}%)')
        
        # 檢查是否接近均等分布
        expected_percentage = 100 / len(materials)
        print(f'\n預期均等分布: 每個材料 {expected_percentage:.1f}%')
        
        is_equal = all(abs(count/100*100 - expected_percentage) < 15 for count in results.values())
        print(f'分布是否均等: {"✅ 是" if is_equal else "❌ 否"}')

if __name__ == '__main__':
    test_equal_probability()