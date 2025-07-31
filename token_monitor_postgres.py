import json
import time
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import threading

# 配置日誌 - 移除 emoji 字符以避免編碼問題
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_postgres.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class TokenMonitorPostgres:
    def __init__(self, config_file):
        """初始化監控器"""
        self.config = self.load_config(config_file)
        self.web3_instances = {}
        self.db_connection = None
        self.init_database()
        self.init_web3_connections()
        
    def load_config(self, config_file):
        """加載配置文件"""
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def init_database(self):
        """初始化 PostgreSQL 數據庫"""
        try:
            # 使用與 app.py 相同的數據庫連接
            self.db_connection = psycopg2.connect(
                host="47.83.207.219",
                port="5432",
                database="user_pysdn_net",
                user="user_pysdn_net",
                password="password_cKcZrJ"
            )
            
            # 創建監控相關的表
            cursor = self.db_connection.cursor()
            
            # 創建發送方地址記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sender_addresses (
                    id SERIAL PRIMARY KEY,
                    chain_name VARCHAR(50) NOT NULL,
                    sender_address VARCHAR(42) NOT NULL,
                    receiver_address VARCHAR(42) NOT NULL,
                    token_address VARCHAR(42) NOT NULL,
                    transaction_hash VARCHAR(66) NOT NULL UNIQUE,
                    block_number BIGINT NOT NULL,
                    amount TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 創建監控地址表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitored_addresses (
                    id SERIAL PRIMARY KEY,
                    chain_name VARCHAR(50) NOT NULL,
                    address VARCHAR(42) NOT NULL,
                    token_address VARCHAR(42) NOT NULL,
                    transaction_hash VARCHAR(66),
                    block_number BIGINT,
                    amount TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(chain_name, address, token_address)
                )
            ''')
            
            # 創建交易記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transaction_records (
                    id SERIAL PRIMARY KEY,
                    chain_name VARCHAR(50) NOT NULL,
                    transaction_hash VARCHAR(66) NOT NULL UNIQUE,
                    block_number BIGINT NOT NULL,
                    from_address VARCHAR(42) NOT NULL,
                    to_address VARCHAR(42) NOT NULL,
                    token_address VARCHAR(42) NOT NULL,
                    amount TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.db_connection.commit()
            logging.info("PostgreSQL 數據庫初始化成功")
            
        except Exception as e:
            logging.error(f"數據庫初始化失敗: {e}")
            raise
    
    def init_web3_connections(self):
        """初始化 Web3 連接"""
        try:
            for chain_name, chain_config in self.config['chains'].items():
                w3 = Web3(Web3.HTTPProvider(chain_config['rpc_url']))
                
                # 為 BSC 鏈添加 POA 中間件
                if chain_name == 'bsc':
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                if w3.is_connected():
                    self.web3_instances[chain_name] = w3
                    logging.info(f"{chain_name} 連接成功")
                else:
                    logging.error(f"{chain_name} 連接失敗")
                    
        except Exception as e:
            logging.error(f"Web3 連接初始化失敗: {e}")
            raise
    
    def add_monitored_address(self, chain_name, address, token_address):
        """添加監控地址"""
        cursor = self.db_connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO monitored_addresses (chain_name, address, token_address)
                VALUES (%s, %s, %s)
                ON CONFLICT (chain_name, address, token_address) DO NOTHING
            ''', (chain_name, address, token_address))
            self.db_connection.commit()
            logging.info(f"添加監控地址: {chain_name} - {address} - {token_address}")
        except Exception as e:
            logging.error(f"添加監控地址失敗: {e}")
    
    def record_sender_address(self, chain_name, from_address, to_address, 
                            token_address, transaction_hash, block_number, amount):
        """記錄發送方地址"""
        cursor = self.db_connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO sender_addresses 
                (chain_name, sender_address, receiver_address, token_address, 
                 transaction_hash, block_number, amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (chain_name, from_address, to_address, token_address, 
                  transaction_hash, block_number, str(amount)))
            
            self.db_connection.commit()
            
            logging.info(f"監控地址收到代幣！")
            logging.info(f"   接收地址: {to_address}")
            logging.info(f"   發送地址: {from_address}")
            logging.info(f"   代幣地址: {token_address}")
            logging.info(f"   交易哈希: {transaction_hash}")
            logging.info(f"   區塊號: {block_number}")
            logging.info(f"   金額: {amount}")
            
        except Exception as e:
            logging.error(f"記錄發送方地址失敗: {e}")
    
    def process_transfer_event(self, chain_name, token_address, log):
        """處理轉賬事件"""
        try:
            # 解析事件數據
            topics = log['topics']
            data = log['data']
            
            # 解碼地址（移除0x前綴並填充到40字符）
            from_address = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
            to_address = Web3.to_checksum_address('0x' + topics[2].hex()[-40:])
            
            # 解碼金額
            if isinstance(data, bytes):
                amount = int.from_bytes(data, byteorder='big')
            else:
                data_str = data.hex() if hasattr(data, 'hex') else str(data)
                if data_str.startswith('0x'):
                    data_str = data_str[2:]
                amount = int(data_str, 16)
            
            transaction_hash = log['transactionHash'].hex()
            block_number = log['blockNumber']
            
            # 檢查是否為監控地址
            monitored_addresses = self.config.get('monitored_addresses', [])
            
            if to_address.lower() in [addr.lower() for addr in monitored_addresses]:
                # 記錄發送方地址
                self.record_sender_address(
                    chain_name, from_address, to_address, token_address,
                    transaction_hash, block_number, amount
                )
            
            # 記錄所有交易
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO transaction_records 
                (chain_name, transaction_hash, block_number, from_address, 
                 to_address, token_address, amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (chain_name, transaction_hash, block_number, from_address,
                  to_address, token_address, str(amount)))
            
            self.db_connection.commit()
            
        except Exception as e:
            logging.error(f"處理轉賬事件失敗: {e}")
    
    def monitor_chain(self, chain_name):
        """監控單個鏈"""
        w3 = self.web3_instances[chain_name]
        chain_config = self.config['chains'][chain_name]
        
        # Transfer 事件簽名
        transfer_signature = Web3.keccak(text="Transfer(address,address,uint256)").hex()
        
        # 獲取最新區塊
        try:
            latest_block = w3.eth.get_block('latest')
            current_block = latest_block.number
        except Exception as e:
            logging.error(f"獲取 {chain_name} 最新區塊失敗: {e}")
            return
        
        logging.info(f"開始監控 {chain_name}，當前區塊: {current_block}")
        
        # 監控每個代幣
        for token_address in chain_config['token_addresses']:
            try:
                # 使用較小的區塊範圍來避免 RPC 限制
                from_block = max(0, current_block - 100)  # 減少到 100 個區塊
                
                logs = w3.eth.get_logs({
                    'address': token_address,
                    'topics': [transfer_signature],
                    'fromBlock': from_block,
                    'toBlock': current_block
                })
                
                logging.info(f"找到 {len(logs)} 個 Transfer 事件")
                
                for log in logs:
                    self.process_transfer_event(chain_name, token_address, log)
                
                logging.info(f"{chain_name} - {token_address} 監控完成")
                
            except ValueError as e:
                if "query returned more than 10000 results" in str(e):
                    logging.warning(f"{chain_name} - {token_address}: RPC 查詢結果過多，跳過此代幣")
                else:
                    logging.error(f"監控 {chain_name} - {token_address} 失敗: {e}")
            except Exception as e:
                logging.error(f"監控 {chain_name} - {token_address} 失敗: {e}")
    
    def start_monitoring(self):
        """開始監控"""
        logging.info("開始代幣監控...")
        
        while True:
            try:
                for chain_name in self.web3_instances.keys():
                    self.monitor_chain(chain_name)
                
                # 等待 60 秒後再次監控
                time.sleep(60)
                
            except KeyboardInterrupt:
                logging.info("監控已停止")
                break
            except Exception as e:
                logging.error(f"監控錯誤: {e}")
                time.sleep(10)
    
    def close(self):
        """關閉連接"""
        if self.db_connection:
            self.db_connection.close()
        logging.info("連接已關閉")

if __name__ == "__main__":
    monitor = TokenMonitorPostgres('config.json')
    try:
        monitor.start_monitoring()
    finally:
        monitor.close()