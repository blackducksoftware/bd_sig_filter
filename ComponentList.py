# from Component import Component
import global_values
import logging
import requests

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

        logging.info(f"{match_count}, {len(src_bomfile_arr)}")
        return

    def process(self):
        # For all components:
        # - if match_type contains Dependency then mark_reviewed
        # - else-if match_type is ONLY Signature then check_signature_rules
        #
        logging.info("\nSIGNATURE SCAN FILTER PHASE")
        for comp in self.components:
            if comp.is_ignored():
                continue
            if comp.is_dependency():
                comp.set_reviewed()
            elif comp.is_only_signature():
                comp.process_signatures()

        # look for duplicate components (same compid) and ignore
        logging.info("\nDUPLICATE SIGNATURE MATCHES FILTER PHASE")
        for i in range(len(self.components)):
            comp1 = self.components[i]
            if comp1.is_ignored() or comp1.is_dependency() or not comp1.is_only_signature() or comp1.ignore:
                continue

            for j in range(i + 1, len(self.components)):
                comp2 = self.components[j]
                if comp2.is_ignored() or comp2.is_dependency() or not comp2.is_only_signature() or comp2.ignore:
                    continue

                if comp1.get_compid() == comp2.get_compid():
                    if comp1.compname_found and not comp2.compname_found:
                        logging.info(f"IGNORING {comp2.name}/{comp2.version} as it is a duplicate to {comp1.name}/{comp1.version}")
                        comp2.set_ignore()
                    elif not comp1.compname_found and comp2.compname_found:
                        logging.info(f"IGNORING {comp1.name}/{comp1.version} as it is a duplicate to {comp2.name}/{comp2.version}")
                        comp1.set_ignore()
                    elif comp1.compver_found and not comp2.compver_found:
                        logging.info(f"Will ignore {comp2.name}/{comp2.version} as it is a duplicate to {comp1.name}/{comp1.version} and path misses version")
                        comp2.set_ignore()
                    elif not comp1.compver_found and comp2.compver_found:
                        logging.info(f"Will ignore {comp1.name}/{comp1.version} as it is a duplicate to {comp2.name}/{comp2.version} and path misses version")
                        comp1.set_ignore()
                    else:
                        # Nothing to do
                        logging.info(f"- Will retain both components {comp1.filter_name}/{comp1.filter_version} and {comp2.filter_name}/{comp2.filter_version} - "
                              f"{comp1.sig_match_result},{comp2.sig_match_result}")

    def update_components(self, ver_dict):
        count_ignored = 0
        ignore_array = []
        ignore_comps = []
        count_reviewed = 0
        review_array = []
        review_comps = []

        logging.info("- Updating components ...")
        count = 0
        if not global_values.no_ignore:
            for comp in self.components:
                if comp.ignore:
                    try:
                        ignore_array.append(comp.data['_meta']['href'])
                        count_ignored += 1
                        count += 1
                    except KeyError:
                        continue
                    if count_ignored >= 99:
                        ignore_comps.append(ignore_array)
                        ignore_array = []
                        count_ignored = 0
            if len(ignore_array) > 0:
                ignore_comps.append(ignore_array)

        if not global_values.no_reviewed:
            for comp in self.components:
                if comp.mark_reviewed:
                    try:
                        review_array.append(comp.data['_meta']['href'])
                        count_reviewed += 1
                        count += 1
                    except KeyError:
                        continue
                    if count_reviewed >= 99:
                        review_comps.append(review_array)
                        review_array = []
                        count_reviewed = 0
            if len(review_array) > 0:
                review_comps.append(review_array)

        if count == 0:
            # Nothing to do
            return

        count = 0
        for ignore_array in ignore_comps:
            bulk_data = {
                "components": ignore_array,
                # "reviewStatus": "REVIEWED",
                "ignored": True,
                # "usage": "DYNAMICALLY_LINKED",
                # "inAttributionReport": true
            }

            try:
                url = ver_dict['_meta']['href'] + '/bulk-adjustment'
                headers = {
                    "Accept": "application/vnd.blackducksoftware.bill-of-materials-6+json",
                    "Content-Type": "application/vnd.blackducksoftware.bill-of-materials-6+json"
                }
                r = global_values.bd.session.patch(url, json=bulk_data, headers=headers)
                r.raise_for_status()
                count += len(ignore_array)
            except requests.HTTPError as err:
                global_values.bd.http_error_handler(err)
        logging.info(f"- Ignored {count} components")

        count = 0
        for review_array in review_comps:
            bulk_data = {
                "components": review_array,
                "reviewStatus": "REVIEWED",
                # "ignored": True,
                # "usage": "DYNAMICALLY_LINKED",
                # "inAttributionReport": true
            }

            try:
                url = ver_dict['_meta']['href'] + '/bulk-adjustment'
                headers = {
                    "Accept": "application/vnd.blackducksoftware.bill-of-materials-6+json",
                    "Content-Type": "application/vnd.blackducksoftware.bill-of-materials-6+json"
                }
                r = global_values.bd.session.patch(url, json=bulk_data, headers=headers)
                r.raise_for_status()
                count += len(review_array)

            except requests.HTTPError as err:
                global_values.bd.http_error_handler(err)

        logging.info(f"- Marked {count} components as reviewed")

        return
