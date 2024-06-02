#!/usr/bin/env python

# import argparse
# import json
import logging
import sys
# import os
# import requests
# import platform
# import asyncio
# import bd_data

from blackduck import Client
from . import global_values
# from ComponentListClass import ComponentList
# from ComponentClass import Component
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
