"""

Help Menu
    Help menu object containing body of help content.
    For printing with formatting

"""

from salt.statics import PACKAGE, CONFIG_SCRIPT
from salt.colors import Colors


PKG_ACCENT = Colors.ORANGE
PARAM_ACCENT = Colors.WHITE


synopsis_cmd = (
    Colors.RESET + PKG_ACCENT + PACKAGE +
    PARAM_ACCENT + ' --profile ' + Colors.RESET + ' [PROFILE] ' +
    PARAM_ACCENT + '--operation ' + Colors.RESET + '[OPERATION]'
    )

url_sc = Colors.URL + 'https://github.com/fstab50/salt' + Colors.RESET

menu_body = Colors.BOLD + """
  DESCRIPTION""" + Colors.RESET + """
            PDF Report Generation (xml, html source)

            Source Code:  """ + url_sc + """
    """ + Colors.BOLD + """
  SYNOPSIS""" + Colors.RESET + """
                """ + synopsis_cmd + """

                    -o, --operation  <value>
                   [-q, --quiet     ]
                   [-V, --version  ]
                   [-d, --debug    ]
                   [-h, --help     ]
    """ + Colors.BOLD + """
  OPTIONS
        -p, --profile""" + Colors.RESET + """ (string) : another option
            slkdjflkjflsjfkjskfj
    """ + Colors.BOLD + """
        -o, --operation""" + Colors.RESET + """ (string) :
    """ + Colors.BOLD + """
        -?, --?????""" + Colors.RESET + """ (string) : this line can stretch to column 100
            lipsum
    """ + Colors.BOLD + """
        -a, --auto""" + Colors.RESET + """ : Suppress output to stdout when """ + PACKAGE + """ triggered via a sched-
            uler such as cron (Linux) or Windows scheduler
    """ + Colors.BOLD + """
        -c, --configure""" + Colors.RESET + """ :  Configure parameters to custom values. If the local
            config file does not exist, option writes a new local configuration
            file to disk.  If file exists, overwrites existing config with up-
            dated values

               Configure runtime options:   |   Display local config file:
                                            |
                  $ """ + PKG_ACCENT + PACKAGE + PARAM_ACCENT + ' --configure' + Colors.RESET + """       |       $ """ + PKG_ACCENT + CONFIG_SCRIPT + PARAM_ACCENT + """
    """ + Colors.BOLD + """
        -d, --debug""" + Colors.RESET + """ : when True, do not write out an actual pdf document.
            Run diagnostics showing user title of report and filesystem
            when generated
    """ + Colors.BOLD + """
        -V, --version""" + Colors.RESET + """ : Print package version
    """ + Colors.BOLD + """
        -h, --help""" + Colors.RESET + """ : Show this help message and exit

    """
