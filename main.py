import bd_data
# from ComponentList import ComponentList
# from Component import Component
import config
import bd_process_bom
import global_values
import logging
# import platform


def main():
    config.check_args()

    bdver_dict = bd_process_bom.get_bdproject(global_values.bd_project, global_values.bd_version)

    complist = bd_process_bom.get_bom_components(global_values.bd, bdver_dict)

    logging.info('- Getting matched file data ... ')
    src_data = bd_data.get_bom_files(bdver_dict)
    complist.add_bomfile_data(src_data)

    complist.process()

    complist.update_components(bdver_dict)

    return

if __name__ == '__main__':
    main()
