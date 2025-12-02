include common.mk

# Our directories
CITIES_DIR = cities
DB_DIR = data
REQ_DIR = .
SEC_DIR = security
API_DIR = server

FORCE:

prod: all_tests github

github: FORCE
	- git commit -a
	git push origin master

all_tests: FORCE
	cd $(API_DIR); make tests
	# cd $(DB_DIR); make tests
	cd $(SEC_DIR); make tests

dev_env: FORCE
	pip install -r $(REQ_DIR)/requirements-dev.txt
	@echo "You should set PYTHONPATH to: "
	@echo $(shell pwd)

prod_env: FORCE
	pip install -r $(REQ_DIR)/requirements.txt

docs: FORCE
	cd $(API_DIR); make docs
