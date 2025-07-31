import json
import sys

def test_config():
    """測試配置文件"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("=== 配置檢查 ===")
        print(f"Ethereum RPC: {config['chains']['ethereum']['rpc_url']}")
        print(f"BSC RPC: {config['chains']['bsc']['rpc_url']}")
        print(f"監控代幣數量: Ethereum={len(config['chains']['ethereum']['token_addresses'])}, BSC={len(config['chains']['bsc']['token_addresses'])}")
        
        # 檢查代幣地址
        print("\n=== 監控的代幣地址 ===")
        print("Ethereum:")
        for addr in config['chains']['ethereum']['token_addresses']:
            print(f"  {addr}")
        
        print("BSC:")
        for addr in config['chains']['bsc']['token_addresses']:
            print(f"  {addr}")
        
        print("\n配置檢查完成！")
        return True
        
    except Exception as e:
        print(f"配置檢查失敗: {e}")
        return False

if __name__ == "__main__":
    test_config()