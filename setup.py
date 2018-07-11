from setuptools import setup

setup(
    name='ictv-plugin-github',
    version='0.1',
    packages=['ictv.plugins.github_reader', 'ictv.renderer'],
    package_dir={'ictv': 'ictv'},
    url='https://github.com/OpenWeek/ictv-plugin-github',
    license='AGPL-3.0',
    author='Florent Dardenne, Alexandre Fiset & Alexandre Gobeaux',
    author_email='',
    description='A plugin that bring events and information about Github repositories and organisations to ICTV',
    include_package_data=True,
)
