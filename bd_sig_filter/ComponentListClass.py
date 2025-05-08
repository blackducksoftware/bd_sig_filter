# from Component import Component
from . import global_values
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

    def count(self):
        return len(self.components)

    def count_ignored(self):
        count = 0
        for comp in self.components:
            if comp.is_ignored():
                count += 1
        return count

    def count_reviewed(self):
        count = 0
        for comp in self.components:
            if comp.get_reviewed_status():
                count += 1
        return count

    def count_to_be_ignored(self):
        count = 0
        for comp in self.components:
            if comp.ignore:
                count += 1
        return count

    def count_to_be_reviewed(self):
        count = 0
        for comp in self.components:
            if comp.mark_reviewed:
                count += 1
        return count

    def count_not_reviewed_ignored(self):
        count = 0
        for comp in self.components:
            if not comp.is_ignored() and not comp.get_reviewed_status():
                count += 1
        return count

    def count_not_to_be_reviewed_ignored(self):
        count = 0
        for comp in self.components:
            if not comp.ignore and not comp.mark_reviewed:
                count += 1
        return count


    def add_bomfile_data(self, src_bomfile_arr):
        match_count = 0
        for src_entry in src_bomfile_arr:
            try:
                src_compverid = src_entry['fileMatchBomComponent']['release']['id']
                if self.add_comp_src_by_compverid(src_compverid, src_entry):
                    match_count += 1
            except KeyError:
                continue

        logging.debug(f"Elements added to comps {match_count}, Elements in src array {len(src_bomfile_arr)}")
        return

    def process(self):
        # For all components:
        # - if match_type contains Dependency then mark_reviewed
        # - else-if match_type is ONLY Signature then check_signature_rules
        #
        def compare_comps(c1, c2):
            if c1.is_dependency():
                if c2.is_only_signature() and not c2.compver_found:
                    logging.debug(
                        f"IGNORING {c2.name[:25]}/{c2.version} as it has no version in sigpaths and is a duplicate to {c1.name[:25]}/{c1.version} which is a dependency")
                    c2.reason = f"Mark IGNORED - Is a duplicate of dependency '{c1.name[:25]}/{c1.version[:10]}', has different component id or version and no version in sigpaths"
                    c2.set_ignore()
                    c2.set_notreviewed()
                elif c1.filter_version == c2.filter_version:
                    logging.debug(
                        f"No Action for {c2.name[:25]}/{c2.version} as it has version in sigpaths but is a duplicate to {c1.name[:25]}/{c1.version} which is a dependency")
                    c2.reason = f"No Action - Is a duplicate of dependency '{c1.name[:25]}/{c1.version[:10]}', has same version and version found in sigpaths but is a duplicate component"
                    c2.set_notreviewed()
                    c2.set_unignore()
            elif c1.is_only_binary() and not c1.has_version():
                if c2.is_dependency() or (c2.is_only_signature() and c2.compver_found):
                    logging.debug(
                        f"IGNORING {c1.name[:25]}/no_version as it is a binary match with no version and is a duplicate to {c2.name[:25]}/{c2.version}")
                    c2.reason = f"Mark IGNORED - Is a duplicate of '{c2.name[:25]}/{c2.version[:10]}', but HAS no version"
                    c2.set_ignore()
                    c2.set_notreviewed()
            elif c1.compname_found and not c2.compname_found:
                logging.debug(
                    f"IGNORING {c2.name[:25]}/{c2.version} as it is a duplicate to {c1.name}/{c1.version}")
                c2.reason = f"Mark IGNORED - Is a duplicate of '{c1.name[:25]}/{c1.version[:10]}' but has no compname in Signature paths"
                c2.set_ignore()
                c2.set_notreviewed()
            elif c1.compver_found and not c2.compver_found:
                logging.debug(
                    f"Will ignore {c2.name}/{c2.version} as it is a duplicate to {c1.name}/{c1.version} and path misses version")
                c2.set_ignore()
                c2.reason = f"Mark IGNORED - Is a duplicate to '{c1.name[:25]}/{c1.version[:10]}' but has no version in Signature paths"
                c2.set_notreviewed()
            elif not c1.compver_found and not c2.compver_found:
                # Both components have no versions - mark c1 reviewed
                logging.debug(
                    f"- Duplicate components {c1.name}/{c1.version} and {c2.name}/{c2.version} - "
                    f"{c1.name} marked as REVIEWED")
                c1.set_reviewed()
                c1.reason = f"Mark REVIEWED - Is a duplicate to '{c2.name[:25]}/{c2.version[:10]}' but both have no version in Signature paths (chose '{c1.version}')"
                c2.set_notreviewed()
                c2.reason = f"No Action - Is a duplicate to '{c1.name[:25]}/{c1.version[:10]}' but both have no version in Signature paths (chose '{c1.version}')"
            else:
                return False
            return True
        # END compare_comps()

        logging.debug("\nSIGNATURE SCAN FILTER PHASE")
        for comp in self.components:
            if comp.is_ignored():
                continue
            # DEBUG
            # if comp.is_only_signature():
            #     arr = comp.get_origin_compnames()
            #     print(f"names '{arr}")
            #     comp.print_sigpaths()
            # continue
            # END DEBUG
            if comp.is_dependency():
                comp.set_reviewed()
                comp.reason = "Mark REVIEWED - Dependency"
            elif comp.is_only_signature():
                comp.process_signatures()
            else:
                comp.reason = 'No action - not Signature match'

        # look for duplicate components (same compid) and ignore
        logging.debug("\nDUPLICATE COMPONENT FILTER PHASE")
        for i in range(len(self.components)):
            comp1 = self.components[i]
            if comp1.is_ignored() or comp1.ignore:
                continue

            for j in range(i + 1, len(self.components)):
                comp2 = self.components[j]
                if comp2.is_ignored() or comp2.ignore:
                    continue

                if comp1.get_compid() == comp2.get_compid() or comp1.name.lower() == comp2.name.lower():
                    if comp1.is_dependency() and comp2.is_dependency():
                        continue
                    else:
                        ret = compare_comps(comp1, comp2)
                        if not ret:
                            ret = compare_comps(comp2, comp1)
                        if not ret:
                            # Duplicate components and versions
                            logging.debug(f"- Will retain both components {comp1.filter_name}/{comp1.filter_version} and {comp2.filter_name}/{comp2.filter_version} - "
                                  f"{comp1.sig_match_result},{comp2.sig_match_result}")

                    # elif comp1.is_dependency():
                    #     if comp2.is_only_signature() and not comp2.compver_found:
                    #         logging.debug(f"IGNORING {comp2.name[:25]}/{comp2.version} as it has no version in sigpaths and is a duplicate to {comp1.name[:25]}/{comp1.version} which is a dependency")
                    #         comp2.reason = f"Mark IGNORED - Is a duplicate of dependency '{comp1.name[:25]}/{comp1.version[:10]}', has different component id or version and no version in sigpaths"
                    #         comp2.set_ignore()
                    #         comp2.set_notreviewed()
                    #     elif comp1.filter_version == comp2.filter_version:
                    #         logging.debug(
                    #             f"No Action for {comp2.name[:25]}/{comp2.version} as it has version in sigpaths but is a duplicate to {comp1.name[:25]}/{comp1.version} which is a dependency")
                    #         comp2.reason = f"No Action - Is a duplicate of dependency '{comp1.name[:25]}/{comp1.version[:10]}', has same version and version found in sigpaths but is a duplicate component"
                    #         comp2.set_notreviewed()
                    #         comp2.set_unignore()
                    # elif comp2.is_dependency():
                    #     if comp1.is_only_signature() and not comp1.compver_found:
                    #         logging.debug(
                    #             f"IGNORING {comp1.name[:25]}/{comp1.version} as it has no version in sigpaths and is a duplicate to {comp2.name[:25]}/{comp2.version} which is a dependency")
                    #         comp1.reason = f"Mark IGNORED - Is a duplicate of dependency '{comp2.name[:25]}/{comp2.version[:10]}' but has different component id or version and no version in sigpaths"
                    #         comp1.set_ignore()
                    #         comp1.set_notreviewed()
                    #     elif comp1.filter_version == comp2.filter_version:
                    #         logging.debug(
                    #             f"No Action for {comp1.name[:25]}/{comp1.version} as it has version in sigpaths but is a duplicate to {comp2.name[:25]}/{comp2.version} which is a dependency")
                    #         comp1.reason = f"No Action - Is a duplicate of dependency '{comp2.name[:25]}/{comp2.version[:10]}', , has same version and version found in sigpaths but is a duplicate component"
                    #         comp1.set_notreviewed()
                    #         comp1.set_unignore()
                    #
                    # elif comp1.compname_found and not comp2.compname_found:
                    #     logging.debug(f"IGNORING {comp2.name[:25]}/{comp2.version} as it is a duplicate to {comp1.name}/{comp1.version}")
                    #     comp2.reason = f"Mark IGNORED - Is a duplicate of '{comp1.name[:25]}/{comp1.version[:10]}' but has no compname in Signature paths"
                    #     comp2.set_ignore()
                    #     comp2.set_notreviewed()
                    # elif not comp1.compname_found and comp2.compname_found:
                    #     logging.debug(f"IGNORING {comp1.name}/{comp1.version} as it is a duplicate to {comp2.name}/{comp2.version}")
                    #     comp1.set_ignore()
                    #     comp1.reason = f"Mark IGNORED - Is a duplicate to '{comp2.name[:25]}/{comp2.version[:10]}' but has no compname in Signature paths"
                    #     comp1.set_notreviewed()
                    # elif comp1.compver_found and not comp2.compver_found:
                    #     logging.debug(f"Will ignore {comp2.name}/{comp2.version} as it is a duplicate to {comp1.name}/{comp1.version} and path misses version")
                    #     comp2.set_ignore()
                    #     comp2.reason = f"Mark IGNORED - Is a duplicate to '{comp1.name[:25]}/{comp1.version[:10]}' but has no version in Signature paths"
                    #     comp2.set_notreviewed()
                    # elif not comp1.compver_found and comp2.compver_found:
                    #     logging.debug(f"Will ignore {comp1.name}/{comp1.version} as it is a duplicate to {comp2.name}/{comp2.version} and path misses version")
                    #     comp1.set_ignore()
                    #     comp1.reason = f"Mark IGNORED - Is a duplicate to '{comp2.name[:25]}/{comp2.version[:10]}' but has no version in Signature paths"
                    #     comp1.set_notreviewed()
                    # elif not comp1.compver_found and not comp2.compver_found:
                    #     # Both components have no versions - mark comp1 reviewed
                    #     logging.debug(f"- Duplicate components {comp1.name}/{comp1.version} and {comp2.name}/{comp2.version} - "
                    #           f"{comp1.name} marked as REVIEWED")
                    #     comp1.set_reviewed()
                    #     comp1.reason = f"Mark REVIEWED - Is a duplicate to '{comp2.name[:25]}/{comp2.version[:10]}' but both have no version in Signature paths (chose '{comp1.version}')"
                    #     comp2.set_notreviewed()
                    #     comp2.reason = f"No Action - Is a duplicate to '{comp1.name[:25]}/{comp1.version[:10]}' but both have no version in Signature paths (chose '{comp1.version}')"
                    # elif comp1.filter_version == comp2.filter_version:
                    #     logging.debug(
                    #         f"- Duplicate components {comp1.name}/{comp1.version} and {comp2.name}/{comp2.version} - "
                    #         f"{comp1.name} marked as REVIEWED")
                    #     comp1.set_reviewed()
                    #     comp1.reason = f"Mark REVIEWED - Is a duplicate to '{comp2.name[:25]}/{comp2.version[:10]}' and both have version in Signature paths (chose '{comp1.version}')"
                    #     comp2.set_notreviewed()
                    #     comp2.reason = f"No Action - Is a duplicate to '{comp1.name[:25]}/{comp1.version[:10]}' and both have version in Signature paths (chose '{comp1.version}')"
                    # else:
                    #     # Duplicate components and versions
                    #     logging.debug(f"- Will retain both components {comp1.filter_name}/{comp1.filter_version} and {comp2.filter_name}/{comp2.filter_version} - "
                    #           f"{comp1.sig_match_result},{comp2.sig_match_result}")

    def update_components(self, ver_dict):
        if global_values.ignore:
            logging.info("- Ignoring components ...")
            self.ignore_components(ver_dict)

        if global_values.review:
            logging.info("- Marking components reviewed ...")
            self.review_components(ver_dict)


    def ignore_components(self, ver_dict):
        count_ignored = 0
        ignore_array = []
        ignore_comps = []

        for comp in self.components:
            if comp.ignore:
                try:
                    ignore_array.append(comp.data['_meta']['href'])
                    count_ignored += 1
                except KeyError:
                    continue
                if count_ignored >= 99:
                    ignore_comps.append(ignore_array)
                    ignore_array = []
                    count_ignored = 0
        if len(ignore_array) > 0:
            ignore_comps.append(ignore_array)
        else:
            # Nothing to do
            return

        count = 0
        for ignore_array in ignore_comps:
            ignore_bulk_data = {
                "components": ignore_array,
                # "reviewStatus": "REVIEWED",
                "ignored": True,
                # "usage": "DYNAMICALLY_LINKED",
                # "inAttributionReport": true
            }

            comment_bulk_data = {
                "components": ignore_array,
                "comment": "Ignored by bd_sig_filter() script - Sig path in excluded/text folder or duplicate",
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
                r = global_values.bd.session.patch(url, json=ignore_bulk_data, headers=headers)
                r.raise_for_status()

                url = ver_dict['_meta']['href'] + '/bulk-comment'
                headers = {
                    "Accept": "application/vnd.blackducksoftware.bill-of-materials-6+json",
                    "Content-Type": "application/vnd.blackducksoftware.bill-of-materials-6+json"
                }
                r = global_values.bd.session.post(url, json=comment_bulk_data, headers=headers)
                r.raise_for_status()

                count += len(ignore_array)
            except requests.HTTPError as err:
                global_values.bd.http_error_handler(err)
        logging.info(f"- Ignored {count} components")

        return

    def review_components(self, ver_dict):
        count_reviewed = 0
        review_array = []
        review_comps = []

        for comp in self.components:
            if comp.mark_reviewed:
                try:
                    review_array.append(comp.data['_meta']['href'])
                    count_reviewed += 1
                except KeyError:
                    continue
                if count_reviewed >= 99:
                    review_comps.append(review_array)
                    review_array = []
                    count_reviewed = 0
        if len(review_array) > 0:
            review_comps.append(review_array)
        else:
            return

        count = 0
        for review_array in review_comps:
            review_bulk_data = {
                "components": review_array,
                "reviewStatus": "REVIEWED",
                # "ignored": True,
                # "usage": "DYNAMICALLY_LINKED",
                # "inAttributionReport": true
            }

            comment_bulk_data = {
                "components": review_array,
                "comment": "Reviewed by bd_sig_filter() script - comp name and/or version found in Sig path",
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
                r = global_values.bd.session.patch(url, json=review_bulk_data, headers=headers)
                r.raise_for_status()

                url = ver_dict['_meta']['href'] + '/bulk-comment'
                headers = {
                    "Accept": "application/vnd.blackducksoftware.bill-of-materials-6+json",
                    "Content-Type": "application/vnd.blackducksoftware.bill-of-materials-6+json"
                }
                r = global_values.bd.session.post(url, json=comment_bulk_data, headers=headers)
                r.raise_for_status()

                count += len(review_array)

            except requests.HTTPError as err:
                global_values.bd.http_error_handler(err)

        logging.info(f"- Marked {count} components as reviewed")

        return

    def get_component_report_data(self):
        data = []
        for comp in self.components:
            if comp.is_signature() and comp.is_dependency():
                type = "Dep+Sig"
            elif comp.is_dependency():
                type = "Dep"
            elif comp.is_only_signature():
                type = "Sig"
            else:
                type = "Other"
            data.append([f"{comp.name[:25]}/{comp.version[:10]}", type, comp.is_ignored(), comp.get_reviewed_status(),
                         comp.ignore, comp.mark_reviewed, comp.reason])
        return data

    def get_unmatched_list(self):
        data = ''
        for comp in self.components:
            if comp.unmatched:
                paths = comp.get_sigpaths()
                orinames = ','.join(comp.oriname_arr)
                data += f"Comp: {comp.name}/{comp.version} (Origin names={orinames}):\n{paths}"
        return data

    def get_list(self):
        comparray = []
        for comp in self.components:
            comparray.append(comp.get_data())
            if len(comparray) > 10:
                break

        return comparray

    def __str__(self):
        valstr = '['
        for comp in self.components:
            valstr += str(comp)
        return valstr + ']'