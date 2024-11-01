test: phase.py test.py
	# run unit tests
	python3 test.py
	rm -rf test-data/** 2>/dev/null

phase.py:
	cp phase.py bin/phase
build: phase.py

bin/Phase.png: Phase.svg
	magick Phase.svg bin/Phase.png
icon: Phase.svg

# requires root priviledges
install: bin/phase bin/Phase.png
	cp bin/phase /usr/bin/phase
	cp bin/Phase.png /usr/share/pixmaps
uninstall:
	rm /usr/bin/phase
	rm /usr/share/pixmaps/Phase.png
