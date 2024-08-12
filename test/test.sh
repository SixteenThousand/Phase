#!/bin/sh


TEST_DIR=$(pwd)
DATA_DIR="test-data"
 
if [ "$(basename $TEST_DIR)" != 'test' ]
then
	echo "seed is being run from the wrong directory!"
	exit 1
fi


function main {
	case $1 in
		seed) seed;;
		*) echo "no e2e tests yet!";
	esac
}

function seed {
	cd ./$DATA_DIR
	# just to double check
	if [ "$(basename $PWD)" = "$DATA_DIR" ]
	then
		rm -r ./*
	fi
	for i in $(seq 5)
	do
		touch "boring_stuff_v$i.ods"
		touch $(printf "boring_padded_v%03d.ods" $i)
	done
	for i in $(seq 20)
    do
		touch "interesting_stuff_v$i.pdf"
		touch $(printf "interesting_padded_v%03d.pdf" $i)
	done
	for i in $(seq 11)
    do
		touch "fascinating_stuff_v$i"
		touch $(printf "fascinating_padding_v%03d.pdf" $i)
	done
	for i in $(seq 20)
    do
		mkdir "interesting_directory_v$i"
	done
	touch "dud"
	touch "oring_stuff_v1.ods"
	touch "boring_stuff_v1Xods"
}


main $@
