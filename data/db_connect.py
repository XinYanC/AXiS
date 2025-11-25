"""
All interaction with MongoDB should be through this file!
We may be required to use a new database at any point.
"""
import os

import certifi
import pymongo as pm
from functools import wraps

LOCAL = "0"
CLOUD = "1"

GEO_DB = 'geo2025DB'

client = None

MONGO_ID = '_id'

MIN_ID_LEN = 4


def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def needs_db(fn):
    """
    Decorator that ensures database connection exists before calling
    the decorated function. If no connection exists, it will create one.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global client
        if not client:
            connect_db()
        return fn(*args, **kwargs)
    return wrapper


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        print('Setting client because it is None.')
        if os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD:
            # Cloud MongoDB connection
            username = os.environ.get('MONGO_USER')
            password = os.environ.get('MONGO_PASSWD')
            if not username:
                raise ValueError('You must set MONGO_USER environment variable '
                                 + 'to use Mongo in the cloud.')
            if not password:
                raise ValueError('You must set MONGO_PASSWD environment variable '
                                 + 'to use Mongo in the cloud.')
            print('Connecting to Mongo in the cloud.')
            client = pm.MongoClient(f'mongodb+srv://{username}:{password}'
                                    + '@geodb.f4tdnzf.mongodb.net/'
                                    + '?appName=geodb',
                                    serverSelectionTimeoutMS=5000,
                                    connectTimeoutMS=5000,
                                    tlsCAFile=certifi.where())
            
            # Test the connection to ensure MongoDB is accessible
            try:
                # This will raise an exception if MongoDB is not accessible
                client.admin.command('ping')
                print('Successfully connected to MongoDB in the cloud.')
            except pm.errors.ServerSelectionTimeoutError:
                raise ConnectionError(
                    'Failed to connect to MongoDB in the cloud. '
                    'Please check your credentials and network connection.'
                )
            except Exception as e:
                raise ConnectionError(
                    f'Error connecting to MongoDB in the cloud: {str(e)}'
                )
        else:
            # Local MongoDB connection
            print("Connecting to Mongo locally.")
            # Get MongoDB connection details from environment or use defaults
            mongo_host = os.environ.get('MONGO_HOST', 'localhost')
            mongo_port = int(os.environ.get('MONGO_PORT', 27017))
            
            # Connection string for local MongoDB
            connection_string = f'mongodb://{mongo_host}:{mongo_port}/'
            
            # Create client with connection timeout to fail fast if MongoDB isn't running
            client = pm.MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000
            )
            
            # Test the connection to ensure MongoDB is running
            try:
                # This will raise an exception if MongoDB is not accessible
                client.admin.command('ping')
                print(f"Successfully connected to MongoDB at {mongo_host}:{mongo_port}")
            except pm.errors.ServerSelectionTimeoutError:
                raise ConnectionError(
                    f'Failed to connect to MongoDB at {mongo_host}:{mongo_port}. '
                    'Please ensure MongoDB is running locally. '
                    'You can start it with: mongod (or brew services start mongodb-community on macOS)'
                )
            except Exception as e:
                raise ConnectionError(
                    f'Error connecting to MongoDB at {mongo_host}:{mongo_port}: {str(e)}'
                )
    return client


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        # Convert mongo ID to a string so it works as JSON
        doc[MONGO_ID] = str(doc[MONGO_ID])


@needs_db
def create(collection, doc, db=GEO_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{doc=}')
    ret = client[db][collection].insert_one(doc)
    return str(ret.inserted_id)


@needs_db
def read_one(collection, filt, db=GEO_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in client[db][collection].find(filt):
        convert_mongo_id(doc)
        return doc


@needs_db
def delete(collection: str, filt: dict, db=GEO_DB):
    """
    Find with a filter and return after deleting the first doc found.
    """
    print(f'{filt=}')
    del_result = client[db][collection].delete_one(filt)
    return del_result.deleted_count


@needs_db
def update(collection, filters, update_dict, db=GEO_DB):
    return client[db][collection].update_one(filters, {'$set': update_dict})


@needs_db
def read(collection, db=GEO_DB, no_id=True) -> list:
    """
    Returns a list from the db.
    """
    ret = []
    for doc in client[db][collection].find():
        if no_id:
            del doc[MONGO_ID]
        else:
            convert_mongo_id(doc)
        ret.append(doc)
    return ret


def read_dict(collection, key, db=GEO_DB, no_id=True) -> dict:
    """
    Doesn't need db decorator because read() has it
    """
    recs = read(collection, db=db, no_id=no_id)
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict

