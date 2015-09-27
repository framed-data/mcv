from setuptools import setup, find_packages
setup(
    name = "mcv",
    version = "0.30.0",
    packages = find_packages(),
    install_requires = [
        'pyyaml',
        'labrador',
        'paramiko',
        'treant',
        'requests',
        'jinja2'],
    author = "Elliot Block",
    author_email = "elliot@framed.io",
    description = "Spartan configuration management in Python",
    url = "https://github.com/framed-data/mcv",
)
