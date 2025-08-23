# Getting Started

For this exercise, you will need to choose a platform for which you can run a python notebook.  Examples include but are not limited to:

- [MyBinder](https://mybinder.org)
- [Google Colab](https://colab.research.google.com/) - Easy Setup
- [SageMaker Studio Lab](https://studiolab.sagemaker.aws/) - Must already have an account - takes time to get approved
 - Local Jupyter - recommended only for experienced python users
    - using a conda/mamba environment
    - using a virtual environment with pip (e.g., python -m venv myenv + pip install jupyter)

For for the purposes of the workshop, I recomment most users use **MyBinder**.  When launched, if will build the environment we need to get started.

## Fork the repo

This part is optional and is only recommended for experieced Github users. Sign into [GitHub](https://github.com)

From your Github Dashboard, use the search bar at the top.
___
![Github Search](assets/github_search.png)
___
Copy and paste the following:

```bash
repo:ianhorn/kyfromabove-gisconference2025-workshop
```

Once you are on this page, click on *Fork* in the top right corner to for this repo.
___
![Github Fork](assets/github_fork.png)
___
You can use my repository name or you can edit to your own.  

Now that you have your own fork you can cmd/terminal to download to get started.

```bash
git clone https://github.com/ianhorn/kyfromabove-gisconference2025-workshop.git kyfromabove-workshop
cd kyfromabove-workshop
```

Now set up your environment with pip

```cmd
python -m venv venv
venv/Scripts/activate.bat
pip install -r requirements.txt
```

or conda

```cmd
conda init
conda env create -f environment.yml
conda activate workshop-env
```

## Local Setup

1. [Fork](../fork-repo/index.md) the repo
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
