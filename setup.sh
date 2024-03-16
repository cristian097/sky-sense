#!/bin/bash

# Eliminar archivos temporales de pip
rm -r ~/.cache/pip
rm -r build

# Actualizar el entorno virtual (si es necesario)
/home/adminuser/venv/bin/python -m pip install --upgrade virtualenv
