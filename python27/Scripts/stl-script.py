#!c:\python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'numpy-stl==1.9.1','console_scripts','stl'
__requires__ = 'numpy-stl==1.9.1'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('numpy-stl==1.9.1', 'console_scripts', 'stl')()
    )
