from config import *


class Filters:
    def __init__(self):
        self._swap_filter = [
            self.filter_time,
            self.filter_name,
            self.filter_to,
            self.filter_value,
            self.filter_gas,
            self.filter_path
        ]

        self._rank_filter = [
            self.filter_ex_rate
        ]

    def swap_filter(self, tx):
        return all(f(tx) for f in self._swap_filter)

    def rank_filter(self, tx):
        return all(f(tx) for f in self._rank_filter)

    @staticmethod
    def filter_time(t):
        if not t.get('timegap'):
            return False
        return 19.9 < t['timegap'] < 20

    @staticmethod
    def filter_name(t):
        if not t.get('name'):
            return False
        return t['name'] == CONTRACT_FUNC_NAME

    @staticmethod
    def filter_to(t):
        if not t.get('to'):
            return False
        return t['to'].lower() in [addr.lower() for addr in PCS_ROUTER_ADDRESS]

    @staticmethod
    def filter_path(t):
        if not t.get('path'):
            return False
        return 0 < len(t['path']) < 3

    @staticmethod
    def filter_gas(t):
        if not t.get('gas'):
            return False
        return t['gas'] <= GAS_LIMIT

    @staticmethod
    def filter_value(t):
        if not t.get('value'):
            return False
        return t['value'] >= VALUE_MIN

    @staticmethod
    def filter_ex_rate(t):
        if not t.get('rate'):
            return False
        return EXCHANGE_RATE_MIN < float(t['rate'])
