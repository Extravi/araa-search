#!/bin/python
# This python script was made to generate a suitable `/_config.py`
# using the current environment variables OR the defaults specified in
# `/resource/_config.py.gen.template`.
# 
# This script uses `/resource/_config.py.gen.template` as a template
# for the generated `/_config.py`
# 
# Also, it's meant to be ran with the cwd at the root of this repository.

# A reference for acceptable environment variables & how to use them
# for `/_config.py`
ENV_VARS = {
    'PORT': { # Name of the env. var.
        'default_val': 8000, # Default value (obvious)
        'pyname': 'PORT', # The name of the variable in Python (_config.py)
        'type': int,
    },
    'SHEBANG': {
        'default_val': '!',
        'pyname': 'BANG',
        'type': str,
    },
    'ORIGIN_REPO': {
        'default_val': 'https://github.com/Extravi/tailsx',
        'pyname': 'REPO',
        'type': str,
    },
    'DEFAULT_THEME': {
        'default_val': 'dark_blur',
        'pyname': 'DEFAULT_THEME',
        'type': str,
    },
    'ENABLE_API': {
        'default_val': False,
        'pyname': 'API_ENABLED',
        'type': bool,
    },
    'ENABLE_TORRENTS': {
        'default_val': True,
        'pyname': 'TORRENTSEARCH_ENABLED',
        'type': bool,
    },
    'INVIDIOUS_INSTANCE': {
        'default_val': 'yt.artemislena.eu',
        'pyname': 'INVIDIOUS_INSTANCE',
        'type': str,
    },
    'TORRENTGALAXY_DOMAIN': {
        'default_val': 'torrentgalaxy.to',
        'pyname': 'TORRENTGALAXY_DOMAIN',
        'type': str,
    },
}

import os

config_py = open('_config.py', 'w')

# Write a disclaimer.
config_py.write(
    '# This _config.py was automatically generated using scripts/generate-pyconfig.py.'
)

for env_var in ENV_VARS.keys():
    val = os.environ.get(env_var)

    # If environ.get() returns None, then the env. var. wasn't supplied.
    # Fall back on the default.
    if val == None:
        val = ENV_VARS[env_var]['default_val']
        print(f"Config var. '{env_var}' not specified. Defaulting to '{val}'")

    # Put quotes around each strings value.
    if ENV_VARS[env_var]['type'] == str:
        val = f"'{val}'"

    config_py.write(f"{ENV_VARS[env_var]['pyname']}={val}\n")

# Write the rest of the template's variables.
# These variables are not yet configurable with this generator.
conf_template = open('resource/_config.py.gen.template', 'r')
config_py.write(conf_template.read())
conf_template.close()

config_py.close()
