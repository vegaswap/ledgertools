#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup  # type: ignore

setup(
    name="ledgertools",
    description="Python tools for ledger",
    long_description_content_type="text/markdown",
    url="https://github.com/vegaswap/ledgertools",
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "eth-account>=0.5.5,<0.6.0",
        "web3[tester]>=5.18.0,<6.0.0",
    ],
    entry_points={
        "console_scripts": ["ltools=cli:cli"],        
    },
    python_requires=">=3.7,<3.10",
    # py_modules=[
    #     "ltools"        
    # ],
    license="MIT",
    keywords="ethereum",
    # packages=find_packages("src"),
    # package_dir={"": "src"},    
)
