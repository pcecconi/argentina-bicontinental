#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import xml.etree.ElementTree as ET
from os.path import isfile
from string import Template
from subprocess import call
from settings import MAPSERVER_URL
import simpleflock
# from django.conf import settings

uso = "\nUso: manage add|remove|list|seed|reseed|mk_preview <mapname>[:<srid>] [ <mapname>[:srid] .. <mapname>[:srid] ]\n"
curr_dir = os.path.dirname(os.path.abspath(__file__))
MAPCACHE_CONFIG = os.path.join(curr_dir, 'mapcache.xml')
MAPCACHE_TEMPLATES_DIR = os.path.join(curr_dir, 'templates')
map_path = os.path.join(os.path.abspath(os.path.join(curr_dir, os.pardir)), 'mapfiles')
cache_path = os.path.join(curr_dir, 'cache')
default_srid = '3857'
preview_dir = map_path

def getDefinedMaps():
	tree = ET.parse(MAPCACHE_CONFIG)
	root = tree.getroot()
	defined_maps=[]
	for child in root.findall("tileset"):
		defined_maps.append(child.attrib['name'])
	return defined_maps	

def seed(maps, min_level, max_level, force):
	defined_maps=getDefinedMaps()
	for arg in maps:
		params = arg.split(':')
		mapa = params[0]
		if len(params) == 2:
			max_level = params[1]
		if len(params) == 3:
			min_level = params[1]
			max_level = params[2]
		if mapa in defined_maps:
			print 'Seeding %s from %s to %s...'%(mapa, min_level, max_level)
			if force:
				mapa = mapa+' -f'
			# call('sudo rm /tmp/map-error.log', shell=True)
			call('sudo mapcache_seed -c mapcache.xml -t '+mapa+' -z %s,%s -n 4'%(min_level, max_level), shell=True)
		else:
			print '\nError: No se encontró '+arg+' en los mapas definidos.\n'	

def gen_preview(mapa):
	print '\nMaking preview image for map: %s.map at %s\n'%(mapa, preview_dir)
	mapa_grande = os.path.join(preview_dir, mapa+'.png')
	call('shp2img -m '+os.path.join(map_path, mapa+'.map')+' -o '+mapa_grande, shell=True)
	# call('convert '+mapa_grande+' -resize 66% '+os.path.join(preview_dir, mapa+'-medio.png'), shell=True)
	# call('convert '+mapa_grande+' -resize 33% '+os.path.join(preview_dir, mapa+'.png'), shell=True)

def remove(maps):
	tree = ET.parse(MAPCACHE_CONFIG)
	root = tree.getroot()
	for mapa in maps:
		elems = root.findall("*[@name='"+mapa+"']")
		if len(elems) > 0:
			for child in elems:
				root.remove(child)
			
			tree.write(MAPCACHE_CONFIG, encoding='utf-8')
			try:
				os.remove(os.path.join(cache_path, mapa+'.mbtiles'))
			except:
				pass
			print '\n- '+mapa+'\n'
		else:
			print '\nError: no se encontro '+mapa+'.\n'

def _add(maps):
	tree = ET.parse(MAPCACHE_CONFIG)
	root = tree.getroot()
	for m in maps:
		params = m.split(':')
		mapa = params[0]
		if len(params) > 1:
			srid = params[1]
		else:
			srid = default_srid
		if len(params) > 2:
			sld = ':'.join(params[2:])
			sld_hash = sld.split('$')
			if len(sld_hash) > 1:
				sld_id = '$'+sld_hash[1]
				sld = sld_hash[0]
			else:
				sld_id = ''
		else:
			sld = ''
			sld_id = ''
		if len(root.findall("*[@name='"+mapa+sld_id+"']")) == 0:
			print os.path.join(map_path,mapa+'.map')
			if isfile(os.path.join(map_path,mapa+'.map')):
				d=dict(mapname=mapa+sld_id,cache_path=cache_path,map_path=map_path)
				with open(os.path.join(MAPCACHE_TEMPLATES_DIR, 'cache.template'), 'r') as file:
					template=Template(file.read())
			    	root.append(ET.fromstring(template.substitute(d)))

				src_template = 'source_sld.template' if sld != '' else 'source.template'
				with open(os.path.join(MAPCACHE_TEMPLATES_DIR, src_template), 'r') as file:
					template=Template(file.read())
					d['mapfile'] = mapa
					d['layers'] = mapa					
					d['sld'] = sld
					d['mapserver_url'] = MAPSERVER_URL
					root.append(ET.fromstring(template.substitute(d)))
			
				with open(os.path.join(MAPCACHE_TEMPLATES_DIR, 'tileset_%s.template'%srid), 'r') as file:
					template=Template(file.read())
			    	root.append(ET.fromstring(template.substitute(d)))    	
					
				tree.write(MAPCACHE_CONFIG, encoding='utf-8')
				print ('\n+ %s (%s)\n')%(mapa, srid)
				# update_demo()
				# call('service apache2 reload', shell=True)
				# mk_preview([mapa])
			else:
				print '\nError: No se encontro el mapa: '+mapa+'\n'
		else:
			print '\nError: '+mapa+sld_id+' ya existe.\n'

def add(maps):
	try:
		if len(sys.argv) <= 1:
			with simpleflock.SimpleFlock(MAPCACHE_CONFIG, timeout=15):
				_add(maps)
		else:
			_add(maps)
	except:
		print "Mapcache filelock!"

def list():
	defined_maps = getDefinedMaps()
	print '- '+'\n- '.join(defined_maps)

#elif sys.argv[1]=='seed':
#	call('mapcache_seed -c /usr/local/usig/mapcache/mapcache.xml -t '+mapa+' -z 0,4 -n 4', shell=True)
#	call('mapcache_seed -c /usr/local/usig/mapcache/mapcache.xml -t '+mapa+' -z 4,9 -n 4 -e 92000,90500,113500,112000', shell=True)

def mk_preview(maps):
	tree = ET.parse(MAPCACHE_CONFIG)
	root = tree.getroot()
	for m in maps:
		params = m.split(':')
		mapa = params[0]
		if len(root.findall("*[@name='"+mapa+"']")) != 0:
			if isfile(os.path.join(map_path, mapa+'.map')):
				gen_preview(mapa)
			else:
				print '\nError: No se encontro el mapa: '+mapa+'\n'
		else:
			print '\nError: No se encontro el mapa: '+mapa+' en la configuración de mapcache.\n'


if len(sys.argv) > 1:
	op = sys.argv[1]
else:
	op = 'help'

if op == 'help':
    print uso
    exit(-1)

if len(sys.argv) >= 2:
	maps = sys.argv[2:]
	if op == 'remove':
		remove(maps)
	elif op == 'add':
		add(maps)
	elif op == 'list':
		list()
	elif op == 'seed':
		seed(maps, 0, 14, False)
	elif op == 'reseed':
		seed(maps, 0, 14, True)
	elif op == 'mk_preview':
		mk_preview(maps)
	else:
		print uso
		exit(-1)
