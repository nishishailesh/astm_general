#!/usr/bin/python3
astm_log_filename='/var/log/vitros_read.log'
file2mysql_log_filename='/var/log/vitros_write.log'
#host_address='12.207.3.240'
#host_address='11.207.1.1'
host_address=''
host_port='2577'
select_timeout=1
alarm_time=10
#trailing slash is must to reconstruct path
inbox_data='/root/vitros.inbox.data/'
inbox_arch='/root/vitros.inbox.arch/'
outbox_data='/root/vitros.outbox.data/'
outbox_arch='/root/vitros.outbox.arch/'
equipment='VITROS3600'
