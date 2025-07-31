import json

def test_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("=== 配置檢查 ===")
        print(f"Ethereum RPC: {config['chains']['ethereum']['rpc_url']}")
        print(f"BSC RPC: {config['chains']['bsc']['rpc_url']}")
        
        # 檢查 PROJECT_ID 是否已配置
        if 'YOUR_PROJECT_ID' in config['chains']['ethereum']['rpc_url']:
            print("❌ 請先配置 Infura PROJECT_ID")
        else:
            print("✅ Infura PROJECT_ID 已配置")
        
        print(f"監控代幣數量: Ethereum={len(config['chains']['ethereum']['token_addresses'])}, BSC={len(config['chains']['bsc']['token_addresses'])}")
        
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    test_config()