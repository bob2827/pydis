from setuptools import setup, find_packages

#Reference on setuptools usage
#https://pythonhosted.org/an_example_pypi_project/setuptools.html

setup(name='pydis',
      version='0.1',
      description='',
      author='Bob Sherbert',
      author_email='bob@carbidelabs.com',
      packages=['pydis'],
      install_requires=['redis', 'json'],
      zip_safe=True,
     )

#'numpy', metering

