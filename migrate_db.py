#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據庫遷移腳本 - 更新現有數據庫結構
"""

from app import app, db, User, Mine, MiningSession, Reward, Achievement, UserAchievement
from datetime import datetime

def migrate_database():
    """執行數據庫遷移"""
    with app.app_context():
        print("開始數據庫遷移...")
        
        # 創建新表
        db.create_all()
        
        # 更新現有用戶數據
        users = User.query.all()
        for user in users:
            # 設置默認值
            if not hasattr(user, 'level') or user.level is None:
                user.level = 1
            if not hasattr(user, 'experience') or user.experience is None:
                user.experience = 0.0
            if not hasattr(user, 'total_mining_time') or user.total_mining_time is None:
                user.total_mining_time = 0.0
            if not hasattr(user, 'consecutive_mining_days') or user.consecutive_mining_days is None:
                user.consecutive_mining_days = 0
        
        # 更新現有礦場數據
        mines = Mine.query.all()
        for mine in mines:
            if not hasattr(mine, 'required_level') or mine.required_level is None:
                mine.required_level = 1
            if not hasattr(mine, 'special_event_chance') or mine.special_event_chance is None:
                mine.special_event_chance = 0.05
        
        # 更新現有挖礦會話數據
        sessions = MiningSession.query.all()
        for session in sessions:
            if not hasattr(session, 'bonus_multiplier') or session.bonus_multiplier is None:
                session.bonus_multiplier = 1.0
        
        # 更新現有獎勵數據
        rewards = Reward.query.all()
        for reward in rewards:
            if not hasattr(reward, 'description') or reward.description is None:
                reward.description = ''
        
        # 創建默認成就
        default_achievements = [
            {
                'name': '新手礦工',
                'description': '完成第一次挖礦',
                'requirement': '完成第一次挖礦',
                'reward_amount': 1000,
                'icon': 'fas fa-user-graduate'
            },
            {
                'name': '勤勞礦工',
                'description': '累計挖礦時間達到10小時',
                'requirement': '累計挖礦時間達到10小時',
                'reward_amount': 5000,
                'icon': 'fas fa-clock'
            },
            {
                'name': '資深礦工',
                'description': '累計挖礦時間達到100小時',
                'requirement': '累計挖礦時間達到100小時',
                'reward_amount': 50000,
                'icon': 'fas fa-crown'
            },
            {
                'name': '連續挖礦者',
                'description': '連續挖礦7天',
                'requirement': '連續挖礦7天',
                'reward_amount': 10000,
                'icon': 'fas fa-calendar-check'
            },
            {
                'name': '等級達人',
                'description': '達到10級',
                'requirement': '達到10級',
                'reward_amount': 20000,
                'icon': 'fas fa-star'
            }
        ]
        
        for achievement_data in default_achievements:
            existing = Achievement.query.filter_by(name=achievement_data['name']).first()
            if not existing:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
                print(f"創建成就：{achievement_data['name']}")
        
        # 提交所有更改
        db.session.commit()
        print("數據庫遷移完成！")

if __name__ == '__main__':
    migrate_database() 