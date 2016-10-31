# -*- coding: utf-8 -*-

import os
import sys
import setuptools as st
from io import open

# Fix so that the setup.py usage is CWD-independent
SETUPDIR = os.path.abspath(os.path.dirname(__file__))
SETUPDIR = os.path.dirname(__file__)
PKGDIR = os.path.join(SETUPDIR, 'src')

sys.path.append(PKGDIR)
import antibarrel

reqsfname = os.path.join(SETUPDIR, 'requirements.txt')
reqs = open(reqsfname, 'r', encoding='utf-8').read().strip().splitlines()

descfname = os.path.join(SETUPDIR, 'doc', 'description.rst')
# longdesc = open(descfname, 'r', encoding='utf-8').read()

st.setup(
    name="antibarrel",
    version=antibarrel.__version__,
    author=u"Matěj Týč",
    author_email="matej.tyc@gmail.com",
    description=("Calibration of (microscope) objective lenses "
                 "against radial (barrel, pincushion) distortion."),
    license="BSD",
    url="https://github.com/matejak/antibarrel",
    package_dir = {'': PKGDIR},
    packages = st.find_packages(PKGDIR),
    entry_points = {
        'console_scripts': [
            "abar-center = antibarrel.mk_center:main",
            "abar-datapoints = antibarrel.mk_datapoints:main",
            "abar-deps = antibarrel.mk_deps:main",
            "abar-labels = antibarrel.mk_labels:main",
            "abar-lines = antibarrel.mk_lines:main",
            "abar-rot = antibarrel.mk_rot:main",
            "abar-solution = antibarrel.mk_solution:main",
            "abar-transform = antibarrel.mk_transform:main",

            "abari-datapoints = antibarrel.inspect_datapoints:main",
            "abari-deps = antibarrel.inspect_deps:main",
            "abari-labels = antibarrel.inspect_labels:main",
            "abari-lines = antibarrel.inspect_lines:main",
        ],
    },
    install_requires=reqs,
    extras_require={
        'inspecting':  ["matplotlib>=1.2"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
    ],
    # long_description=longdesc,
    zip_safe=True,
)
