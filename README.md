### About
If you wish **unidirectional communication** with medical equipment using **ASTM protocol** this might be useful

It handles both RS232 (COM Port, ttyS0 etc ) and TCP connections via LAN/wifi

It is tested with

	Erba biochemistry analysers (XL-640)
	Note: Erba XL-640 with Windows-XP have problem with resources. Use Windows 7 or above
	ElitePro Coagulation analyser
	It must work with any analyser following ASTM protocol

### prerequisites
  * Linux ( Tested in debian, but must work with any)
  * Python3 +
  * Some python 3 libraries like sys,logging, signal time,datetime,socket,serial
  * Most libraries are deault installation with python in Linux
  * See log file for missing libraries
  
### This project have astm_general.py file as sole code
  * The program simply sends ACK on receipt of ENQ and LF from equipment
  * The data received (from ENQ to EOT ) is saved in a file (see below)
  * It is up to user to decide what to do with this data (e.g. database interfacing)  
  * manual edit of file required for following
    * to select the mode (tty or tcp)
    * to select tty device (if tty mode)
    * to select ip and port (if tcp mode)
    * to specify folder for saving data files
    * to specify file where log will be stored
  * make file executable
  ```
  chmod +x astm_general.py
  ```
  * run script
  * use inotifywait to see files being created
  * see log file for error
  
### What Next
  * create service to run at boot time (I am planning to add its example)
  * create mysql support for database insertion
  * program for bidirectional service
  
### Contact
  * Dr Shaileshkumar Manubhai Patel
  * biochemistrygmcs@gmail.com
  * WhatsApp: 9664555812 (India)
	
