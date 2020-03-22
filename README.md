### About
If you wish **unidirectional communication** with medical equipment using **ASTM protocol** this might be useful

It handles both RS232 (COM Port, ttyS0 etc ) and TCP connections wia LAN/wifi
### prerequisites
  * Linux ( Tested in debian, but must work with any
  * Python3 +
  * Some python 3 libraries like time,datetime,socket,serial
  *
# This project have astm_general.py file

It is tested with
	Erba biochemistry analysers (XL-640)
		Note: Erba XL-640 with Windows-XP have problem with resources. Use Windows 7 or above
	ElitePro Coagulation analyser
It can be used for both rs232 and TCP communication
	manual edit of file required to select the mode
It will save data sent by equipment in to a file in specified folder
	manual edit of file to sepecify folder and log location
It is up to user to decide what to do with this data (datbase interfacing)
The file will contain everything between ENQ and EOT
The program simply sends ACK on receipt of ENQ and LF from equipment

What Next
	You need to write own program to read files saved
	The data may be inserted in database
<code>
