
## Local Setup

1. [Fork](#fork-the-repo---optional) the repo
2. Setup python environoment

Conda
```bash
conda init
conda env create -f environment.yml
conda activate workshop-env
```

Virtual Environment
 
 - Windows
```bash
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requiements.txt
```
 - mac/linux
```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requiements.txt
```
