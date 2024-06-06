from thefuzz import fuzz
import os
import re
from . import global_values
import logging

class SigEntry:
    def __init__(self, src_entry):
        try:
            self.src_entry = src_entry
            self.path = src_entry['commentPath']
            elements = re.split(r"!|#|" + os.sep, self.path)
            # self.elements = self.path.replace("!", os.sep).replace("#", os.sep).split(os.sep)
            self.elements = list(filter(None, elements))

        except KeyError:
            return

    def search_component(self, compname_arr, compver):
        # logging.debug("")
        # logging.debug(f"search_component() Checking Comp '{compname}/{compver}' - {self.path}:")
        # If component_version_reqd:
        # - folder matches compname and compver
        # - folder1 matches compname and folder2 matches compver
        # Else:
        # - folder matches compname
        # Returns:
        # Bool1 - compname found
        # Bool2 - version found
        # Match_value - search result against both


        best_match_name = 0
        best_match_ver = 0
        # match_path = ''
        for cname in compname_arr:
            # compstring = f"{cname} {compver}"

            # test of path search
            newpath = self.path.replace(os.sep, " ")
            # comp_in_path = fuzz.token_set_ratio(compstring, newpath)
            compname_in_path = fuzz.token_set_ratio(cname, newpath)
            compver_in_path = fuzz.token_set_ratio(compver, newpath)
            if compname_in_path + compver_in_path > 100:
                if compname_in_path + compver_in_path > best_match_name + best_match_ver:
                    best_match_name = compname_in_path
                    best_match_ver = compver_in_path
                    # match_path = self.path
                    logging.debug(f"search_component(): TEST '{cname}/{compver}' - {compname_in_path,compver_in_path}: path='{self.path}")

        name_bool = False
        ver_bool = False
        if best_match_name > 45:
            name_bool = True
        if best_match_ver > 60:
            ver_bool = True

        return name_bool, ver_bool, best_match_name + best_match_ver
        # compstring = f"{compname} {compver}"
        # element_in_compname = 0
        # compver_in_element = 0
        # found_compname_only = False
        # for element in self.elements:
        #     pos = re.search(r"\.dll|\.obj|\.o|\.a|\.lib|\.iso|\.qcow2|\.vmdk|\.vdi|\.ova|\.nbi|\.vib|\.exe|\.img|"
        #                     "\.bin|\.apk|\.aac|\.ipa|\.msi|\.zip|\.gz|\.tar|\.xz|\.lz|\.bz2|\.7z|\.rar|"
        #                     "\.cpio|\.Z|\.lz4|\.lha|\.arj|\.jar|\.ear|\.war|\.rpm|\.deb|\.dmg|\.pki", element)
        #     if pos is not None:
        #         element = element[:pos.start()]
        #     # How much of the element string is from the compname and version?
        #     # - for example acl-1.3.0.jar
        #     # - Value of 100 indicates either compname or version exists in element
        #     element_in_compstring = fuzz.token_set_ratio(element, compstring)
        #     element_in_compname = fuzz.token_set_ratio(element, compname)
        #     compver_in_element = fuzz.token_set_ratio(compver, element)
        #
        #     if element_in_compstring > 80:
        #         if compver_in_element > 50:
        #             # element has both compname and version
        #             logging.debug(f"search_component() - MATCHED component name & version ({compstring}) in '{element}'")
        #             return True, True, element_in_compname + compver_in_element
        #         elif element_in_compname > 50 and len(element) > 2:
        #             found_compname_only = True
        #             logging.debug(f"search_component() - FOUND component name ONLY ({compname}) in '{element}'")
        #     elif found_compname_only:
        #         if compver_in_element > 50:
        #             logging.debug(f"search_component() - MATCHED component version ({compver}) in '{element}'")
        #             return True, True, element_in_compname + compver_in_element
        #         else:
        #             test = 1
        #
        # if found_compname_only:
        #     logging.debug("search_component() - MATCHED Compname only")
        #     return True, False, element_in_compname + compver_in_element
        #
        # logging.debug(f"search_component() - NOT MATCHED")


    def filter_folders(self):
        # Return True if path should be ignored + reason
        if not global_values.no_ignore_synopsys:
            # syn_folders = ['.synopsys', 'synopsys-detect', '.coverity', 'synopsys-detect.jar',
            #                'scan.cli.impl-standalone.jar', 'seeker-agent.tgz', 'seeker-agent.zip',
            #                'Black_Duck_Scan_Installation']

            syn_folders_re = (f"{os.sep}(\.synopsys|synopsys-detect|\.coverity|synopsys-detect.*\.jar|scan\.cli\.impl-standalone\.jar|"
                              f"seeker-agent.*|Black_Duck_Scan_Installation){os.sep}")
            res = re.search(syn_folders_re, self.path)
            if res:
                return True, f"Found {res.group()} folder in Signature match path '{self.path}'"

        if not global_values.no_ignore_defaults:
            # def_folders = ['.cache', '.m2', '.local', '.cache','.config', '.docker', '.npm', '.npmrc', '.pyenv',
            #                '.Trash', '.git', 'node_modules']
            def_folders_re = (f"{os.sep}(\.cache|\.m2|\.local|\.config|\.docker|\.npm|\.npmrc|"
                              f"\.pyenv|\.Trash|\.git|node_modules){os.sep}")
            res = re.search(def_folders_re, os.sep + self.path + os.sep)
            if res:
                return True, f"Found {res.group()} folder in Signature match path '{self.path}'"

        if not global_values.no_ignore_test:
            test_folders = f"{os.sep}(test|tests|testsuite){os.sep}"
            res = re.search(test_folders, os.sep + self.path + os.sep, flags=re.IGNORECASE)
            if res:
                return True, f"Found {res.group()} in Signature match path '{self.path}'"
                # if e in test_folders:
                #     return True, f"Found '{e}' in Signature match path '{self.path}'"

        return False, ''

    def get_sigpath(self):
        return(f"- {self.path}")