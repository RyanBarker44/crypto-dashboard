import os
import sqlalchemy


def init_engine():

	RDS_USERNAME = os.getenv('RDS_USERNAME')
	RDS_PASSWORD = os.getenv('RDS_PASSWORD')
	RDS_HOSTNAME = os.getenv('RDS_HOSTNAME')
	RDS_DB_NAME = os.getenv('RDS_DB_NAME')
	RDS_PORT = os.getenv('RDS_PORT')

	return sqlalchemy.create_engine(f'mysql://{RDS_USERNAME}:{RDS_PASSWORD}@{RDS_HOSTNAME}:{RDS_PORT}/{RDS_DB_NAME}')