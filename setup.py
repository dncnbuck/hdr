from setuptools import setup, find_packages
import re

with open('version', 'r') as properties_file:
    properties = properties_file.read()
version = re.search(r'version=([0-9.\-A-Za-z]+)', properties).group(1)

setup(
    name='hdr',
    version=version,
    description="Python project",
    classifiers=[],
    keywords='',
    author='Duncan Buck',
    author_email='dncnbuck@gmail.com',
    url='https://github.com/dncnbuck/hdr',
    license='',
    packages=find_packages(exclude=['ez_setup', 'test']),
    package_data={
      'hdr': []
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'numpy',
        'opencv-python',
    ],
    extras_require={},
    entry_points={
        'console_scripts': [
            'hdr = hdr.__main__:main',
            ]
        },
)
