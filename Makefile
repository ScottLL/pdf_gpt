install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt &&\
		   apt-get update &&\
		   apt-get install -y packages.txt 