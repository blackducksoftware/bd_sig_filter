# import bd_data
# from ComponentList import ComponentList
# from Component import Component
from . import config
# import bd_project
import logging
from .BOMClass import BOM
from . import global_values
import json
import sys
# import platform


def main():
    config.check_args()

    bom = BOM()

    logging.debug('- Getting matched file data ... ')
    bom.get_bom_files()
    data = bom.get_data()
    with open("out.json", "w") as outfile:
        outfile.write(json.dumps(data, indent=4))

    sys.exit(0)
    bom.process()
    bom.update_components()
    bom.report_summary()
    bom.report_full()
    if global_values.report_unmatched:
        bom.report_unmatched()

    return

if __name__ == '__main__':
    main()
