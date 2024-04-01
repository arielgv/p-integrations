import json
import logging
import threading
import time

from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
from hyperliquid.utils.signing import get_timestamp_ms
from hyperliquid.utils.types import (
    SIDES,
    Dict,
    L2BookMsg,
    L2BookSubscription,
    Literal,
    Optional,
    Side,
    TypedDict,
    Union,
    UserEventsMsg,
)


def side_to_int(side: Side) -> int:
    return 1 if side == "A" else -1


def side_to_uint(side: Side) -> int:
    return 1 if side == "A" else 0


class OrderBook:
    def __init__(self, coin: str = "ETH"):
        self.info = Info(skip_ws=False)
        self.coin = coin
        self.book_data = {"bids": [], "asks": [], "time": 0}
        subscription: L2BookSubscription = {"type": "l2Book", "coin": self.coin}
        self.info.subscribe(subscription, self.on_book_update)
        self.poller = threading.Thread(target=self.poll)
        self.poller.start()

    def on_book_update(self, book_msg: L2BookMsg) -> None:
        logging.debug(f"book_msg {book_msg}")
        book_data = book_msg["data"]
        if book_data["coin"] != self.coin:
            print("Unexpected book message, skipping")
            return
        self.book_data = {
            "bids": book_data["levels"][0],
            "asks": book_data["levels"][1],
            "time": book_data["time"],
        }

    def bbo(self):
        try:
            best_bid = self.book_data["bids"][0]
            best_ask = self.book_data["asks"][0]
            return best_bid, best_ask
        except:
            return None, None

    def mid_price(self):
        best_bid, best_ask = self.bbo()
        if best_bid is None or best_ask is None:
            return None
        return (float(best_bid["px"]) + float(best_ask["px"])) / 2

    def poll(self):
        """Polling loop"""
        while True:
            logging.debug("OB polling")
            time.sleep(10)
