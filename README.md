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
				<cast_string>True</cast_string>
				<read_StartCharacter>0</read_StartCharacter>
				<read_EndCharacter>5</read_EndCharacter>
			</field>

		</table>
	</import_tables>
</data>
```
Values for each field are the following:

```
        "FIELD": [
            {
                column_name: column_name,
                column_number: 0,1,2...
                type: string,datetime,time,numeric,
                cast_string:True,False, (default False)
                read_StartCharacter:0,1,2...,
                read_EndCharacter:5,6,7...,
                univoque:True,False, (default False)
            }
```
