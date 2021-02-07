from dotenv import load_dotenv
from flask import Flask, render_template
import api_helpers.swyftx_helper as swyftx
import api_settings
import json
import os
import requests


app = Flask(__name__)


@app.route('/', methods=['GET'])
def dashboard():

	# Create an access token 
	access_token = swyftx.get_access_token()

	# Retrieve general profile data 
	profile_data = swyftx.get_profile()
	
	market_asset_data = swyftx.get_market_assets()
	# print(market_asset_data)

	user_balance_data = swyftx.get_user_balance()
	# print(user_balance_data)

	# We now need to cross reference the market data with the users balance to get the coin name
	# since balance only provides the fields 'assetId' and 'availableBalance'
	portfolio = swyftx.get_portfolio_balance(market_asset_data, user_balance_data)

	# Next we need to find the current prices of the assets
	return render_template('dashboard.html', profile_data=profile_data, portfolio=portfolio)


if __name__ == '__main__':

	load_dotenv()
	
	app.run(debug=True)


