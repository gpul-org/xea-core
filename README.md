XEA Core
========

This is the API Backend for XEA.

Usage
=====

To run this project, you will need:
- Python 3

The rest of the dependencies can be installed through `pip install -r
requirements.txt`.

In order to install the dependencies locally for the project, create a
virtual environment. A folder `env` is already ignored from version
control, so you can use the following commands to set it up:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

This should be enough to let you then run `./manage.py runserver`.

First run
=========

Before running the server, remember to run any possible migrations with:

`./manage.py migrate`
