#!/usr/bin/python3
import fcntl
import time

fh=open('/root/yumizen_h500.data/xyz','wb')
fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
while True:
  time.sleep(2)
  pass
