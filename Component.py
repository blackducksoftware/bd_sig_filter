from SigEntry import SigEntry

class Component:
    def __init__(self, name, version, data):
        self.name = name
        self.version = version
        self.data = data
        self.sigentry_arr = []
        self.ignore = False
        self.mark_reviewed = False

    def get_compverid(self):
        try:
            return self.data['componentVersion'].split('/')[-1]
        except KeyError:
            return ''

    def add_src(self, src_entry):
        sigentry = SigEntry(src_entry)
        self.sigentry_arr.append(sigentry)

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

    def process_signatures(self):
        all_paths_ignoreable = True
        reason = ''
        for sigentry in self.sigentry_arr:
            ignore, reason = sigentry.filter_folders()
            if not ignore:
                all_paths_ignoreable = False
                break
            else:
                self.sigentry_arr.remove(sigentry)

        if all_paths_ignoreable:
            # Ignore
            print(f"Ignoring {self.name}/{self.version} - {reason}")
            self.set_ignore()
        else:
        #     print(f"NOT Ignoring {self.name}/{self.version}")

            for sigentry in self.sigentry_arr:
                set_ratio, sort_ratio = sigentry.search_component(self.name, self.version)
                if set_ratio > 0:
                    self.set_reviewed()
                    break
                # print(self.name, self.version, src['commentPath'])

