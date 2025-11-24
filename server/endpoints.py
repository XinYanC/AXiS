"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

import cities.queries as cityqry
import countries.queries as countryqry
import states.queries as stateqry
from flask import Flask
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
    Get all cities from the database.
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


# ==================== COUNTRIES ENDPOINTS ====================

@api.route(f'{COUNTRIES_EPS}/{READ}')
class CountriesRead(Resource):
    """
    Get all countries from the database.
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


# ==================== STATES ENDPOINTS ====================

@api.route(f'{STATES_EPS}/{READ}')
class StatesRead(Resource):
    """
    Get all states from the database.
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
