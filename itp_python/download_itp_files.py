import re
import os
import ftputil


"""
This is a script to download all the itp*final.zip files from the WHOI FTP
site and put them into a local folder 'files'. Once the folder is populated, 
the script will only download the file again if a newer version is found
on the FTP site.
"""


print('Connecting')
local_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'files'))
r = re.compile(r'itp[0-9]*final.zip')

with ftputil.FTPHost('ftp.whoi.edu', 'anonymous', 'guest') as ftp_host:
    print('Changing directory')
    ftp_host.chdir('/whoinet/itpdata/')
    files = ftp_host.listdir(ftp_host.curdir)
    final_files = list(filter(r.match, files))
    print('Getting file list')
    print('Downloading Files')
    new_files = False
    for file_name in final_files:
        print('Downloading ' + file_name)
        state = ftp_host.download_if_newer(
            file_name,
            os.path.join(local_directory, file_name))
        new_files = new_files or state
if new_files:
    print('New files downloaded')