import os
import argparse
import sys
import logging

from blackduck import Client
from . import global_values

parser = argparse.ArgumentParser(description='Black Duck Signature component filter',
                                 prog='bd_sig_filter')

# parser.add_argument("projfolder", nargs="?", help="Yocto project folder to analyse", default=".")

parser.add_argument("--blackduck_url", type=str, help="Black Duck server URL (REQUIRED)", default="")
parser.add_argument("--blackduck_api_token", type=str, help="Black Duck API token (REQUIRED)", default="")
parser.add_argument("--blackduck_trust_cert", help="Black Duck trust server cert", action='store_true')
parser.add_argument("-p", "--project", help="Black Duck project to create (REQUIRED)", default="")
parser.add_argument("-v", "--version", help="Black Duck project version to create (REQUIRED)", default="")
parser.add_argument("--debug", help="Debug logging mode", action='store_true')
parser.add_argument("--logfile", help="Logging output file", default="")
parser.add_argument("--report_file", help="Report output file", default="")
parser.add_argument("--version_match_reqd", help="Component matches require version string in path", action='store_true')
parser.add_argument("--ignore", help="Ignore components in synopsys, default or test folders and duplicates with wrong version", action='store_true')
parser.add_argument("--review", help="Mark components reviewed", action='store_true')
parser.add_argument("--no_ignore_test", help="Do not ignore components in test folders", action='store_true')
parser.add_argument("--no_ignore_synopsys", help="Do not ignore components in synopsys tool folders", action='store_true')
parser.add_argument("--no_ignore_defaults", help="Do not ignore components in default folders", action='store_true')
parser.add_argument("--ignore_no_path_matches", help="Also ignore components with no component/version match in signature path", action='store_true')
parser.add_argument("--report_unmatched", help="Report unmatched (not reviewed or ignored) components", action='store_true')

args = parser.parse_args()

def check_args():
    terminate = False
    # if platform.system() != "Linux":
    #     print('''Please use this program on a Linux platform or extract data from a Yocto build then
    #     use the --bblayers_out option to scan on other platforms\nExiting''')
    #     sys.exit(2)
    if args.debug:
        global_values.debug = True
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    if args.logfile != '':
        if os.path.exists(args.logfile):
            logging.error(f"Specified logfile '{args.logfile}' already exists - EXITING")
            sys.exit(2)
        logging.basicConfig(encoding='utf-8',
                            handlers=[logging.FileHandler(args.logfile), logging.StreamHandler(sys.stdout)],
                            level=loglevel)
    else:
        logging.basicConfig(level=loglevel)

    logging.info("ARGUMENTS:")
    for arg in vars(args):
        logging.info(f"--{arg}={getattr(args, arg)}")
    logging.info('')

    url = os.environ.get('BLACKDUCK_URL')
    if args.blackduck_url != '':
        global_values.bd_url = args.blackduck_url
    elif url is not None:
        global_values.bd_url = url
    else:
        logging.error("Black Duck URL not specified")
        terminate = True

    if args.project != "" and args.version != "":
        global_values.bd_project = args.project
        global_values.bd_version = args.version
    else:
        logging.error("Black Duck project/version not specified")
        terminate = True

    api = os.environ.get('BLACKDUCK_API_TOKEN')
    if args.blackduck_api_token != '':
        global_values.bd_api = args.blackduck_api_token
    elif api is not None:
        global_values.bd_api = api
    else:
        logging.error("Black Duck API Token not specified")
        terminate = True

    trustcert = os.environ.get('BLACKDUCK_TRUST_CERT')
    if trustcert == 'true' or args.blackduck_trust_cert:
        global_values.bd_trustcert = True

    if args.version_match_reqd:
        global_values.version_match_reqd = True

    if args.ignore:
        global_values.ignore = True

    if args.review:
        global_values.review = True

    if args.no_ignore_test:
        global_values.no_ignore_test = True

    if args.no_ignore_synopsys:
        global_values.no_ignore_synopsys = True

    if args.no_ignore_defaults:
        global_values.no_ignore_defaults = True

    if args.ignore_no_path_matches:
        if not args.ignore:
            logging.warning(f"Option --ignore_no_path_matches set without --ignore")
        global_values.ignore_no_path_matches = True

    if args.report_file:
        if os.path.exists(args.report_file):
            logging.error(f"Report file '{args.report_file}' already exists - exiting")
            terminate = True
        global_values.report_file = args.report_file

    if args.report_unmatched:
        global_values.report_unmatched = True


    if terminate:
        sys.exit(2)
    return


def connect():
    if global_values.bd_url == '':
        return None

    bd = Client(
        token=global_values.bd_api,
        base_url=global_values.bd_url,
        timeout=30,
        verify=global_values.bd_trustcert  # TLS certificate verification
    )
    try:
        bd.list_resources()
    except Exception as exc:
        logging.warning(f'Unable to connect to Black Duck server - {str(exc)}')
        return None

    logging.info(f'Connected to Black Duck server {global_values.bd_url}')
    return bd
