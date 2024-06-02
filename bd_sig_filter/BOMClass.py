from .ComponentListClass import ComponentList
from .ComponentClass import Component
from . import bd_data
from . import bd_project
from . import global_values
from tabulate import tabulate
import logging

class BOM:
    def __init__(self):
        self.complist = ComponentList()
        logging.info(f"Working on project '{global_values.bd_project}' version '{global_values.bd_version}'")

        self.bdver_dict = bd_project.get_bdproject(global_values.bd_project, global_values.bd_version)

        res = global_values.bd.list_resources(self.bdver_dict)
        projver = res['href']
        thishref = f"{projver}/components?limit=1000"

        bom_arr = bd_data.get_paginated_data(thishref, "application/vnd.blackducksoftware.bill-of-materials-6+json")

        for comp in bom_arr:
            if 'componentVersion' not in comp:
                continue
            # compver = comp['componentVersion']

            compclass = Component(comp['componentName'], comp['componentVersionName'], comp)
            self.complist.add(compclass)

        return

    def get_bom_files(self):
        res = global_values.bd.list_resources(self.bdver_dict)
        projver = res['href']
        thishref = f"{projver}/source-bom-entries?filter=bomMatchType%3Afiles_modified&filter=bomMatchType%3Afiles_added_deleted&filter=bomMatchType%3Afile_exact&filter=bomMatchType%3Afiles_exact&limit=1000"
        thishref = thishref.replace("/api/", "/api/internal/")

        # https://poc39.blackduck.synopsys.com/api/internal/projects/9a25dee6-bc03-416c-a5bb-70ceb58ada28/versions/067cd508-ff40-46b8-ae0d-23218f224eeb/source-bom-entries?filter=bomMatchType%3Afiles_modified&filter=bomMatchType%3Afiles_added_deleted&filter=bomMatchType%3Afile_exact&filter=bomMatchType%3Afiles_exact&limit=100&offset=0

        # return bd_data.get_paginated_data(thishref, "application/vnd.blackducksoftware.internal-1+json")
        src_data = bd_data.get_paginated_data(thishref, "application/json")
        self.complist.add_bomfile_data(src_data)
        return

    def process(self):
        self.complist.process()
        return

    def update_components(self):
        self.complist.update_components(self.bdver_dict)

    def report_summary(self):
        table = [['Before', self.complist.count(), self.complist.count_ignored(), self.complist.count_reviewed(),
                  self.complist.count_not_reviewed_ignored()],
                 ['After', self.complist.count(), self.complist.count_to_be_ignored(),
                  self.complist.count_to_be_reviewed(), self.complist.count_not_to_be_reviewed_ignored()]]
        print("SUMMARY:")
        print(tabulate(table, headers=["", "Components", "Ignored", "Reviewed", "Neither"], tablefmt="simple"))
        print()

        if global_values.report_file != '':
            with open(global_values.report_file, "w") as rfile:
                # Writing data to a file
                rfile.writelines("SUMMARY:")
                rfile.writelines(tabulate(table, headers=["", "Components", "Ignored", "Reviewed", "Neither"],
                                          tablefmt="Simple"))
                rfile.writelines("")

    def report_full(self):
        table = self.complist.get_component_report_data()
        print(tabulate(table, headers=["Component", "Match Type", "Ignored", "Reviewed", "To be Ignored",
                                       "To be Reviewed", "Action"]))
        print()
