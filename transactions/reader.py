# from bot import Bot
from config.abis import PCS_ROUTER
from config import *
from .filter import Filters
from network import w3n, RandWeb3
from time import time
import asyncio
from functools import partial

rw = RandWeb3()


async def get_tx_detail(tx_hash):
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(None, partial(rw.w3.eth.get_transaction, tx_hash))
    except:
        return None


async def _get_pends():
    pends = []
    a = w3n.eth.filter("pending").get_new_entries()
    if a:
        txs = await asyncio.gather(*[get_tx_detail(h) for h in a], return_exceptions=False)
        pends = [tx for tx in txs if tx]
    return pends


class Reader:
    def __init__(self, wallet):
        self.bot = wallet
        self.ftr = Filters()
        router_address = self.bot.network.toChecksumAddress(PCS_ROUTER_ADDRESS[0])
        self.decoder = self.bot.network.eth.contract(router_address, abi=PCS_ROUTER)

    def read_tx(self, tx):
        try:
            obj = self.decoder.decode_function_input(tx.input)
        except:
            return False
        call_name = obj[0].__class__.__name__
        args = obj[1]
        return {
            'name': call_name,
            'args': args,
            'path': args.get('path', []),
            'to': tx.to,
            'gas': tx.gasPrice / 1e9,
            'value': tx.value,
            'timegap': (args['deadline'] - time()) / 60 if args.get('deadline') else None
        }

    def set_swap_rates(self, txs: list):
        def exchangeRate(x, y, z):
            """
            get gap of current price
            :param x: source
            :param y: to
            :param z: amount
            :return:
            """
            z *= 0.997
            bef = y / x * z / 1e18
            aft = y * z / (x + z)
            return aft / y * 100

        tokens = [p['path'][-1] for p in txs]
        routers = [self.bot.network.toChecksumAddress(p['to']) for p in txs]
        data = self.bot.contract.functions.getReserves(tokens, routers).call()
        resv0 = data[0]
        resv1 = data[1]
        for i, tx in enumerate(txs):
            tx['rate'] = exchangeRate(resv0[i], resv1[i], tx['value'])
        return txs

    def get_pends(self):
        data = asyncio.run(_get_pends())
        pends = []
        for tx in data:
            tx_data = self.read_tx(tx)
            if not tx_data:
                continue
            if self.ftr.swap_filter(tx_data):
                pends.append(tx_data)
        self.set_swap_rates(pends)
        result = []
        for p in pends:
            if self.ftr.rank_filter(p):
                result.append(p)
        result = sorted(result, key=lambda x: x['timegap'], reverse=True)
        return result

    def get_tx_status(self, hash_id):
        recp = self.bot.network.eth.get_transaction_receipt(hash_id)
        return recp.status
