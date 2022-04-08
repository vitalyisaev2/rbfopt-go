test:
	go test -count=1 -v ./...

lint:
	golangci-lint run ./...

python_release_build:
	rm -rf ./build/* ./dist/*
	python setup.py sdist bdist_wheel
	twine check dist/*

python_release_test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

python_release_prod:
	twine upload dist/*