# import aiohttp
# import asyncio
# import platform
# import logging

# import bd_data
from . import global_values


# async def async_main(comps, token):
#     async with aiohttp.ClientSession(trust_env=True) as session:
#         data_tasks = []
#         file_tasks = []
#
#         count = 0
#         for url, comp in comps.items():
#             count += 1
#
#             file_task = asyncio.ensure_future(async_get_files(session, comp, token))
#             file_tasks.append(file_task)
#
#         await asyncio.gather(*data_tasks)
#         all_files = dict(await asyncio.gather(*file_tasks))
#
#         await asyncio.sleep(0.250)
#         # print(f'- {count} components ')
#         #
#         # print(all_files)
#
#     return all_files


# async def async_get_files(session, comp, token):
#     filelist = []
#
#     if not global_values.bd_trustcert:
#         ssl = False
#     else:
#         ssl = None
#
#     # retfile = "NOASSERTION"
#     hrefs = comp['_meta']['links']
#
#     link = next((item for item in hrefs if item["rel"] == "matched-files"), None)
#     # link = next((item for item in hrefs if item["rel"] == "origins"), None)
#     if link:
#         thishref = link['href'] + '?limit=1000'
#         headers = {
#             'Authorization': f'Bearer {token}',
#             'accept': "application/vnd.blackducksoftware.bill-of-materials-6+json",
#             # 'accept': "application/vnd.blackducksoftware.component-detail-5+json",
#         }
#
#         # archive_ignore = False
#         async with session.get(thishref, headers=headers, ssl=ssl) as resp:
#             result_data = await resp.json()
#             for item in result_data['items']:
#                 filelist.append(item['filePath']['compositePathContext'])
#
#     return comp['componentVersion'], filelist
#
#
# def get_file_data(compdict):
#     if platform.system() == "Windows":
#         asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     file_dict = asyncio.run(async_main(compdict, global_values.bd.session.auth.bearer_token))
#
#     return file_dict


def get_paginated_data(url, accept_hdr):
    headers = {
        'accept': accept_hdr,
    }
    res = global_values.bd.get_json(url, headers=headers)
    if 'totalCount' in res and 'items' in res:
        total_comps = res['totalCount']
    else:
        return []

    ret_arr = []
    downloaded_comps = 0
    while downloaded_comps < total_comps:
        downloaded_comps += len(res['items'])

        ret_arr += res['items']

        newurl = f"{url}&offset={downloaded_comps}"
        res = global_values.bd.get_json(newurl, headers=headers)
        if 'totalCount' not in res or 'items' not in res:
            break

    return ret_arr
