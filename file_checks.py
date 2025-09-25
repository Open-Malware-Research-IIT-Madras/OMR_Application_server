<<<<<<< HEAD
import os
import zipfile
import subprocess
import math 
=======
import zipfile
import subprocess
>>>>>>> bc7eae3a1ef1255a73788d98f6366e9d68dfc7f2

def process_zip(zip_file, allowed_rawfile_size, extension_list):
    
    error_list=[]
    hash_value=""
    zip=zipfile.ZipFile(zip_file)
     
    information=zip.infolist()
    filename = information[0].filename
    file_size = information[0].file_size / (25*1024*1024) #file size in MB
    file_ext = filename.split(".")[1]

    
    if not zipfile.is_zipfile(zip_file):
        error_list.append("The file uploaded is not a Zip file!")
     
    if len(information) != 1:
        error_list.append("There is more than one file in the zip, only one file allowed!")    
    
    if len(information) == 1 and zipfile.is_zipfile == True:
        P = subprocess.Popen("unzip -p "+zip_file+" | md5sum", shell=True, stdout=subprocess.PIPE)
        P.wait()
        (output,err)=P.communicate()    
        hash_value = str(output)[2:34]
        print(hash_value)
        
    if file_size > allowed_rawfile_size: 
        error_list.append("File is more than 25 MB, please upload a smaller file")    
    
    if file_ext not in extension_list:
        error_list.append(f"{file_ext} File extension is not supported")
    
    if len(error_list)>0:
<<<<<<< HEAD
        hash_value="Errors found"
        filename="Errors found"
        file_size=None 
        error_list=error_list
    else:                    
        # if all checks are clear then go ahead and split the file 
        filepath=os.path.abspath(zip_file)
        basename=os.path.basename(filepath)
        os.rename(basename,hash_value)
        round_size=math.floor(file_size/(1024*1024))
        p=subprocess.Popen([''])
    
    return (hash_value, error_list)

=======
        hash_value="NA"
        filename="NA"
    
    return (hash_value, filename, file_size, error_list)
>>>>>>> bc7eae3a1ef1255a73788d98f6366e9d68dfc7f2

#unit testing 
