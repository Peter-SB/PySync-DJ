from setuptools import setup, find_packages

setup(
    name='PySyncDJ',
    version='0.1.0',
    description='Sync Spotify playlists to DJ software libraries (using YouTube to download files audio)',
    author='Peter SB',
    url='https://github.com/Peter-SB/PySync-DJ',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'setuptools~=68.2.0',
        'requests~=2.31.0',
        'mutagen~=1.47.0',
        'PyYAML~=6.0.1',
        'spotipy~=2.23.0',
        'pytube~=15.0.0',
    ],
    entry_points={
        'console_scripts': [
            'pysyncdj=pysync_dj:main'
        ],
    },
    classifiers=[
        'Intended Audience :: DJs, Music Enthusiasts',
        'Topic :: Multimedia :: Sound/Audio',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='spotify youtube dj music playlist sync',  # Add more relevant keywords
)

