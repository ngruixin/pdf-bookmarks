from distutils.core import setup
import py2exe, sys, os
import json
from PyPDF2 import PdfFileReader

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    console = [{'script': "bookmark.py"}],
    zipfile = None,
)
