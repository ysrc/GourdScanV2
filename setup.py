#!/usr/bin/env python
# coding=utf-8


from setuptools import find_packages, setup

from gourdscan import VERSION

setup(
    name='gourdscan',
    version=VERSION,
    url='git@github.com:ysrc/GourdScanV2.git',
    description='被动式漏洞扫描系统',
    author='ysrc',
    author_email='Cond0r@Codescan,range@Codescan',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "gourdscan = gourdscan.cli:main"
        ]
    },
    install_requires=[
        'requests',
        'tornado',
        'redis',
        'scapy',
    ],
    extras_require={}
)
