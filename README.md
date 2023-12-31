# REFLOW REport-FLOW import utility

V = 1.0
This is a python utility for monitoring a folder for changes in log files (csv, txt) and upload new data to a user database. Useful to build a datawarehouse with minimal data preprocessing included.

## File structure
The file structure before and after install is the following:

### Virgin File Structure

```
├── dist                    # Compiled files to be installed on the system
├── dist/test               # Sample log files
├── tools                   # Tools and utilities and other scripts
├── install_reflow.cmd		# Install distribution into system (default C:\ProgramData\reflowimporter)
└── README.md				# This file
```

### Installed File Structure

```
├── test/                      # Sample log files
├── launch_reflow_service.cmd  # Start service in background
├── config_file.xml            # Configuration file to edit
├── 010_reflow_core.py		   # Python executable file
├── __data_cache__/		       # Folder with imported data cache: don't remove
└── README.md
```

## Config file structure

```
<?xml version='1.0' encoding='utf-8'?>
<data>
	<general_config>
		<server_address>127.0.0.1</server_address>
		<uid>user</uid>
		<pwd>password</pwd>
		<database>default</database>
		<refresh_period_seconds>60</refresh_period_seconds>
	</general_config>
	
	
	<import_tables>
		<table name="saldatrice1">
			<source_directory>C:\ProgramData\ReflowImporter\test\test_logs</source_directory>
			<destination_table>Saldatrice</destination_table>
			<delimiter>\t</delimiter>
			<header>False</header>
			<field>
				<column_name>BoardName</column_name>
				<column_number>0</column_number>
				<type>string</type>
				<cut_string>True</cut_string>
				<cut_StartCharacter>0</cut_StartCharacter>
				<cut_EndCharacter>5</cut_EndCharacter>
			</field>

		</table>
	</import_tables>
</data>
```
### Table properties are the following:

**source_directory**: [directory]

**destination_table**: name of the table in the SQL database

**delimiter**:<br>
This is the default delimiter used in the file and can be any character as , ; \t (space)

**header**: False, True (default false)<br>
If the source file has a header, the first row must be skipped

### Values for each field are the following:

**column_name**: column_name

**column_number**: 0,1,2...

**type**: string,datetime,time,numeric,

**cut_string**: True,False, (default False)<br>
cut string is used to cut part of the full string. Example: "file20230201" can be cut form start_character 4 to end_character 8 in order to obtain string "2023"

**cut_StartCharacter**: 0,1,2...,

**cut_EndCharacter**: 5,6,7...,

**univoque**: True,False, (default False)<br>
not implemented yet, useful to check if this record already exist in the database

**format**: refer to https://docs.python.org/3/library/datetime.html#format-codes

**source_timezone**: only for datetime type, specifies the reference timezone code of the data imported (default: CET)

**destination_timezone**: only for datetime type, specifies the output timezone to convert the datetime (default: UTC)

**export_to_sql**: (True,False)(default:true) if this value if False then the column is not exported into database 

## Disclaimer
**THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.**

---