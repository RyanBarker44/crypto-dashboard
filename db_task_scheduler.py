from dotenv import load_dotenv
from flask import Flask
from flask_apscheduler import APScheduler
import api_helpers.gecko_helper as gecko
import db.db_helper as db_helper
import db.db_core as db_core
import pandas as pd
import api_helpers.swyftx_helper as swyftx
import pandas as pd
import time
import os 


app = Flask(__name__)

engine = db_core.init_engine()


if __name__ == '__main__':

	load_dotenv()

	# NOTE: Currently triggers twice due to the Flask debug reloader
	# Initialize scheduler (background scheduler by default)
	scheduler = APScheduler()
	scheduler.api_enabled = True

	# loop through each users balance and add a balance to the db
	@scheduler.task('interval', id='user_balance_update', hours=1, misfire_grace_time=600)
	def user_balance_update():

		# Update the market data before making a new balance entry
		coin_list = gecko.get_market_data()

		if coin_list:
			gecko.save_data(coin_list)

		market_asset_data = swyftx.get_market_assets()
		user_balance_data = swyftx.get_user_balance()

		# We now need to cross reference the market data with the users balance to get the coin name
		# since balance only provides the fields 'assetId' and 'availableBalance'
		portfolio = swyftx.get_portfolio_balance(market_asset_data, user_balance_data)

		row = {'total': portfolio['total'], 'user_id': os.getenv('USER_DB_ID'), 'date_created': time.time()}
		df = pd.DataFrame([row])

		db_helper.insert_user_balance(df)

		print(f'\nAdded entry into user balance table: {row}\n')


	scheduler.init_app(app)
	scheduler.start()

	app.run(port=5001, debug=True)

