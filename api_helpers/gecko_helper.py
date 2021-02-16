from pycoingecko import CoinGeckoAPI
import api_settings
import json
import requests

cg = CoinGeckoAPI()
 

base_url = 'https://api.coingecko.com'






 # 
 # 
 # NEXT ILL EITHER WORK OUT HOW TO GET AND STORE THE LINE GRAPH DATA 
 # OR
 # GO FOR THE LOWER HANGING FRUIT OF THE PIE GRAPH
 # 
 # 









def get_current_price(tickers, gecko_all_coins, index=0):
	"""Takes a ticker symbol and returns an object containing all coin data"""

	try:
		coin_data = cg.get_coin_by_id(tickers[index])

		localised_current_price = coin_data["market_data"]["current_price"][api_settings.CURRENCY]

		return float(localised_current_price)

	except Exception as e:
		if index+1 <= len(tickers):
			return get_current_price(tickers, index+1)

	raise


def get_all_coin_data():

	def get_market_page(page_num):

		vs_currency 			= r'aud'
		page_limit 				= r'250'
		order 					= r'market_cap_desc'
		sparkline				= r'false'
		price_change_intervals 	= r'1h%2C%2024h%2C%207d%2C%2014d%2C%2030d%2C%20200d%2C%201y'
		
		url = f'{base_url}/api/v3/coins/markets?vs_currency={vs_currency}&order={order}&per_page={page_limit}&page={page_num}&sparkline={sparkline}&price_change_percentage={price_change_intervals}'
		headers = {'content-type': 'application/json'}

		req = requests.get(url, headers=headers)
		decoded_data = json.loads(req.content)

		return decoded_data

	# NOTE: Doesnt currently fetch all coins on coingecko, I did this because of duplicate tickers.
	# Figured the coins below 2500 probs I aint interested in anyways. 
	page_num = 1 
	max_limit = 10

	decoded_data = get_market_page(page_num)
	response = decoded_data

	while decoded_data:
		decoded_data = get_market_page(page_num)
		page_num += 1

		print(page_num, len(decoded_data))

		response += decoded_data

		if page_num >= max_limit: 
			print(f'[*] EXITED FROM get_market_page LOOP WITH MAX LIMIT {max_limit}')
			break

	print(type(response), len(response))
	return response


def save_data(coin_list):

	formatted_data = format_json_response(coin_list)

	file = 'api_helpers/gecko_data.txt'

	with open(file, 'w') as outfile:
		json.dump(formatted_data, outfile)

	print(f'[*] Saved {len(formatted_data)} to {file}')	


def format_json_response(coin_list):
	# NOTE: Currently does not account for coins with the same symbol 

	coin_dict = {}
	print('Formatting\n')

	for coin in coin_list:

		# Build a unique key
		key = f"{coin['symbol'].lower()}"

		# If its a duplicate key dont replace the old one as the previous should have a higher market cap
		if coin_dict.get(key):
			continue

		coin_dict[key] = coin

	return coin_dict
