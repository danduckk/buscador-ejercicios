#!/bin/bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
git clone https://github.com/danduckk/buscador-ejercicios.git
cd buscador-ejercicios
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
echo "Listo. Para usar: cd buscador-ejercicios && ./run.sh"
