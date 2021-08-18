from eth_account import Account
from web3 import Web3
import toml
import json

ca = Web3.toChecksumAddress

URL = "https://bsc-dataseed.binance.org"
w3 = Web3(Web3.HTTPProvider(URL))

def get_contract(ctr_name):
    with open("%s.json"%ctr_name,"r") as f:
        b = json.loads(f.read())
        print (b.keys())
        abi = b["abi"]
        bin = b["bytecode"]

    contract = w3.eth.contract(abi=abi, bytecode=bin)
    return contract

def get_deploy_tx(address):
    ctr_name = "NRT"
    contract = get_contract(ctr_name)

    nonce = w3.eth.getTransactionCount(address) #, 'pending')
    # print(acct.address, nonce)

    txparams = {
                # 'from': myadress,
                # 'to': '',
                # "gas": 999000,
                'nonce': nonce,
                "gasPrice": w3.toWei('5', 'gwei')}
    tx = contract.constructor("VegaNRT", "Seed").buildTransaction(txparams)
    # print(tx)

    est = w3.eth.estimate_gas(tx)
    print("estimated gas ", est)
    #add some gas just in case
    use_gas = int(est*1.2)
    txparams["gas"] = use_gas
    tx = contract.constructor("VegaNRT", "Seed").buildTransaction(txparams)
    # print(tx)

    return tx

if __name__ == "__main__":
    from pathlib import Path
    home = str(Path.home())
    f = "bsc_mainnet.toml"
    p = Path(home, ".chaindev", f)
    secrets = toml.load(p)
    pk = secrets["PRIVATEKEY"]
    import toml

    account = Account()
    acct = account.privateKeyToAccount(pk)
    addr = acct.address
    print (addr)

    # myadress = ledger_account.address
    tx = get_deploy_tx(addr)

    # signedtx = w3.eth.account.signTransaction(tx, pk)
    # print(signedtx)
    # w3.eth.sendRawTransaction(signedtx.rawTransaction)
    # pushtx(signedtx)
