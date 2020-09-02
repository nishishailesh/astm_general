#!/bin/bash
inotifywait -m /root/inbox* -e create -e moved_from |
    while read path action file; do
	if [ "$action" == 'CREATE' ]
	then
		echo "+++Result received at '$file' and stored in '$path"
	fi
        if [ "$action" = 'MOVED_FROM' ]
        then
		echo -e "---Its Result is stored in LIS\n"
        fi

        # do something with the file
    done
