XEA Core
========

This is the API Backend for XEA.

Usage
=====

To run this project, you will need:
- Python 3

The rest of the dependencies can be installed through `pip install -r
requirements.txt`.

In order to install the dependencies locally for the project, create a virtual
environment. A folder `env` is already ignored from version control, so you
can use the following commands to set it up:

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

Contributing
============

In order to contribute a patch (feature, bugfix, whatever), we are
using a GitHub-like approach: just fork the repo, create a feature
or a bugfix branch and then send us a merge request ;)

But first remember that you have to read the CONTRIBUTORS file, sign our CLA
and add your name to that file.

License
=========

This file is part of XEA-core. XEA-core is free software: you can redistribute
it and/or modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

XEA-core is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License along
with XEA-core. If not, see http://www.gnu.org/licenses/.
