"""
Summary:
    salt (python3) | Create PDF from xml, html

Author:
    Blake Huber
    Copyright Blake Huber, All Rights Reserved.

License:
    Apache License Version 2.0
    Additional terms may be found in the complete license agreement:
    https://github.com/fstab50/salt/blob/master/LICENSE.txt

OS Support:
    - RedHat Linux, Amazon Linux, Ubuntu & variants
    - Windows 7+

Dependencies:
    - Requires python3, tested under py3.5 and py3.6
"""

import os
import sys
import platform
from configparser import ConfigParser
import argparse
import xmltodict
from collections import OrderedDict
import inspect
import subprocess
from salt.renderers import shortAnnotation, json2html
from salt.colors import Colors
from salt.statics import PACKAGE, CONFIG_SCRIPT, local_config
from salt.help_menu import menu_body
from salt.script_utils import stdout_message, debug_mode
from salt import about, logd, __version__

try:
    from salt.oscodes_unix import exit_codes
    splitchar = '/'     # character for splitting paths (linux)
except Exception:
    from salt.oscodes_win import exit_codes    # non-specific os-safe codes
    splitchar = '\\'    # character for splitting paths (window

# global objects
config = ConfigParser()
logger = logd.getLogger(__version__)

# global vars
VALID_OPERATIONS = ('test', 'write')
REPORT_OPERATIONS = ('up', 'keyup', 'rotate')


def help_menu():
    """
    Displays help menu contents
    """
    print(
        Colors.BOLD + '\n\t\t\t  ' + PACKAGE + Colors.RESET +
        ' help contents'
        )
    print(menu_body)
    return


def parse_awscli():
    """
    Summary:
        parse, update local awscli config credentials
    Args:
        :user (str):  USERNAME, only required when run on windows os
    Returns:
        TYPE: configparser object, parsed config file
    """
    OS = platform.system()
    if OS == 'Linux':
        HOME = os.environ['HOME']
        default_credentials_file = HOME + '/.aws/credentials'
        alt_credentials_file = shared_credentials_location()
        awscli_file = alt_credentials_file or default_credentials_file
    elif OS == 'Windows':
        win_username = os.getenv('username')
        default_credentials_file = 'C:\\Users\\' + win_username + '\\.aws\\credentials'
        alt_credentials_file = shared_credentials_location()
        awscli_file = alt_credentials_file or default_credentials_file
    else:
        logger.warning('Unsupported OS. Exit')
        logger.warning(exit_codes['E_ENVIRONMENT']['Reason'])
        sys.exit(exit_codes['E_ENVIRONMENT']['Code'])

    try:
        if os.path.isfile(awscli_file):
            # parse config
            config.read(awscli_file)
        else:
            logger.info(
                'awscli credentials file [%s] not found. Abort' % awscli_file
            )
            raise OSError
    except Exception as e:
        logger.exception(
            '%s: problem parsing local awscli config file %s' %
            (inspect.stack()[0][3], awscli_file))
    return config, awscli_file


def set_logging(cfg_obj):
    """
    Enable or disable logging per config object parameter
    """
    log_status = cfg_obj['LOGGING']['ENABLE_LOGGING']

    if log_status:
        logger.disabled = False
    elif not log_status:
        logger.info(
            '%s: Logging disabled per local configuration file (%s) parameters.' %
            (inspect.stack()[0][3], cfg_obj['PROJECT']['CONFIG_PATH'])
            )
        logger.disabled = True
    return log_status


def binary_check(binary, version, parameter=None):
    """
    Summary:
        Validates installation and version of 3rd party binary
    Platform:
        - Linux, Windows
    Args:
        - binary (str): binary executable to validate
        - version (str): min acceptable binary version number
        - parameter (str): cmd line parameter (switch) required to return
              binary version. if None, defaults to ``--version``
    Returns:
        Success | Failure, TYPE: bool
    """
    if parameter is None:
        parameter = '--version'
    if platform.system() == 'Linux':
        cmd = binary + ' ' + parameter + ' 2>/dev/null'
    elif platform.system() == 'Windows':
        cmd = binary + ' ' + parameter + ' 2>&1 | out-null'
    if subprocess.getoutput(cmd):
        try:
            output = subprocess.getoutput(cmd)
            reported_version = output.split()[1]
            if reported_version >= version:
                return True
            else:
                logger.warning(
                    '%s: Binary version (%s, %s) not adequate (required = %s)' %
                    (inspect.stack()[0][3], binary, version, reported_version))
        except NameError as e:
            logger.info('%s: binary application not installed (%s)' % str(e))
        except Exception as e:
            logger.warning('failed to execute command (%s)' % str(e))
    return False


def precheck(status=False):
    """
    Verify project runtime dependencies
    """
    cfg_path = local_config['PROJECT']['CONFIG_PATH']
    # enable or disable logging based on config/ defaults
    logging = set_logging(local_config)
    if binary_check(binary='wkhtmltopdf', version='0.12.4'):
        if os.path.exists(cfg_path):
            logger.info('%s: config_path parameter: %s' % (inspect.stack()[0][3], cfg_path))
            logger.info(
                '%s: Existing configuration file found. precheck pass.' %
                (inspect.stack()[0][3]))
            return True
        elif not os.path.exists(cfg_path) and logging is False:
            logger.info(
                '%s: No pre-existing configuration file found at %s. Using defaults. Logging disabled.' %
                (inspect.stack()[0][3], cfg_path)
                )
            return True
        if logging:
            logger.info(
                '%s: Logging enabled per config file (%s).' %
                (inspect.stack()[0][3], cfg_path))
    return status


def main(operation, auto, debug):
    """
    End-to-end renew of access keys for a specific profile in local awscli config
    """
    if user_name:
        logger.info('user_name parameter given (%s) as surrogate' % user_name)

    # find out to which iam user profile name maps
    user, aws_account = map_identity(profile=profile)
    try:
        if operation in REPORT_OPERATIONS:
            # check local awscli config for active temporary sts credentials
            if clean_config(quiet=auto):
                keylist, key_metadata = list_keys(
                        account=aws_account,
                        profile=profile,
                        iam_user=user,
                        surrogate=user_name,
                        stage='BEFORE ROTATION',
                        quiet=auto
                    )
        elif operation == 'list':
            # list operation; display current access key(s) and exit
            keylist, key_metadata = list_keys(
                    account=aws_account, profile=profile, iam_user=user,
                    surrogate=user_name, quiet=auto
                )
            return True
        elif not operation:
            msg_accent = (Colors.BOLD + 'list' + Colors.RESET + ' | ' + Colors.BOLD + 'up' + Colors.RESET)
            msg = """You must provide a valid OPERATION for --operation parameter:

                    --operation { """ + msg_accent + """ }
            """
            stdout_message(msg)
            logger.warning('%s: No valid operation provided. Exit' % (inspect.stack()[0][3]))
            sys.exit(exit_codes['E_MISC']['Code'])
        else:
            msg = 'Unknown operation. Exit'
            stdout_message(msg)
            logger.warning('%s: %s' % (msg, inspect.stack()[0][3]))
            sys.exit(exit_codes['E_MISC']['Code'])
    except KeyError as e:
        logger.critical(
            '%s: Cannot find Key %s' %
            (inspect.stack()[0][3], str(e)))
        return False
    except OSError as e:
        logger.critical(
            '%s: problem writing to file %s. Error %s' %
            (inspect.stack()[0][3], output_file, str(e)))
        return False
    except Exception as e:
        logger.critical(
            '%s: Unknown error. Error %s' %
            (inspect.stack()[0][3], str(e)))
        raise e


def options(parser, help_menu=False):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-p", "--profile", nargs='?', default="default",
                              required=False, help="type (default: %(default)s)")
    parser.add_argument("-o", "--operation", nargs='?', default='list', type=str,
                        choices=VALID_OPERATIONS, required=False)
    parser.add_argument("-a", "--auto", dest='auto', action='store_true', required=False)
    parser.add_argument("-c", "--configure", dest='configure', action='store_true', required=False)
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def package_version():
    """
    Prints package version and requisite PACKAGE info
    """
    print(about.about_object)
    sys.exit(exit_codes['EX_OK']['Code'])


def option_configure(debug=False, path=None):
    """
    Summary:
        Initiate configuration menu to customize keyup runtime options.
        Console script ```keyconfig``` invokes this option_configure directly
        in debug mode to display the contents of the local config file (if exists)
    Args:
        :path (str): full path to default local configuration file location
        :debug (bool): debug flag, when True prints out contents of local
         config file
    Returns:
        TYPE (bool):  Configuration Success | Failure
    """
    if CONFIG_SCRIPT in sys.argv[0]:
        debug = True    # set debug mode if invoked from CONFIG_SCRIPT
    if path is None:
        path = local_config['PROJECT']['CONFIG_PATH']
    if debug:
        if os.path.isfile(path):
            debug_mode('local_config file: ', local_config, debug, halt=True)
        else:
            msg = """  Local config file does not yet exist. Run:

            $ keyup --configure """
            debug_mode(msg, {'CONFIG_PATH': path}, debug, halt=True)
    r = configuration.init(debug, path)
    return r


def init_cli():
    """ Initialize setup, check dependencies """
    parser = argparse.ArgumentParser(add_help=False)

    try:
        args = options(parser)
    except Exception as e:
        help_menu()
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['EX_OK']['Code'])

    if len(sys.argv) == 1:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.help:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.version:
        package_version()

    #elif args.configure:
    #    r = option_configure(args.debug, local_config['PROJECT']['CONFIG_PATH'])
    #    return r
    else:
        if precheck():              # if prereqs set, run
            # execute operation
            success = main(
                        operation=args.operation,
                        auto=args.auto,
                        debug=args.debug
                        )
            if success:
                logger.info('PDF generation complete')
                sys.exit(exit_codes['EX_OK']['Code'])
            else:
                stdout_message(
                    'Precheck (dependency) Fail. Exit %s' % str(args),
                    prefix='WARN',
                    severity='WARNING'
                    )
                sys.exit(exit_codes['E_AUTHFAIL']['Code'])
    # precheck fail
    failure = """ : Check of runtime parameters failed for unknown reason.
    Please ensure local awscli is configured. Then run keyconfig to
    configure keyup runtime parameters.   Exiting. Code: """
    logger.warning(failure + 'Exit. Code: %s' % sys.exit(exit_codes['E_MISC']['Code']))
    print(failure)
    sys.exit(0)


def strip_keys(process):
    """
    Strips @ symbol if present in keynames

    THIS NEEDS MICHAL'S FUNCTION WHICH WALKS THE DICT TO PROCESS NESTED
    KEY,VALUE PAIRS UNTIL REACHES BOTTOM LEVEL
    """
    processed = {}
    try:
        while True:
            for key, value in processed.items():
                if '@' in key:
                    processed[key[1:]] = value
    except KeyError as e:
        logger.exception(
            '%s: Error when attempting to strip keys (%s)' %
            (inspect.stack()[0][3], str(e)))
    return processed


def build_controlresult(raw_dict):
    """
    Summary:
        Transforms raw json from xml to formatted json dictionary object
    Args:
        - raw_dict (dict): untransformed json object, direct xml import
        - transformed (list): container for all transformed control structures
        - cleaned (dict): raw_dict with keys stripped of special characters
        - temp_dict (dict): temporary json container for a single control
    Returns:
        transformed, TYPE: list
    """
    transformed = []
    cleaned = strip_keys(raw_dict)
    for k,v in clean.items():
        temp_dict = {}
        temp_dict['scorded'] = cleaned['executed']  # INSTEAD OF CLEAN, SHOULD TRAVERSE ANY DICT FOUND IN 'v' (values)
        temp_dict['result'] = cleaned['result']
        temp_dict['control'] = cleaned['name']
        transformed.append(
                {
                    'Result': cleaned['result'],
                    'failReason': failReason,
                    'Offenders': report,
                    'ScoredControl': cleaned['scored'],
                    'Description': cleaned['description'],
                    'ControlId': cleaned['name']
                }
            )


if __name__ == '__main__':
    #init_cli()
    with open('results.xml') as fd:
        doc = xmltodict.parse(fd.read())
        fd.close()
    controlResult = build_controlresult(doc['test-results']['test-suite'])
    print(json.dumps(controlResult, indent=4, sort_keys=True))
    sys.exit(0)
