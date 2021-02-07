import api_settings
import api_helpers.gecko_helper as gecko
import json
import multiprocessing
import os
import pprint
import requests
from joblib import delayed, Parallel


pp = pprint.PrettyPrinter(indent=1)
n_threads = 10


def build_asset_data(asset, market_asset_list, portfolio, semaphore):
	"""Fetch current price and return a dict containing base data for an asset"""

	with semaphore:

		# Format the coin balance as a float
		available_balance = float(asset['availableBalance'])
		available_balance = float("{:.4f}".format(available_balance))

		# Retrieve the matching asset's dict from the entire market data
		asset_data = market_asset_list[asset['assetId']]

		# Remove spaces from the name to match coin gecko's expectation
		cleaned_coin_name = asset_data['name'].lower().replace(' ', '')

		# Init the base fields for the asset
		cleaned_asset_data = {
			'balance': available_balance,
			'code': asset_data['code'],
			'fiat_value': available_balance,
			'id': asset_data['id'],
			'name': asset_data['name'],
		}

		try:
			# Get current price info about the asset 
			current_asset_price = gecko.get_current_price(cleaned_coin_name)

			# Calculate the dollar value of the asset
			fiat_value = available_balance * float(current_asset_price)
			fiat_value = float("{:.2f}".format(fiat_value))

			# Add the fields to the base dict
			cleaned_asset_data['fiat_value'] = fiat_value
			cleaned_asset_data['price'] = current_asset_price

		except ValueError as e:
			# If the ticker symbol is not found we leave the fiat value as the balance.
			# This triggers for fiat currency
			print(f"[*] No matching ticker found for {cleaned_coin_name}")
		
		# Append our new asset dict to the users portfolio
		portfolio.append(cleaned_asset_data)


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
	

def get_market_assets():
	request_data = request_wrapper("/markets/assets/")

	return request_data


def get_portfolio_balance(market_asset_data, user_balance_data):

	# Reformat the market data to have the coin id as the key 
	market_asset_list = {asset['id']: asset for asset in market_asset_data}

	portfolio = []

	# Itterate through the users balances and retrieve the names of the coins using the assetId
	# Process each 'asset' and add to a list of results
	semaphore = multiprocessing.Semaphore(1)
	Parallel(n_jobs=1, backend="threading")(
		delayed(build_asset_data)(asset, market_asset_list, portfolio, semaphore) for asset in user_balance_data
	)

	portfolio = sorted(portfolio, key=lambda i: i['fiat_value'], reverse=True)

	return portfolio


def get_profile():

	request_data = request_wrapper("/user/")

	user_name = request_data['user']['profile']['name']

	response_data = {
		'user_name': user_name, 
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
