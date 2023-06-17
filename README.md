# Multimedia editor
### Using PostgreSQL, FFmpeg, Pyhon3.10, CUDA, PULSE
https://github.com/adamian98/pulse

## Quick Start
1. Download Repository
```shell
git clone git@github.com:edonssfall/multimedia_editor.git
```
2. Create environment and install requirements
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Install FFmpeg and PostgreSQL
```shell
sudo apt install ffmpeg

echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

sudo apt-get update
sudo apt-get install -y postgresql-15

sudo pg_createcluster 15 main --start

sudo systemctl start postgresql@15-main.service

sudo systemctl enable postgresql@15-main.service
```
4. Copy and configeru .env
```shell
cp example.env .env
```
```text
PROJECT_DIR='/global/path/to/project/folder'
```
5. Run app
```shell
python3 main.py
```

### Optional to use UPScale
6. Install CUDA and CUDA Tools\
install for your version system can use this scripts\
https://github.com/edonssfall/Razer-Blade-2020-Ubuntu/tree/main/DataScience


## Instructions
### Using terminal
It read your system, so it can move to home folder or drivers
```text
cd      -Move to home folder
-d      -Show list of external drivers
/d      -Show list and can chose driver to move
-v      -Use it in folder with video, to start process of search same frames
-i      -Use to start scale up all images in folders(Need to finish)
-sql    -Give access to PostgreSQL commands
...
over commands in BASH
```

All changes write in logs.txt