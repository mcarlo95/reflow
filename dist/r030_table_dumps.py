import pandas
import os
from datetime import datetime
from datetime import date
import pymysql
import pymssql
from configparser import ConfigParser
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
import sys

from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

import xml.etree.ElementTree as ET

from sqlalchemy import URL

from sqlalchemy import create_engine



tree = ET.parse('config_file.xml')
root = tree.getroot()

DEBUGMODE1=False
if root.find('test_mode').text.upper()=="TRUE": DEBUGMODE1=True
if DEBUGMODE1:
    try: os.mkdir("__table_dump__")
    except FileExistsError:
        pass

#define output message stream
def print_and_log(textmessage):
    print(textmessage)

################################################################################
## MAIN IMPORT UTILITY
################################################################################


def reflow_core():
    print_and_log("####### START ACTIVITY ########")


    ######## START IMPORT PROCEDURE, TABLE FOR TABLE
        
    for folder_index in root.find('import_tables').iter('table'):

        #set scan directory
        path=folder_index.find('source_directory').text
        print_and_log(path)
        delimiter=folder_index.find('delimiter').text
        header_csv=folder_index.find('header').text

        #if <header>=True then skip first row of file
        if header_csv=="True": header_csv=0
        else: header_csv=None
        header_csv=None

        ##open directory to scan
        try:
            filenames = os.listdir(path)
        except:
            print_and_log("Impossible to access "+path+" please check the path")

        #get file paths
        filepaths = [os.path.join(path, file) for file in filenames]
        filteredfilenames=[]
        
        #function to find the values of fields inside xml, with also a default value fallback
        def get_properties(fields,find,default):
            Arr=[]
            for column in fields.iter('field'):
                try: Arr.append(column.find(find).text)
                except: Arr.append(default)
            return Arr
        

        #get details about fields that must be imported
        TF=pandas.DataFrame()
        fields=folder_index
        TF['column_name']=[column.find('column_name').text for column in fields.iter('field')]
        TF['column_number']=[int(column.find('column_number').text) for column in fields.iter('field')]
        TF['column_type']=[column.find('type').text for column in fields.iter('field')]
        TF['column_type_format']=[column.find('type').attrib for column in fields.iter('field')]
        TF['cast_string']=get_properties(fields,'cut_string','False')
        TF['read_StartCharacter']=[int(v) for v in get_properties(fields,'cut_StartCharacter',0)]
        TF['read_EndCharacter']=[int(v) for v in get_properties(fields,'cut_EndCharacter',0)]
        TF['export_to_sql']=get_properties(fields,'export_to_sql','True')
        

        TF.to_html(buf='__table_dump__/Buf_'+folder_index.attrib['name']+r"_structure.html")
    
        #0211 SPECIAL COLUMN FILENAME THAT COLLECT THE FILE NAME
        df2 = pandas.DataFrame(columns=TF.columns)
        rows = TF.loc[TF['column_number']==-1, :]
        df2 = rows
        TF.drop(rows.index, inplace=True)
        
        #order by column number
        TF=TF.sort_values(by=['column_number'])
        dpcTF=TF.loc[TF['column_number'].duplicated(),:]
        TFu=TF.drop_duplicates(subset=['column_number'],keep='first')
        #print(dpcTF)
        

        ######## IMPORT EACH FILE
        for FileName in filenames:
            Filepath = os.path.join(path,FileName)
            NewUpdatedTime=datetime.fromtimestamp(os.path.getmtime(Filepath))
            
            try: Tfile=open(Filepath)
            except: print_and_log("impossibile aprire file")
            else:
                TotalRows=sum(1 for line in Tfile)

            #Import csv
            data = pandas.read_csv(Filepath,sep=delimiter,engine="python",header=header_csv)
            #describe new quantity of read data
            print_and_log("{0} righe importate: {1}".format(data.shape[0],FileName))

            #log data table
            data.to_html(buf='__table_dump__/Buf_'+folder_index.attrib['name']+r'_table.html')

            break
        
        print_and_log("Done importing")
        print_and_log(" ")

################################################################################

#run script 1 time
reflow_core()


