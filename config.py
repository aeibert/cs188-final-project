import os
from dotenv import load_dotenv

# Load secrets when running locally
if "WEBSITE_HOSTNAME" not in os.environ:
    load_dotenv(".secret.env")

TMDB_API_KEY = os.environ["TMDB_API_KEY"]
BIGBOOK_API_KEY = os.environ["BIGBOOK_API_KEY"]
CONNECTION_STRING = os.environ["AZURE_SQL_CONNECTIONSTRING"]
