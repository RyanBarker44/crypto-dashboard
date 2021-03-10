import api_settings
import api_helpers.gecko_helper as gecko
import collections
import json
import multiprocessing
import os
import pprint
import requests
from joblib import delayed, Parallel


pp = pprint.PrettyPrinter(indent=1)
n_jobs = 10


def build_asset_data(asset, market_asset_list, portfolio, gecko_all_coins, semaphore):
	"""Fetch current price and return a dict containing base data for an asset"""

	with semaphore:

		# Format the coin balance as a float
		available_balance = float(asset['availableBalance'])
		available_balance = float("{:.4f}".format(available_balance))

		# Retrieve the matching asset's dict from the entire market data
		asset_data = market_asset_list[asset['assetId']]

		asset_ticker = asset_data['code'].lower()

		# Init the base fields for the asset
		cleaned_asset_data = {
			'balance': available_balance,
			'code': asset_ticker,
			'fiat_value': available_balance,
			'name': asset_data['name'],
			'swyftx_id': asset_data['id'],
		}

		try:
			gecko_coin_data = gecko_all_coins[asset_ticker]

			# Get current price info about the asset 
			current_asset_price = gecko_coin_data["current_price"]

			# Calculate the dollar value of the asset
			fiat_value = available_balance * float(current_asset_price)
			fiat_value = float("{:.2f}".format(fiat_value))

			# Add the fields to the base dict
			cleaned_asset_data['fiat_value'] = fiat_value
			cleaned_asset_data['price'] = current_asset_price

		except KeyError as e:
			# If the ticker symbol is not found we leave the fiat value as the balance.
			# This triggers for fiat currency
			print(f"[*] No matching ticker found for {asset_ticker}")
		
		# Append our new asset dict to the users portfolio
		portfolio['coins'][asset_data['code']] = cleaned_asset_data


def get_access_token():
	"""Retrieve an access token for swyftx given an api key"""

	json_data = {
		'apiKey': os.environ['SWYFTX_API_KEY'],
	}

	headers = {'content-type': 'application/json'}

	req = requests.post(f'{api_settings.BASE_URL}/auth/refresh/', headers=headers, data=json.dumps(json_data))

	decoded_data = json.loads(req.content)

	return decoded_data['accessToken']


def get_asset_info(asset_code):
	request_data = request_wrapper(f"/markets/info/basic/{asset_code}/")

	return request_data


def get_detailed_asset_info(asset_code):
	request_data = request_wrapper(f"/markets/info/detail/{asset_code}/")

	return request_data


def get_market_assets():
	request_data = request_wrapper("/markets/assets/")

	return request_data


def get_portfolio_balance(market_asset_data, user_balance_data):

	# Reformat the market data to have the coin id as the key 
	market_asset_list = {asset['id']: asset for asset in market_asset_data}

	portfolio = {
		'coins': {},
		'total': 0
	}

	with open('api_helpers/gecko_data.txt') as json_file:
		gecko_market_data = json.load(json_file)
	
	if not gecko_market_data:
		raise Exception("Could not load gecko_data.txt")

	# Itterate through the users balances and retrieve the names of the coins using the assetId
	# Process each 'asset' and add to a list of results
	semaphore = multiprocessing.Semaphore(n_jobs)
	Parallel(n_jobs=n_jobs, backend="threading")(
		delayed(build_asset_data)(
			asset, 
			market_asset_list, 
			portfolio, 
			gecko_market_data, 
			semaphore
	) for asset in user_balance_data)

	total = 0
	for coin in portfolio['coins'].values():
		total += float(coin.get('fiat_value', 0))

	portfolio['total'] = total
	portfolio['coins'] = sorted(portfolio['coins'].values(), key=lambda i: i['fiat_value'], reverse=True)

	return portfolio


def get_profile():

	request_data = request_wrapper("/user/")

	response_data = {
		'user_name': request_data['user']['profile']['name'], 
	}

	return response_data


def get_user_balance():
	request_data = request_wrapper("/user/balance/")

	return request_data


def request_wrapper(endpoint_url):

	access_token = get_access_token()

	headers = {
		'content-type': 'application/json',
		'authorization': f"Bearer {access_token}"
	}

	url = f'{api_settings.BASE_URL}{endpoint_url}'
	request_data = requests.get(url, headers=headers)

	return json.loads(request_data.content)
