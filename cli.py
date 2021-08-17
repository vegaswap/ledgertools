"""
todo record commands
"""

import click
from ledger_usb import *
import sys

from account import LedgerAccount
from web3 import Web3
import utils

BSC_USDT = "0x55d398326f99059fF775485246999027B3197955"

def get_ledger(accountID):
    try:
        ledger_account = LedgerAccount(account_id=accountID)
        address = ledger_account.get_address(accountID)
        #{ledger_account} \t
        click.secho(f"ledger loaded accountID {accountID}\taddress: {address}", bg='black', fg='green')

        return ledger_account
    except LedgerUsbException:
        click.secho(f"ledger not active", bg='black', fg='blue')
        sys.exit(1)

@click.group()
@click.option('--aid', help='account ID')
@click.pass_context
def main(ctx, aid: int):
    aid = int(aid)
    print ("main ",ctx, aid, type(aid))

    ledger_account = get_ledger(aid)

    ctx.obj['ledger_account'] = ledger_account

    URL = "https://bsc-dataseed.binance.org"
    w3 = Web3(Web3.HTTPProvider(URL))
    ctx.obj['w3'] = w3

    critical_accounts = [0 , 1]
    #critical
    if aid in critical_accounts:
        click.secho(f"PERFORMING CRITICAL TASKS", bg='black', fg='red')
        click.secho(f"YES/NO (Y/N)", bg='black', fg='red')
        yesno = input()
        if yesno == "Y":
            click.secho(f"PROCEED", bg='black', fg='red')
        elif yesno == "N":
            click.secho(f"dont proceed", bg='black', fg='red')
            sys.exit(0)
        else:
            click.secho(f"dont proceed", bg='black', fg='red')
            sys.exit(0)


def show_balance(w3, addr):
    ercabi = utils.load_abi("./", "erc20")
    ctr = utils.load_contract(w3, BSC_USDT, ercabi)
    name = ctr.functions.name().call()
    sym = ctr.functions.symbol().call()
    b = ctr.functions.balanceOf(addr).call()
    click.secho(f"{name}: {b/10**18} ({sym})", fg="green")


@main.command()
@click.pass_context
def balanceusdt(ctx):
    # get my address
    myaddr = ctx.obj['ledger_account'].address
    show_balance(myaddr)



@main.command()
@click.pass_context
def balancebnb(ctx):
    ledger_account = ctx.obj['ledger_account']
    myaddr = ledger_account.address
    bnb_bal = ctx.obj['w3'].eth.getBalance(myaddr)

    click.secho(f"BNB {bnb_bal/10**18}", fg="green")

@main.command()
@click.pass_context
def listaccounts(ctx):
    ledger_account = ctx.obj['ledger_account']
    for i in range(3):
        addr = ledger_account.get_address(i)
        click.secho(f"addr:  {addr}", fg="green")


@main.command()
@click.pass_context
def listall(ctx):
    ledger_account = ctx.obj['ledger_account']
    for i in range(3):
        addr = ledger_account.get_address(i)
        click.secho(f"addr:  {addr}", fg="green")
        bnb_bal = ctx.obj['w3'].eth.getBalance(addr)
        click.secho(f"BNB {bnb_bal/10**18}", fg="green")
        show_balance(ctx.obj['w3'], addr)
        click.secho(f"---------", fg="white")



@main.command()
@click.option('--name', help='full name')
@click.pass_context
def version(ctx, name):
    click.secho(f"{ctx.obj['ledger_account'].get_version()}", fg="green")


def start():
    main(obj={})

if __name__ == '__main__':
    start()