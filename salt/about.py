"""
Summary:
    Copyright, legal plate for display with PACKAGE version information
Args:
    url_doc (str): http url location pointer to official PACKAGE documentation
    url_sc (str):  http url location pointer to PACKAGE source code
    current_year (int): the current calendar year (4 digit)
Returns:
    copyright, legal objects
"""

import sys
import datetime
from salt.statics import PACKAGE, LICENSE
from salt.colors import Colors
from salt import __version__


# copyright range thru current calendar year
current_year = datetime.datetime.today().year
copyright_range = str(current_year)

# python version number header
python_version = sys.version.split(' ')[0]
python_header = 'python' + Colors.RESET + ' ' + python_version

# formatted package header
package_name = Colors.BOLD + PACKAGE + Colors.RESET


# --- package about statement -------------------------------------------------


title_separator = (
    ('\t').expandtabs(4) +
    '________________________________________________________________________\n\n'
    )

package_header = (
    '\n\n\n    ' + Colors.CYAN + PACKAGE + Colors.RESET + ' version: ' + Colors.WHITE +
    Colors.BOLD + __version__ + Colors.RESET + '  |  ' + python_header + '\n\n\n'
    )

copyright = Colors.LT2GRAY + """
    ________________________________________________________________________

    Copyright """ + copyright_range + """, Blake Huber.  This program distributed under """ + LICENSE + """
    This copyright notice must remain with derivative works.""" + Colors.RESET + """
    ________________________________________________________________________
        """ + Colors.RESET

about_object = title_separator + package_header + copyright
