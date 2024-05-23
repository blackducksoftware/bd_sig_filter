import bd_data
from ComponentList import ComponentList
from Component import Component
import config
import bd_process_bom
import global_values
import logging
import platform


def process_ignores(comp_dict, file_dict):
    for url, comp in comp_dict.items():
        if url in file_dict.keys():
            print(f"{comp_dict[url]['componentName']}/{comp_dict[url]['componentVersionName']}: {file_dict[url]}")


def main():
    config.check_args()

    bdver_dict = bd_process_bom.get_bdproject(global_values.bd_project, global_values.bd_version)

    complist = bd_process_bom.get_bom_components(global_values.bd, bdver_dict)

    # logging.info('- Filtering Signature matches ... ')
    # sig_dict = bd_process_bom.filter_sig_comps(comp_dict)

    # logging.info('- Getting component data ... ')
    # file_dict = bd_data.get_file_data(sig_dict)

    logging.info('- Getting matched file data ... ')
    src_data = bd_data.get_bom_files(bdver_dict)
    complist.add_bomfile_data(src_data)

    complist.process()

    # process_components(sig_dict, src_arr)

    # process_ignores(comp_dict, file_dict)

    # bd_process_bom.ignore_components(file_dict, bdver_dict)

    return

if __name__ == '__main__':
    main()
