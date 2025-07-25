#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掛機挖礦服務 - 主應用程序
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import schedule
import time
import threading
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mining_service.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 數據庫模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    balance = db.Column(db.Float, default=0.0)  # 原礦餘額
    
    # 關聯
    mining_sessions = db.relationship('MiningSession', backref='user', lazy=True)
    rewards = db.relationship('Reward', backref='user', lazy=True)

class Mine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    base_reward_rate = db.Column(db.Float, default=1.0)  # 基礎獎勵倍率
    max_capacity = db.Column(db.Integer, default=100)  # 最大容量
    current_players = db.Column(db.Integer, default=0)  # 當前玩家數
    is_active = db.Column(db.Boolean, default=True)
    
    # 關聯
    mining_sessions = db.relationship('MiningSession', backref='mine', lazy=True)

class MiningSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mine_id = db.Column(db.Integer, db.ForeignKey('mine.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    total_mining_time = db.Column(db.Float, default=0.0)  # 總挖礦時間（小時）

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mine_id = db.Column(db.Integer, db.ForeignKey('mine.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reward_time = db.Column(db.DateTime, default=datetime.utcnow)
    reward_type = db.Column(db.String(20), default='daily')  # daily, hourly

    mine = db.relationship('Mine', foreign_keys=[mine_id])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('用戶名已存在')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('郵箱已存在')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('註冊成功！請登錄')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('用戶名或密碼錯誤')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # 獲取用戶的挖礦會話
    active_session = MiningSession.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    
    # 獲取所有礦場
    mines = Mine.query.filter_by(is_active=True).all()
    
    # 獲取用戶的獎勵歷史
    recent_rewards = Reward.query.filter_by(user_id=current_user.id)\
        .order_by(Reward.reward_time.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         active_session=active_session,
                         mines=mines,
                         recent_rewards=recent_rewards)

@app.route('/start_mining', methods=['POST'])
@login_required
def start_mining():
    mine_id = request.form.get('mine_id')
    
    # 檢查是否已有活躍會話
    active_session = MiningSession.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    
    if active_session:
        return jsonify({'success': False, 'message': '您已在挖礦中'})
    
    # 檢查礦場容量
    mine = Mine.query.get(mine_id)
    if not mine or not mine.is_active:
        return jsonify({'success': False, 'message': '礦場不存在或已關閉'})
    
    if mine.current_players >= mine.max_capacity:
        return jsonify({'success': False, 'message': '礦場已滿'})
    
    # 創建新的挖礦會話
    session = MiningSession(
        user_id=current_user.id,
        mine_id=mine_id
    )
    
    # 更新礦場玩家數
    mine.current_players += 1
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '開始挖礦！'})

@app.route('/stop_mining', methods=['POST'])
@login_required
def stop_mining():
    active_session = MiningSession.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    if not active_session:
        return jsonify({'success': False, 'message': '沒有活躍的挖礦會話'})
    # 停止時結算獎勵
    end_time = datetime.utcnow()
    mining_duration = (end_time - active_session.start_time).total_seconds() / 3600
    base_reward_per_hour = 3600
    reward_amount = mining_duration * base_reward_per_hour * active_session.mine.base_reward_rate
    if reward_amount > 0.0001:
        reward = Reward(
            user_id=active_session.user_id,
            mine_id=active_session.mine_id,
            amount=reward_amount,
            reward_type='stop'
        )
        user = User.query.get(active_session.user_id)
        user.balance += reward_amount
        db.session.add(reward)
    # 更新會話
    active_session.end_time = end_time
    active_session.is_active = False
    active_session.total_mining_time += mining_duration
    # 更新礦場玩家數
    mine = active_session.mine
    mine.current_players = max(0, mine.current_players - 1)
    db.session.commit()
    return jsonify({
        'success': True, 
        'message': f'挖礦結束！本次挖礦時長：{mining_duration:.2f}小時，結算獎勵：{reward_amount:.2f} 原礦'
    })

@app.route('/api/mining_status')
@login_required
def mining_status():
    active_session = MiningSession.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    
    if active_session:
        duration = (datetime.utcnow() - active_session.start_time).total_seconds() / 3600
        return jsonify({
            'is_mining': True,
            'mine_name': active_session.mine.name,
            'duration': round(duration, 2)
        })
    
    return jsonify({'is_mining': False})

# 獎勵發放函數
def distribute_rewards():
    """在指定時間發放獎勵（只記錄用戶參與時的時間到發獎點）"""
    with app.app_context():
        active_sessions = MiningSession.query.filter_by(is_active=True).all()
        for session in active_sessions:
            now = datetime.utcnow()
            duration = (now - session.start_time).total_seconds() / 3600
            base_reward_per_hour = 3600  # 每小時3600個原礦（每秒1個原礦）
            reward_amount = duration * base_reward_per_hour * session.mine.base_reward_rate
            if reward_amount > 0.0001:
                reward = Reward(
                    user_id=session.user_id,
                    mine_id=session.mine_id,
                    amount=reward_amount,
                    reward_type='auto'
                )
                user = User.query.get(session.user_id)
                user.balance += reward_amount
                session.start_time = now  # 更新為當前時間
                db.session.add(reward)
                db.session.commit()
                print(f"發放獎勵給用戶 {user.username}: {reward_amount:.2f} 原礦")

def schedule_rewards():
    """設置定時獎勵發放（每1秒）"""
    while True:
        distribute_rewards()
        time.sleep(1)

# 初始化數據庫和礦場
def init_database():
    with app.app_context():
        db.create_all()
        
        # 創建默認礦場
        if not Mine.query.first():
            mines = [
                Mine(name="新手礦場", description="適合新手的基礎礦場", base_reward_rate=1.0, max_capacity=50),
                Mine(name="進階礦場", description="中等難度的礦場", base_reward_rate=1.5, max_capacity=30),
                Mine(name="專家礦場", description="高難度高回報礦場", base_reward_rate=2.0, max_capacity=20),
                Mine(name="傳說礦場", description="最高難度的傳說礦場", base_reward_rate=3.0, max_capacity=10)
            ]
            
            for mine in mines:
                db.session.add(mine)
            
            db.session.commit()
            print("數據庫和礦場初始化完成")

if __name__ == '__main__':
    init_database()
    # reward_thread = threading.Thread(target=schedule_rewards, daemon=True)
    # reward_thread.start()
    app.run(debug=True, host='0.0.0.0', port=5000) 