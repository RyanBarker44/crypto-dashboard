from pycoingecko import CoinGeckoAPI
import api_settings
import requests


cg = CoinGeckoAPI()


def get_current_price(ticker):

	coin_data = cg.get_coin_by_id(ticker)

	localised_current_price = coin_data["market_data"]["current_price"][api_settings.CURRENCY]

	return float(localised_current_price)