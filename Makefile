test:
	@cd tests; PYTHONPATH=.. py.test --cov=liten *.py

install:
	pip install -r requirements.txt

lint:
	pylint --disable=R,C,W0402 liten

lint-full:
	pylint --disable=R, liten

clean:
	find . -name '*.pyc' -delete

all: lint test
