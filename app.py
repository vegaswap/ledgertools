def pushtx(signedtx):
    result = w3.eth.sendRawTransaction(signedtx.rawTransaction)
    rh = result.hex()
    print('result ', rh)

    tx_receipt = w3.eth.waitForTransactionReceipt(rh)
    print(tx_receipt['status'])
    print(tx_receipt['blockNumber'])
    print(tx_receipt['gasUsed'])
    # contractAddress
    # cumulativeGasUsed


def send_simple_tx(ledger_account, sendamount, to_address):

    # get my address
    myaddr = ledger_account.address
    nonce = w3.eth.getTransactionCount(myaddr)

    txd = {
        "chainId": 56,
        "to": to_address,
        "value": sendamount,
        "gas": 21000,
        "gasPrice": 5000 * 10 ** 6,
        "nonce": nonce,
    }

    signedtx = ledger_account.signTransaction(txd)
    print(signedtx)
    pushtx(signedtx)


def send_erc20(ledger_account, USD_amount, to_address):

    ercabi = utils.load_abi("./", "erc20")
    ctr = utils.load_contract(w3, BSC_USDT, ercabi)
    print(ctr.functions.name().call())

    # get my address
    myaddr = ledger_account.address
    nonce = w3.eth.getTransactionCount(myaddr)

    bnbvalue = 0

    tx_params = {
        "chainId": 56,
        # "to": to_address,
        "value": bnbvalue,
        "gas": 50000,
        "gasPrice": 5000 * 10 ** 6,
        "nonce": nonce,
    }

    usdfull = USD_amount * 10 ** 18
    btx = ctr.functions.transfer(
        to_address, usdfull).buildTransaction(tx_params)

    signedtx = ledger_account.signTransaction(btx)

    print(signedtx)
    pushtx(signedtx)

def deploy_example(ledger_account):
    import deploytx
    tx = deploytx.get_deploy_tx(ledger_account)

    signedtx = ledger_account.signTransaction(tx)
    print(signedtx)
    pushtx(signedtx)




# USD_amount = 1000
# vega_corp = "0xe537ce8a0C8bB913A97EA18b148752bc84c67F5d"
# to_address = ca(vega_corp)
# send_erc20(USD_amount, to_address)

# bnb_dec = 18
# amount = int(0.001 * 10 ** bnb_dec)
# trading_address = ca("0xe537ce8a0C8bB913A97EA18b148752bc84c67F5d")
# to_address = ca("0xEA5037E97803021Ab91b276dfe0e93724BCaE370")
# send_simple_tx(ledger_account, amount, to_address)

