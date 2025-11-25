#!/bin/bash

export FLASK_ENV=development
export PROJ_DIR=$PWD
export DEBUG=1

# Use local MongoDB (set CLOUD_MONGO=1 to use cloud MongoDB)
export CLOUD_MONGO=1
# UNCOMMENT AND EDIT THIS WHILE TESTING LOCALLY
# export MONGO_USER=
# export MONGO_PASSWD=

# Override MongoDB host/port in the future
# export MONGO_HOST=localhost
# export MONGO_PORT=27017

# run our server locally:
PYTHONPATH=$(pwd):$PYTHONPATH
FLASK_APP=server.endpoints flask run --debug --host=127.0.0.1 --port=8000
