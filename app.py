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
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user_pysdn_net:password_cKcZrJ@47.83.207.219:5432/user_pysdn_net'
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
    level = db.Column(db.Integer, default=1)  # 用戶等級
    experience = db.Column(db.Float, default=0.0)  # 經驗值
    total_mining_time = db.Column(db.Float, default=0.0)  # 總挖礦時間
    consecutive_mining_days = db.Column(db.Integer, default=0)  # 連續挖礦天數
    last_mining_date = db.Column(db.Date)  # 最後挖礦日期
    
    # 元素庫存 - 使用JSON字段存儲所有元素
    element_inventory = db.Column(db.JSON, default=dict)  # 元素庫存
    
    # 關聯
    mining_sessions = db.relationship('MiningSession', backref='user', lazy=True)
    rewards = db.relationship('Reward', backref='user', lazy=True)
    refining_records = db.relationship('RefiningRecord', backref='user', lazy=True)

class Mine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    base_reward_rate = db.Column(db.Float, default=1.0)  # 基礎獎勵倍率
    max_capacity = db.Column(db.Integer, default=100)  # 最大容量
    current_players = db.Column(db.Integer, default=0)  # 當前玩家數
    is_active = db.Column(db.Boolean, default=True)
    required_level = db.Column(db.Integer, default=1)  # 所需等級
    special_event_chance = db.Column(db.Float, default=0.05)  # 特殊事件機率
    
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
    bonus_multiplier = db.Column(db.Float, default=1.0)  # 獎勵倍數

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mine_id = db.Column(db.Integer, db.ForeignKey('mine.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reward_time = db.Column(db.DateTime, default=datetime.utcnow)
    reward_type = db.Column(db.String(20), default='daily')  # daily, hourly, bonus, level_up
    description = db.Column(db.String(200))  # 獎勵描述

    mine = db.relationship('Mine', foreign_keys=[mine_id])

# 原礦精煉相關模型
class Refinery(db.Model):
    """精煉廠模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)  # 精煉廠開關
    efficiency = db.Column(db.Float, default=1.0)  # 精煉效率
    cost_per_ore = db.Column(db.Float, default=100.0)  # 每單位原礦精煉成本
    max_capacity = db.Column(db.Integer, default=1000)  # 最大容量
    current_usage = db.Column(db.Integer, default=0)  # 當前使用量
    
    # 新增參數
    refining_multiplier = db.Column(db.Float, default=1.0)  # 精煉倍數
    environment_multiplier = db.Column(db.Float, default=1.0)  # 環境倍數
    correction_factor = db.Column(db.Float, default=1.0)  # 修正系數

class Material(db.Model):
    """元素材料模型"""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)  # 元素符號
    name = db.Column(db.String(50), nullable=False)  # 元素中文名
    description = db.Column(db.Text)
    base_value = db.Column(db.Float, default=0.0)  # 基礎價值
    rarity = db.Column(db.String(20), default='common')  # 稀有度: common, rare, very-rare
    color = db.Column(db.String(7), default='#000000')  # 元素顏色
    is_active = db.Column(db.Boolean, default=True)  # 是否可精煉

class RefiningRecord(db.Model):
    """精煉記錄"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    refinery_id = db.Column(db.Integer, db.ForeignKey('refinery.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    ore_amount = db.Column(db.Float, nullable=False)  # 消耗原礦數量
    material_amount = db.Column(db.Float, nullable=False)  # 獲得材料數量
    refining_time = db.Column(db.DateTime, default=datetime.utcnow)
    cost = db.Column(db.Float, nullable=False)  # 精煉成本
    
    refinery = db.relationship('Refinery', foreign_keys=[refinery_id])
    material = db.relationship('Material', foreign_keys=[material_id])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 獎勵計算函數
def calculate_reward(user, mine, duration, bonus_multiplier=1.0):
    """計算獎勵金額"""
    # 基礎獎勵
    base_reward_per_hour = 5000  # 提高基礎獎勵
    
    # 等級加成 (每級增加10%)
    level_bonus = 1.0 + (user.level - 1) * 0.1
    
    # 連續挖礦加成 (每天增加5%)
    consecutive_bonus = 1.0 + user.consecutive_mining_days * 0.05
    
    # 特殊事件加成
    special_event_bonus = 1.0
    if random.random() < mine.special_event_chance:
        special_event_bonus = random.uniform(1.5, 3.0)
    
    # 計算總獎勵
    total_reward = (duration * base_reward_per_hour * mine.base_reward_rate * 
                   level_bonus * consecutive_bonus * special_event_bonus * bonus_multiplier)
    
    return total_reward, special_event_bonus > 1.0

def check_level_up(user):
    """檢查並處理等級提升"""
    required_exp = user.level * 1000  # 每級需要1000經驗
    if user.experience >= required_exp:
        user.level += 1
        user.experience -= required_exp
        
        # 等級提升獎勵
        level_up_reward = user.level * 1000
        user.balance += level_up_reward
        
        reward = Reward(
            user_id=user.id,
            mine_id=1,  # 默認礦場
            amount=level_up_reward,
            reward_type='level_up',
            description=f'等級提升到 {user.level} 級！'
        )
        db.session.add(reward)
        
        return True, level_up_reward
    return False, 0

def update_consecutive_mining(user):
    """更新連續挖礦天數"""
    today = datetime.utcnow().date()
    
    if user.last_mining_date:
        if today - user.last_mining_date == timedelta(days=1):
            user.consecutive_mining_days += 1
        elif today - user.last_mining_date > timedelta(days=1):
            user.consecutive_mining_days = 1
    else:
        user.consecutive_mining_days = 1
    
    user.last_mining_date = today

# 精煉相關函數
def calculate_refining_result(ore_amount, refinery, material):
    """計算精煉結果"""
    # 基礎精煉比例
    base_ratio = 0.1  # 10個原礦 = 1個材料
    
    # 精煉廠效率影響
    efficiency_ratio = base_ratio * refinery.efficiency
    
    # 新增參數影響
    # 精煉倍數：直接影響材料產出
    refining_ratio = efficiency_ratio * refinery.refining_multiplier
    
    # 環境倍數：模擬環境因素對精煉的影響
    environment_ratio = refining_ratio * refinery.environment_multiplier
    
    # 修正系數：最終調整因子
    final_ratio = environment_ratio * refinery.correction_factor
    
    # 計算獲得材料數量
    material_amount = ore_amount * final_ratio
    
    # 計算成本（成本不受新參數影響）
    cost = ore_amount * refinery.cost_per_ore
    
    return material_amount, cost

def get_refining_materials():
    """獲取可精煉的材料列表"""
    return Material.query.filter_by(is_active=True).all()

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
        
        # 檢查用戶是否已存在
        if User.query.filter_by(username=username).first():
            flash('用戶名已存在')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('郵箱已被註冊')
            return redirect(url_for('register'))
        
        # 創建新用戶
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
    
    # 獲取可用礦場
    mines = Mine.query.filter_by(is_active=True).all()
    
    # 獲取用戶的獎勵記錄
    recent_rewards = Reward.query.filter_by(user_id=current_user.id).order_by(
        Reward.reward_time.desc()
    ).limit(10).all()
    
    # 獲取精煉廠信息
    refineries = Refinery.query.filter_by(is_active=True).all()
    materials = get_refining_materials()
    
    return render_template('dashboard.html', 
                          active_session=active_session,
                          mines=mines,
                          recent_rewards=recent_rewards,
                          refineries=refineries,
                          materials=materials)

@app.route('/start_mining', methods=['POST'])
@login_required
def start_mining():
    mine_id = request.form.get('mine_id', type=int)
    
    if not mine_id:
        flash('請選擇礦場')
        return redirect(url_for('dashboard'))
    
    mine = Mine.query.get(mine_id)
    if not mine:
        flash('礦場不存在')
        return redirect(url_for('dashboard'))
    
    # 檢查等級要求
    if current_user.level < mine.required_level:
        flash(f'需要等級 {mine.required_level} 才能進入此礦場')
        return redirect(url_for('dashboard'))
    
    # 檢查是否已在挖礦
    existing_session = MiningSession.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    
    if existing_session:
        flash('您已在挖礦中')
        return redirect(url_for('dashboard'))
    
    # 檢查礦場容量
    if mine.current_players >= mine.max_capacity:
        flash('礦場已滿')
        return redirect(url_for('dashboard'))
    
    # 創建新的挖礦會話
    session = MiningSession(
        user_id=current_user.id,
        mine_id=mine_id
    )
    db.session.add(session)
    
    # 更新礦場玩家數
    mine.current_players += 1
    
    db.session.commit()
    
    flash('開始挖礦！')
    return redirect(url_for('dashboard'))

@app.route('/stop_mining', methods=['POST'])
@login_required
def stop_mining():
    # 獲取當前挖礦會話
    session = MiningSession.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    
    if not session:
        return jsonify({'success': False, 'message': '您沒有在挖礦'})
    
    try:
        # 計算挖礦時間
        end_time = datetime.utcnow()
        duration = (end_time - session.start_time).total_seconds() / 3600  # 轉換為小時
        
        # 更新會話
        session.end_time = end_time
        session.is_active = False
        session.total_mining_time = duration
        
        # 更新礦場玩家數
        mine = Mine.query.get(session.mine_id)
        mine.current_players -= 1
        
        # 計算獎勵
        reward_amount, special_event = calculate_reward(current_user, mine, duration)
        current_user.balance += reward_amount
        
        # 更新用戶統計
        current_user.total_mining_time += duration
        current_user.experience += duration * 100  # 每小時100經驗
        update_consecutive_mining(current_user)
        
        # 檢查等級提升
        level_up, level_reward = check_level_up(current_user)
        
        # 創建獎勵記錄
        reward = Reward(
            user_id=current_user.id,
            mine_id=session.mine_id,
            amount=reward_amount,
            reward_type='hourly',
            description=f'挖礦獎勵 - {mine.name} ({duration:.2f}小時)'
        )
        db.session.add(reward)
        
        db.session.commit()
        
        # 準備返回消息
        message = f'挖礦結束！獲得 {reward_amount:.0f} 原礦'
        if special_event:
            message += ' (特殊事件！)'
        if level_up:
            message += f' 等級提升到 {current_user.level} 級！'
        
        return jsonify({
            'success': True, 
            'message': message,
            'reward_amount': reward_amount,
            'duration': round(duration, 2)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'停止挖礦失敗：{str(e)}'})

@app.route('/api/mining_status')
@login_required
def mining_status():
    """API: 獲取挖礦狀態"""
    session = MiningSession.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    
    if session:
        duration = (datetime.utcnow() - session.start_time).total_seconds() / 3600
        return jsonify({
            'is_mining': True,
            'mine_name': session.mine.name,
            'duration': round(duration, 2)
        })
    else:
        return jsonify({'is_mining': False})

# 精煉相關路由
@app.route('/refinery')
@login_required
def refinery():
    """精煉廠頁面"""
    refineries = Refinery.query.filter_by(is_active=True).all()
    materials = get_refining_materials()
    
    # 獲取用戶的精煉記錄
    recent_refining = RefiningRecord.query.filter_by(user_id=current_user.id).order_by(
        RefiningRecord.refining_time.desc()
    ).limit(10).all()
    
    return render_template('refinery.html',
                          refineries=refineries,
                          materials=materials,
                          recent_refining=recent_refining)

@app.route('/refine', methods=['POST'])
@login_required
def refine():
    """執行精煉"""
    refinery_id = request.form.get('refinery_id', type=int)
    ore_amount = request.form.get('ore_amount', type=float)
    
    if not all([refinery_id, ore_amount]):
        flash('請填寫完整的精煉信息')
        return redirect(url_for('refinery'))
    
    # 檢查精煉廠
    refinery = Refinery.query.get(refinery_id)
    if not refinery or not refinery.is_active:
        flash('精煉廠不可用')
        return redirect(url_for('refinery'))
    
    # 檢查原礦餘額
    if current_user.balance < ore_amount:
        flash('原礦餘額不足')
        return redirect(url_for('refinery'))
    
    # 隨機選擇產出元素
    available_materials = Material.query.filter_by(is_active=True).all()
    if not available_materials:
        flash('沒有可用的元素')
        return redirect(url_for('refinery'))
    
    # 基於稀有度的加權隨機選擇
    materials_by_rarity = {
        'common': [],
        'rare': [],
        'very-rare': []
    }
    
    for material in available_materials:
        materials_by_rarity[material.rarity].append(material)
    
    # 設定稀有度權重
    rarity_weights = {
        'common': 0.7,      # 70% 機率獲得常見元素
        'rare': 0.25,       # 25% 機率獲得稀有元素
        'very-rare': 0.05   # 5% 機率獲得極稀有元素
    }
    
    # 根據權重選擇稀有度
    selected_rarity = random.choices(
        list(rarity_weights.keys()),
        weights=list(rarity_weights.values())
    )[0]
    
    # 從選中的稀有度中隨機選擇元素
    if materials_by_rarity[selected_rarity]:
        selected_material = random.choice(materials_by_rarity[selected_rarity])
    else:
        # 如果該稀有度沒有元素，從常見元素中選擇
        selected_material = random.choice(materials_by_rarity['common'])
    
    # 計算精煉結果
    material_amount, cost = calculate_refining_result(ore_amount, refinery, selected_material)
    
    # 檢查精煉廠容量
    if refinery.current_usage + ore_amount > refinery.max_capacity:
        flash('精煉廠容量不足')
        return redirect(url_for('refinery'))
    
    # 執行精煉
    current_user.balance -= ore_amount
    current_user.balance -= cost
    
    # 根據元素類型增加庫存
    element_name = selected_material.name
    if element_name not in current_user.element_inventory:
        current_user.element_inventory[element_name] = 0.0
    current_user.element_inventory[element_name] += material_amount
    
    # 更新精煉廠使用量
    refinery.current_usage += ore_amount
    
    # 創建精煉記錄
    record = RefiningRecord(
        user_id=current_user.id,
        refinery_id=refinery_id,
        material_id=selected_material.id,
        ore_amount=ore_amount,
        material_amount=material_amount,
        cost=cost
    )
    db.session.add(record)
    
    db.session.commit()
    
    flash(f'精煉成功！消耗 {ore_amount:.0f} 原礦，獲得 {material_amount:.2f} {selected_material.name}')
    return redirect(url_for('refinery'))

# 定時任務
def distribute_rewards():
    """分發獎勵（每小時執行）"""
    with app.app_context():
        active_sessions = MiningSession.query.filter_by(is_active=True).all()
        
        for session in active_sessions:
            # 計算挖礦時間
            duration = (datetime.utcnow() - session.start_time).total_seconds() / 3600
            
            user = User.query.get(session.user_id)
            mine = Mine.query.get(session.mine_id)
            reward_amount, _ = calculate_reward(user, mine, 1.0)  # 1小時獎勵
            
            # 更新用戶餘額
            user.balance += reward_amount
            user.experience += 100  # 每小時100經驗
            user.total_mining_time += 1.0
            
            # 檢查等級提升
            check_level_up(user)
            
            # 創建獎勵記錄
            reward = Reward(
                user_id=user.id,
                mine_id=session.mine_id,
                amount=reward_amount,
                reward_type='hourly',
                description=f'定時獎勵 - {mine.name}'
            )
            db.session.add(reward)
        
        db.session.commit()

def schedule_rewards():
    """調度獎勵分發"""
    schedule.every().hour.do(distribute_rewards)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def init_database():
    """初始化數據庫"""
    with app.app_context():
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
        
        # 創建默認精煉廠
        if not Refinery.query.first():
            refineries = [
                Refinery(name="基礎精煉廠", description="適合新手的基礎精煉廠", efficiency=1.0, cost_per_ore=50.0),
                Refinery(name="高效精煉廠", description="高效率的精煉廠", efficiency=1.5, cost_per_ore=100.0),
                Refinery(name="大師精煉廠", description="最高效率的精煉廠", efficiency=2.0, cost_per_ore=200.0)
            ]
            db.session.add_all(refineries)
            db.session.commit()
        
        # 創建默認材料
        if not Material.query.first():
            materials = [
                Material(name="鐵", description="基礎金屬材料", base_value=100.0, rarity="common"),
                Material(name="銅", description="導電性良好的金屬", base_value=150.0, rarity="common"),
                Material(name="石", description="基礎建築材料", base_value=50.0, rarity="common")
            ]
            db.session.add_all(materials)
            db.session.commit()

if __name__ == '__main__':
    init_database()
    
    # 啟動定時任務
    reward_thread = threading.Thread(target=schedule_rewards, daemon=True)
    reward_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 