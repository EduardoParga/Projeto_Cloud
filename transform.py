DATA_FILE = "250923"
FILE_NAME = "BGBG186_{DATA_FILE}.xml"

def transform ():
    xml_storage_file=get_file_from_blob(FILE_NAME)
    print(xml_storage_file)  

transform() 
    
