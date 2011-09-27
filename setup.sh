#!/bin/bash
set -e

virtualenv venv
source venv/bin/activate

pip install django
pip install lxml
pip install rdflib==3.1.0


