if exist venv rmdir /S /Q venv
virtualenv venv
call venv\scripts\activate.bat
pip install -r requirements.txt
call venv\scripts\deactivate.bat