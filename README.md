# AXiS - GeoData SWE 2025 Project

## Team Members

- Aisha Roslan ar7805
- Si Yue Jiang sj3834
- XinYan Chen xc2496

## Project Description

Senior Design Project based on geographical database.

## Potential App Features/Goals

- Vacation Destination/Planning
- Market Analysis
- Transportation
- Real Estate
- Town/City/Country Population
- ... still brainstorming

## flask-api

An example flask rest API server.

To build production, type `make prod`.

To create the env for a new developer, run `make dev_env`.

## Running the API with a local MongoDB

This project can connect to a MongoDB instance locally. The code will default to
connecting to `mongodb://localhost:27017` when no cloud configuration is set.

Quick steps to run locally:

1. Activate the virtualenv if needed:

   ```zsh
   source .venv/bin/activate
   # or: . .venv/bin/activate
   ```

2. Install dependencies:

   pip install -r requirements.txt

3. Start a MongoDB server locally. On macOS with Homebrew (example):

   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb-community

   Or run `mongod` directly if you have a standalone install.

4. Run the API server from the repository root:

   python -m server.run

If the Flask endpoint cannot reach MongoDB the server will return an error
message indicating the DB is not reachable. To use a cloud MongoDB deployment
set the `CLOUD_MONGO=1` environment variable and the `MONGO_PASSWD` environment
variable as required by the cloud connection code.
