# Pydis - Transparent Redis bindings for Python
# Copyright (C) 2014 Bob Sherbert
# bob@carbidelabs.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

#Reference on setuptools usage
#https://pythonhosted.org/an_example_pypi_project/setuptools.html

setup(name='pydis',
      version='0.4',
      description='',
      author='Bob Sherbert',
      author_email='bob@carbidelabs.com',
      packages=['pydis'],
      install_requires=['redis', 'datetime'],
      zip_safe=True,
     )

#'numpy', metering

