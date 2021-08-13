import requests


def write_abi(name, contract_address):
    response = requests.get(
        f"https://api.bscscan.com/api?"
        f"module=contract&"
        f"action=getabi&"
        f"address={contract_address}"
    )

    abi = response.json()["result"]
    with open("%s.abi" % name, "w") as f:
        f.write(abi)


def load_abi(wdir, name):
    with open("%s/%s.abi" % (wdir, name), "r") as f:
        return f.read()


def load_contract(w3, address, abi):
    return w3.eth.contract(address=address, abi=abi)
