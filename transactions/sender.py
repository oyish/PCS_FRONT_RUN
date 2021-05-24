from network import w3, w3t
from time import time
from config.abis import BOT_TEST
from config import *


class Sender:

    def __init__(self, account):
        self.bot = account

    def withdraw(self):
        tx = self.bot.contract.functions.withdraw().buildTransaction({
            'gas': 1000261,
            'gasPrice': self.bot.network.eth.gas_price,
            'nonce': self.bot.nonce,
            'from': self.bot.address,
        })
        return self.bot.sign_tx(tx)

    def sendBNB(self, value, gas=None, gas_price=None):
        tx = {
            'nonce': self.bot.nonce,
            'to': BOT_CONTRACT,
            'value': self.bot.network.toWei(value, 'ether'),
            'gas': 100000,
            'gasPrice': self.bot.network.toWei(gas_price if gas_price else 50, 'gwei')
        }
        return self.bot.sign_tx(tx)

    def buy(self, bnb_amount, token_address, router, gwei):
        token_address = self.bot.network.toChecksumAddress(token_address)
        router = self.bot.network.toChecksumAddress(router)
        tx = self.bot.contract.functions.buyToken(bnb_amount, token_address, router).buildTransaction({
            'gas': 1000261,
            'gasPrice': self.bot.network.toWei(gwei, 'gwei'),
            'from': self.bot.address,
            'nonce': self.bot.nonce
        })
        try:
            return self.bot.sign_tx(tx)
        except Exception as e:
            print(e)
            tx['gasPrice'] = self.bot.network.toWei(gwei + 1, 'gwei')
            tx['nonce'] = self.bot.nonce + 1
            return self.bot.sign_tx(tx)

    def sell(self, token_address, router, gwei, nonce=0):
        token_address = self.bot.network.toChecksumAddress(token_address)
        router = self.bot.network.toChecksumAddress(router)
        tx = self.bot.contract.functions.sellToken(token_address, router).buildTransaction({
            'gas': 1000261,
            'gasPrice': self.bot.network.toWei(gwei, 'gwei'),
            'from': self.bot.address,
            'nonce': self.bot.nonce + nonce
        })
        try:
            return self.bot.sign_tx(tx)
        except Exception as e:
            print(e)
            tx['gasPrice'] = self.bot.network.toWei(gwei + 1, 'gwei')
            tx['nonce'] = self.bot.nonce + 1
            return self.bot.sign_tx(tx)

    def emergencySell(self, token_address, router, gwei, nonce=0):
        token_address = self.bot.network.toChecksumAddress(token_address)
        router = self.bot.network.toChecksumAddress(router)
        tx = self.bot.contract.functions.emergencySell(token_address, router).buildTransaction({
            'gas': 1000261,
            'gasPrice': self.bot.network.toWei(gwei, 'gwei'),
            'from': self.bot.address,
            'nonce': self.bot.nonce + nonce
        })
        try:
            return self.bot.sign_tx(tx)
        except Exception as e:
            print(e)
            tx['gasPrice'] = self.bot.network.toWei(gwei + 1, 'gwei')
            tx['nonce'] = self.bot.nonce + 1
            return self.bot.sign_tx(tx)
