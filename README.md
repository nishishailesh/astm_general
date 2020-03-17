This project have astm_general.py file

It can do unidirectional communication with equipments using ASTM protocol (Many Medical Equipments)

It is tested with

	Erba biochemistry analysers
	
	ElitePro Coagulation analyser
	
It can be used for both rs232 and TCP communication

It will save data sent by equipment in to a file in specified folder 

It is up to user to decide what to do with this data (datbase interfacing)

The file will contain everything between ENQ and EOT

The program simply sends ACK on receipt of ENQ and LF from equipment

