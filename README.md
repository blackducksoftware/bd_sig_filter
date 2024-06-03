# bd_sig_filter
BD Script to ignore components matched from Signature scan likely to be partial or invalid matches.

## PROVISION OF THIS SCRIPT
This script is provided under the MIT OSS license (see LICENSE file).
It does not represent any extension of licensed functionality of Synopsys software itself and is provided as-is, without warranty or liability.
If you have comments or issues, please raise a GitHub issue here. Synopsys support is not able to respond to support tickets for this OSS utility. Users of this pilot project commit to engage properly with the authors to address any identified issues.

## INTRODUCTION
Black Duck Signature matching is a unique and powerful way to find OSS and 3rd party code within your applications and
environments.

Signature matching uses hierarchical folder analysis to find matches with depth, identifying the most likely components matching the project.
Many competitive SCA solutions use individual file matching across all files in the project which is not effective 
to identify component matches because the majority of files in a component do not change between versions, 
so multiple matches will be identified for every file.

However, Signature matching can still produce false positive matches, especially where template code hierarchies 
exist in custom and OSS code.

Furthermore, Signature matches can be identified in folders created by Synopsys tools, or in cache/config
locations or test folders; these folders can be ignored at scan time, but can exist in the Black Duck project and need to 
be removed after scan completion. Additionally, when scanning
modified OSS, Signature scanning can identify the same component with multiple versions from a single project
location, with the need to curate the BOM to ignore duplicate components.

This script uses several techniques to examine the Signature match paths for components, searching for the component
name and version in the path to determine matches which are likely correct and optionally marking them as reviewed.

It can also ignore components only matched from paths which should be excluded (Synopsys tools, cache/config folders 
and test folders), and components which are duplicates across versions where the version string is not found
in the signature match path.

Options can be used to enable ignore and review actions, and other features.

## PREREQUISITES

Python 3.8+ must be installed prior to using this script.

## INSTALLATION

The package can be installed using the command:

    python3 -m pip install bd-sig-filter

Upgrade from a previous version using:

    python3 -m pip install bd-sig-filter --upgrade

Alternatively, the repository can be cloned and the script run directly using the command:

    python3 bd_sig_filter/bd_sig_filter.py OPTIONS

## USAGE

If installed as a package, run the utility using the command `bd-sig-filter`.

Alternatively if you have cloned the repo, use a command similar to:

    python3 bd_sig_filter/bd_sig_filter.py OPTIONS

The package can be invoked as follows:

    usage: bd_sig_filter [-h] [--blackduck_url BLACKDUCK_URL] [--blackduck_api_token BLACKDUCK_API_TOKEN] [--blackduck_trust_cert] [-p PROJECT] [-v VERSION] [--debug] [--logfile LOGFILE]
                         [--report_file REPORT_FILE] [--version_match_reqd] [--ignore] [--review] [--no_ignore_test] [--no_ignore_synopsys] [--no_ignore_defaults]
                         [--ignore_no_path_matches]

    options:
      -h, --help            show this help message and exit 
      --blackduck_url BLACKDUCK_URL
                            Black Duck server URL (REQUIRED)
      --blackduck_api_token BLACKDUCK_API_TOKEN
                            Black Duck API token (REQUIRED)
      --blackduck_trust_cert
                            Black Duck trust server cert
      -p PROJECT, --project PROJECT
                            Black Duck project to create (REQUIRED)
      -v VERSION, --version VERSION
                            Black Duck project version to create (REQUIRED)
      --debug               Debug logging mode
      --logfile LOGFILE     Logging output file
      --report_file REPORT_FILE
                            Report output file
      --version_match_reqd  Component matches require version string in path
      --ignore              Ignore components in synopsys, default or test folders and duplicates with wrong version
      --review              Mark components reviewed
      --no_ignore_test      Do not ignore components in test folders
      --no_ignore_synopsys  Do not ignore components in synopsys tool folders
      --no_ignore_defaults  Do not ignore components in default folders
      --ignore_no_path_matches
                            Also ignore components with no component/version match in signature path
                            (Use with caution)

The minimum required options are:
    
    --blackduck_url https://BLACKDUCK_SERVER_URL
    --blackduck_api_token BLACKDUCK_API_TOKEN
    --project PROJECT
    --version VERSION

Environment variables BLACKDUCK_URL, BLACKDUCK_API_TOKEN and BLACKDUCK_TRUST_CERT may also be used.

## SCRIPT BEHAVIOUR
The default behaviour of the script is to create a table of BOM components with details about what actions can be taken.
By default no actions will be taken, with only the table being created.

An example of the output table is shown below:

    SUMMARY:
              Components    Ignored    Reviewed    Neither
    ------  ------------  ---------  ----------  ---------
    Before           641          0           0        641
    After            641         24         615          2
    
    Component                             Match Type    Ignored    Reviewed    To be Ignored    To be Reviewed    Action
    ------------------------------------  ------------  ---------  ----------  ---------------  ----------------  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    aggs-matrix-stats/1.3.14              Dep+Sig       False      False       False            True              Mark REVIEWED - Dependency
    aggs-matrix-stats/2.11.1              Sig           False      False       False            True              Mark REVIEWED - Compname & version in path '/Plugins/ActOnePluginInstaller/image/actone-plugins-installer 10.0.0.67/RCM_Plugins/actOne-opensearch-2.x-connector/lib/aggs-matrix-stats-client-2.11.1.jar', Match result 200
    aircompressor/0.10                    Dep+Sig       False      False       False            True              Mark REVIEWED - Dependency
    Amazon MSK Library for AW/2.0.2       Dep+Sig       False      False       False            True              Mark REVIEWED - Dependency
    Apache HttpComponents Cor/5.2.4       Sig           False      False       True             False             Mark IGNORED - compname or version not found in paths & --ignore_no_path_matches set
    WSDL4J/1.5.1                          Sig           False      False       False            False             No Action

Note component names are truncated at 25 characters.

The `Before` and `After` rows in the SUMMARY list the total number of components, and how many components would be ignored or
marked reviewed by the script (if the `--ignore` and `--review` options are supplied).

The list of components shows the name, matchtypes and current ignore/review statuses, with the future status
(after running the script with the `--ignore` and `--review` options) in the `To Be Ignored` and `To Be Reviewed` 
columns with an explanation in the `Action` column.

The following options can be specified:

    --ignore:               Ignore components as shown in the `To Be Ignored` column
    --review:               Mark components as reviewed as shown in the `To Be Reviewed` column
    --no_ignore_test:       Do not ignore components with signature paths within test folders
    --no_ignore_synopsys:   Do not ignore components with signature paths within Synopsys tools folders (for example '.synopsys')
    --no_ignore_defaults:   Do not ignore components with signature paths in cache/config folders (for example '.git', '.m2', '.local')
    --version_match_required:
                            Enforce search for component version string in signature paths for marking reviewed
                            (Paths containing only the component name will be used for matching otherwise)
    --ignore_no_path_matches:
                            Components with no match in the signature path are left unreviewed by default, allowing
                            manual review. Use this option to ignore these components instead but use with caution
                            as it may exclude components which are legitimate (the Signature match path does not
                            have to include the component name or version).

The options --report_file and --logfile can be used to output the tabular report and logging data to
specified files.

## PROPOSED WORKFLOW

The script provides automatic classification of Signature scan results.

It can mark components as reviewed which are either Dependencies, or which have signature match paths containing
the component name (and optionally component version) and therefore highly likely to be correctly identified
by Signature matching. Fuzzy pattern matching is used so there is the possibility
that components could be marked as reviewed where only a partial match exists, or components which should be matched
are not identified meaning that manual curation may still be required.

It will also ignore components only matched within extraneous folders (for example created by Synopsys tools, 
config/cache folders or test folders).

Components shown with `No action` are Signature matches where the component name or version 
could not be identified in the signature paths, so they are potential false matches and require manual review.
Specify the `--ignore_no_path_matches` option to ignore these components automatically.
Duplicate components with multiple versions where the version 
is not found in the signature match path are also marked as ignored.

