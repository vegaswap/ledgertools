"""
work in progress
"""

import transact

# contractAddress = '0x345ca3e014aaf5dca488057592ee47305d9b3e10'
# contract = w3.eth.contract(address=contractAddress, abi=abiJson['abi'])
# accounts = w3.eth.accounts
import time

from web3 import Web3


def log_loop(ctr, event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            print (event)
            # receipt = w3.eth.waitForTransactionReceipt(event['transactionHash'])
            # result = ctr.events.greeting.processReceipt(receipt)
            # print(result[0]['args'])
            # time.sleep(poll_interval)
        print ("..")
        time.sleep(poll_interval)

w3 = transact.get_w3()
nrt = transact.get_contract(w3, "NRT")
address = Web3.toChecksumAddress('0x2ad42d20b5f8a1826ce6a08de78bdf974ac66ea1')

bh = w3.eth.get_block_number()

for p in range(10):
    fb = bh - ((p+1)*5000)
    tb = bh - (p*5000)
    print (fb, tb)
    fd = {'fromBlock': fb, 'toBlock': tb,'address': address}
    f1 = w3.eth.filter(fd)
    print (f1)

    e1 = f1.get_all_entries()
    print(len(e1))

# 
# # block_filter = w3.eth.filter({'fromBlock':10185090-100000, 'address':address})
# block_filter = w3.eth.filter({'fromBlock':0, 'address':address})
# log_loop(nrt, block_filter, 60)

# log_loop(block_filter, 2)