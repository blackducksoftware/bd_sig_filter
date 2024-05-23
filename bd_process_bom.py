#!/usr/bin/env python

# import argparse
# import json
import logging
import sys
# import os
import requests
import platform
import asyncio
import bd_data

from blackduck import Client
import global_values
from ComponentList import ComponentList
from Component import Component
# logging.basicConfig(level=logging.INFO)


def check_projver(bd, proj, ver):
	params = {
		'q': "name:" + proj,
		'sort': 'name',
	}

	projects = bd.get_resource('projects', params=params)
	for p in projects:
		if p['name'] == proj:
			versions = bd.get_resource('versions', parent=p, params=params)
			for v in versions:
				if v['versionName'] == ver:
					return v
			break
	else:
		logging.error(f"Version '{ver}' does not exist in project '{proj}'")
		sys.exit(2)

	logging.warning(f"Project '{proj}' does not exist")
	print('Available projects:')
	projects = bd.get_resource('projects')
	for proj in projects:
		print(proj['name'])
	sys.exit(2)


def get_bom_components(bd, ver_dict):
	# comp_dict = {}
	complist = ComponentList()

	res = bd.list_resources(ver_dict)
	projver = res['href']
	thishref = f"{projver}/components?limit=1000"

	bom_arr = bd_data.get_paginated_data(thishref, "application/vnd.blackducksoftware.bill-of-materials-6+json")

	for comp in bom_arr:
		if 'componentVersion' not in comp:
			continue
		# compver = comp['componentVersion']

		compclass = Component(comp['componentName'], comp['componentVersionName'], comp)
		complist.add(compclass)

	return complist


def get_all_projects(bd):
	projs = bd.get_resource('projects', items=True)

	projlist = []
	for proj in projs:
		projlist.append(proj['name'])
	return projlist


def get_bdproject(bdproj, bdver):
	global_values.bd = Client(
		token=global_values.bd_api,
		base_url=global_values.bd_url,
		verify=(not global_values.bd_trustcert),  # TLS certificate verification
		timeout=60
	)

	ver_dict = check_projver(global_values.bd, bdproj, bdver)
	return ver_dict


def ignore_components(compdict, ver_dict):
	ignore_comps = []
	count_ignored = 0
	ignore_array = []

	logging.info("- Ignoring partial components ...")
	count = 0
	for comp in compdict.keys():
		ignored = False
		if pkg_ignore_dict[comp]:
			# Ignore this component
			ignore_array.append(compdict[comp]['_meta']['href'])
			count_ignored += 1
			count += 1
			ignored = True
		if ignored and count_ignored >= 99:
			ignore_comps.append(ignore_array)
			ignore_array = []
			count_ignored = 0

	ignore_comps.append(ignore_array)
	if count == 0:
		return
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
		except requests.HTTPError as err:
			global_values.bd.http_error_handler(err)

	logging.info(f"- Ignored {count} components")
	return


def filter_sig_comps(compdict):
	sig_dict = {}
	for url, comp in compdict.items():
		if 'FILE_EXACT' in comp['matchTypes']:
			sig_dict[url] = comp

	return sig_dict
