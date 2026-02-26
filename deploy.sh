#!/bin/bash
# This shell script deploys a new version to a server.

PROJ_DIR=AXiS
VENV=myvirtualenv
PA_DOMAIN="xinyanc.pythonanywhere.com"
PA_USER='XinYanC'
echo "Project dir = $PROJ_DIR"
echo "PA domain = $PA_DOMAIN"
echo "Virtual env = $VENV"

CRITICAL_PY_PACKAGES=("bcrypt" "flask" "pymongo")

if [ ! -f "requirements.txt" ]
then
    echo "Missing requirements.txt in the current directory."
    exit 1
fi

echo "Running dependency sanity check."
for package in "${CRITICAL_PY_PACKAGES[@]}"
do
    if ! grep -Eiq "^${package}([[:space:]]*([<>=!~]=?|===).*)?$" requirements.txt
    then
        echo "Missing critical package '${package}' in requirements.txt."
        echo "Add it before deploy so PythonAnywhere installs it during rebuild."
        exit 1
    fi
done
echo "Dependency sanity check passed."

if [ -z "$DEMO_PA_PWD" ]
then
    echo "The PythonAnywhere password var (DEMO_PA_PWD) must be set in the env."
    exit 1
fi

echo "PA user = $PA_USER"
echo "PA password = $DEMO_PA_PWD"

echo "SSHing to PythonAnywhere."
sshpass -p $DEMO_PA_PWD ssh -o "StrictHostKeyChecking no" $PA_USER@ssh.pythonanywhere.com << EOF
    cd ~/$PROJ_DIR; PA_USER=$PA_USER PROJ_DIR=~/$PROJ_DIR VENV=$VENV PA_DOMAIN=$PA_DOMAIN ./rebuild.sh
EOF
