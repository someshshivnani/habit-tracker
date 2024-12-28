from flask import Flask
from routes import pages
import os,json
from pymongo import MongoClient
from dotenv import load_dotenv



def create_app():
	app=Flask(__name__)
	app.secret_key='SpwEY4cQhH9DwM4bqfX5fOJOyNTR-vgz4DhMxXDe-I4'
	# with open("config.json") as conf:
	# 	params=json.load(conf)["params"]
	load_dotenv()
	db_uri=os.geten("MONGODB_URI")
	# db_conn=params["db_uri"]
	client= MongoClient(db_conn)
	app.db=client.habitrack

	app.register_blueprint(pages)
	app.jinja_env.lstrip_blocks = True
	app.jinja_env.trim_blocks = True
	return app