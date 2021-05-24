from web3 import Web3, HTTPProvider, WebsocketProvider
from random import randint

w3 = Web3(provider=HTTPProvider("https://bsc-dataseed.binance.org/"))

w3t = Web3(provider=HTTPProvider("https://data-seed-prebsc-1-s1.binance.org:8545/"))

w3n = Web3(provider=WebsocketProvider('wss://bsc-ws-node.nariox.org:443'))


class RandWeb3:
    providers = ["https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed1.ninicoin.io/"]

    def __init__(self):
        self.web3s = [Web3(provider=HTTPProvider(p)) for p in self.providers]

    @property
    def w3(self) -> Web3:
        index = randint(0, 1)
        return self.web3s[index]
