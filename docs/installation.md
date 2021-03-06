# Installation
This guide will help you install ITP-Python and setup a virtual environment to run it.

## Requirements
- A computer running Windows, Linux, or MacOS
- Python 3.7 installed on your computer ([download](https://www.python.org/downloads/ "download"))
- If installing via Git, Git must be installed on your computer ([download](https://git-scm.com/downloads "download"))

## Option 1: Clone ITP-Python onto your computer using Git
1. In Git Bash, browse to your projects directory
2. In Git bash: `git clone https://github.com/WHOI-ITP/ITP-Python`

## Option 2: Download Zip File
1. Download zip file from https://github.com/WHOI-ITP/ITP-Python

## (Optional) Setup Virtual Environment
1. Using a shell, browse to the ITP-Python folder that was just cloned
2. From the command line: `python -m venv venv`
3. `venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `pip install .`