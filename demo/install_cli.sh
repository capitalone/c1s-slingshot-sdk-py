# Source this script to install slingshot in a virtual environment at ../venv


SLINGSHOT_HOME="$(dirname "$(dirname "$(readlink -f $0)")")"

function find_python() {
  local python_candidate

  while read python_candidate; do
    if [[ $("$python_candidate" --version 2>/dev/null) =~ (^|[^[:digit:].])3\.(7|8|9|10|11)(\.|$) ]]; then
      echo $python_candidate
      return
    fi
  done < <(command -v python python3)
}

function install_slingshot() {
  local SLINGSHOT_PYTHON="$(find_python)"

  if [[ -z $SLINGSHOT_PYTHON ]]; then
    >&2 echo "Python 3.7+ is required"
    return 1
  fi

  if [[ -z $VIRTUAL_ENV ]]; then
    if ! { "$SLINGSHOT_PYTHON" -m venv "$SLINGSHOT_HOME/venv" && source "$SLINGSHOT_HOME/venv/bin/activate"; }; then
      >&2 echo "Failed to activate virtual environment"
      return 1
    fi
  fi

  local SLINGSHOT_PIP="$(command -v pip3 pip | sed q)"

  if "$SLINGSHOT_PIP" install -e $SLINGSHOT_HOME; then
    cat <<"EOD"
      ______ __                   __          __ 
     /   __// (_)___  ____ ______/ /_  ____  / /_
     \__  \/ / / __ \/ __ `/ ___/ __ \/ __ \/ __/
     ___/ / / / / / / /_/ (__  ) / / / /_/ / /_  
    /____/_/_/_/ /_/\__, /____/_/ /_/\____/\__/  
                   /____/                       

    Installation successful!

    Try `slingshot --help` to see available commands and options.

EOD
  else
    >&2 echo "Failed to install Slingshot CLI"
    return 1
  fi
}

install_slingshot
