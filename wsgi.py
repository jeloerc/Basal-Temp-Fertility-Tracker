#!/usr/bin/env python3
import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación Flask
from app import app as application

# This is the object that Apache WSGI will load
if __name__ == '__main__':
    application.run() 