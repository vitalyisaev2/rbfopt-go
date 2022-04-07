test:
	go test -count=1 -v ./...

lint:
	golangci-lint run ./...

release_python:
	# Just for the reference
	git tag v0.2.0
	python setup.py sdist bdist_wheel
	twine check dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	# twine upload dist/*