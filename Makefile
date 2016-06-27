test:
	nosetests tests/

init:
	pip install -r requirements.txt

clean:
	find . -name '*.pyc' -delete
