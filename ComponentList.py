from Component import Component

class ComponentList:
    components = []
    def __init__(self):
        pass

    def add(self, comp):
        self.components.append(comp)

    def add_comp_src_by_compverid(self, src_compverid, src_entry):
        for comp in self.components:
            compverid = comp.get_compverid()
            if compverid == src_compverid:
                comp.add_src(src_entry)
                return True
        return False

    def add_bomfile_data(self, src_bomfile_arr):
        match_count = 0
        for src_entry in src_bomfile_arr:
            try:
                src_compverid = src_entry['fileMatchBomComponent']['release']['id']
                if self.add_comp_src_by_compverid(src_compverid, src_entry):
                    match_count += 1
            except KeyError:
                continue

        print(match_count, len(src_bomfile_arr))
        return

    def process(self):
        # For all components:
        # - if match_type contains Dependency then mark_reviewed
        # - else-if match_type is ONLY Signature then check_signature_rules
        #
        for comp in self.components:
            if comp.is_ignored():
                continue
            if comp.is_dependency():
                comp.set_reviewed()
            elif comp.is_only_signature():
                comp.process_signatures()
