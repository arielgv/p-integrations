from typing import Dict

from .feed import BinanceListener


class BBO(BinanceListener):

    def __init__(self):
        self.bbo = {}

    def on_book_ticker(self, symbol: str, bbo: Dict[str, float]):
        self.bbo[symbol] = bbo
