"""
Summary:
    saci (python3) | Create PDF from xml, html

Author:
    Blake Huber

OS Support:
    - RedHat Linux, Amazon Linux, Ubuntu & variants
    - Windows 7+

Dependencies:
    - Requires python3, tested under py3.5 and py3.6
    - Requires wkhtmltopdf, v0.12.4+ binary installed
"""

import os
import sys
import platform
import json
from configparser import ConfigParser
import argparse
import tempfile
import xmltodict
import inspect
import subprocess
import pdfkit
from saci.renderers import shortAnnotation, json2html
from saci.colors import Colors
from saci.help_menu import menu_body
from saci.script_utils import export_json_object, stdout_message, debug_mode
from saci.statics import PACKAGE, CONFIG_SCRIPT, local_config, BASEDIR
from saci import about, loggers, __version__

try:
    from saci.oscodes_unix import exit_codes
    splitchar = '/'     # character for splitting paths (linux)
except Exception:
    from saci.oscodes_win import exit_codes    # non-specific os-safe codes
    splitchar = '\\'    # character for splitting paths (window

# static globals
config = ConfigParser()
logger = loggers.getLogger(__version__)
TMPDIR = tempfile.gettempdir() + '/'


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
    if binary_check(binary='wkhtmltopdf', version='0.12.2'):
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


def options(parser, help_menu=False):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-i", "--input", nargs='?', default="aarti.xml", type=str,
                              required=False, help="type (default: %(default)s)")
    parser.add_argument("-o", "--output", nargs='?', default='myfile.pdf', type=str, required=False)
    parser.add_argument("-q", "--quiet", dest='quiet', action='store_true', required=False)
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


def build_controlresults(raw_list):
    """
    Summary:
        Transforms raw json from xml to formatted json dictionary object
    Args:
        - raw_list (dict): untransformed json object, direct xml import
        - transformed (list): container for all transformed control structures
    Returns:
        transformed, TYPE: list
    """
    transformed = []
    try:
        # loop thru each test transforming
        for test in raw_list:
            transformed.append(
                    {
                        'Result': test['@result'],
                        'failReason': test['failure']['message'] if test.get('failure') else 'NA',
                        'Offenders': ['Future Use'],
                        'ScoredControl': test['@executed'],
                        'Description': test['@description'],
                        'ControlId': test['@description'][:3]
                    }
                )
    except KeyError as e:
        logger.exception('Key not found (%s). Exit' % str(e))
        raise e
    return transformed


def pdf_generate(htmlReport, account):
    """Summary

    Args:
        htmlReport (TYPE): Description

    Returns:
        TYPE: Description
    """
    baseName = "cis_report_" + str(account) + "_" + str(datetime.now().strftime('%Y%m%d_%H%M'))

    # pdf report format
    pdfName = baseName + ".pdf"
    # html report format
    reportName = baseName + ".html"

    with tempfile.NamedTemporaryFile(delete=False) as f:
        for item in htmlReport:
            f.write(item.encode())
            f.flush()
            f.close()
            #os.unlink(f.name) -- causes exception when returning urls to caller
            try:
                with open(f.name) as f1:
                    newname = f1.name + '.html'
                    os.rename(f1.name, newname)
                    f1.close()
                    pdfkit.from_file(newname, TMPDIR + pdfName)
            except ClientError as e:
                logger.warning("Boto3 Error: Failed to upload report (pdf) to s3 (Code: %s Message: %s)" %
                        (e.response['Error']['Code'], e.response['Error']['Message']))
                return False
            except Exception as e:
                logger.warning("Unknown Error: Failed to upload report (pdf) to S3: " + str(e))
                return False
    return True


def main(infile, outfile, quiet, debug):
    """
    End-to-end renew of access keys for a specific profile in local awscli config
    """
    def readfile(fname):
        #basedir = os.path.dirname(sys.argv[0])
        basedir = os.getcwd()
        return open(os.path.join(basedir, fname)).read()

    account_name = 'Azure-test-account'
    account_number = '012345678912'
    cwd = os.getcwd()
    filepath = os.path.join(cwd, infile)
    print('filepath is: %s' % filepath)

    with open(os.path.join(cwd, infile)) as fd:
        doc = xmltodict.parse(fd.read())
        fd.close()

    controlResult = []
    results_list = doc['test-results']['test-suite']['results']['test-suite']['results']['test-suite']['results']['test-case']
    controlResult.append(build_controlresults(results_list))
    if debug:
        export_json_object(controlResult, 'testdata.json')
    # create html
    htmlReport = json2html(controlResult, account_number, account_name, 'azure')[0]
    sys.exit(0)
    try:
        pdf_generate(htmlReport, account_name)
        stdout_message('html file created (%s)' % outfile)
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
    return True


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

    else:
        if precheck():              # if prereqs set, run
            if args.debug:
                basedir = os.path.dirname(sys.argv[0])
                print('BASEDIR: %s' % BASEDIR)
                print('input file is: %s' % args.input)
                print('output file is: %s' % args.output)
                print('quiet is: %s' % args.quiet)
                print('debug is: %s' % args.debug)

            # execute operation
            success = main(
                        infile=args.input,
                        outfile=args.output,
                        quiet=args.quiet,
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
    failure = """ : Check of runtime parameters failed for unknown reason. Exit. Code: """
    logger.warning(failure + 'Exit. Code: %s' % sys.exit(exit_codes['E_MISC']['Code']))
    print(failure)


if __name__ == '__main__':
    init_cli()
