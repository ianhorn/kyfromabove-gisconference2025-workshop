
# Fork the repo

This part is optional and is only recommended for experieced Github users. Sign into [GitHub](https://github.com)

From your Github Dashboard, use the search bar at the top.
___
![Github Search](../assets/github_search.png)
___
Copy and paste the following:

```
repo:ianhorn/kyfromabove-gisconference2025-workshop
```

Once you are on this page, click on *Fork* in the top right corner to for this repo.
___
![Github Fork](../assets/github_fork.png)
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