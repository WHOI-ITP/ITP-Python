from admin_tools.download_itp_files import download_itp_files, unzip_files
from admin_tools.database import build_database
from pathlib import Path

"""
Download the latest files and rebuild the databases
"""

path = Path('D:/ITP Data')


for product in ['final', 'grid', 'cormat']:
    download_itp_files(path, product)
    unzip_files(path / product)
    build_database(path, product)
