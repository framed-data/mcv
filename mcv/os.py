"""OS utilities"""


def get_os_info():
    """Parse machine release information

    This only works for Ubuntu and certain Debian variants right now. A
    complete solution needs to parse different files.

    Returns:
        dict: A mapping of relevant distro information
              {
                'os': DISTRO,
                'version': DISTRO_VERSION,
              }
    """
    os_info = {}
    mapping = {
        'DISTRIB_ID': 'os',
        'DISTRIB_RELEASE': 'version',
    }

    with open('/etc/lsb-release', 'r') as f:
        for line in f:
            key, value = line.strip().split('=')

            if key in mapping:
                os_info[mapping[key]] = value

    return os_info
