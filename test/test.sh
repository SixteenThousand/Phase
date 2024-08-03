#!/bin/sh


TEST_DIR=$(pwd)
DATA_DIR="./test-data"
 
function main {
	open_latest_num_no_pad
}

function open_latest_num_no_pad {
	# seed data directory
	cd $DATA_DIR
    for i in $(seq 5)
	do
		touch "boring_stuff_v$i.ods"
	done
	cat <<- EOF > $DATA_DIR/.phase
	pattern = "boring_stuff_v%V.ods"
	EOF
	cd $TEST_DIR
	../phase $DATA_DIR
}

function clean_num_no_pad {
	# seed data directory
	cd $DATA_DIR
    for i in $(seq 5)
	do
		touch "boring_stuff_v$i.ods"
	done
	cat <<- EOF > $DATA_DIR/.phase
	pattern = "boring_stuff_v%V.ods"
	EOF
	cd $TEST_DIR
	../phase $DATA_DIR
}

main
