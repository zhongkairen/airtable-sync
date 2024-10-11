### Setting up Python
Requires python 3.8+. In the project root directory, run
```bash
brew install pyenv
brew install pyenv-virtualenv

cd src
pyenv versions
pyenv install  3.10.15

### this creates artifact .python-version in the current folder
pyenv local  3.10.15
****
```
Add pyenv to path in `~/.zshrc`.
```bash
# Add Homebrew's bin to the PATH
export PATH="/opt/homebrew/bin:$PATH"

# Load pyenv
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
Then run `source ~/.zshrc`.
Verify python version
```bash
python --version
Python 3.10.15
```

### Setting up Python virtual environment
Set up python virtual environment. change to the parent dir of the module i.e. `src`, then create a virtual env and activate it.
```bash
python -m venv .venv
source .venv/bin/activate
```