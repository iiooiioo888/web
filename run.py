#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掛機挖礦服務啟動腳本
"""

import os
import sys
from app import app, init_database

def main():
    """主函數"""
    print("=" * 50)
    print("掛機挖礦服務啟動中...")
    print("=" * 50)
    
    # 初始化數據庫
    print("正在初始化數據庫...")
    init_database()
    print("數據庫初始化完成！")
    
    # 顯示服務信息
    print("\n服務信息：")
    print("- 服務地址：http://localhost:5000")
    print("- 獎勵時間：每天 08:00, 16:00, 24:00")
    print("- 數據庫：SQLite (mining_service.db)")
    print("\n按 Ctrl+C 停止服務")
    print("=" * 50)
    
    # 啟動服務
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n服務已停止")
        sys.exit(0)

if __name__ == '__main__':
    main() 