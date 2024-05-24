from thefuzz import fuzz
import os
import re
import global_values

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
        print(f"Checking Comp '{compname} {compver}' - {self.path}:")
        # If component_version_reqd:
        # - folder matches compname and compver
        # - folder1 matches compname and folder2 matches compver
        # Else:
        # - folder matches compname

        compstring = f"{compname} {compver}"

        max_set_ratio = 0
        set_ratio_match = ''
        max_sort_ratio = 0
        for element in self.elements:
            set_ratio = fuzz.token_set_ratio(element, compstring)
            # how much of the folder name exists in the component
            if set_ratio > max_set_ratio:
                sort_ratio = fuzz.token_sort_ratio(element, compstring)
                # print(f"- INTERMEDIATE {element} - {set_ratio},{sort_ratio}")
                if sort_ratio > 45:
                    match = True
                    if global_values.version_match_reqd:
                        ver_ratio = fuzz.token_set_ratio(compver, element)
                        if ver_ratio < 70:
                            match = False

                    if match:
                        max_set_ratio = set_ratio
                        max_sort_ratio = sort_ratio
                        set_ratio_match = element

        print(f"- FINAL {set_ratio_match} - {max_set_ratio},{max_sort_ratio}")
        return max_set_ratio,max_sort_ratio

    def filter_folders(self):
        # Return True if path should be ignored
        syn_folders = ['.synopsys', 'synopsys-detect', '.coverity', 'synopsys-detect.jar',
                       'scan.cli.impl-standalone.jar', 'seeker-agent.tgz', 'seeker-agent.zip',
                       'Black_Duck_Scan_Installation']
        for e in syn_folders:
            if e in self.elements:
                return True, f"Found {e} in Signature match path"

        def_folders = ['.cache', '.m2', '.local', '.cache','.config', '.docker', '.npm', '.npmrc', '.pyenv',
        '.Trash', '.git', 'node_modules']
        for e in def_folders:
            if e in self.elements:
                return True, f"Found {e} in Signature match path"

        return False, ''
