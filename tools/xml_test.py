import xml.etree.ElementTree as ET
import pandas

tree = ET.parse('config_file_new.xml')
root = tree.getroot()
root.tag
root.attrib

for i in root.iter('general_config'):
    host=i.find('server_address').text,
    user=i.find('uid').text,
    password=i.find('pwd').text,
    database=i.find('database').text

TF=pandas.DataFrame()
fields=root.find('import_tables').find('table')
TF['column_name']=[column.find('column_name').text for column in fields.iter('field')]
TF['column_number']=[column.find('column_number').text for column in fields.iter('field')]
TF['column_type']=[column.find('type').text for column in fields.iter('field')]
TF['cast_string']=[column.find('cast_string').text for column in fields.iter('field')]
TF['read_StartCharacter']=[column.find('read_StartCharacter').text for column in fields.iter('field')]
TF['read_EndCharacter']=[column.find('read_EndCharacter').text for column in fields.iter('field')]

print(TF)

##
##TF=pandas.DataFrame()
##            TF['column_name']=[column["column_name"] for column in access[folder_index]["FIELD"]]
##            TF['column_number']=[column["column_number"] for column in access[folder_index]["FIELD"]]
##            TF['column_type']=[column["type"] for column in access[folder_index]["FIELD"]]
##            TF['cast_string']=[column.get('cast_string') for column in access[folder_index]["FIELD"]]
##            TF['read_StartCharacter']=[column.get('read_StartCharacter') for column in access[folder_index]["FIELD"]]
##            TF['read_EndCharacter']=[column.get('read_EndCharacter') for column in access[folder_index]["FIELD"]] 
##
##
##xtree = et.parse("config_file_new.xml")
##xroot = xtree.getroot() 
##
##df_cols = ["name", "email", "grade", "age"]
##rows = []
##
##for node in xroot:
##    print(node)
##    s_name = node.attrib.get("name")
##    s_mail = node.find("email").text if node is not None else None
##    s_grade = node.find("grade").text if node is not None else None
##    s_age = node.find("age").text if node is not None else None
##    
##    rows.append({"name": s_name, "email": s_mail, 
##                 "grade": s_grade, "age": s_age})
##
##out_df = pd.DataFrame(rows, columns = df_cols)
##
##
##import pandas
##import mxml
##
##df = pandas.read_xml(open('config_file_new.xml','r'))
##print(df)
