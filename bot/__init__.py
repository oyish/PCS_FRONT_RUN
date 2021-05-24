from network import w3t, w3
from web3 import Web3, exceptions
from config.account import *
from config import *
from config.abis import *
from transactions.reader import Reader
from transactions.sender import Sender
import os
import json

# print(w3t.eth.account.create("").address)

kf_path = os.path.join(os.path.dirname(__file__), 'wallets')
black_path = os.path.join(os.path.dirname(__file__), 'blacks')


class Bot:
    networks = {
        'mainnet': w3,
        'testnet': w3t
    }

    network_mode: str

    _w: Web3
    _address: str
    pk: str

    def __init__(self, network: str):
        self._w = self.networks[network]
        self.network_mode = network
        self.address = ACCOUNT_ADDRESS
        self.pk = ACCOUNT_PK
        self.pcs = None
        self.reader = Reader(self)
        self.sender = Sender(self)
        self.contract = self._w.eth.contract(BOT_CONTRACT, abi=BOT_TEST)
        with open(black_path + '/blacklist.json', 'r') as f:
            self.black_list = json.load(f)

    def balanceOf(self, token_addr):
        contract = self._w.eth.contract(token_addr, abi=BEP20)
        balance = contract.functions.balanceOf(self.address).call()
        return balance

    def end_pending(self, hash_id):
        try:
            return self._w.eth.get_transaction(hash_id).blockHash
        except exceptions.TransactionNotFound:
            return True
        except:
            return False

    def get_status(self, hash_id):
        try:
            return self._w.eth.get_transaction_receipt(hash_id).status
        except:
            return 0

    def sign_tx(self, tx):
        signed_tx = self.network.eth.account.sign_transaction(tx, self.pk)
        tx_hash = self.network.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()

    def add_black_list(self, token):
        if token in self.black_list:
            return True
        self.black_list.append(token.lower())
        with open(black_path + '/blacklist.json', 'w') as f:
            json.dump(self.black_list, f)
        return True

    def check_black_list(self, token):
        return token.lower() in self.black_list

    @property
    def address(self):
        return self._w.toChecksumAddress(self._address)

    @address.setter
    def address(self, v):
        self._address = self._w.toChecksumAddress(v)

    @property
    def nonce(self):
        return self._w.eth.get_transaction_count(self.address)

    @property
    def balance(self):
        return self._w.eth.get_balance(self.address)

    @property
    def contract_balance(self):
        return self._w.eth.get_balance(self.contract.address)

    @property
    def network(self):
        return self._w

    @property
    def block(self):
        return self._w.eth.get_block_number()

    @property
    def gas_price(self):
        return self._w.eth.gas_price
