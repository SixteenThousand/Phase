test:
	# run unit tests
	python3 test.py
	rm -rf ./test-data/**
build: test
	cp phase.py ./bin/phase
# requires root priviledges
install: build
	cp ./bin/phase /usr/bin/phase
uninstall: install
	rm /usr/bin/phase
