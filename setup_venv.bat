if exist venv rmdir /S /Q venv
python -m venv venv
call venv\scripts\activate.bat
pip install -e .
call venv\scripts\deactivate.bat