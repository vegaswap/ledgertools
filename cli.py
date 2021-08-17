"""
todo record commands
"""

import click
from app import get_ledger
from ledger_usb import *
import sys

from account import LedgerAccount

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

@main.command()
@click.pass_context
def balance(ctx):
    print(ctx.obj['ledger_account'])


@main.command()
@click.option('--name', help='full name')
@click.pass_context
def version(ctx, name, scale: int = 10):
    print (ctx.obj['aid'])

def start():
    main(obj={})


if __name__ == '__main__':
    start()