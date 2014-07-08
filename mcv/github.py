"""GitHub utility functions"""

def keys_uri(username):
    template = 'https://github.com/{username}.keys'
    return template.format(username=username)
