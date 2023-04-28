install:
	pip install --upgrade pip && \
		pip install -r requirements.txt && \
		sudo apt-get update && \
		sudo xargs -a packages.txt apt-get install -y