# from brownie import contract

# erc2= Contract.from_abi("erc20", "")
# from solc import compile_source
from eth_account import Account
import solcx

from web3 import Web3
from web3.types import TxParams
import utils

ca = Web3.toChecksumAddress

URL = "https://bsc-dataseed.binance.org"
w3 = Web3(Web3.HTTPProvider(URL))

ercabi = utils.load_abi("./", "erc20")


def get_deploy_tx():
    contract_source_code = '''
    pragma solidity ^0.8.5;

    contract Greeter {
        uint256 public x;

        constructor() {
            x = 42;
        }

        function setGreeting(uint256 _x) public {
            x = _x;
        }

    }
    '''

    compiled_sol = solcx.compile_source(contract_source_code)
    contract_interface = compiled_sol['<stdin>:Greeter']

    contract_ = w3.eth.contract(
        abi=contract_interface['abi'], bytecode=contract_interface['bin'])

    nonce = w3.eth.getTransactionCount(acct.address, 'pending')
    # print(acct.address, nonce)

    # est = w3.eth.estimate_gas(tx)
    # print("EST ", est)

    txparams = {'from': acct.address,
                # 'to': '',
                'nonce': nonce,
                "gas": 140000,
                "gasPrice": w3.toWei('5', 'gwei')}
    tx = contract_.constructor().buildTransaction(txparams)
    print(tx)

    return tx


def pushtx(signedtx):
    result = w3.eth.sendRawTransaction(signedtx.rawTransaction)
    rh = result.hex()
    print('result ', rh)

    tx_receipt = w3.eth.waitForTransactionReceipt(rh)
    print('status ', tx_receipt['status'])
    print('blockNumber ', tx_receipt['blockNumber'])
    print('gasUsed ', tx_receipt['gasUsed'])
    # contractAddress
    # cumulativeGasUsed


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

    tx = get_deploy_tx()

    signedtx = w3.eth.account.signTransaction(tx, pk)
    print(signedtx)
    w3.eth.sendRawTransaction(signedtx.rawTransaction)
    pushtx(signedtx)

    account = Account()
    acct = account.privateKeyToAccount(pk)

    tx = get_deploy_tx()

    signedtx = w3.eth.account.signTransaction(tx, pk)
    print(signedtx)
    w3.eth.sendRawTransaction(signedtx.rawTransaction)
    pushtx(signedtx)
