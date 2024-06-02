# import bd_data
# from ComponentList import ComponentList
# from Component import Component
import config
# import bd_project
import global_values
import logging
from BOMClass import BOM
# import platform


def main():
    config.check_args()

    bom = BOM()

    logging.debug('- Getting matched file data ... ')
    bom.get_bom_files()
    bom.process()
    bom.update_components()
    bom.report_summary()
    bom.report_full()

    return

if __name__ == '__main__':
    main()
