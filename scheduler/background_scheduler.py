from flask_apscheduler import APScheduler
import api_helpers.gecko_helper as gecko

# NOTE: Currently triggers twice due to the Flask debug reloader
# Initialize scheduler (background scheduler by default)

def start_scheduler(app):
	scheduler = APScheduler()
	scheduler.api_enabled = True
	scheduler.init_app(app)
	scheduler.start()

	# Interval example
	@scheduler.task('interval', id='job_gecko_coin_list', seconds=300, misfire_grace_time=600)
	def job_gecko_coin_list():
		coin_list = gecko.get_market_data()

		if coin_list:
			gecko.save_data(coin_list)

		print(f'\nGecko coin list background update executed with: #{len(coin_list)} coins.\n')
