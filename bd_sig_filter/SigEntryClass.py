from thefuzz import fuzz
import os
import re
from . import global_values
import logging
import json

class SigEntry:
    def __init__(self, src_entry):
        try:
            self.src_entry = src_entry
            self.path = src_entry['commentPath']
            elements = re.split(r"!|#|" + os.sep, self.path)
            self.elements = list(filter(None, elements))

        except KeyError:
            return

    def search_component(self, compname_arr, compver):
        # If component_version_reqd:
        # - folder matches compname and compver
        # - folder1 matches compname and folder2 matches compver
        # Else:
        # - folder matches compname
        # Returns:
        # - Bool1 - compname found
        # - Bool2 - version found
        # - Match_value - search result against both


        best_match_name = 0
        best_match_ver = 0
        name_bool = False
        ver_bool = False
        # match_path = ''
        for cname in compname_arr:
            # compstring = f"{cname} {compver}"

            # test of path search
            rep = f"[{os.sep}!#]"
            newpath = re.sub(rep, ' ', self.path).lower()
            compname_setratio = fuzz.token_set_ratio(cname, newpath)
            # compname_sortratio = fuzz.token_sort_ratio(cname, newpath)
            # compname_partialratio = fuzz.partial_ratio(cname, newpath)
            # compver_setratio = fuzz.token_set_ratio(compver, newpath)
            # compver_sortratio = fuzz.token_sort_ratio(compver, newpath)
            compver_partialratio = fuzz.partial_ratio(compver, newpath)

            if compname_setratio + compver_partialratio > best_match_name + best_match_ver:
                best_match_name = compname_setratio
                best_match_ver = compver_partialratio
                logging.debug(f"search_component(): TEST '{cname}/{compver}' - {compname_setratio,compver_partialratio}: path='{self.path}")

        if best_match_name > 45:
            name_bool = True
        if best_match_ver > 80:
            ver_bool = True
        return name_bool, ver_bool, best_match_name + best_match_ver


    def filter_folders(self):
        # Return True if path should be ignored + reason
        if not global_values.no_ignore_synopsys:
            syn_folders_re = (f"\\{os.sep}(\.synopsys|synopsys-detect|\.coverity|synopsys-detect.*\.jar|scan\.cli\.impl-standalone\.jar|"
                              f"seeker-agent.*|Black_Duck_Scan_Installation)\\{os.sep}")
            res = re.search(syn_folders_re, os.sep + self.path + os.sep)
            if res:
                return True, f"Found {res.group()} folder in Signature match path '{self.path}'"

        if not global_values.no_ignore_defaults:
            def_folders_re = (f"\\{os.sep}(\.cache|\.m2|\.local|\.config|\.docker|\.npm|\.npmrc|"
                              f"\.pyenv|\.Trash|\.git|node_modules)\\{os.sep}")
            res = re.search(def_folders_re, os.sep + self.path + os.sep)
            if res:
                return True, f"Found {res.group()} folder in Signature match path '{self.path}'"

        if not global_values.no_ignore_test:
            test_folders = f"\\{os.sep}(test|tests|testsuite|testsuites)\\{os.sep}"
            res = re.search(test_folders, os.sep + self.path + os.sep, flags=re.IGNORECASE)
            if res:
                return True, f"Found {res.group()} in Signature match path '{self.path}'"

        return False, ''

    def get_sigpath(self):
        return(f"- {self.path}")

    def json(self):
        data = {
            'name': self.src_entry['name'],
            'compositePath': self.src_entry['name']
        }

    def get_data(self):
        data = {
            'size': self.src_entry['size'],
            'type': self.src_entry['type'],
            'path': self.src_entry['compositePath']['path'],
            'sigMatch': self.src_entry['fileSignaturePair']['signatureType']
        }
        return data

    def __str__(self):
        goodkeys = ["scanId",
                "name",
                "size",
                "type",
                "compositePath",
                "fileSignaturePair",
                "fileMatchBomComponent",
                "fileDependencyBomComponents",
                "partialFileMatchBomComponents",
                "binaryFileMatchBomComponents",
                "fileSnippetBomComponents",
                "fileStringSearchMatches",
                "policyApprovalStatus",
                "activePolicies",
                "uri",
                "policyOverriddenBySet",
                "fileMatchComponentUsage"]

        newdata = {}

        for key in self.src_entry.keys():
            if key in goodkeys:
                newdata[key] = self.src_entry[key]

        return(json.dumps(newdata, indent=4))