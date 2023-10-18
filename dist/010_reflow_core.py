import pandas
import os
from datetime import datetime
from datetime import date
import pymysql
import pymssql
from configparser import ConfigParser
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

import xml.etree.ElementTree as ET



from sqlalchemy import URL

from sqlalchemy import create_engine




tree = ET.parse('config_file.xml')
root = tree.getroot()

DEBUGMODE1=True
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


################################################################################
## MAIN IMPORT UTILITY
################################################################################


def reflow_core():
    print("####### START ACTIVITY ########")
    
    NewTime=datetime.now()
    print(NewTime)

    #import database fields
    
    for i in root.iter('general_config'):
        Host=i.find('server_address').text
        User=i.find('uid').text
        Password=i.find('pwd').text
        Database=i.find('database').text

    print("creating database connection...")
    
    ##CREATING DATABASE CONNECTION
    from sqlalchemy import create_engine
    url_object = URL.create(
        "mssql+pymssql",
        username=User,
        password=Password,  # plain (unescaped) text
        host=Host,
        database=Database,
    )
    dbconnection = create_engine(url_object)

    #create virtual database in debug mode
    if DEBUGMODE1:
        print('Debug ON: simulating database')
        from sqlalchemy import create_engine
        dbconnection = create_engine('sqlite:///:memory:', echo=False)

    ######## START IMPORT PROCEDURE, TABLE FOR TABLE
        
    for folder_index in root.find('import_tables').iter('table'):
        logging.info("importing dataset "+folder_index.tag)

        #set scan directory
        path=folder_index.find('source_directory').text
        print(path)
        delimiter=folder_index.find('delimiter').text
        header_csv=folder_index.find('header').text

        #if <header>=True then skip first row of file
        if header_csv=="True": header_csv=0
        else: header_csv=None

        #open list of imported files
        try: open("__data_cache__/ImportedFileList.csv")
        except:
            print("ImportedFileList not found. Creating new file...")
            #create folder, if it already exist(err 183) ignore error
            try: os.mkdir("__data_cache__")
            except 183:
                pass
            new_cache=open("__data_cache__/ImportedFileList.csv", "x")
            new_cache.close()
        try:
            ReadIndexes = pandas.read_csv("__data_cache__/ImportedFileList.csv",sep="\t",engine="python",skiprows=[0],usecols=[0,1,2],names=['FileIndex','ImportedRows','LastUpdatedTime'])
        except:
            print("error reading cache file")

        ##open directory to scan
        try:
            filenames = os.listdir(path)
        except:
            print("Impossible to access "+path+" please check the path")

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
        
        #print("files recent found:")
        #print(filepaths)
        #for files in filenames: print(datetime.fromtimestamp(os.path.getmtime(os.path.join(path, files))))
        #print("newtime:")
        #print(NewTime)
        
        logging.info("file found: ".join(filenames))
        print("New files to import: {0}".format(len(filepaths)))

        #get details about fields that must be imported
        TF=pandas.DataFrame()
        fields=folder_index
        TF['column_name']=[column.find('column_name').text for column in fields.iter('field')]
        TF['column_number']=[int(column.find('column_number').text) for column in fields.iter('field')]
        TF['column_type']=[column.find('type').text for column in fields.iter('field')]
        TF['cast_string']=[column.find('cut_string').text for column in fields.iter('field')]
        TF['read_StartCharacter']=[int(column.find('cut_StartCharacter').text) for column in fields.iter('field')]
        TF['read_EndCharacter']=[int(column.find('cut_EndCharacter').text) for column in fields.iter('field')]
    
        #print(folder_index.attrib['name'])
        
        #order by column number
        TF=TF.sort_values(by=['column_number'])
        if DEBUGMODE1:
            TF.to_html(buf='__table_dump__/Buf_'+folder_index.attrib['name']+r"_structure.html")

        ######## IMPORT EACH FILE
        for FileName in filenames:
            Filepath = os.path.join(path,FileName)
            NewUpdatedTime=datetime.fromtimestamp(os.path.getmtime(Filepath))
          
##            logging.info("importing "+Filepath)
##            logging.info("{0} righe saltate".format(skipRows[0]))
##            print("importing "+Filepath)
##            print("{0} righe saltate".format(skipRows[0]))
            
            try: Tfile=open(Filepath)
            except: print("impossibile aprire file")
            else:
                TotalRows=sum(1 for line in Tfile)

            skipRows=ReadIndexes[ReadIndexes.FileIndex==(folder_index.attrib['name']+"/"+FileName)]['ImportedRows'].tolist()[0]

            #if total rows is equal to imported rows
            if TotalRows<=skipRows:
                #logging.info("tutte le righe importate")
                #print("tutte le righe importate")
                continue

            #Import csv
            data = pandas.read_csv(Filepath,sep=delimiter,engine="python",skiprows=skipRows,usecols=TF['column_number'].tolist(),names=TF['column_name'],header=header_csv)
            #describe new quantity of read data
            logging.info("{0} righe importate".format(data.shape[0]))
            print("{0} righe importate: {1}".format(data.shape[0],FileName))

            ######## POSTPROCESSING OF COLUMNS
            print("processing columns")
            for column in data:
                #postprocesso
                actTF=TF[TF['column_name']==column]
                
                #taglia stringa
                if actTF['cast_string'].item()=='True':
                    data[column]=data[column].astype(str).str[actTF['read_StartCharacter'].item():actTF['read_EndCharacter'].item()]
                pass

                #tipo stringa
                if actTF['column_type'].item()=='string':
                    data[column]=data[column].astype(str)

                #tipo:datetime
                if actTF['column_type'].item()=='datetime':
                    data[column]=pandas.to_datetime(data[column])
                
                #tipo:date
                
                #tipo:time
                if actTF['column_type'].item()=='time':
                    data[column]=pandas.to_datetime(data[column])

                #tipo:numeric
                if actTF['column_type'].item()=='numeric':
                    data[column]=pandas.to_numeric(data[column])

            #log data table
            if DEBUGMODE1:
                data.to_html(buf='__table_dump__/Buf_'+folder_index.attrib['name']+r'_table.html')

            ######## UPLOAD TO DATABASE
            print("uplading to database...",end=" ")
            #print(folder_index.find('destination_table').text)
            #print(data)
            try:
                data.to_sql(name=folder_index.find('destination_table').text, con=dbconnection, index=False, if_exists='append')
            except 2003:
                print("conenction failed")
            else:
                print("successful")
                #update number of read lines
                ReadIndexes.loc[ReadIndexes.FileIndex==(folder_index.attrib['name']+"/"+FileName),'ImportedRows']=len(data)+skipRows
                ReadIndexes.loc[ReadIndexes.FileIndex==(folder_index.attrib['name']+"/"+FileName),'LastUpdatedTime']=NewUpdatedTime
                ReadIndexes.to_csv("__data_cache__/ImportedFileList.csv", encoding='utf-8', index=False, sep="\t")

        ##
        #update last updated time
        #print(NewTime.strftime('%Y-%m-%d %H:%M:%S'))
        #logging.info("Done importing")
        print("Done importing")
        print(" ")

################################################################################

refresh_interval=int(root.find('general_config').find('refresh_period_seconds').text)
print("Reflow importer started: running every {0} seconds".format(refresh_interval))

#run script 1 time
reflow_core()


##create scheduler and run script every n-sec
scheduler = BlockingScheduler()
job_defaults = {
    'coalesce': False,
    'max_instances': 1
}
scheduler.configure(job_defaults=job_defaults)
#scheduler.configure({'apscheduler.daemon': False})
scheduler.add_job(reflow_core, 'interval', seconds=refresh_interval)

scheduler.start()
         

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


