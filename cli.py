"""
todo
handle
ledger_usb.LedgerUsbException: Invalid status in reply: 0x6985 (User declined on device)
"""

import click
from ledger_usb import *
import sys

from account import LedgerAccount
from web3 import Web3
import utils

# import logging

from loguru import logger

logger.add("ltools.log", rotation="500 MB")
logger.add(
    sys.stdout, format="{time} {level} {message}", filter="my_module", level="INFO"
)

BSC_USDT = "0x55d398326f99059fF775485246999027B3197955"


try:
    from config import whitelist, critical_accounts
except:
    whitelist = dict()
    critical_accounts = list()


def get_ledger(accountID):
    try:
        ledger_account = LedgerAccount(account_id=accountID)
        address = ledger_account.get_address(accountID)
        click.secho(
            f"ledger loaded accountID {accountID}\taddress: {address}",
            bg="black",
            fg="green",
        )

        return ledger_account
    except LedgerUsbException:
        click.secho(f"ledger not active", bg="black", fg="red")
        sys.exit(1)


def check_critical():
    click.secho(f"PERFORMING CRITICAL TASKS", bg="black", fg="red")
    click.secho(f"YES/NO (Y/N)", bg="black", fg="red")
    yesno = input()
    if yesno == "Y":
        click.secho(f"PROCEED", bg="black", fg="red")
    elif yesno == "N":
        click.secho(f"dont proceed", bg="black", fg="red")
        sys.exit(0)
    else:
        click.secho(f"dont proceed", bg="black", fg="red")
        sys.exit(0)


@click.group()
@click.option("--aid", help="account ID", type=int)
@click.pass_context
def ltools(ctx, aid: int):
    try:
        aid = int(aid)
    except:
        click.secho(f"account id has to be an integer", fg="red")
        sys.exit(0)

    logger.debug(f"main {ctx} {aid}")

    ledger_account = get_ledger(aid)

    ctx.obj["ledger_account"] = ledger_account

    URL = "https://bsc-dataseed.binance.org"
    w3 = Web3(Web3.HTTPProvider(URL))
    ctx.obj["w3"] = w3


def show_balance(w3, addr):
    ercabi = utils.load_abi("./", "erc20")
    ctr = utils.load_contract(w3, BSC_USDT, ercabi)
    name = ctr.functions.name().call()
    sym = ctr.functions.symbol().call()
    b = ctr.functions.balanceOf(addr).call()
    s1 = f"{name}: {b/10**18} ({sym})"
    click.secho(s1, fg="green")
    logger.debug(s1)


def pushtx(w3, signedtx):
    logger.debug(f"push tx {signedtx.rawTransaction}")
    result = w3.eth.sendRawTransaction(signedtx.rawTransaction)
    rh = result.hex()
    logger.debug(f"txhash {rh}")

    tx_receipt = w3.eth.waitForTransactionReceipt(rh)
    s1 = f"status: {tx_receipt['status']}"
    s2 = f"blockNumber: {tx_receipt['blockNumber']}"
    s3 = f"gasUsed: {tx_receipt['gasUsed']}"

    logger.debug(f"{s1}")
    logger.debug(f"{s2}")
    logger.debug(f"{s3}")
    click.secho(s1, fg="green")
    click.secho(s2, fg="green")
    click.secho(s3, fg="green")

    return tx_receipt

    # contractAddress
    # cumulativeGasUsed


@ltools.command()
@click.pass_context
def balanceusdt(ctx):
    myaddr = ctx.obj["ledger_account"].address
    show_balance(myaddr)


@ltools.command()
@click.pass_context
def balancebnb(ctx):
    ledger_account = ctx.obj["ledger_account"]
    myaddr = ledger_account.address
    bnb_bal = ctx.obj["w3"].eth.getBalance(myaddr)

    click.secho(f"BNB {bnb_bal/10**18}", fg="green")


@ltools.command()
@click.pass_context
def listaccounts(ctx):
    logger.debug(f"list accounts")
    ledger_account = ctx.obj["ledger_account"]
    for i in range(3):
        addr = ledger_account.get_address(i)
        click.secho(f"addr:  {addr}", fg="green")


@ltools.command()
@click.pass_context
def listall(ctx):
    logger.debug(f"listall")
    ledger_account = ctx.obj["ledger_account"]
    for i in range(3):
        addr = ledger_account.get_address(i)
        s1 = f"addr:\t{addr}"
        logger.debug(s1)
        click.secho(s1, fg="green")
        bnb_bal = ctx.obj["w3"].eth.getBalance(addr)
        s2 = f"BNB {bnb_bal/10**18}"
        click.secho(s2, fg="green")
        logger.debug(s2)
        show_balance(ctx.obj["w3"], addr)
        click.secho(f"---------", fg="white")


def send_tx(ledger_account, w3, sendamount, to_address):
    logger.debug(f"send_tx {sendamount} {to_address}")

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
    pushtx(w3, signedtx)


def send_erc20(ledger_account, w3, USD_amount, to_address):
    logger.debug(f"send_erc20 {USD_amount} {to_address}")

    ercabi = utils.load_abi("./", "erc20")
    ctr = utils.load_contract(w3, BSC_USDT, ercabi)
    print(ctr.functions.name().call())

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

    btx = ctr.functions.transfer(to_address, USD_amount).buildTransaction(tx_params)

    signedtx = ledger_account.signTransaction(btx)
    logger.debug(f"signedtx {signedtx}")

    print(signedtx)
    pushtx(w3, signedtx)


import json


def get_contract(w3, ctr_name):
    with open("%s.json" % ctr_name, "r") as f:
        b = json.loads(f.read())
        print(b.keys())
        abi = b["abi"]
        bin = b["bytecode"]

    contract = w3.eth.contract(abi=abi, bytecode=bin)
    return contract


def get_deploy_tx(w3, address, ctr_name):

    contract = get_contract(w3, ctr_name)

    nonce = w3.eth.getTransactionCount(address)  # , 'pending')
    # print(acct.address, nonce)

    txparams = {
        # 'from': myadress,
        # 'to': '',
        # "gas": 999000,
        "nonce": nonce,
        "gasPrice": w3.toWei("5", "gwei"),
    }
    tx = contract.constructor("VegaNRT", "Seed").buildTransaction(txparams)
    # print(tx)

    est = w3.eth.estimate_gas(tx)
    print("estimated gas ", est)
    # add some gas just in case
    use_gas = int(est * 1.2)
    txparams["gas"] = use_gas
    tx = contract.constructor("VegaNRT", "Seed").buildTransaction(txparams)
    # print(tx)

    return tx


@ltools.command()
@click.pass_context
@click.option("--amount", help="amount", type=int)
@click.option("--to", help="address")
def sendbnb(ctx, amount, to):
    logger.debug(f"sendbnb {amount} {to}")
    ledger_account = ctx.obj["ledger_account"]
    print("send ", amount)
    print("to ", to)
    # TODO check high amounts
    w3 = ctx.obj["w3"]
    # TODO whitelist addresses
    if to in whitelist.keys():
        addr = whitelist[to]
        send_tx(ledger_account, w3, amount, addr)
    else:
        print("address not whitelisted")


@ltools.command()
@click.pass_context
@click.option("--amount", help="amount", type=int)
@click.option("--to", help="address")
def sendusdt(ctx, amount, to):
    logger.debug(f"send usdt {amount} {to}")
    ledger_account = ctx.obj["ledger_account"]
    print("send ", amount)
    print("to ", to)
    # TODO check high amounts
    w3 = ctx.obj["w3"]
    # TODO whitelist addresses
    if to in whitelist.keys():
        addr = whitelist[to]
        send_erc20(ledger_account, w3, amount, addr)
    else:
        print("address not whitelisted")


# def append_deploymap(name, contractAddress):
    

@ltools.command()
@click.option("--contractname", help="the name of the contract to deploy")
@click.pass_context
def deploytx(ctx, contractname):
    # ctr_name = "NRT"
    if contractname == "" or contractname == None:
        click.secho("no contract name provided", fg="red")
        sys.exit(1)
    s1 = f"deploytx {contractname}"
    click.secho(s1, fg="red")
    logger.debug(s1)
    ledger_account = ctx.obj["ledger_account"]
    myaddr = ledger_account.address
    tx = get_deploy_tx(ctx.obj["w3"], myaddr, contractname)
    print(tx)
    
    signedtx = ledger_account.signTransaction(tx)
    click.secho(f"signedtx {signedtx}", fg="green")
    print(signedtx)
    tx_receipt = pushtx(ctx.obj["w3"], signedtx)
    print (tx_receipt)
    if tx_receipt["status"] == 1:
        click.secho(f"deploy success {tx_receipt}", fg="green")
        contractAddress = tx_receipt["contractAddress"]
        click.secho(f"deployed to {contractAddress}", fg="green")
        # append to map of addresses
        # append_deploymap
    else:
        click.secho(f"deploy failed {tx_receipt}", fg="red")


@ltools.command()
@click.pass_context
def version(ctx):
    logger.debug("version")
    click.secho(f"{ctx.obj['ledger_account'].get_version()}", fg="green")


if __name__ == "__main__":
    ltools(obj={})
