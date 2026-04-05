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
2. Create and activate the virtual environment:
   ```zsh
   python3 -m venv path/to/venv
   source venv/bin/activate
   # or: . venv/bin/activate
   ```

### Running ETL Scripts

All ETL scripts are located in the `ETL/` directory and can be run from the project root.

#### Load Countries

Loads country data from a tab-separated file:

```bash
python3 ETL/load_countries.py ETL/countries.tsv
```

The file should have columns: `country_name` and `country_code`.

#### Load States

Loads state/province data:

```bash
python3 ETL/load_states.py ETL/states.tsv
```

The file should have columns: `country_code`, `code`, and `name` (e.g. `USA` / `NY` / `New York`). If the `country_code` column is omitted from the header, every row is treated as `USA`.

**Note**: If states already exist in the database, the script will raise a duplicate key error. You may need to clear existing states first or modify the script to handle duplicates.

**How dropdowns tie states to countries:** Each state document stores `country_code`. The API `GET /system/dropdown-options?country_code=USA` returns only states whose `country_code` matches (case-insensitive). Clients load countries first, then request states with the selected country’s code.

#### Load Cities

Loads city data from a tab-separated file:

```bash
python3 ETL/load_cities.py ETL/cities.tsv
```

Or with an optional state_code override (applies the same state_code to all cities):

```bash
python3 ETL/load_cities.py ETL/cities.tsv CA
```

The file should have columns: `city_name`, `state_code`, `latitude`, `longitude`, and optional `country_code` (defaults to `USA` when missing or blank). Use `country_code` so the same `state_code` in two countries (e.g. `WA` for Washington state vs Western Australia) does not mix cities in `GET /system/dropdown-options?state_code=…&country_code=…`.

#### Load Users

Loads user data from a tab-separated file:

```bash
python3 ETL/load_users.py ETL/users.tsv
```

The file should have columns: `username`, `password`, `name`, `age`, `bio`, `is_verified`, `email`, `city`, `state`, `country`.

#### Load Listings

Loads marketplace listing data from a tab-separated file:

```bash
python3 ETL/load_listings.py ETL/listings.tsv
```

The file should have columns: `title`, `description`, `transaction_type`, `owner`, `city`, `state`, `country`, and optionally `images`, `price`, `num_likes`, `created_at`. Use `transaction_type` values `free` or `sell` only. The `owner` field should match a username from the users collection (load users first).

## Environment Variables

To use a cloud MongoDB deployment, you need to set environment variables:

1. Edit `local.sh` and fill in your MongoDB credentials:

   - `MONGO_USER`: Your MongoDB username
   - `MONGO_PASSWD`: Your MongoDB password
   - `CLOUD_MONGO`: Set to `1` for cloud MongoDB, `0` for local

2. Run `source local.sh` and try executing a read.

**Important**: Do not push your username and password to GitHub. Only modify it locally.

**TroubleShooting**

If you see a `FormulaUnavailableError: No available formula with the name "formula.jws.json".` error when trying to `brew install mongodb-community`, you can try running `brew reinstall llvm`. I also updated my MacOS and XCode. It should allow you to install mongodb-community after.
