# AXiS - GeoData SWE 2025 Project

## Team Members

- Aisha Roslan ar7805
- Si Yue Jiang sj3834
- XinYan Chen xc2496

## Project Description
Senior Design Project based on geographical database.

[Progress and Goals](ProgressAndGoals.md)

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
   brew tap mongodb/brew
   brew install mongodb-community

3. Start a MongoDB server locally. On macOS with Homebrew (example):

   brew services start mongodb-community

   or run `brew services start mongodb/brew/mongodb-community`

   Or run `mongod` directly if you have a standalone install.

4. Go to `local.sh` and uncomment login and set CLOUD_MONGO=1

5. Run the API server from the repository root:

   PYTHONPATH=$(pwd):$PYTHONPATH
   FLASK_APP=server.endpoints flask run --debug --host=127.0.0.1 --port=8000

6. To stop the mongo serviice:

   brew services stop mongodb-community

7. Go to `local.sh` and comment login and set CLOUD_MONGO=0

If the Flask endpoint cannot reach MongoDB the server will return an error
message indicating the DB is not reachable.

## Loading Data with ETL Scripts

The project includes ETL (Extract, Transform, Load) scripts to populate the database with geographical data.

### Prerequisites

1. Ensure MongoDB is running locally (see steps above)
2. Activate the virtual environment:
   ```zsh
   source venv/bin/activate
   # or: . venv/bin/activate
   ```

### Running ETL Scripts

All ETL scripts are located in the `ETL/` directory and can be run from the project root.

#### Load Countries

Loads country data from a tab-separated CSV file:

```bash
python3 ETL/load_countries.py ETL/countries.csv
```

The CSV file should have columns: `country_name` and `country_code`.

#### Load States

Loads state/province data with latitude and longitude coordinates:

```bash
python3 ETL/load_states_lat_long.py ETL/states_lat_long.csv
```

The CSV file should have columns: `code`, `latitude`, `longitude`, and `name`. The script automatically adds `country_code: 'USA'` to each state.

**Note**: If states already exist in the database, the script will raise a duplicate key error. You may need to clear existing states first or modify the script to handle duplicates.

#### Load Cities

Loads city data from a tab-separated CSV file:

```bash
python3 ETL/load_cities.py ETL/cities.csv
```

Or with an optional state_code override (applies the same state_code to all cities):

```bash
python3 ETL/load_cities.py ETL/cities.csv CA
```

The CSV file should have columns: `city_name` and `state_code`.

## Environment Variables

To use a cloud MongoDB deployment, you need to set environment variables:

1. Edit `local.sh` and fill in your MongoDB credentials:

   - `MONGO_USER`: Your MongoDB username
   - `MONGO_PASSWD`: Your MongoDB password
   - `CLOUD_MONGO`: Set to `1` for cloud MongoDB, `0` for local

2. Run `./local.sh` and try executing a read.

**Important**: Do not push your username and password to GitHub. Only modify it locally.

**TroubleShooting**

If you see a `FormulaUnavailableError: No available formula with the name "formula.jws.json".` error when trying to `brew install mongodb-community`, you can try running `brew reinstall llvm`. I also updated my MacOS and XCode. It should allow you to install mongodb-community after.
