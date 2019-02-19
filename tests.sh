#!bin/bash

if [[ -z "$1" ]]
	then
		echo 'Please provide a filename for testing'
		exit 1
else	
	echo I am the CAT output of "$1" > "$1" &&
	printf "Output of POST request:\n\n" &&
	curl -i -X POST -F file=@"$1" http://127.0.0.1:5000 &&
	printf "\n"
	printf "Output of GET request:\n" &&
	curl http://127.0.0.1:5000 &&
	printf "\n"
	printf "Output of GET\<FILENAMESTRING> request:\n" &&
	curl http://127.0.0.1:5000/"$1"
	printf "\n"
fi



