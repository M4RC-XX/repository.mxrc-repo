# -*- coding: utf-8 -*-

import sys
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import time
from datetime import datetime, timedelta
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote, unquote  # Python 2.X
else: 
	from urllib.parse import urlencode, quote, unquote  # Python 3.X

from .common import *


if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

def mainMenu():
	addDir(translation(30601), artpic+'watchlist.png', {'mode': 'listShowsFavs'})
	config = traversing.get_config()
	for pick in config['picks']:
		title = pick['title']
		idd = str(pick['id'])
		catURL = config['category_entries'].format(idd)
		addDir(title, artpic+idd+'.png', {'mode': 'listVideos', 'url': catURL, 'extras': title})
	addDir(translation(30621), artpic+'genres.png', {'mode': 'listGenres'})
	addDir(translation(30622), artpic+'search.png', {'mode': 'SearchNETZKINO'})
	if enableADJUSTMENT:
		addDir(translation(30623), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30624), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listGenres():
	debug_MS("(navigator.listThemes) ------------------------------------------------ START = listThemes -----------------------------------------------")
	config = traversing.get_config()
	for genre in config['genres']:
		title = genre['title']
		idd = str(genre['id'])
		image = (config['category_thumb'].format(idd) or icon)
		catURL = config['category_entries'].format(idd)
		if not approvedAge and idd == '71': continue
		addDir(title, image, {'mode': 'listVideos', 'url': catURL, 'extras': title})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listVideos(url, CAT):
	debug_MS("(navigator.listVideos) ------------------------------------------------ START = listVideos -----------------------------------------------")
	debug_MS("(navigator.listVideos) ### URL : {0} ### CATEGORY : {1} ###".format(url, CAT))
	FOUND = 0
	DATA = getUrl(url)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listVideos) XXXXX CONTENT : {0} XXXXX".format(str(DATA)))
	debug_MS("++++++++++++++++++++++++")
	for post in DATA['posts']:
		Note_1, Note_2 = ("" for _ in range(2))
		aired, begins, age, mpaa, year, score, rating, cast, director, genre, quality, youtubeID, duration = (None for _ in range(13))
		if 'Streaming' in post.get('custom_fields', {}) and not 'plus-exclusive' in post.get('properties'):
			def get_fields(_post, field_name):
				custom_fields = post.get('custom_fields', {})
				field = custom_fields.get(field_name, [])
				if len(field) >= 1 and len(field[0]) != 0:
					return cleaning(field[0])
				return None
			FOUND += 1
			slug = (post.get('slug', '') or "")
			IDD = str(post['id'])
			title = cleaning(post['title'])
			try:
				broadcast = datetime(*(time.strptime(post['date'][:19], '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2021-11-08T08:57:33.777135+00:00
				aired = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
				begins = broadcast.strftime('%d{0}%m{0}%Y').format('.')
			except: pass
			Note_1 = translation(30644).format(str(aired)) if aired else '[CR]'
			Note_2 = get_Description(post)
			image = (get_Picture(IDD, post, 'thumbnail') or get_Picture(IDD, post.get('custom_fields', []), 'Artikelbild'))
			image = image.split('.jpg')[0].rstrip()+'.jpg' if image and '.jpg' in image else image
			BANNER = get_Picture(IDD, post.get('custom_fields', []), 'featured_img_seven')
			banner = BANNER.split('.jpg')[0].rstrip()+'.jpg' if BANNER and '.jpg' in BANNER else BANNER
			FANART = (get_Picture(IDD, post.get('custom_fields', []), 'featured_img_all') or defaultFanart)
			background = FANART.split('.jpg')[0].rstrip().replace('_slider', '_img_all')+'.jpg' if FANART and '.jpg' in FANART else FANART
			stream = get_fields(post, 'Streaming')
			studio = stream.split('/')[0].strip().replace('_', ' ') if stream else 'Netzkino'
			studio = re.sub(r' flat| NKS| NK EV| NK(\d+)?| SG| MG', '', studio)
			age = get_fields(post, 'FSK')
			if age and str(age).isdigit():
				mpaa = translation(30645).format(str(age)) if str(age) != '0' else translation(30646)
				if not approvedAge and str(age) == '18': continue
			year = get_fields(post, 'Jahr')
			score = get_fields(post, 'IMDb-Bewertung')
			if score and score != '0': rating = score.replace(',', '.')
			cast = get_fields(post, 'Stars')
			director = get_fields(post, 'Regisseur')
			genre = get_fields(post, 'TV_Movie_Genre')
			quality = get_fields(post, 'Adaptives_Streaming')
			if quality and quality == 'HD': title += translation(30647)
			youtubeID = get_fields(post, 'Youtube_Delivery_Id')
			duration = get_fields(post, 'Duration')
			plot = title+'[CR]'+Note_1+Note_2
			addType = 1
			if xbmcvfs.exists(videoFavsFile):
				with open(videoFavsFile, 'r') as fp:
					watch = json.load(fp)
					for item in watch.get('items', []):
						if item.get('url') == stream: addType = 2
			addLink(title, image, {'mode': 'playVideo', 'url': stream}, plot, duration, begins, year, genre, director, cast, rating, mpaa, background, banner, studio, addType)
	if FOUND >= 1:
		for method in getSorting():
			xbmcplugin.addSortMethod(ADDON_HANDLE, method)
	else:
		debug_MS("(navigator.listVideos) ##### Keine VIDEO-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30524).format('Einträge'), translation(30526).format(CAT), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchNETZKINO():
	debug_MS("(navigator.SearchNETZKINO) ------------------------------------------------ START = SearchNETZKINO -----------------------------------------------")
	config = traversing.get_config()
	keyword = None
	if xbmcvfs.exists(searchHackFile):
		with open(searchHackFile, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30625), type=xbmcgui.INPUT_ALPHANUM, autoclose=10000)
		if keyword:
			keyword = quote(keyword)
			with open(searchHackFile, 'w') as record:
				record.write(keyword)
	if keyword: return listVideos(config['search_query'].format(keyword), unquote(keyword))
	return None

def playVideo(SLUG):
	debug_MS("(navigator.playVideo) ------------------------------------------------ START = playVideo -----------------------------------------------")
	debug_MS("(navigator.playVideo) ### URL : {0} ###".format(SLUG))
	finalURL, STREAM = (False for _ in range(2))
	config = traversing.get_config()
	if (prefSTREAM == '0' or enableINPUTSTREAM):
		STREAM = 'HLS' if enableINPUTSTREAM else 'M3U8'
		MIME, finalURL = 'application/vnd.apple.mpegurl', config['streaming_hls'].format(SLUG)
	if not finalURL:
		STREAM, MIME, finalURL = 'MP4', 'video/mp4', config['streaming_pmd'].format(SLUG)
	if finalURL and STREAM:
		LSM = xbmcgui.ListItem(path=finalURL)
		LSM.setMimeType(MIME)
		if ADDON_operate('inputstream.adaptive') and STREAM in ['HLS', 'MPD']:
			LSM.setProperty(INPUT_APP, 'inputstream.adaptive')
			LSM.setProperty('inputstream.adaptive.manifest_type', STREAM.lower())
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
		log("(navigator.playVideo) {0}_stream : {1} ".format(STREAM, finalURL))
	else: 
		failing("(navigator.playVideo) ##### Die angeforderte Video-Url wurde leider NICHT gefunden !!! #####")
		return dialog.notification(translation(30521).format('PLAY'), translation(30527), icon, 8000)

def listShowsFavs():
	debug_MS("(navigator.listShowsFavs) ------------------------------------------------ START = listShowsFavs -----------------------------------------------")
	def corr(s):
		return s if s !='None' else None
	for method in getSorting():
		xbmcplugin.addSortMethod(ADDON_HANDLE, method)
	if xbmcvfs.exists(videoFavsFile):
		with open(videoFavsFile, 'r') as fp:
			watch = json.load(fp)
			for item in watch.get('items', []):
				name = corr(item.get('name'))
				logo = icon if corr(item.get('pict', 'None')) is None else item.get('pict')
				debug_MS("(navigator.listShowsFavs) ### NAME : {0} || URL : {1} || IMAGE : {2} ###".format(name, item.get('url'), logo))
				addLink(name, logo, {'mode': 'playVideo', 'url': item.get('url')}, corr(item.get('plot')), corr(item.get('duration')), corr(item.get('begins')), corr(item.get('year')), corr(item.get('genre')), corr(item.get('director')), corr(item.get('cast')), corr(item.get('rating')), \
					corr(item.get('mpaa')), corr(item.get('background')), corr(item.get('banner', 'None')), item.get('studio', 'Netzkino'), FAVclear=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(videoFavsFile):
		with open(videoFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url, 'plot': plot, 'duration': duration, 'begins': begins, 'year': year, 'genre': genre, 'director': director, 'cast': cast, 'rating': rating, 'mpaa': mpaa, 'background': background, 'banner': banner, 'studio': studio})
		with open(videoFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.sleep(500)
		dialog.notification(translation(30528), translation(30529).format(name), icon, 8000)
	elif action == 'DEL':
		TOPS['items'] = [obj for obj in TOPS['items'] if obj.get('url') != url]
		with open(videoFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30528), translation(30530).format(name), icon, 8000)

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, background=None, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Studio': 'Netzkino'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if background and useThumbAsFanart and background != icon:
		liz.setArt({'fanart': background})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addLink(name, image, params={}, plot=None, duration=None, begins=None, year=None, genre=None, director=None, cast=None, rating=None, mpaa=None, background=None, banner=None, studio=None, addType=0, FAVclear=False):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	info = {}
	info['Tvshowtitle'] = None
	info['Title'] = name
	info['Tagline'] = None
	info['Plot'] = plot
	info['Duration'] = duration
	if begins: info['Date'] = begins
	info['Year'] = year
	info['Genre'] = [genre]
	info['Director'] = [director]
	info['Cast'] = [cast]
	info['Studio'] = studio
	info['Rating'] = rating
	info['Mpaa'] = mpaa
	info['Mediatype'] = 'movie'
	liz.setInfo(type='Video', infoLabels=info)
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'banner': banner, 'fanart': defaultFanart})
	if background and useThumbAsFanart:
		liz.setArt({'fanart': background})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	entries = []
	if addType == 1 and FAVclear is False:
		entries.append([translation(30651), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'ADD', 'name': name, 'pict': None if image == icon else image, 'url': params.get('url'),
			'plot': None if plot is None else plot.replace('\n', '[CR]'), 'duration': duration, 'begins': begins, 'year': year, 'genre': genre, 'director': director, 'cast': cast, 'rating': rating, 'mpaa': mpaa, 'background': background, 'banner': banner, 'studio': studio}))])
	if FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image, 'url': params.get('url'),
			'plot': plot, 'duration': duration, 'begins': begins, 'year': year, 'genre': genre, 'director': director, 'cast': cast, 'rating': rating, 'mpaa': mpaa, 'background': background, 'banner': banner, 'studio': studio}))])
	entries.append([translation(30654), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, 'mode=AddToQueue')])
	liz.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)
