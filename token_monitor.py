import json
import sqlite3
import time
import threading
from datetime import datetime
from web3 import Web3
from web3.exceptions import BlockNotFound
import requests
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)

class TokenMonitor:
    def __init__(self, config_file='config.json'):
        """
        初始化監控器
        config.json 格式:
        {
            "chains": {
                "ethereum": {
                    "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
                    "chain_id": 1,
                    "token_addresses": ["0x..."]
                },
                "bsc": {
                    "rpc_url": "https://bsc-dataseed.binance.org/",
                    "chain_id": 56,
                    "token_addresses": ["0x..."]
                }
            },
            "database": "addresses.db"
        }
        """
        self.config = self.load_config(config_file)
        self.db_connection = self.init_database()
        self.web3_instances = {}
        self.setup_web3_connections()
        
    def load_config(self, config_file):
        """加載配置文件"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # 創建默認配置文件
            default_config = {
                "chains": {
                    "ethereum": {
                        "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
                        "chain_id": 1,
                        "token_addresses": []
                    }
                },
                "database": "addresses.db"
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            raise Exception(f"請先配置 {config_file} 文件")
    
    def init_database(self):
        """初始化數據庫"""
        conn = sqlite3.connect(self.config['database'], check_same_thread=False)
        cursor = conn.cursor()
        
        # 創建地址表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitored_addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain_name TEXT NOT NULL,
                address TEXT NOT NULL,
                token_address TEXT NOT NULL,
                transaction_hash TEXT,
                block_number INTEGER,
                amount TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chain_name, address, token_address)
            )
        ''')
        
        # 創建交易記錄表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain_name TEXT NOT NULL,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                token_address TEXT NOT NULL,
                transaction_hash TEXT NOT NULL,
                block_number INTEGER,
                amount TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 創建發送方地址記錄表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sender_addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain_name TEXT NOT NULL,
                sender_address TEXT NOT NULL,
                receiver_address TEXT NOT NULL,
                token_address TEXT NOT NULL,
                transaction_hash TEXT NOT NULL,
                block_number INTEGER,
                amount TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        return conn
    
    def setup_web3_connections(self):
        """設置Web3連接"""
        for chain_name, chain_config in self.config['chains'].items():
            try:
                w3 = Web3(Web3.HTTPProvider(chain_config['rpc_url']))
                if w3.is_connected():
                    self.web3_instances[chain_name] = w3
                    logging.info(f"成功連接到 {chain_name} 網絡")
                else:
                    logging.error(f"無法連接到 {chain_name} 網絡")
            except Exception as e:
                logging.error(f"連接 {chain_name} 網絡時出錯: {e}")
    
    def get_erc20_transfer_event_signature(self):
        """獲取ERC20 Transfer事件的簽名"""
        return Web3.keccak(text="Transfer(address,address,uint256)").hex()
    
    def decode_transfer_event(self, log):
        """解碼Transfer事件"""
        try:
            # ERC20 Transfer事件的ABI
            transfer_event_abi = {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "from", "type": "address"},
                    {"indexed": True, "name": "to", "type": "address"},
                    {"indexed": False, "name": "value", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            }
            
            contract = self.w3.eth.contract(abi=[transfer_event_abi])
            event_data = contract.events.Transfer().process_log(log)
            return event_data
        except Exception as e:
            logging.error(f"解碼事件時出錯: {e}")
            return None
    
    def monitor_chain(self, chain_name, chain_config):
        """監控單個鏈"""
        w3 = self.web3_instances.get(chain_name)
        if not w3:
            logging.error(f"未找到 {chain_name} 的Web3實例")
            return
        
        self.w3 = w3  # 為了解碼事件使用
        event_signature = self.get_erc20_transfer_event_signature()
        
        # 獲取當前區塊號
        try:
            latest_block = w3.eth.get_block('latest')
            current_block = latest_block['number']
            logging.info(f"{chain_name} 當前區塊號: {current_block}")
        except Exception as e:
            logging.error(f"獲取 {chain_name} 最新區塊時出錯: {e}")
            return
        
        # 從最後一個已知區塊開始監控
        start_block = max(current_block - 1000, 0)  # 回溯1000個區塊
        
        while True:
            try:
                latest_block = w3.eth.get_block('latest')
                latest_block_number = latest_block['number']
                
                # 檢查新區塊
                if latest_block_number > current_block:
                    logging.info(f"{chain_name} 檢查區塊 {current_block + 1} 到 {latest_block_number}")
                    
                    # 分批處理區塊以避免RPC限制
                    batch_size = 100
                    for start in range(current_block + 1, latest_block_number + 1, batch_size):
                        end = min(start + batch_size - 1, latest_block_number)
                        self.check_blocks(chain_name, chain_config, start, end, event_signature)
                    
                    current_block = latest_block_number
                
                time.sleep(15)  # 每15秒檢查一次
                
            except Exception as e:
                logging.error(f"{chain_name} 監控時出錯: {e}")
                time.sleep(30)  # 出錯時等待30秒再重試
    
    def check_blocks(self, chain_name, chain_config, start_block, end_block, event_signature):
        """檢查指定區塊範圍內的交易"""
        w3 = self.web3_instances[chain_name]
        
        # 為每個監控的代幣地址創建過濾器
        for token_address in chain_config.get('token_addresses', []):
            try:
                # 創建事件過濾器
                event_filter = w3.eth.filter({
                    'address': Web3.to_checksum_address(token_address),
                    'topics': [event_signature],
                    'fromBlock': start_block,
                    'toBlock': end_block
                })
                
                logs = event_filter.get_all_entries()
                
                for log in logs:
                    self.process_transfer_event(chain_name, token_address, log)
                
                # 清理過濾器
                w3.eth.uninstall_filter(event_filter.filter_id)
                
            except Exception as e:
                logging.error(f"{chain_name} 檢查區塊 {start_block}-{end_block} 時出錯: {e}")
    
    def process_transfer_event(self, chain_name, token_address, log):
        """處理轉賬事件"""
        try:
            # 解析事件數據
            topics = log['topics']
            data = log['data']
            
            # 解碼地址（移除0x前綴並填充到40字符）
            from_address = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
            to_address = Web3.to_checksum_address('0x' + topics[2].hex()[-40:])
            
            # 解碼金額 - 修復 bytes 轉換問題
            if isinstance(data, bytes):
                amount = int.from_bytes(data, byteorder='big')
            else:
                # 如果是字符串格式，移除 0x 前綴
                data_str = data.hex() if hasattr(data, 'hex') else str(data)
                if data_str.startswith('0x'):
                    data_str = data_str[2:]
                amount = int(data_str, 16)
            
            transaction_hash = log['transactionHash'].hex()
            block_number = log['blockNumber']
            
            logging.info(f"{chain_name} 發現轉賬: {from_address} -> {to_address}, 金額: {amount}")
            
            # 記錄交易
            self.record_transaction(chain_name, from_address, to_address, token_address, 
                                 transaction_hash, block_number, str(amount))
            
            # 檢查是否是監控地址收到代幣
            monitored_addresses = self.config.get('monitored_addresses', [])
            if to_address.lower() in [addr.lower() for addr in monitored_addresses]:
                # 記錄轉出方地址（發送方）
                self.record_sender_address(chain_name, from_address, to_address, token_address, 
                                         transaction_hash, block_number, str(amount))
            
        except Exception as e:
            logging.error(f"處理轉賬事件時出錯: {e}")
            # 添加更詳細的錯誤信息
            logging.debug(f"數據格式: {type(data)}, 數據內容: {data}")
            logging.debug(f"Topics: {topics}")
    
    def record_transaction(self, chain_name, from_address, to_address, token_address, 
                          transaction_hash, block_number, amount):
        """記錄交易到數據庫"""
        cursor = self.db_connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO transaction_records 
                (chain_name, from_address, to_address, token_address, transaction_hash, block_number, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (chain_name, from_address, to_address, token_address, transaction_hash, block_number, amount))
            self.db_connection.commit()
        except sqlite3.IntegrityError:
            # 交易已存在
            pass
        except Exception as e:
            logging.error(f"記錄交易時出錯: {e}")
    
    def add_address_if_monitored(self, chain_name, address, token_address, 
                               transaction_hash, block_number, amount):
        """如果地址被監控則添加到數據庫"""
        # 檢查配置中的監控地址列表
        monitored_addresses = self.config.get('monitored_addresses', [])
        
        # 檢查當前地址是否在監控列表中
        if address.lower() in [addr.lower() for addr in monitored_addresses]:
            cursor = self.db_connection.cursor()
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO monitored_addresses 
                    (chain_name, address, token_address, transaction_hash, block_number, amount)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (chain_name, address, token_address, transaction_hash, block_number, amount))
                self.db_connection.commit()
                
                if cursor.rowcount > 0:
                    logging.info(f"監控地址收到代幣: {address} ({chain_name})")
                    logging.info(f"  代幣地址: {token_address}")
                    logging.info(f"  交易哈希: {transaction_hash}")
                    logging.info(f"  區塊號: {block_number}")
                    logging.info(f"  金額: {amount}")
                    
            except Exception as e:
                logging.error(f"添加地址到監控列表時出錯: {e}")
    
    def record_sender_address(self, chain_name, from_address, to_address, token_address, 
                            transaction_hash, block_number, amount):
        """記錄轉出方地址到數據庫"""
        cursor = self.db_connection.cursor()
        try:
            # 創建發送方記錄表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sender_addresses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chain_name TEXT NOT NULL,
                    sender_address TEXT NOT NULL,
                    receiver_address TEXT NOT NULL,
                    token_address TEXT NOT NULL,
                    transaction_hash TEXT NOT NULL,
                    block_number INTEGER,
                    amount TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 插入發送方記錄
            cursor.execute('''
                INSERT OR IGNORE INTO sender_addresses 
                (chain_name, sender_address, receiver_address, token_address, transaction_hash, block_number, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (chain_name, from_address, to_address, token_address, transaction_hash, block_number, amount))
            self.db_connection.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"🎯 監控地址收到代幣！")
                logging.info(f"  接收地址: {to_address}")
                logging.info(f"  發送地址: {from_address}")
                logging.info(f"  代幣地址: {token_address}")
                logging.info(f"  交易哈希: {transaction_hash}")
                logging.info(f"  區塊號: {block_number}")
                logging.info(f"  金額: {amount}")
                
        except Exception as e:
            logging.error(f"記錄發送方地址時出錯: {e}")
    
    def add_monitored_address(self, chain_name, address, token_address):
        """手動添加監控地址"""
        cursor = self.db_connection.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO monitored_addresses 
                (chain_name, address, token_address)
                VALUES (?, ?, ?)
            ''', (chain_name, Web3.to_checksum_address(address), Web3.to_checksum_address(token_address)))
            self.db_connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"添加監控地址時出錯: {e}")
            return False
    
    def get_monitored_addresses(self, chain_name=None):
        """獲取監控的地址列表"""
        cursor = self.db_connection.cursor()
        if chain_name:
            cursor.execute('SELECT * FROM monitored_addresses WHERE chain_name = ?', (chain_name,))
        else:
            cursor.execute('SELECT * FROM monitored_addresses')
        return cursor.fetchall()
    
    def start_monitoring(self):
        """開始監控所有鏈"""
        threads = []
        
        for chain_name, chain_config in self.config['chains'].items():
            if chain_name in self.web3_instances:
                thread = threading.Thread(
                    target=self.monitor_chain,
                    args=(chain_name, chain_config),
                    daemon=True
                )
                thread.start()
                threads.append(thread)
                logging.info(f"開始監控 {chain_name}")
        
        # 等待所有線程
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logging.info("監控已停止")
    
    def close(self):
        """關閉連接"""
        if self.db_connection:
            self.db_connection.close()

def main():
    """主函數"""
    try:
        monitor = TokenMonitor('config.json')
        
        # 示例：手動添加監控地址
        # monitor.add_monitored_address('ethereum', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', '0xdAC17F958D2ee523a2206206994597C13D831ec7')
        
        # 開始監控
        monitor.start_monitoring()
        
    except Exception as e:
        logging.error(f"程序執行出錯: {e}")
    finally:
        if 'monitor' in locals():
            monitor.close()

if __name__ == "__main__":
    main()