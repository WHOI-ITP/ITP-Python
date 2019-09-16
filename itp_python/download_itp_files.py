import re
import ftputil
from hashlib import md5
from pathlib import Path


"""
This is a script to download all the itp*final.zip files from the WHOI FTP
site and put them into a local folder 'files'. Once the folder is populated, 
the script will only download the file again if a newer version is found
on the FTP site.
"""


def parse_checksums(path):
    md5_dict = {}
    with open(path, 'r') as fid:
        for line in fid:
            md5_hash, file = line.split()
            md5_dict[file] = md5_hash
    return md5_dict


def calc_md5(path):
    return md5(open(path, 'rb').read()).hexdigest()


def download_itp_files(destination):
    r = re.compile(r'itp[0-9]*final.zip')
    with ftputil.FTPHost('ftp.whoi.edu', 'anonymous', 'guest') as ftp_host:
        print('Changing directory')
        ftp_host.chdir('/whoinet/itpdata/')
        print('Getting file list')
        files = ftp_host.listdir(ftp_host.curdir)
        final_files = list(filter(r.match, files))
        print('{} files found'.format(len(final_files)))
        ftp_host.download('MD5SUMS', destination / 'md5.txt')
        checksums = parse_checksums(destination / 'md5.txt')
        new_files = False
        for file_name in final_files:
            local_path = destination / file_name
            state = ftp_host.download_if_newer(file_name, local_path)
            if calc_md5(local_path) != checksums[file_name]:
                local_path.unlink()
                print('{} failed the checksum test. The file has been '
                      'deleted. Please try running this script '
                      'again.'.format(file_name))
                raise ValueError('{} failed checksum test'.format(file_name))
            if state:
                print(file_name + ' downloaded')
                new_files = True

    if new_files:
        print('New files downloaded')
    else:
        print('All files up to date')


if __name__ == '__main__':
    download_itp_files(Path() / 'files')
