import re
import sys
from ftputil import FTPHost
from hashlib import md5
from pathlib import Path
from zipfile import ZipFile


"""
This is a script to download all the itp*final.zip files from the WHOI FTP
site and put them into a local folder 'files'. Once the folder is populated, 
the script will only download the file again if a newer version is found
on the FTP site.
"""


PRODUCTS = {
    'final': re.compile(r'itp([0-9]+)final.zip'),
    'grid': re.compile(r'itp([0-9]+)grddata.zip'),
    'cormat': re.compile(r'itp([0-9]+)cormat.zip'),
    'raw': re.compile(r'itp([0-9]+)rawmat.zip'),
    'rawlocs': re.compile(r'itp[0-9]*rawlocs.dat')
}

exclude_pattern = {
    'grid': PRODUCTS['final'],
    'raw': PRODUCTS['cormat'],
}

CHECKSUM = False


def download_itp_files(directory, product):
    assert product in PRODUCTS
    directory = Path(directory) / product
    print('Starting download')

    if product != 'rawlocs':
        (directory / 'zipped').mkdir(parents=True, exist_ok=True)
    with FTPHost('ftp.whoi.edu', 'anonymous', 'guest') as ftp_host:
        ftp_host.use_list_a_option = False
        print('Connecting ftp.whoi.edu')
        ftp_host.chdir('/whoinet/itpdata/')
        print('Retrieving file list')
        files = ftp_host.listdir(ftp_host.curdir)

        product_re = PRODUCTS[product]
        final_n = []
        if product in exclude_pattern:
            file_n = \
                [m[1] for m in [re.search(product_re, f) for f in files] if m]
            exclude_re = exclude_pattern[product]
            exclude_n = \
                [m[1] for m in [re.search(exclude_re, f) for f in files] if m]
            file_n = set(file_n) - set(exclude_n)
            final_files = \
                [m[0] for m in [re.search(product_re, f) for f in files]
                 if m and m[1] in file_n]
        else:
            final_files = list(filter(product_re.match, files))
        print(f'{len(final_files)} ITP files found')
        ftp_host.download('MD5SUMS', directory / 'md5.txt')
        checksums = parse_checksums(directory / 'md5.txt')
        new_files = False


        for file_name in final_files:
            if product != 'rawlocs':
                local_path = directory / 'zipped' / file_name
            else:
                local_path = directory / file_name
            state = ftp_host.download_if_newer(file_name, local_path)
            if CHECKSUM and calc_md5(local_path) != checksums[file_name]:
                local_path.unlink()
                print('{} failed the checksum test. The file has been '
                      'deleted. Please try running this script '
                      'again.'.format(file_name))
                # raise ValueError(f'{file_name} failed checksum test')
            if state:
                print(f'{file_name} downloaded')
                new_files = True

    if new_files:
        print('New files were downloaded')
    else:
        print('All files are up to date')

def exclude_by_itp_number():
    pass

def unzip_files(directory):
    zip_directory = directory / 'zipped'
    files = list(zip_directory.glob('*.zip'))
    for file in files:
        zip = ZipFile(file)
        out_directory = directory / file.stem
        if not compare_zip_to_folder(zip, out_directory):
            zip.extractall(path=out_directory)
            print(f'{file.stem} extracted')


def compare_zip_to_folder(zip_file, folder_path):
    zipped_files = zip_file.namelist()
    itp_file_paths = Path(folder_path).glob('*.*')
    itp_files = set([x.name for x in itp_file_paths])
    return set(zipped_files) == set(itp_files)


def parse_checksums(path):
    md5_dict = {}
    with open(path, 'r') as fid:
        for line in fid:
            md5_hash, file = line.split()
            md5_dict[file] = md5_hash
    return md5_dict


def calc_md5(path):
    return md5(open(path, 'rb').read()).hexdigest()


if __name__ == '__main__':
    destination = Path('')
    product_arg = 'final'
    if len(sys.argv) > 1:
        destination = Path(sys.argv[1])
    if len(sys.argv) > 2:
        product_arg = sys.argv[2]
        assert product_arg in PRODUCTS.keys()
    download_itp_files(destination, product_arg)
    if product_arg != 'rawlocs':
        unzip_files(destination)
