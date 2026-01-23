if ! [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "This script must be sourced, not executed directly."
  echo "Run 'source setup.sh' instead."
  exit 1
fi

# Get required major.minor from .python-version
required_version=$(head -n 1 .python-version | cut -d. -f1,2)
# Get current python major.minor version
current_version=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
not_current_python=false
if [ "$current_version" != "$required_version" ]; then
  echo "Python version mismatch: required $required_version, found $current_version"
  not_current_python=true
fi

if $not_current_python && ! command -v pyenv >/dev/null 2>&1; then
  echo "pyenv not found, installing..."
  rm -rf "$HOME/.pyenv" devnull 2>&1
  curl -fsSL https://pyenv.run | bash
fi

if $not_current_python; then
  echo "Installing required Python version via pyenv..."
  export PATH="$HOME/.pyenv/bin:$PATH"
  eval "$(pyenv init --path)"
  head -n 1 .python-version | xargs pyenv install -s
fi

pyenv local $(head -n 1 .python-version)

python -m venv ./.venv && source ./.venv/bin/activate

command -v poetry > /dev/null 2>&1
poetry_command_exists=$?
poetry --version > /dev/null 2>&1
poetry_installed_for_active_python=$?
# Poetry doesn't exist at all, or exists but not for the active python version
if [[ $poetry_command_exists -ne 0 || $poetry_installed_for_active_python -ne 0 ]]; then
  echo "Poetry not found, installing..."
  pip install poetry
fi
poetry lock && poetry install
if ! [ -f .env ]; then
  echo ".env file not found, copying sample.env to .env"
  cp sample.env .env
fi
echo "Setup complete. Make sure you edit the .env file with appropriate values."