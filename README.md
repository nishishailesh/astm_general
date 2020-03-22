#This project have astm_general.py file
It can do unidirectional communication with equipments using ASTM protocol (Many Medical Equipments)
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
