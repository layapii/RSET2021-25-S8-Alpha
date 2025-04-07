
import json
from web3 import Web3, HTTPProvider


# truffle development blockchain address
blockchain_address = 'http://127.0.0.1:9545'
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = 'C:/Users/ami1p/OneDrive/Documents/Online_Vehicle_Shop_rajagiri new/Online_Vehicle_Shop_rajagiri/Online_Vehicle_Shop/Online_vehicle_shop_web/node_modules/.bin/build/contracts/vehicles.json'
# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = '0xa90a8aF1ab87006f4aEb47E1429A3E972bBE240f'
syspath=r"C:\Users\Riss\Desktop\RISS\BLOCKCHAIN\EHR\static\\"




