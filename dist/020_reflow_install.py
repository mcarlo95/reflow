#Automatical install of all the python libraries required

import sys
import os

def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        print("installing "+package, end="... ")
        import subprocess
        #r=subprocess.check_output([sys.executable, "-m", "pip", "install", package])
        try: subprocess.check_output([sys.executable, "-m", "pip","--no-color","--log=pip_error_log.txt","install", package])
        except: print("install failed, please check pip_error_log.txt or manually run <python> -m pip install "+package)
    finally:
        try:
            importlib.import_module(package)
        except:
            print("Error in installing package {0}".format(package))
            return 1
        else:
            print("{0} installed correctly".format(package))
        
if (os.getcwd()=="C:\ProgramData\ReflowImporter"):
    print("already installed system. To remove this install just remove all files.")
    #add uninstall script
    sys.exit()

print(r"Do you want to install the files in C:\ProgramData\ReflowImporter (Y/N)?")
if input()!='Y':
    exit()

install_files=['010_reflow_core.py', 'README.md', 'config_file.xml', 'test\\ /E', 'launch_reflow_service.cmd']
update_files=['010_reflow_core.py', 'README.md', 'test\\ /E', 'launch_reflow_service.cmd']

print("installing packages:")
install_and_import('subprocess')
import subprocess
#install_and_import('pymysql')
install_and_import('pandas')
install_and_import('configparser')
install_and_import('apscheduler')
install_and_import('pymssql')


#install software in intsall directory
print("creating install directory in C:\\ProgramData\\ReflowImporter\\")
try: os.mkdir(r"C:\ProgramData\ReflowImporter")
except FileExistsError:
    print("Directory already exists. Forcing update")
    for file in update_files:
        try:subprocess.check_output("xcopy "+file+" C:\\ProgramData\\ReflowImporter\\ /Y")
        except: print("error in writing files!!!!!!! installation may failed")
except: print(r"error in creating directory.")
else:
    print("Created install directory on C:\ProgramData\ReflowImporter")
    for file in install_files:
        try:subprocess.check_output("xcopy "+file+" C:\\ProgramData\\ReflowImporter\\")
        except: print("error in writing files!!!!!!! installation may failed")
print("done copying file")

#create task scheduler event
#os.system("runas "+sys.executable+" ".join(sys.argv))
print("installing automatic startup on windows scheduler")
try:
    subprocess.check_output(r'schTasks /create /SC ONSTART /TN "Reflow report importer" /TR "C:\ProgramData\ReflowImporter\010_reflow.py"')
except:
    print("Impossible to create automatic start at startup, please execute again this script as administrator or manually add the service in <windows task scheduler>")
else:
    print("successfully installed automatic startup")

input()
