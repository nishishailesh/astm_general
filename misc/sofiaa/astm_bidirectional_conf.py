#!/usr/bin/python3
astm_log_filename='/var/log/sofia_read.log'
file2mssql_log_filename='/var/log/sofia_write.log'
#host_address='12.207.3.240'
#host_address='11.207.1.1'
host_address=''
host_port='2576'
select_timeout=1
alarm_time=5    #as per sofia manual
#trailing slash is must to reconstruct path
inbox_data='/root/sofia.inbox.data/'
inbox_arch='/root/sofia.inbox.arch/'
outbox_data='/root/sofia.outbox.data/'
outbox_arch='/root/sofia.outbox.arch/'

