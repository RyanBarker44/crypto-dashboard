import os
import pandas as pd
from app import engine

# https://hackersandslackers.com/connecting-pandas-to-a-sql-database-with-sqlalchemy/

# Coinspot graph data fetching
# $.getJSON('/my/charts/portfolio?timeframe='+'D')
#     .done(function(data) {
#       pfdata['D'] = createGraphData(data);
#         console.log("pfdata:", pfdata['D'])
#       renderPfChart(pfdata['D']);
#         console.log('renferpf: ', renderPfChart(pfdata['D']))
#     })

# $.getJSON('/my/charts/portfolio?timeframe='+'D')
#     .done(function(data) {
#       pfdata['D'] = createGraphData(data);
#       renderPfChart(pfdata['D']);
#     })

def get_user():

	sql_df = pd.read_sql_query(
	    f"SELECT * FROM User WHERE id = {os.environ['USER_DB_ID']}",
	    con=engine,
	    parse_dates=[
	        'date_created',
	    ]
	)

	return sql_df


def get_balances():

	sql_df = pd.read_sql_query(
	    f"SELECT * FROM User_Balance WHERE user_id = {os.environ['USER_DB_ID']}",
	    con=engine,
	    parse_dates=[
	        'date_created',
	    ]
	)
	
	return sql_df


def insert_user_balance(df):

	if not isinstance(df, pd.DataFrame):
		raise Exception(f'Incorrect data type in insert attempt, type {type(df)} when it should be <pandas.DataFrame>')

	df.to_sql('User_Balance', engine, if_exists='append', index=False)
	print(f'Inserted {df} into User_Balance')

	# sql_df = pd.read_sql_query(
	#     f"INSERT INTO User_Balance(user_id, total) VALUES({os.environ['USER_DB_ID']}, {balance})",
	#     con=engine
	# )

	
	# return sql_df
