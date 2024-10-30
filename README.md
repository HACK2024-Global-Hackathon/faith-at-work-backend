# faith-at-work-backend
#HACK2024 missional challenge: To Gather Christians to reach their workplace for Christ

# Overview
todo

# Quickstart
```bash
pyenv local 3.12.7
python src/main.py
```

# Developer setup (Linux/Mac)

Note: For developing on Windows, install [wsl](https://learn.microsoft.com/en-us/windows/wsl/setup/environment) for a virtual Linux environment (eg. Ubuntu)

Prerequisite packages
```bash
apt update -y
apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git tk-dev libsqlite3-dev libffi-dev libreadline-dev
curl https://pyenv.run | bash
```

Append this to your .bashrc or .zshrc
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
 eval "$(pyenv init -)"
fi
````

Setup Python virtual environment (change as needed)
```bash
pyenv install 3.12.7
pyenv versions
pyenv local 3.12.7
```

Install docker and check that it is running (Optional) (Ubuntu)
```bash
sudo snap install docker
docker --version

sudo apt install docker-compose

sudo snap disable docker
sudo snap enable docker
sudo snap start docker
sudo snap services docker
sudo addgroup --system docker
sudo adduser $USER docker
newgrp docker
ls -l /var/run/docker.sock
sudo chmod 666 /var/run/docker.sock

docker-compose up --build
docker-compose down
```

Deploy as Cloud Run Service
```bash
sudo snap install --classic google-cloud-cli

gcloud auth login
gcloud config set project faith-at-work-backend-440004
gcloud config set run/region asia-east1

gcloud run deploy faith-at-work-backend --timeout=600 --service-account 392395172966-compute@developer.gserviceaccount.com --memory=512Mi --region asia-east1 --source .
```
