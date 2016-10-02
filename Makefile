test:
	@cd tests; PYTHONPATH=.. pytest --cov=liten *.py

install:
	pip install -r requirements.txt

lint:
	pylint --disable=R,C liten

lint-full:
	pylint --disable=R, liten

clean:
	find . -name '*.pyc' -delete

all: lint test
