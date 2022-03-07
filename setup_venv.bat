if exist venv rmdir /S /Q venv
python -m venv venv
call venv\scripts\activate.bat
pip install -e . --no-cache-dir
pip install -r requirements_dev.txt
call venv\scripts\deactivate.bat