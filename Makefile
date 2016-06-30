test:
	nosetests tests/

init:
	pip install -e .[test]

cleanpyc:
	find . -name '*.pyc' -delete

clean:
	python setup.py clean
