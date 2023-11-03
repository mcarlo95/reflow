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

import r011_reflow_interface
from r011_reflow_interface import text as text
from r011_reflow_interface import win as win


tree = ET.parse('config_file.xml')
root = tree.getroot()

DEBUGMODE1=False
if root.find('test_mode').text.upper()=="TRUE": DEBUGMODE1=True
if DEBUGMODE1:
    try: os.mkdir("__table_dump__")
    except FileExistsError:
        pass

#logging library
import logging
FORMAT = '%(asctime)s\t%(message)s'
logging.basicConfig(format=FORMAT, filename="log.txt", level=logging.DEBUG)
logging.info("Program is working as expected")
logging.basicConfig(format=FORMAT)

#define output message stream
def print_and_log(textmessage):
    logging.info(textmessage)
    #print(textmessage)
    text.insert('end',textmessage)
    text.insert('end',"\n")
    text.pack()
    win.update_idletasks()
    win.update()

#redirect standard output errors to log file
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w') #initialize stderr with null stream
    sys.stderr.write = print_and_log
    
################################################################################
## MAIN IMPORT UTILITY
################################################################################


def reflow_core():
    print_and_log("####### START ACTIVITY ########")
    
    NewTime=datetime.now()
    print_and_log(NewTime)

    #import database fields
    
    for i in root.iter('general_config'):
        Host=i.find('server_address').text
        User=i.find('uid').text
        Password=i.find('pwd').text
        Database=i.find('database').text

    print_and_log("creating database connection...")
    
    ##CREATING DATABASE CONNECTION
    from sqlalchemy import create_engine
    url_object = URL.create(
        "mssql+pymssql",
        username=User,
        password=Password,  # plain (unescaped) text
        host=Host,
        database=Database,
    )



    #create virtual database in debug mode
    if DEBUGMODE1:
        print_and_log('Debug ON: simulating database')
        from sqlalchemy import create_engine
        dbconnection = create_engine('sqlite:///:memory:', echo=False)
    else:
        try:
            dbconnection = create_engine(url_object)
        except:
            print_and_log('Database connection error')
        

    ######## START IMPORT PROCEDURE, TABLE FOR TABLE
        
    for folder_index in root.find('import_tables').iter('table'):
        logging.info("importing dataset "+folder_index.tag)

        #set scan directory
        path=folder_index.find('source_directory').text
        print_and_log(path)
        delimiter=folder_index.find('delimiter').text
        header_csv=folder_index.find('header').text

        #if <header>=True then skip first row of file
        if header_csv=="True": header_csv=0
        else: header_csv=None

        #open list of imported files
        try: open("__data_cache__/ImportedFileList.csv")
        except:
            print_and_log("ImportedFileList not found. Creating new file...")
            #create folder, if it already exist(err 183) ignore error
            try: os.mkdir("__data_cache__")
            except 183:
                pass
            new_cache=open("__data_cache__/ImportedFileList.csv", "x")
            new_cache.close()
        try:
            ReadIndexes = pandas.read_csv("__data_cache__/ImportedFileList.csv",sep="\t",engine="python",skiprows=[0],usecols=[0,1,2],names=['FileIndex','ImportedRows','LastUpdatedTime'])
        except:
            print_and_log("error reading cache file")

        ##open directory to scan
        try:
            filenames = os.listdir(path)
        except:
            print_and_log("Impossible to access "+path+" please check the path")

        #get file paths
        filepaths = [os.path.join(path, file) for file in filenames]
        filteredfilenames=[]
        #for each file verify if it must be imported
        for file in filenames:
            LastUpdatedTime=ReadIndexes[ReadIndexes.FileIndex==(folder_index.attrib['name']+"/"+file)]['LastUpdatedTime'].tolist()
            #if it is a new file, add a new entry with filename, 0 imported row, import time=1900-01-01
            if LastUpdatedTime==[]:
                LastUpdatedTime=["1900-01-01 01:01:01"]
                ReadIndexes.loc[len(ReadIndexes)] = [(folder_index.attrib['name']+"/"+file),0,"1900-01-01 01:01:01"] 
            #if it is updated, then add to the import file list
            if pandas.to_datetime(LastUpdatedTime) < datetime.fromtimestamp(os.path.getmtime(os.path.join(path, file))):
                filteredfilenames.append(file)
        filenames=filteredfilenames
        filepaths = [os.path.join(path, file) for file in filenames]
        
        #print_and_log("files recent found:")
        #print_and_log(filepaths)
        #for files in filenames: print_and_log(datetime.fromtimestamp(os.path.getmtime(os.path.join(path, files))))
        #print_and_log("newtime:")
        #print_and_log(NewTime)
        
        logging.info("file found: ".join(filenames))
        print_and_log("New files to import: {0}".format(len(filepaths)))

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
        TF['cast_string']=get_properties(fields,'cut_string',"Ciao")
        TF['read_StartCharacter']=[int(v) for v in get_properties(fields,'cut_StartCharacter',0)]
        TF['read_EndCharacter']=[int(v) for v in get_properties(fields,'cut_EndCharacter',0)]
        TF['export_to_sql']=get_properties(fields,'export_to_sql','True')
        

        if DEBUGMODE1:
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
          
##            logging.info("importing "+Filepath)
##            logging.info("{0} righe saltate".format(skipRows[0]))
##            print_and_log("importing "+Filepath)
##            print_and_log("{0} righe saltate".format(skipRows[0]))
            
            try: Tfile=open(Filepath)
            except: print_and_log("impossibile aprire file")
            else:
                TotalRows=sum(1 for line in Tfile)

            skipRows=ReadIndexes[ReadIndexes.FileIndex==(folder_index.attrib['name']+"/"+FileName)]['ImportedRows'].tolist()[0]

            #if total rows is equal to imported rows
            if TotalRows<=skipRows:
                #logging.info("tutte le righe importate")
                #print_and_log("tutte le righe importate")
                continue

            #Import csv
            data = pandas.read_csv(Filepath,sep=delimiter,engine="python",skiprows=skipRows,usecols=TFu['column_number'].tolist(),names=TFu['column_name'],header=header_csv)
            #describe new quantity of read data
            logging.info("{0} righe importate".format(data.shape[0]))
            print_and_log("{0} righe importate: {1}".format(data.shape[0],FileName))

            #RECALL COLUMNS WITH DUPLICATED column_number
            for index, row in dpcTF.iterrows():
                colnam=TFu[TFu['column_number']==row['column_number']]['column_name']
                #print(colnam)
                data[row['column_name']]=data.loc[:,colnam]
                #print(data.to_string())

            #0211 INSERT AGAIN INTO DATA THE FILE NAME IF THERE IS A FILENAME COLUMN
            #print(df2)
            TF1 = pandas.concat([TF,df2])
            if (df2['column_name'].tolist()!=[]):
                data[df2['column_name'].tolist()[0]]=[FileName]*len(data)
            
            ######## FORMATTING OF COLUMNS
            print_and_log("processing columns")
            for column in data:
                #postprocesso
                actTF=TF1[TF1['column_name']==column]
                
                #taglia stringa
                if actTF['cast_string'].iloc[0]=='True':
                    data[column]=data[column].astype(str).str[actTF['read_StartCharacter'].item():actTF['read_EndCharacter'].item()]

                #tipo stringa
                if actTF['column_type'].iloc[0]=='string':
                    data[column]=data[column].astype(str)

                #tipo:datetime
                if actTF['column_type'].iloc[0]=='datetime':
                    if 'format' in actTF['column_type_format'].iloc[0]:
                        data[column]=pandas.to_datetime(data[column],format=actTF['column_type_format'].item()['format'])
                    else:
                        data[column]=pandas.to_datetime(data[column])
                
                #tipo:date
                if actTF['column_type'].iloc[0]=='date':
                    if f'format' in actTF['column_type_format'].iloc[0]:
                        data[column]=pandas.to_datetime(data[column],format=actTF['column_type_format'].item()['format'])
                    else:
                        data[column]=pandas.to_datetime(data[column])
                
                #tipo:time
                if actTF['column_type'].iloc[0]=='time':
                    if 'format' in actTF['column_type_format'].iloc[0]:
                        data[column]=pandas.to_timedelta(data[column],format=actTF['column_type_format'].item()['format'])
                    else:
                        data[column]=pandas.to_timedelta(data[column])

                #tipo:numeric
                if actTF['column_type'].item()=='numeric':
                    data[column]=pandas.to_numeric(data[column])

            ######## POSTPROCESSING OF COLUMNS
            #custom functions
            for column in fields.iter('postprocess'):

                #combined date+time
                if column.find('function').text=="combine_date_time":
                    newrow=pandas.DataFrame([{'column_name':column.find('parameter1').text,'column_type':'datetime','export_to_sql':'True'}])#insert new row description
                    TF1=pandas.concat([TF1,newrow])
                    data[column.find('parameter1').text]=pandas.to_datetime(data[column.find('parameter2').text] + data[column.find('parameter3').text])
                    print(newrow.to_string())

            ####### FILTER OUT FIELDS export_to_sql==false
            if DEBUGMODE1:
                TF1.to_html(buf='__table_dump__/Buf_'+folder_index.attrib['name']+r"_structure.html")
            #print(TF1.to_string())
            data=data.filter(TF1[TF1['export_to_sql']!='False']['column_name'])
            #print(data.to_string())


            #log data table
            if DEBUGMODE1:
                data.to_html(buf='__table_dump__/Buf_'+folder_index.attrib['name']+r'_table.html')

            ######## UPLOAD TO DATABASE
            print_and_log("uplading to database...")
            #print_and_log(folder_index.find('destination_table').text)
            #print_and_log(data)

            try:
                data.to_sql(name=folder_index.find('destination_table').text, con=dbconnection, index=False, if_exists='append')
            except 2003:
                print_and_log("conenction failed")
            except:
                print_and_log("other error")
            else:
                print_and_log("successful")
                #update number of read lines
                ReadIndexes.loc[ReadIndexes.FileIndex==(folder_index.attrib['name']+"/"+FileName),'ImportedRows']=len(data)+skipRows
                ReadIndexes.loc[ReadIndexes.FileIndex==(folder_index.attrib['name']+"/"+FileName),'LastUpdatedTime']=NewUpdatedTime
                ReadIndexes.to_csv("__data_cache__/ImportedFileList.csv", encoding='utf-8', index=False, sep="\t")

        ##
        #update last updated time
        #print_and_log(NewTime.strftime('%Y-%m-%d %H:%M:%S'))
        #logging.info("Done importing")
        print_and_log("Done importing")
        print_and_log(" ")

################################################################################

refresh_interval=int(root.find('general_config').find('refresh_period_seconds').text)
#print_and_log("Reflow importer started: running every {0} seconds".format(refresh_interval))

#print_and_log("ciao",text)

#run script 1 time
reflow_core()


##create scheduler and run script every n-sec
#scheduler = BlockingScheduler()
scheduler = BackgroundScheduler()
job_defaults = {
    'coalesce': False,
    'max_instances': 1
}
scheduler.configure(job_defaults=job_defaults)
## scheduler.configure({'apscheduler.daemon': False})
scheduler.add_job(reflow_core, 'interval', seconds=refresh_interval)

scheduler.start()
print_and_log("Scheduler started. Execution every: {0} sec ".format(refresh_interval))

win.mainloop()
         

            #df = pandas.DataFrame(data)
            #df = df[df['MatrixPTH'].notnull()]
    ##        #set timezone to rome
    ##        df['TimezonedTime']=pandas.to_datetime(df['DateTime'].str[:19])
    ##        df['TimezonedTime']=df['TimezonedTime'].dt.tz_localize('CET').dt.tz_convert("UTC")
    ##
    ##
    ##        # Insert DataFrame to Table
    ##        for row in df.itertuples():
    ##            #upload only datas of today
    ##            if (pandas.to_datetime(row.DateTime[:19])>pandas.to_datetime('today').normalize()):


