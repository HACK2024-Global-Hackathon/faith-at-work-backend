# faith-at-work-backend
#HACK2024 missional challenge: To Gather Christians to reach their workplace for Christ

# Overview
todo

# Quickstart
todo 

# Developer setup (Linux/Mac)

Note: For developing on Windows, install [wsl](https://learn.microsoft.com/en-us/windows/wsl/setup/environment) for a virtual Linux environment (eg. Ubuntu)

Prerequisite packages
```bash
apt update -y
apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git tk-dev libsqlite3-dev libffi-dev libreadline-dev
curl https://pyenv.run | bash
```

Update your .bashrc or .zshrc with pyenv env vars
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.bashrc
````

Install specific Python version (change as needed)
```bash
pyenv install 3.12.7
```

Activate Python version (change as needed)
```bash
pyenv versions
pyenv local 3.12.7
```
