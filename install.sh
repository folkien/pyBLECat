#!/bin/bash
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

if [ "${1}" == "deps" ]; then
    sudo apt-get -yf install python-pip libglib2.0-dev
    sudo pip install bluepy
    sudo pip install pygatt
    sudo pip install --user bleak
fi
sudo ln -sf ${DIR}/pyBleCat.py /usr/bin/bleCat
