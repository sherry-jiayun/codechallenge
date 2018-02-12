#!/bin/bash
success=0
total=0
cd ./tests
for d in */ ; do
	let total=total+1
	python ../../src/test.py $d
	result=$?
	if [ $result -ne 0 ]; then
		echo "[FAIL]: ${d///}"
	else
		let success=success+1
		echo "[PASS]: ${d///}"
	fi
	echo "[$(date +%a) $(date +%b) $(date +%d) $(date +%H:%M:%S) $(date +%Z) $(date +%Y)] $success of $total tests passed"
done