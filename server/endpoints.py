"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

import cities.queries as cityqry
import countries.queries as countryqry
import states.queries as stateqry
from flask import Flask, request
from flask_restx import Resource, Api  # , fields  # Namespace
from flask_cors import CORS

# import werkzeug.exceptions as wz

app = Flask(__name__)
CORS(app)
api = Api(app)

ERROR = 'Error'
MESSAGE = 'Message'
NUM_RECS = 'Number of Records'
SUCCESS = 'Success'
ID = 'id'
READ = 'read'
CREATE = 'create'
DELETE = 'delete'
SEARCH = 'search'
COUNT = 'count'

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'

HELLO_EP = '/hello'
HELLO_RESP = 'hello'

CITIES_EPS = '/cities'
CITY_RESP = 'Cities'

COUNTRIES_EPS = '/countries'
COUNTRY_RESP = 'Countries'

STATES_EPS = '/states'
STATE_RESP = 'States'


# ==================== CITIES ENDPOINTS ====================

@api.route(f'{CITIES_EPS}/{READ}')
class CitiesRead(Resource):
    """
    Interact with cities collection
    """
    def get(self):
        """
        Returns all cities in the database.
        """
        try:
            cities = cityqry.read()
            num_recs = len(cities)
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500
        return {
            CITY_RESP: cities,
            NUM_RECS: num_recs,
        }


@api.route(f'{CITIES_EPS}/{SEARCH}')
class CitiesSearch(Resource):
    """
    Search cities by name
    """
    def get(self):
        """
        Search for cities by name (case-insensitive partial match).
        Query param: 'q' (search term)
        """
        try:
            search_term = request.args.get('q')
            if not search_term:
                return {ERROR: 'Query parameter "q" is required'}, 400
            cities = cityqry.search_cities_by_name(search_term)
            num_recs = len(cities)
            return {
                CITY_RESP: cities,
                NUM_RECS: num_recs,
                'search_term': search_term,
            }
        except ValueError as e:
            return {ERROR: str(e)}, 400
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


@api.route(f'{CITIES_EPS}/{COUNT}')
class CitiesCount(Resource):
    """
    Get count of cities
    """
    def get(self):
        """
        Returns the total number of cities in the database.
        """
        try:
            count = cityqry.num_cities()
            return {
                'count': count,
                CITY_RESP: f'Total cities: {count}',
            }
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


@api.route(f'{CITIES_EPS}/{CREATE}')
class CitiesCreate(Resource):
    """
    Create a new city
    """
    def post(self):
        """
        Create a new city.
        Required JSON body: {"name": "CityName", "state_code": "XX"}
        """
        try:
            city_data = request.json
            if not city_data:
                return {ERROR: 'Request body must contain JSON data'}, 400
            # Store original data before create modifies it
            original_data = dict(city_data)
            rec_id = cityqry.create(city_data)
            return {
                MESSAGE: 'City created successfully',
                'id': str(rec_id),
                'city': original_data,
            }, 201
        except ValueError as e:
            return {ERROR: str(e)}, 400
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


@api.route(f'{CITIES_EPS}/{DELETE}')
class CitiesDelete(Resource):
    """
    Delete a city
    """
    def delete(self):
        """
        Delete a city by name and state_code.
        Query params: 'name' and 'state_code'
        """
        try:
            name = request.args.get('name')
            state_code = request.args.get('state_code')
            if not name or not state_code:
                return {
                    ERROR: 'Query parameters "name" and '
                           '"state_code" are required'
                }, 400
            cityqry.delete(name, state_code)
            return {
                MESSAGE: f'City "{name}, {state_code}" deleted successfully',
            }
        except ValueError as e:
            return {ERROR: str(e)}, 404
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


# ==================== COUNTRIES ENDPOINTS ====================

@api.route(f'{COUNTRIES_EPS}/{READ}')
class CountriesRead(Resource):
    """
    Interact with countries collection
    """
    def get(self):
        """
        Returns all countries in the database.
        """
        try:
            countries = countryqry.read()
            num_recs = len(countries)
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500
        return {
            COUNTRY_RESP: countries,
            NUM_RECS: num_recs,
        }


@api.route(f'{COUNTRIES_EPS}/{SEARCH}')
class CountriesSearch(Resource):
    """
    Search countries by name
    """
    def get(self):
        """
        Search for countries by name (case-insensitive partial match).
        Query param: 'q' (search term)
        """
        try:
            search_term = request.args.get('q')
            if not search_term:
                return {ERROR: 'Query parameter "q" is required'}, 400
            countries = countryqry.search_countries_by_name(search_term)
            num_recs = len(countries)
            return {
                COUNTRY_RESP: countries,
                NUM_RECS: num_recs,
                'search_term': search_term,
            }
        except ValueError as e:
            return {ERROR: str(e)}, 400
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


@api.route(f'{COUNTRIES_EPS}/{COUNT}')
class CountriesCount(Resource):
    """
    Get count of countries
    """
    def get(self):
        """
        Returns the total number of countries in the database.
        """
        try:
            count = countryqry.num_countries()
            return {
                'count': count,
                COUNTRY_RESP: f'Total countries: {count}',
            }
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


@api.route(f'{COUNTRIES_EPS}/{CREATE}')
class CountriesCreate(Resource):
    """
    Create a new country
    """
    def post(self):
        """
        Create a new country.
        Required JSON body: {"name": "CountryName", "code": "XX"}
        """
        try:
            country_data = request.json
            if not country_data:
                return {ERROR: 'Request body must contain JSON data'}, 400
            # Store original data before create modifies it
            original_data = dict(country_data)
            rec_id = countryqry.create(country_data)
            return {
                MESSAGE: 'Country created successfully',
                'id': str(rec_id),
                'country': original_data,
            }, 201
        except ValueError as e:
            return {ERROR: str(e)}, 400
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


@api.route(f'{COUNTRIES_EPS}/{DELETE}')
class CountriesDelete(Resource):
    """
    Delete a country
    """
    def delete(self):
        """
        Delete a country by name and code.
        Query params: 'name' and 'code'
        """
        try:
            name = request.args.get('name')
            code = request.args.get('code')
            if not name or not code:
                return {
                    ERROR: 'Query parameters "name" and "code" are required'
                }, 400
            countryqry.delete(name, code)
            return {
                MESSAGE: f'Country "{name}, {code}" deleted successfully',
            }
        except ValueError as e:
            return {ERROR: str(e)}, 404
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


# ==================== STATES ENDPOINTS ====================

@api.route(f'{STATES_EPS}/{READ}')
class StatesRead(Resource):
    """
    Interact with states collection
    """
    def get(self):
        """
        Returns all states in the database.
        """
        try:
            states = stateqry.read()
            num_recs = len(states)
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500
        return {
            STATE_RESP: states,
            NUM_RECS: num_recs,
        }


@api.route(f'{STATES_EPS}/{SEARCH}')
class StatesSearch(Resource):
    """
    Search states by name
    """
    def get(self):
        """
        Search for states by name (case-insensitive partial match).
        Query param: 'q' (search term)
        """
        try:
            search_term = request.args.get('q')
            if not search_term:
                return {ERROR: 'Query parameter "q" is required'}, 400
            states = stateqry.search_states_by_name(search_term)
            num_recs = len(states)
            return {
                STATE_RESP: states,
                NUM_RECS: num_recs,
                'search_term': search_term,
            }
        except ValueError as e:
            return {ERROR: str(e)}, 400
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


@api.route(f'{STATES_EPS}/{COUNT}')
class StatesCount(Resource):
    """
    Get count of states
    """
    def get(self):
        """
        Returns the total number of states in the database.
        """
        try:
            count = stateqry.num_states()
            return {
                'count': count,
                STATE_RESP: f'Total states: {count}',
            }
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


@api.route(f'{STATES_EPS}/{CREATE}')
class StatesCreate(Resource):
    """
    Create a new state
    """
    def post(self):
        """
        Create a new state.
        Required JSON body:
        {"name": "StateName", "code": "XX", "country_code": "YYY"}
        """
        try:
            state_data = request.json
            if not state_data:
                return {ERROR: 'Request body must contain JSON data'}, 400
            # Store original data before create modifies it
            original_data = dict(state_data)
            rec_id = stateqry.create(state_data)
            return {
                MESSAGE: 'State created successfully',
                'id': str(rec_id),
                'state': original_data,
            }, 201
        except ValueError as e:
            return {ERROR: str(e)}, 400
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


@api.route(f'{STATES_EPS}/{DELETE}')
class StatesDelete(Resource):
    """
    Delete a state
    """
    def delete(self):
        """
        Delete a state by code and country_code.
        Query params: 'code' and 'country_code'
        """
        try:
            code = request.args.get('code')
            country_code = request.args.get('country_code')
            if not code or not country_code:
                return {
                    ERROR: 'Query parameters "code" and '
                           '"country_code" are required'
                }, 400
            stateqry.delete(code, country_code)
            return {
                MESSAGE: f'State "{code}, {country_code}" deleted '
                         f'successfully',
            }
        except ValueError as e:
            return {ERROR: str(e)}, 404
        except ConnectionError as e:
            return {ERROR: str(e)}, 500
        except Exception as e:
            return {ERROR: str(e)}, 500


# ==================== UTILITY ENDPOINTS ====================

@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}
