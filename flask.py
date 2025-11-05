from flask import Flask, request, jsonify
import requests
import pyodbc
import os

app = Flask(__name__)

# === API Keys ===
OMDB_API_KEY = "35a0d4cf"
BIGBOOK_API_KEY = "dec57ed47cb341449df3b7ab2ce678f2"

# === Database Connection ===
# Adjust with your actual connection string
conn_str = (
    "Driver={SQL Server};"
    "Server=YOUR_SERVER_NAME;"
    "Database=YOUR_DB_NAME;"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    return pyodbc.connect(conn_str)
