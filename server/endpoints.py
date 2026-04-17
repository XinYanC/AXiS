"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

import os
import secrets
import cities.queries as cityqry
import countries.queries as countryqry
import data.cloudinary_connect as cloudinarycon
import listings.queries as listingqry
import states.queries as stateqry
import users.queries as userqry
from functools import wraps
from server import dropdown_form
from flask import Flask, request
from flask_restx import Resource, Api, fields  # Namespace
from flask_cors import CORS
from werkzeug.datastructures import FileStorage


app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
api = Api(app)


def handle_endpoint_errors(value_error_status=400):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except ValueError as e:
                return {ERROR: str(e)}, value_error_status
            except ConnectionError as e:
                return {ERROR: str(e)}, 500
            except Exception as e:
                return {ERROR: str(e)}, 500
        return wrapper
    return decorator


ERROR = 'Error'
MESSAGE = 'Message'
NUM_RECS = 'Number of Records'
SUCCESS = 'Success'
ID = 'id'
READ = 'read'
CREATE = 'create'
DELETE = 'delete'
UPDATE = 'update'
SEARCH = 'search'
COUNT = 'count'
BY_USER = 'by-user'
UPLOAD_IMAGE = 'upload-image'

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

USERS_EPS = '/users'
USER_RESP = 'User'

LISTINGS_EPS = '/listings'
LISTING_RESP = 'Listings'

SYSTEM_EPS = '/system'
SYSTEM_DROPDOWN_FORM = 'dropdown-form'
SYSTEM_DROPDOWN_OPTIONS = 'dropdown-options'

AUTH_LOGIN_EP = '/auth/login'

# Dev-only: tail or list files under the PA log root (default /var/log).
DEV_LOGS_EP = '/dev/logs'
DEV_LOG_TOKEN_ENV = 'AXIS_DEV_LOG_TOKEN'
DEV_LOG_ROOT_ENV = 'AXIS_DEV_LOG_ROOT'
DEV_LOG_TOKEN_HEADER = 'X-AXIS-Dev-Log-Token'
_DEV_LOG_MAX_TAIL_LINES = 5000
_DEV_LOG_MAX_TAIL_SCAN_BYTES = 10 * 1024 * 1024
_DEV_LOG_MAX_DIR_ENTRIES = 500

# ==================== SWAGGER MODELS ====================

city_model = api.model('City', {
    'name': fields.String(required=True, description='City name'),
    'state_code': fields.String(
        required=True,
        description='State code (e.g., "NY", "CA")'
    ),
    'latitude': fields.Float(
        required=True,
        description='Latitude (decimal degrees, WGS84)',
    ),
    'longitude': fields.Float(
        required=True,
        description='Longitude (decimal degrees, WGS84)',
    ),
    'country_code': fields.String(
        required=False,
        description='ISO-style country code (e.g. USA, CAN); defaults to USA',
    ),
})

country_model = api.model('Country', {
    'name': fields.String(required=True, description='Country name'),
    'code': fields.String(
        required=True,
        description='Country code (e.g., "USA", "FRA")'
    )
})

state_model = api.model('State', {
    'name': fields.String(required=True, description='State name'),
    'code': fields.String(
        required=True,
        description='State code (e.g., "NY", "CA")'
    ),
    'country_code': fields.String(
        required=True,
        description='Country code (e.g., "USA")'
    )
})

user_model = api.model('User', {
    'username': fields.String(
        required=True, description='Username (unique)'
    ),
    'password': fields.String(
        required=True, description='Password (will be hashed)'
    ),
    'name': fields.String(required=True, description='User full name'),
    'age': fields.Integer(required=False, description='User age'),
    'bio': fields.String(required=False, description='User biography'),
    'is_verified': fields.Boolean(
        required=False, description='Verification status'
    ),
    'email': fields.String(
        required=True, description='Email (must end in .edu)'
    ),
    'city': fields.String(
        required=True, description='City (e.g. from location dropdown value)'
    ),
    'state': fields.String(
        required=True, description='State or region code'
    ),
    'country': fields.String(
        required=True, description='Country code (e.g. USA)'
    ),
    'created_at': fields.String(
        required=False,
        readonly=True,
        description='Server-generated UTC timestamp (ISO-8601)'
    ),
    'saved_listings': fields.List(
        fields.String,
        description='List of listing IDs the user has liked/saved',
        default=[]
    ),
})

listing_model = api.model('Listing', {
    'title': fields.String(
        required=True, description='Listing title'
    ),
    'description': fields.String(
        required=True, description='Listing description'
    ),
    'images': fields.List(
        fields.String,
        description='Image URLs (optional)',
        default=[]
    ),
    'transaction_type': fields.String(
        required=True,
        description='One of: free, sell'
    ),
    'owner': fields.String(
        required=True,
        description='Owner identifier (e.g. email)'
    ),
    'city': fields.String(
        required=True,
        description='Listing city (dropdown value)'
    ),
    'state': fields.String(
        required=True,
        description='State or region code'
    ),
    'country': fields.String(
        required=True,
        description='Country code'
    ),
    'price': fields.Float(description='Price (optional)', default=None),
    'num_likes': fields.Integer(
        description='Number of likes (optional, default 0)',
        default=0
    ),
    'status': fields.String(
        required=False,
        description='Listing status (e.g., "available", "sold")'
    ),
})

login_model = api.model('Login', {
    'email': fields.String(
        required=True, description='User email (.edu)'
    ),
    'password': fields.String(
        required=True, description='Password'
    ),
})

upload_image_parser = api.parser()
upload_image_parser.add_argument(
    'image',
    location='files',
    type=FileStorage,
    required=True,
    help='Image file to upload',
)


# ==================== CITIES ENDPOINTS ====================

@api.route(f'{CITIES_EPS}/{READ}')
class CitiesRead(Resource):
    """
    Interact with cities collection
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns all cities in the database.
        """
        cities = cityqry.read()
        num_recs = len(cities)
        return {
            CITY_RESP: cities,
            NUM_RECS: num_recs,
        }


@api.route(f'{CITIES_EPS}/{COUNT}')
class CitiesCount(Resource):
    """
    Get count of cities
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns the total number of cities in the database.
        """
        count = cityqry.num_cities()
        return {
            'count': count,
            CITY_RESP: f'Total cities: {count}',
        }


@api.route(f'{CITIES_EPS}/{SEARCH}')
class CitiesSearch(Resource):
    """
    Search cities by name
    """
    @api.param('q', 'Search term (case-insensitive)', required=True)
    @handle_endpoint_errors()
    def get(self):
        """
        Search for cities by name (case-insensitive partial match).
        Query param: 'q' (search term)
        """
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


@api.route(f'{CITIES_EPS}/{CREATE}')
class CitiesCreate(Resource):
    """
    Create a new city
    """
    @api.expect(city_model)
    @handle_endpoint_errors()
    def post(self):
        """
        Create a new city.
        Required JSON body: name, state_code, latitude, longitude
        """
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


@api.route(f'{CITIES_EPS}/{DELETE}')
class CitiesDelete(Resource):
    """
    Delete a city
    """
    @api.param('name', 'City name', required=True)
    @api.param('state_code', 'State code (e.g., "NY", "CA")', required=True)
    @handle_endpoint_errors(404)
    def delete(self):
        """
        Delete a city by name and state_code.
        Query params: 'name' and 'state_code'
        """
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


# ==================== COUNTRIES ENDPOINTS ====================

@api.route(f'{COUNTRIES_EPS}/{READ}')
class CountriesRead(Resource):
    """
    Interact with countries collection
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns all countries in the database.
        """
        countries = countryqry.read()
        num_recs = len(countries)
        return {
            COUNTRY_RESP: countries,
            NUM_RECS: num_recs,
        }


@api.route(f'{COUNTRIES_EPS}/{COUNT}')
class CountriesCount(Resource):
    """
    Get count of countries
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns the total number of countries in the database.
        """
        count = countryqry.num_countries()
        return {
            'count': count,
            COUNTRY_RESP: f'Total countries: {count}',
        }


@api.route(f'{COUNTRIES_EPS}/{SEARCH}')
class CountriesSearch(Resource):
    """
    Search countries by name
    """
    @api.param('q', 'Search term (case-insensitive)', required=True)
    @handle_endpoint_errors()
    def get(self):
        """
        Search for countries by name (case-insensitive partial match).
        Query param: 'q' (search term)
        """
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


@api.route(f'{COUNTRIES_EPS}/{CREATE}')
class CountriesCreate(Resource):
    """
    Create a new country
    """
    @api.expect(country_model)
    @handle_endpoint_errors()
    def post(self):
        """
        Create a new country.
        Required JSON body: {"name": "CountryName", "code": "XX"}
        """
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


@api.route(f'{COUNTRIES_EPS}/{DELETE}')
class CountriesDelete(Resource):
    """
    Delete a country
    """
    @api.param('name', 'Country name', required=True)
    @api.param('code', 'Country code (e.g., "USA", "FRA")', required=True)
    @handle_endpoint_errors(404)
    def delete(self):
        """
        Delete a country by name and code.
        Query params: 'name' and 'code'
        """
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


# ==================== STATES ENDPOINTS ====================

@api.route(f'{STATES_EPS}/{READ}')
class StatesRead(Resource):
    """
    Interact with states collection
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns all states in the database.
        """
        states = stateqry.read()
        num_recs = len(states)
        return {
            STATE_RESP: states,
            NUM_RECS: num_recs,
        }


@api.route(f'{STATES_EPS}/{COUNT}')
class StatesCount(Resource):
    """
    Get count of states
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns the total number of states in the database.
        """
        count = stateqry.num_states()
        return {
            'count': count,
            STATE_RESP: f'Total states: {count}',
        }


@api.route(f'{STATES_EPS}/{SEARCH}')
class StatesSearch(Resource):
    """
    Search states by name
    """
    @api.param('q', 'Search term (case-insensitive)', required=True)
    @handle_endpoint_errors()
    def get(self):
        """
        Search for states by name (case-insensitive partial match).
        Query param: 'q' (search term)
        """
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


@api.route(f'{STATES_EPS}/{CREATE}')
class StatesCreate(Resource):
    """
    Create a new state
    """
    @api.expect(state_model)
    @handle_endpoint_errors()
    def post(self):
        """
        Create a new state.
        Required JSON body:
        {"name": "StateName", "code": "XX", "country_code": "YYY"}
        """
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


@api.route(f'{STATES_EPS}/{DELETE}')
class StatesDelete(Resource):
    """
    Delete a state
    """
    @api.param('code', 'State code (e.g., "NY", "CA")', required=True)
    @api.param('country_code', 'Country code (e.g., "USA")', required=True)
    @handle_endpoint_errors(404)
    def delete(self):
        """
        Delete a state by code and country_code.
        Query params: 'code' and 'country_code'
        """
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


# ==================== USERS ENDPOINTS ====================

@api.route(f'{USERS_EPS}/{READ}')
class UsersRead(Resource):
    """
    Interact with users collection
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns all users in the database.
        """
        users = userqry.read()
        num_recs = len(users)
        return {
            USER_RESP: users,
            NUM_RECS: num_recs,
        }


@api.route(f'{USERS_EPS}/{COUNT}')
class UsersCount(Resource):
    """
    Get count of users
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns the total number of users in the database.
        """
        count = userqry.num_users()
        return {
            'count': count,
            USER_RESP: f'Total users: {count}',
        }


@api.route(f'{USERS_EPS}/{SEARCH}')
class UsersSearch(Resource):
    """
    Search users by name or username
    """
    @api.param('q', 'Search term (case-insensitive)', required=True)
    @handle_endpoint_errors()
    def get(self):
        """
        Search for users by name or username (case-insensitive partial match).
        Query param: 'q' (search term)
        """
        search_term = request.args.get('q')
        if not search_term:
            return {ERROR: 'Query parameter "q" is required'}, 400
        users = userqry.search_users_by_name(search_term)
        num_recs = len(users)
        return {
            USER_RESP: users,
            NUM_RECS: num_recs,
            'search_term': search_term,
        }


@api.route(f'{USERS_EPS}/{CREATE}')
class UsersCreate(Resource):
    """
    Create a new user
    """
    @api.expect(user_model)
    @handle_endpoint_errors()
    def post(self):
        """
        Create a new user.
        Required JSON body: {
            "username": "johndoe",
            "password": "password123",
            "name": "John Doe",
            "email": "johndoe@example.edu",
            "age": 25,
            "bio": "User bio",
            "is_verified": false,
            "city": "New York",
            "state": "NY",
            "country": "USA"
        }
        Note: password will be hashed, email must end in .edu.
        Note: created_at is generated by the server; do not send it.
        """
        user_data = request.json
        if not user_data:
            return {ERROR: 'Request body must contain JSON data'}, 400
        # Store original data before create modifies it
        original_data = dict(user_data)
        # Don't return password in response
        if 'password' in original_data:
            original_data['password'] = '[REDACTED]'
        rec_id = userqry.create(user_data)
        return {
            MESSAGE: 'User created successfully',
            'id': str(rec_id),
            'user': original_data,
        }, 201


@api.route(f'{USERS_EPS}/{UPDATE}')
class UsersUpdate(Resource):
    """
    Update a user
    """
    @api.param('username', 'Username or MongoDB ObjectId', required=True)
    @api.expect(user_model)
    @handle_endpoint_errors()
    def put(self):
        """
        Update a user by username or ObjectId.
        Query param: 'username'. Body: any subset of name, age, bio,
        is_verified, city, state, country, saved_listings,
        password (hashed).
        """
        username_or_id = request.args.get('username')
        if not username_or_id:
            return {
                ERROR: 'Query parameter "username" is required'
            }, 400
        body = request.json
        if not body:
            return {ERROR: 'Request body must contain JSON data'}, 400
        updated = userqry.update(username_or_id, body)
        return {USER_RESP: updated, MESSAGE: 'User updated successfully'}


@api.route(f'{USERS_EPS}/{DELETE}')
class UsersDelete(Resource):
    """
    Delete a user
    """
    @api.param('username', 'Username or MongoDB ObjectId', required=True)
    @handle_endpoint_errors(404)
    def delete(self):
        """
        Delete a user by username or MongoDB ObjectId.
        Query param: 'username' (username string or ObjectId)
        """
        username_or_id = request.args.get('username')
        if not username_or_id:
            return {
                ERROR: 'Query parameter "username" is required'
            }, 400
        userqry.delete(username_or_id)
        return {
            MESSAGE: f'User "{username_or_id}" deleted successfully',
        }


# ==================== LISTINGS ENDPOINTS ====================

@api.route(f'{LISTINGS_EPS}/{READ}')
class ListingsRead(Resource):
    """
    Interact with listings collection
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns all listings in the database.
        """
        listings = listingqry.read()
        num_recs = len(listings)
        return {
            LISTING_RESP: listings,
            NUM_RECS: num_recs,
        }


@api.route(f'{LISTINGS_EPS}/{COUNT}')
class ListingsCount(Resource):
    """
    Get count of listings
    """
    @handle_endpoint_errors()
    def get(self):
        """
        Returns the total number of listings in the database.
        """
        count = listingqry.num_listings()
        return {
            'count': count,
            LISTING_RESP: f'Total listings: {count}',
        }


@api.route(f'{LISTINGS_EPS}/{SEARCH}')
class ListingsSearch(Resource):
    """
    Search listings by title
    """
    @api.param('q', 'Search term (case-insensitive)', required=True)
    @handle_endpoint_errors()
    def get(self):
        """
        Search for listings by title (case-insensitive partial match).
        Query param: 'q' (search term)
        """
        search_term = request.args.get('q')
        if not search_term:
            return {ERROR: 'Query parameter "q" is required'}, 400
        listings = listingqry.search_listings_by_title(search_term)
        num_recs = len(listings)
        return {
            LISTING_RESP: listings,
            NUM_RECS: num_recs,
            'search_term': search_term,
        }


@api.route(f'{LISTINGS_EPS}/{BY_USER}')
class ListingsByUser(Resource):
    """
    Get listings by owner username
    """
    @api.param('username', 'Listing owner username', required=True)
    @handle_endpoint_errors()
    def get(self):
        """
        Return all listings for a given owner username.
        Query param: 'username'
        """
        username = request.args.get('username')
        if not username:
            return {ERROR: 'Query parameter "username" is required'}, 400
        listings = listingqry.search_listings_by_owner(username)
        num_recs = len(listings)
        return {
            LISTING_RESP: listings,
            NUM_RECS: num_recs,
            'username': username,
        }


@api.route(f'{LISTINGS_EPS}/{UPLOAD_IMAGE}')
class ListingsUploadImage(Resource):
    """
    Upload an image for a listing to Cloudinary.
    """
    @api.expect(upload_image_parser)
    @api.doc(consumes=['multipart/form-data'])
    @handle_endpoint_errors()
    def post(self):
        """
        Upload a single image file to Cloudinary and receive its URL.
        Send as multipart/form-data with a field named 'image'.
        Returns the Cloudinary HTTPS URL to include in the listing's
        'images' array when calling POST /listings/create.
        """
        if 'image' not in request.files:
            return {ERROR: 'No image file provided (field: "image")'}, 400
        file = request.files['image']
        if file.filename == '':
            return {ERROR: 'No image file selected'}, 400
        url = cloudinarycon.upload_image(file)
        return {'url': url}, 200


@api.route(f'{LISTINGS_EPS}/{CREATE}')
class ListingsCreate(Resource):
    """
    Create a new listing
    """
    @api.expect(listing_model)
    @handle_endpoint_errors()
    def post(self):
        """
        Create a new listing.
        Required JSON body: title, description, transaction_type, owner,
        city, state, country. Optional: images (list), price (number).
        """
        listing_data = request.json
        if not listing_data:
            return {ERROR: 'Request body must contain JSON data'}, 400
        original_data = dict(listing_data)
        rec_id = listingqry.create(listing_data)
        return {
            MESSAGE: 'Listing created successfully',
            'id': str(rec_id),
            'listing': original_data,
        }, 201


@api.route(f'{LISTINGS_EPS}/{UPDATE}')
class ListingsUpdate(Resource):
    """
    Update a listing
    """
    @api.param('id', 'Listing MongoDB _id', required=True)
    @api.expect(listing_model)
    @handle_endpoint_errors()
    def put(self):
        """
        Update a listing by its ID.
        Query param: 'id'. Body: any subset of title, description,
        transaction_type, city, state, country, price, num_likes.
        """
        listing_id = request.args.get('id')
        if not listing_id:
            return {ERROR: 'Query parameter "id" is required'}, 400
        body = request.json
        if not body:
            return {ERROR: 'Request body must contain JSON data'}, 400
        updated = listingqry.update(listing_id, body)
        return {
            LISTING_RESP: updated,
            MESSAGE: 'Listing updated successfully',
        }


@api.route(f'{LISTINGS_EPS}/{DELETE}')
class ListingsDelete(Resource):
    """
    Delete a listing
    """
    @api.param('id', 'Listing MongoDB _id', required=True)
    @handle_endpoint_errors(404)
    def delete(self):
        """
        Delete a listing by its ID.
        Query param: 'id' (MongoDB _id)
        """
        listing_id = request.args.get('id')
        if not listing_id:
            return {ERROR: 'Query parameter "id" is required'}, 400
        listingqry.delete(listing_id)
        return {
            MESSAGE: f'Listing "{listing_id}" deleted successfully',
        }


# ==================== AUTH ENDPOINTS ====================

@api.route(AUTH_LOGIN_EP)
class AuthLogin(Resource):
    """
    Authenticate user by email and password.
    """
    @api.expect(login_model)
    @handle_endpoint_errors()
    def post(self):
        """
        Login with email and password.
        Request body: {"email": "user@example.edu", "password": "plaintext"}
        Returns user object (without password) on success, 401 on failure.
        """
        data = request.json
        if not data:
            return {ERROR: 'Request body must contain JSON'}, 400
        email = data.get('email')
        password = data.get('password')
        if not email:
            return {ERROR: 'Email is required'}, 400
        if not password:
            return {ERROR: 'Password is required'}, 400
        user = userqry.authenticate(email, password)
        if not user:
            return {ERROR: 'Invalid email or password'}, 401
        return {USER_RESP: user, MESSAGE: 'Login successful'}, 200


# ==================== SYSTEM / HATEOAS DROPDOWN ENDPOINTS ====================

def _option(value, label):
    return {'value': value, 'label': label}


def _dropdown_links(country_code=None, state_code=None):
    base = f'{SYSTEM_EPS}/{SYSTEM_DROPDOWN_OPTIONS}'
    links = {
        'self': {'href': base},
        'form': {'href': f'{SYSTEM_EPS}/{SYSTEM_DROPDOWN_FORM}'},
        'countries': {'href': base},
    }
    if country_code:
        links['states'] = {
            'href': f'{base}?country_code={country_code}',
        }
    else:
        links['states'] = {
            'href': f'{base}?country_code={{country_code}}',
            'templated': True,
        }
    if state_code:
        q = f'state_code={state_code}'
        if country_code:
            q = f'{q}&country_code={country_code}'
        links['cities'] = {'href': f'{base}?{q}'}
    else:
        links['cities'] = {
            'href': (
                f'{base}?country_code={{country_code}}'
                f'&state_code={{state_code}}'
            ),
            'templated': True,
        }
    return links


@api.route(f'{SYSTEM_EPS}/{SYSTEM_DROPDOWN_FORM}')
class SystemDropdownForm(Resource):
    """
    Machine-readable form description for dropdown fields (Swagger + clients).
    """

    @handle_endpoint_errors()
    def get(self):
        return {
            'form': dropdown_form.get_form(),
            'form_descr': dropdown_form.get_form_descr(),
            'fld_names': dropdown_form.get_fld_names(),
            '_links': {
                'self': {
                    'href': f'{SYSTEM_EPS}/{SYSTEM_DROPDOWN_FORM}',
                },
                'options': {
                    'href': f'{SYSTEM_EPS}/{SYSTEM_DROPDOWN_OPTIONS}',
                },
            },
        }, 200


@api.route(f'{SYSTEM_EPS}/{SYSTEM_DROPDOWN_OPTIONS}')
class SystemDropdownOptions(Resource):
    """
    HATEOAS: returns dropdown option lists from live DB reads.
    - No query: all countries (value=code, label=name).
    - ?country_code=USA: states for that country.
    - ?state_code=NY&country_code=USA: cities in that state and country
      (country_code recommended; if omitted, only USA cities are returned).
    """

    @api.param('country_code', 'Filter states by country code', required=False)
    @api.param('state_code', 'Filter cities by state code', required=False)
    @handle_endpoint_errors()
    def get(self):
        country_code = request.args.get('country_code')
        state_code = request.args.get('state_code')

        if state_code:
            cities_raw = cityqry.read()
            cities = (
                cities_raw.values()
                if isinstance(cities_raw, dict)
                else cities_raw
            )
            req_cc = (
                str(country_code).strip().upper()
                if country_code and str(country_code).strip()
                else None
            )
            options = []
            for c in cities:
                sc = c.get('state_code', '')
                if str(sc).upper() != str(state_code).upper():
                    continue
                city_cc = str(
                    c.get('country_code', '') or 'USA'
                ).strip().upper() or 'USA'
                if req_cc:
                    if city_cc != req_cc:
                        continue
                else:
                    if city_cc != 'USA':
                        continue
                name = c.get('name', '')
                options.append(
                    _option(
                        name,
                        f'{name}, {sc}',
                    )
                )
            options.sort(key=lambda o: o['label'].lower())
            cc_echo = req_cc if req_cc else 'USA'
            return {
                'kind': 'cities',
                'state_code': state_code,
                'country_code': cc_echo,
                'options': options,
                NUM_RECS: len(options),
                '_links': _dropdown_links(
                    country_code=cc_echo,
                    state_code=state_code,
                ),
            }, 200

        if country_code:
            states_raw = stateqry.read()
            states = (
                states_raw.values()
                if isinstance(states_raw, dict)
                else states_raw
            )
            options = []
            for s in states:
                cc = s.get('country_code', '')
                if str(cc).upper() != str(country_code).upper():
                    continue
                code = s.get('code', '')
                name = s.get('name', code)
                options.append(_option(code, f'{name} ({code})'))
            options.sort(key=lambda o: o['label'].lower())
            return {
                'kind': 'states',
                'country_code': country_code,
                'options': options,
                NUM_RECS: len(options),
                '_links': _dropdown_links(
                    country_code=country_code,
                    state_code=state_code,
                ),
            }, 200

        # countries by default
        countries_raw = countryqry.read()
        countries = (
            countries_raw.values()
            if isinstance(countries_raw, dict)
            else countries_raw
        )
        options = []
        for c in countries:
            code = c.get('code', '')
            name = c.get('name', code)
            options.append(_option(code, f'{name} ({code})'))
        options.sort(key=lambda o: o['label'].lower())
        return {
            'kind': 'countries',
            'options': options,
            NUM_RECS: len(options),
            '_links': _dropdown_links(),
        }, 200


# ==================== DEVELOPER / OPS (NOT FOR END USERS) ====================


def _dev_logs_root():
    """Log root directory (default /var/log on PA)."""
    base = os.environ.get(DEV_LOG_ROOT_ENV, '/var/log')
    return os.path.realpath(base)


def _dev_logs_safe_target(relative_path):
    """
    Resolve a path under the configured log root (default /var/log on PA).
    Rejects absolute paths and path-traversal outside the root.
    """
    root = _dev_logs_root()
    rel = (relative_path or '').strip().replace('\\', os.sep).lstrip(os.sep)
    joined = os.path.join(root, rel) if rel else root
    full = os.path.realpath(joined)
    root_prefix = root if root.endswith(os.sep) else root + os.sep
    if full != root and not full.startswith(root_prefix):
        raise ValueError('path must stay under the server log root')
    return full


def _dev_logs_auth_or_reject():
    expected = os.environ.get(DEV_LOG_TOKEN_ENV, '').strip()
    if not expected:
        return (
            {
                ERROR: (
                    'Developer log endpoint is disabled until '
                    f'{DEV_LOG_TOKEN_ENV} is set on the server.'
                ),
            },
            503,
        )
    auth = request.headers.get('Authorization', '') or ''
    token = ''
    if len(auth) >= 7 and auth[:7].lower() == 'bearer ':
        token = auth[7:].strip()
    if not token:
        token = request.headers.get(DEV_LOG_TOKEN_HEADER, '').strip()
    if not token:
        return (
            {
                ERROR: (
                    f'Send {DEV_LOG_TOKEN_HEADER} or '
                    'Authorization: Bearer <token>.'
                ),
            },
            401,
        )
    if not secrets.compare_digest(token, expected):
        return ({ERROR: 'Invalid token'}, 401)
    return None


def _tail_log_file(path, n):
    """Return the last n lines of a text log as a single string."""
    n = max(1, min(int(n), _DEV_LOG_MAX_TAIL_LINES))
    buf = b''
    with open(path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        pos = f.tell()
        if pos == 0:
            return ''
        block = 65536
        while pos > 0:
            step = min(block, pos)
            pos -= step
            f.seek(pos)
            buf = f.read(step) + buf
            if buf.count(b'\n') >= n:
                break
            if len(buf) > _DEV_LOG_MAX_TAIL_SCAN_BYTES:
                buf = buf[-_DEV_LOG_MAX_TAIL_SCAN_BYTES:]
                break
    parts = buf.split(b'\n')
    if len(parts) > n:
        parts = parts[-n:]
    return b'\n'.join(parts).decode('utf-8', errors='replace')


@api.route(DEV_LOGS_EP)
class DevLogs(Resource):
    """
    Developer / ops only: list or tail files under the host log directory.
    On PythonAnywhere, application logs typically live under `/var/log`.

    Requires `AXIS_DEV_LOG_TOKEN` on the server. Authenticate with header
    `X-AXIS-Dev-Log-Token: <token>` or `Authorization: Bearer <token>`.

    Optional env `AXIS_DEV_LOG_ROOT` overrides the directory (defaults to
    `/var/log`) for local testing or non-PA hosts.
    """

    @api.param(
        'path',
        'Path relative to the log root; omit to list the root directory.',
        required=False,
    )
    @api.param(
        'lines',
        'Number of lines to return from the end of a file (default 400).',
        required=False,
    )
    @handle_endpoint_errors()
    def get(self):
        auth_err = _dev_logs_auth_or_reject()
        if auth_err is not None:
            return auth_err

        rel = request.args.get('path', '') or ''
        lines_arg = request.args.get('lines', '400')
        try:
            n_lines = int(lines_arg)
        except (TypeError, ValueError):
            return {ERROR: 'lines must be an integer'}, 400

        try:
            target = _dev_logs_safe_target(rel)
        except ValueError as e:
            return {ERROR: str(e)}, 400

        if not os.path.exists(target):
            return {ERROR: 'path does not exist'}, 404

        root = _dev_logs_root()
        rel_display = rel.strip() or '.'

        try:
            if os.path.isdir(target):
                all_names = sorted(os.listdir(target))
                truncated = len(all_names) > _DEV_LOG_MAX_DIR_ENTRIES
                names = all_names[:_DEV_LOG_MAX_DIR_ENTRIES]
                return {
                    'kind': 'directory',
                    'log_root': root,
                    'path': rel_display,
                    'entries': names,
                    NUM_RECS: len(names),
                    'truncated': truncated,
                }, 200

            if os.path.isfile(target):
                text = _tail_log_file(target, n_lines)
                return {
                    'kind': 'file',
                    'log_root': root,
                    'path': rel_display,
                    'lines_requested': max(
                        1, min(n_lines, _DEV_LOG_MAX_TAIL_LINES)
                    ),
                    'content': text,
                }, 200
        except PermissionError:
            return {ERROR: 'permission denied for this path'}, 403

        return {ERROR: 'not a readable file or directory'}, 400


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
