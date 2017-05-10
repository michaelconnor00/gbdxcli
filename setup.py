from setuptools import setup

setup(
    name='gbdxcli',
    version='0.0.3',
    install_requires=[
        'Click',
        # 'gbdxtools',
        # 'gbdx-auth',
        'simplejson',
        'docker-py',
        'jsonschema==2.4.0',
        'glob2',
        'arrow'
    ],
    packages=['gbdxcli'],
    entry_points='''
        [console_scripts]
        gbdx=gbdxcli.main:cli
    '''

)
