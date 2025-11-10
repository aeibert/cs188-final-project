from flask import Flask, request, jsonify
import requests
import pyodbc
import os
from dotenv import load_dotenv

if "WEBSITE_HOSTNAME" not in os.environ:
    # Development
    load_dotenv(".secret.env")


# We now load the connection string from the environment variable.
CONNECTION_STRING = os.environ["AZURE_SQL_CONNECTIONSTRING"]

# === API Keys ===
TMDB_API_KEY = os.environ["TMDB_API_KEY"]
BIGBOOK_API_KEY = os.environ["BIGBOOK_API_KEY"]

app = Flask(__name__)

def get_db_connection():
    connection = pyodbc.connect(CONNECTION_STRING)
    return connection
