from setuptools import setup, find_packages
setup(
    name = "mcv",
    version = "0.1.0",
    packages = find_packages(),
    install_requires = [
        'pyyaml',
        'labrador',
        'fabric'],
    author = "Elliot Block",
    author_email = "elliot@deck36.net",
    description = "Dumb-is-the-new-smart configuration management",
    url = "https://github.com/elliot42/mcv",
    scripts = ['bin/mcv']
)
