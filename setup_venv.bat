if exist venv rmdir /S /Q venv
python -m venv venv
call venv\scripts\activate.bat
pip install ..\Itp-Python
call venv\scripts\deactivate.bat