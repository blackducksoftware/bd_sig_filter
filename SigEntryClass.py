from thefuzz import fuzz
import os
import re
import global_values
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

    def search_component(self, compname, compver):
        logging.debug(f"search_component() Checking Comp '{compname} {compver}' - {self.path}:")
        # If component_version_reqd:
        # - folder matches compname and compver
        # - folder1 matches compname and folder2 matches compver
        # Else:
        # - folder matches compname
        # Returns:
        # Bool1 - compname found
        # Bool2 - version found
        # Match_value - search result against both

        compstring = f"{compname} {compver}"
        element_in_compname = 0
        compver_in_element = 0

        found_compname_only = False
        for element in self.elements:
            pos = re.search(r"\.dll|\.obj|\.o|\.a|\.lib|\.iso|\.qcow2|\.vmdk|\.vdi|\.ova|\.nbi|\.vib|\.exe|\.img|"
                            "\.bin|\.apk|\.aac|\.ipa|\.msi|\.zip|\.gz|\.tar|\.xz|\.lz|\.bz2|\.7z|\.rar|"
                            "\.cpio|\.Z|\.lz4|\.lha|\.arj|\.jar|\.ear|\.war|\.rpm|\.deb|\.dmg|\.pki", element)
            if pos is not None:
                element = element[:pos.start()]
            # How much of the element string is from the compname and version?
            # - for example acl-1.3.0.jar
            # - Value of 100 indicates either compname or version exists in element
            element_in_compstring = fuzz.token_set_ratio(element, compstring)
            element_in_compname = fuzz.token_set_ratio(element, compname)
            compver_in_element = fuzz.token_set_ratio(compver, element)

            if element_in_compstring > 80:
                if compver_in_element > 50:
                    # element has both compname and version
                    logging.debug(f"search_component() - MATCHED component name & version ({compstring}) in '{element}'")
                    return True, True, element_in_compname + compver_in_element
                elif element_in_compname > 50 and len(element) > 2:
                    found_compname_only = True
                    logging.debug(f"search_component() - FOUND component name ONLY ({compname}) in '{element}'")
            elif found_compname_only:
                if compver_in_element > 50:
                    logging.debug(f"search_component() - MATCHED component version ({compver}) in '{element}'")
                    return True, True, element_in_compname + compver_in_element

        if found_compname_only:
            logging.debug("search_component() - MATCHED Compname only")
            return True, False, element_in_compname + compver_in_element

        logging.debug(f"search_component() - NOT MATCHED")
        return False, False, 0


    def filter_folders(self):
        # Return True if path should be ignored + reason
        if not global_values.no_ignore_synopsys:
            syn_folders = ['.synopsys', 'synopsys-detect', '.coverity', 'synopsys-detect.jar',
                           'scan.cli.impl-standalone.jar', 'seeker-agent.tgz', 'seeker-agent.zip',
                           'Black_Duck_Scan_Installation']
            for e in self.elements:
                if e in syn_folders:
                    return True, f"Found '{e}' in Signature match path '{self.path}'"

        if not global_values.no_ignore_defaults:
            def_folders = ['.cache', '.m2', '.local', '.cache','.config', '.docker', '.npm', '.npmrc', '.pyenv',
                           '.Trash', '.git', 'node_modules']
            for e in self.elements:
                if e in def_folders:
                    return True, f"Found '{e}' in Signature match path '{self.path}'"

        if not global_values.no_ignore_test:
            test_folders = ['test', 'tests']
            for e in self.elements:
                if e in test_folders:
                    return True, f"Found '{e}' in Signature match path '{self.path}'"

        return False, ''
