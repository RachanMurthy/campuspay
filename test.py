from eth_connect import connect_to_ethereum, get_transactions_by_address


w3 = connect_to_ethereum()
if connect_to_ethereum() == -1:
    raise Exception("CONNECTION TO BLOCKCHAIN FAILED")

address = "0x1A167E78485aFcab05b81A3bF5a3cD1C1948c16F"

for i in get_transactions_by_address(w3, address=address):
    print(f"Date: {i['block_date']}")
    print(f"From: {i['from']}")
    print(f"To: {i['to']}")
    print(f"Value: {w3.from_wei(i['value'], 'ether')} ETH")
    print("\n")


