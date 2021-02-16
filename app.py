from flask_apscheduler import APScheduler
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
import api_helpers.swyftx_helper as swyftx
import api_helpers.gecko_helper as gecko
import api_settings
import json
import os
import requests
import api_helpers.gecko_helper as gecko


app = Flask(__name__)


# NOTE: Currently triggers twice due to the Flask debug reloader
# Initialize scheduler (background scheduler by default)
scheduler = APScheduler()
scheduler.api_enabled = True

# Interval example
@scheduler.task('interval', id='job_gecko_coin_list', seconds=300, misfire_grace_time=600)
def job_gecko_coin_list():
	coin_list = gecko.get_all_coin_data()

	if coin_list:
		gecko.save_data(coin_list)

	print(f'\nGecko coin list background update executed with: #{len(coin_list)} coins.\n')


scheduler.init_app(app)
scheduler.start()


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


@app.route('/getPieData', methods=['GET'])
def get_pie_data():

	market_asset_data = swyftx.get_market_assets()
	user_balance_data = swyftx.get_user_balance()
	portfolio = swyftx.get_portfolio_balance(market_asset_data, user_balance_data)

	return jsonify(portfolio)


if __name__ == '__main__':

	load_dotenv()
	
	app.run(debug=True)


