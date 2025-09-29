"""
Module Name: file_checks.py

Description:
    Handles validation and preprocessing of uploaded ZIP files. 
    Performs checks on file type, number of files, size, and 
    allowed extensions. Computes MD5 hash, renames the file, and 
    splits it for storage if all validations pass.

Functions:
    process_zip(zip_file, allowed_rawfile_size, extension_list):
        Validates and processes a ZIP file. Returns the file’s hash 
        value and a list of errors (if any). On success, the file is 
        renamed with its hash and split into chunks for storage.

Classes:
    None defined in this file.

Usage:
    Call process_zip() with a ZIP file path, size limit, and list of 
    allowed extensions:
        hash_value, errors = process_zip("sample.zip", 25, ["exe", "apk", "elf"])

Author:
    Allan Pais
"""

from imports import *
from app_config import *

def process_zip(zip_file, allowed_rawfile_size, extension_list):
    
    error_list=[]
    hash_value=""
    zip=zipfile.ZipFile(zip_file)
    
     
    information=zip.infolist()
    filename = information[0].filename
    file_size = information[0].file_size / (25*1024*1024) #file size in MB
    file_ext_temp = filename.split('.')
    file_ext = file_ext_temp[-1]
    print("This is the file extension stored ",file_ext)

    try:
        if not zipfile.is_zipfile(zip_file):
            error_list.append("The file uploaded is not a Zip file!")
    except: 
        pass 
        
    try:    
        if len(information) != 1:
            error_list.append("There is more than one file in the zip, only one file allowed!")    
    except: 
        pass
    
    if len(information) == 1 and zipfile.is_zipfile == True:
        P = subprocess.Popen("unzip -p "+zip_file+" | md5sum", shell=True, stdout=subprocess.PIPE)
        P.wait()
        (output,err)=P.communicate()    
        hash_value = str(output)[2:34]
        print(hash_value)
    try:    
        if file_size > allowed_rawfile_size: 
            error_list.append("File is more than 25 MB, please upload a smaller file")    
    except: 
        pass
    
    try:    
        if file_ext not in extension_list:
            error_list.append(f"{file_ext} File extension is not supported")
    except: 
        pass
    
    if len(error_list)>0:
        hash_value="Errors found"
        filename="Errors found"
        file_size=None 
        error_list=error_list
        
    else:                    
        # if all checks are clear then go ahead and split the file 
        os.rename(filename,hash_value+".zip")
        round_size=math.ceil(file_size/(1024*1024))
        p=subprocess.Popen([f'split -b {round_size}M {hash_value}.zip ; mv hash_value* ../filehash/']) #zip the file and save it to the NFS 
        p.wait() #wait for the process to finish 
        print("Done the split and zip function")
        
    return (hash_value, error_list)


#unit testing 
