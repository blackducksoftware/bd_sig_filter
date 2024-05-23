from SigPath import SigPath

class Component:
    def __init__(self, name, version, data):
        self.name = name
        self.version = version
        self.data = data
        self.src_arr = []
        self.ignore = False
        self.mark_reviewed = False

    def get_compverid(self):
        try:
            return self.data['componentVersion'].split('/')[-1]
        except KeyError:
            return ''

    def add_src(self, src_entry):
        self.src_arr.append(src_entry)

    def get_matchtypes(self):
        try:
            return self.data['matchTypes']
        except KeyError:
            return []

    def is_dependency(self):
        dep_types = ['FILE_DEPENDENCY_DIRECT', 'FILE_DEPENDENCY_TRANSITIVE']
        match_types = self.get_matchtypes()
        for m in dep_types:
            if m in match_types:
                return True
        return False

    def is_signature(self):
        sig_types = ['FILE_EXACT', 'FILE_SOME_FILES_MODIFIED']
        match_types = self.get_matchtypes()
        for m in sig_types:
            if m in match_types:
                return True
        return False

    def is_only_signature(self):
        return (not self.is_dependency() and self.is_signature())

    def set_ignore(self):
        self.ignore = True

    def get_reviewed_status(self):
        try:
            if self.data['reviewStatus'] == 'REVIEWED':
                return True
        except KeyError:
            return False
        return False

    def set_reviewed(self):
        if not self.get_reviewed_status():
            self.mark_reviewed = True
        return

    def is_ignored(self):
        try:
            return self.data['ignored']
        except KeyError:
            return False

    def process_signature(self):
        for src in self.src_arr:
            try:
                sigpath = SigPath(src['commentPath'])
                if sigpath.filter_folders():
                    # Ignore
                    print(f"Ignoring {src['commentPath']}")
                    self.set_ignore()
                    continue

                sigpath.search_component(self.name, self.version)
                # print(self.name, self.version, src['commentPath'])
            except KeyError:
                continue
