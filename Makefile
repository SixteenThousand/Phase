test:
	# run unit tests
	python3 test.py
	# make executable version of phase
	cp phase.py ./test/dist/phase
	# run end-to-end tests
	cd ./test && bash ./e2e_test.sh
