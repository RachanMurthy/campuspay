from time import time
from web3 import Web3

from .utils import generate_random_string, json_dump_file, json_read_file
from .settings import KEYSTORE_PATH, GENESIS_PUB_ADDRESS, GENESIS_FILE, GENESIS_PASSWORD


def connect_to_ethereum(link='http://127.0.0.1:8545'):
    w3 = Web3(Web3.HTTPProvider(link))

    # Check if connected to Ethereum
    if w3.is_connected():
        return w3
    else:
        return -1

    
def blocknumber(w3):
    # Returns current active block
    return w3.eth.block_number


def wallet_balance(w3, pub_address):
    # pub_sender is public address
    # Returns balance in ETH
    balance = w3.eth.get_balance(pub_address)
    return  w3.from_wei(balance, 'ether')


def create_wallet(w3, count = 4):
    # Address: account.address
    # Private Key:account.key.hex()
    # generate_random_string() used for generating random keys
    # passphare is a 4 digit integer password
    # encrypted_key encrypts the private key using passphare
    # filename stores filename under standrard format
    # KEYSTORE_PATH is the folder location of keystore stored in settings.py
    # encrypted key stored in keystore folder after encryption

    rand_string = generate_random_string()
    account = w3.eth.account.create(rand_string) 
    passphrase = generate_random_string(count)
    encrypted_key = w3.eth.account.encrypt(account.key.hex(), passphrase)
    filename = f'UTC--{int(time())}--{account.address[2:]}.json'
    json_dump_file(KEYSTORE_PATH, filename, encrypted_key)

    return passphrase, account.address, filename


def get_private_key(w3, filename, passphrase):
    # filename stores filename under standrard format
    # KEYSTORE_PATH is the folder location of keystore stored in settings.py
    # encrypted file is read and decrypted to get private key

    encrypted_key = json_read_file(KEYSTORE_PATH, filename)
    private_key = w3.eth.account.decrypt(encrypted_key, passphrase).hex()

    return private_key


# need to add more detail while returning tx_receipt
def send_eth(w3, pub_sender, pri_sender, pub_receiver, value, gas=21000, chainid=999, gasprice=0):
    # nonce is no of transaction by an address
    # pub_sender and receiver both wallet public address
    # pri_sender is private address
    # w3.to_wei(x, 'ether') converts eth to wei (1 WEI = 10^-18 ETH)

    nonce = w3.eth.get_transaction_count(pub_sender)
    tx = {
        'nonce': nonce,
        'to': pub_receiver,
        'value': w3.to_wei(value, 'ether'),
        'gas': gas,
        'gasPrice': gasprice,
        'chainId': chainid
    }

    # Sign the transaction using the genesis account's private key
    signed_tx = w3.eth.account.sign_transaction(tx, pri_sender)

    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if tx_receipt.status == 1:
        return True
    else:
        return False

def send_eth_from_genesis(w3, pub_receiver, value):
    # SEND ETH TO ANY RECIEVER THROUGH THE GENESIS FILE
    # pub_sender wallet public address
    # value : amount to send
    gen_pri = get_private_key(w3, GENESIS_FILE, GENESIS_PASSWORD)
    gen_pub = GENESIS_PUB_ADDRESS
    w3 = w3
    pub_receiver = pub_receiver
    value = value

    gen_transaction = send_eth(w3,gen_pub, gen_pri, pub_receiver, value)

    if gen_transaction:
        return True
    else:
        return False