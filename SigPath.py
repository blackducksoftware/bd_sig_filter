from thefuzz import fuzz
import os
import re

class SigPath:
    def __init__(self, path):
        self.path = path
        self.elements = re.split(r"!|#|" + os.sep, path)

    def search_component(self, compname, compver):
        print(f"Comp '{compname}' Ver {compver}: {self.path} - {fuzz.token_sort_ratio(self.path, compname)}")

    def filter_folders(self):
        # Return True if path should be ignored
        syn_folders = ['.synopsys', 'synopsys-detect', '.coverity',
                       'scan.cli.impl-standalone.jar', 'seeker-agent.tgz', 'seeker-agent.zip']
        for e in syn_folders:
            if e in self.elements:
                return True

        def_folders = ['.cache', '.m2', '.local', '.cache','.config', '.docker', '.npm', '.npmrc', '.pyenv',
        '.Trash', '.git', 'node_modules']
        for e in def_folders:
            if e in self.elements:
                return True

        return False
