from web3 import Web3

def connect_to_ethereum(link='http://127.0.0.1:8545'):
    w3 = Web3(Web3.HTTPProvider(link))

    # Check if connected to Ethereum
    if w3.is_connected():
        return w3
    else:
        return -1
