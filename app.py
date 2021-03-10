from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
import db.db_helper as db_helper
import db.db_core as db_core
import api_helpers.swyftx_helper as swyftx
import api_settings
import scheduler.background_scheduler as sheduler
import json
import os
import requests
import pandas as pd

# 
# FLASK IS UPDATING EVERYTIME GECKO_DATA.txt: FIX ME!!!!!!!!!!!!
#

# 
# Retrieve the users balance and coin totals
# Store in a db table
# Do this every hour 
# 

# 
# approximately update users balance table, 
# then calculate the correct tick interval seperately, 
# then apply the date to the ticks, 
# assuming it was calculated close enough to the time the tick says to the user
# 


app = Flask(__name__)

load_dotenv()

sheduler.start_scheduler(app)

engine = db_core.init_engine()


@app.route('/', methods=['GET'])
def dashboard():

	user = db_helper.get_user()
	
	balance_history = db_helper.get_balances()

	# Create an access token 
	access_token = swyftx.get_access_token()

	# Retrieve general profile data 
	profile_data = swyftx.get_profile()
	
	market_asset_data = swyftx.get_market_assets()
	user_balance_data = swyftx.get_user_balance()

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

	app.run(debug=True)

