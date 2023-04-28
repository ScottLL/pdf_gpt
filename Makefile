install:
	pip install --upgrade pip && \
		pip install -r requirements.txt && \
		sudo apt-get update && \
		sudo xargs -a packages.txt apt-get install -y
format:	
	black app/**/*.py

lint:
	pylint --disable=R, app/*.py

refactor: 
	format lint

build:
	uvicorn app.main:app --reload

all: install lint format build