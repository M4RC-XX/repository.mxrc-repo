# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import xbmcvfs
import shutil
import time
from datetime import datetime, timedelta
import requests
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote, unquote, unquote_plus  # Python 2.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmc.translatePath, xbmc.LOGNOTICE, 'inputstreamaddon' # Stand: 05.12.20 / Python 2.X
else:
	from urllib.parse import urlencode, quote, unquote, unquote_plus  # Python 3.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmcvfs.translatePath, xbmc.LOGINFO, 'inputstream' # Stand: 05.12.20  / Python 3.X
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from .provider import Client


global debuging
HOST_AND_PATH                 = sys.argv[0]
ADDON_HANDLE                  = int(sys.argv[1])
dialog                                      = xbmcgui.Dialog()
addon                                     = xbmcaddon.Addon()
addon_id                                = addon.getAddonInfo('id')
addon_name                         = addon.getAddonInfo('name')
addon_version                      = addon.getAddonInfo('version')
addonPath                             = TRANS_PATH(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath                                = TRANS_PATH(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
searchHackFile                     = os.path.join(dataPath, 'searchString')
videoFavsFile                         = os.path.join(dataPath, 'watchlist_NETZKINO.json')
defaultFanart                        = (os.path.join(addonPath, 'fanart.jpg') if PY2 else os.path.join(addonPath, 'resources', 'media', 'fanart.jpg'))
icon                                         = (os.path.join(addonPath, 'icon.png') if PY2 else os.path.join(addonPath, 'resources', 'media', 'icon.png'))
artpic                                      = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
enableINPUTSTREAM          = addon.getSetting('useInputstream') == 'true'
prefSTREAM                           = addon.getSetting('prefer_stream')
approvedAge                          = addon.getSetting('no_age_restriction') == 'true'
useThumbAsFanart              = addon.getSetting('useThumbAsFanart') == 'true'
enableADJUSTMENT            = addon.getSetting('show_settings') == 'true'
DEB_LEVEL                            = (LOG_MESSAGE if addon.getSetting('enableDebug') == 'true' else xbmc.LOGDEBUG)
BASE_URL                              = 'https://www.netzkino.de/'
traversing                              = Client(Client.CONFIG_NETZKINO)

xbmcplugin.setContent(ADDON_HANDLE, 'movies')

def py2_enc(s, nom='utf-8', ign='ignore'):
	if PY2:
		if not isinstance(s, basestring):
			s = str(s)
		s = s.encode(nom, ign) if isinstance(s, unicode) else s
	return s

def py2_uni(s, nom='utf-8', ign='ignore'):
	if PY2 and isinstance(s, str):
		s = unicode(s, nom, ign)
	return s

def py3_dec(d, nom='utf-8', ign='ignore'):
	if not PY2 and isinstance(d, bytes):
		d = d.decode(nom, ign)
	return d

def translation(id):
	return py2_enc(addon.getLocalizedString(id))

def failing(content):
	log(content, xbmc.LOGERROR)

def debug_MS(content):
	log(content, DEB_LEVEL)

def log(msg, level=LOG_MESSAGE): # kompatibel mit Python-2 und Python-3
	msg = py2_enc(msg)
	return xbmc.log('[{0} v.{1}]{2}'.format(addon_id, addon_version, msg), level)

def get_userAgent():
	base = 'Mozilla/5.0 {0} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
	if xbmc.getCondVisibility('System.Platform.Android'):
		if 'arm' in os.uname()[4]: return base.format('(X11; CrOS armv7l 7647.78.0)') # ARM based Linux
		return base.format('(X11; Linux x86_64)') # x86 Linux
	elif xbmc.getCondVisibility('System.Platform.Windows'):
		return base.format('(Windows NT 10.0; WOW64)') # Windows
	elif xbmc.getCondVisibility('System.Platform.IOS'):
		return base.format('(iPhone; CPU iPhone OS 10_3 like Mac OS X)') # iOS iPhone/iPad
	elif xbmc.getCondVisibility('System.Platform.Darwin'):
		return base.format('(Macintosh; Intel Mac OS X 10_10_1)') # Mac OSX
	return base.format('(X11; Linux x86_64)') # x86 Linux

def _header():
	header = {}
	header['Connection'] = 'keep-alive'
	header['Pragma'] = 'no-cache'
	header['Cache-Control'] = 'no-cache'
	header['Accept'] = 'application/json, text/javascript, */*; q=0.01'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'en-US,en;q=0.8,de;q=0.7'
	return header

def getUrl(url, method='GET', headers=None, cookies=None, allow_redirects=True, verify=False, stream=None, data=None, json=None):
	simple = requests.Session()
	config = traversing.get_config()
	debug_MS("(common.getUrl) === URL that wanted : {0} ===".format(url))
	ANSWER = None
	simple.headers.update(config['header'])
	simple.headers.update(_header())
	try:
		if method in ['GET', 'LOAD']:
			response = simple.get(url, headers=headers, allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=30)
		elif method == 'POST':
			response = simple.post(url, headers=headers, allow_redirects=allow_redirects, verify=verify, data=data, json=json, timeout=30)
		ANSWER = response.json() if method in ['GET', 'POST'] else py2_enc(response.text)
		debug_MS("(common.getUrl) === send url-HEADERS : {0} ===".format(str(simple.headers)))
	except requests.exceptions.RequestException as e:
		failing("(common.getUrl) ERROR - ERROR - ERROR : ##### url: {0} === error: {1} #####".format(url, str(e)))
		dialog.notification(translation(30521).format('URL'), translation(30523).format(str(e)), icon, 10000)
		return sys.exit(0)
	return ANSWER

def ADDON_operate(IDD):
	js_query = xbmc.executeJSONRPC('{{"jsonrpc":"2.0", "id":1, "method":"Addons.GetAddonDetails", "params":{{"addonid":"{}", "properties":["enabled"]}}}}'.format(IDD))
	if '"enabled":false' in js_query:
		try:
			xbmc.executeJSONRPC('{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{}", "enabled":true}}}}'.format(IDD))
			failing("(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{0}* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####".format(IDD))
		except: pass
	if '"error":' in js_query:
		dialog.ok(addon_id, translation(30501).format(IDD))
		failing("(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{0}* ist NICHT installiert !!! #####".format(IDD))
		return False
	if '"enabled":true' in js_query:
		return True

def get_Description(info):
	if 'content' in info and info['content'] and len(info['content']) > 10:
		return cleaning(info['content'])
	return ""

def get_Picture(elem_id, resources, elem_type):
	if elem_type == 'thumbnail' and resources[elem_type] is not None and len(resources[elem_type]) != 0:
		return quote(py2_enc(resources[elem_type]), safe='/:?=')
	elif elem_type in resources and resources[elem_type] is not None and isinstance(resources[elem_type], list) and len(resources[elem_type][0]) != 0:
		return quote(py2_enc(resources[elem_type][0]), safe='/:?=')
	return None

def getSorting():
	method = [xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_VIDEO_YEAR, xbmcplugin.SORT_METHOD_VIDEO_RATING, xbmcplugin.SORT_METHOD_DATE]
	return method

def cleaning(text):
	if text is not None:
		text = py2_enc(text)
		for n in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&apos;', "'"), ("&quot;", "\""), ("&Quot;", "\""), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '), ('&hellip;', '...'), ('\xc2\xb7', '-'),
					("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''),
					('&#xC4;', 'Ä'), ('&#xE4;', 'ä'), ('&#xD6;', 'Ö'), ('&#xF6;', 'ö'), ('&#xDC;', 'Ü'), ('&#xFC;', 'ü'), ('&#xDF;', 'ß'), ('&#x201E;', '„'), ('&#xB4;', '´'), ('&#x2013;', '-'), ('&#xA0;', ' '),
					('&Auml;', 'Ä'), ('&Euml;', 'Ë'), ('&Iuml;', 'Ï'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&euml;', 'ë'), ('&iuml;', 'ï'), ('&ouml;', 'ö'), ('&uuml;', 'ü'), ('&#376;', 'Ÿ'), ('&yuml;', 'ÿ'),
					('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'),
					('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'Ó'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'),
					('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
					('&atilde;', 'ã'), ('&Atilde;', 'Ã'), ('&ntilde;', 'ñ'), ('&Ntilde;', 'Ñ'), ('&otilde;', 'õ'), ('&Otilde;', 'Õ'), ('&Scaron;', 'Š'), ('&scaron;', 'š'), ('&ccedil;', 'ç'), ('&Ccedil;', 'Ç'),
					('&alpha;', 'a'), ('&Alpha;', 'A'), ('&aring;', 'å'), ('&Aring;', 'Å'), ('&aelig;', 'æ'), ('&AElig;', 'Æ'), ('&epsilon;', 'e'), ('&Epsilon;', 'Ε'), ('&eth;', 'ð'), ('&ETH;', 'Ð'), ('&gamma;', 'g'), ('&Gamma;', 'G'),
					('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '), ('<br />', ' - '),
					("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
					('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ('\\x20', ' '), ('\\x3A', ':'), ('\\"', '"')):
					text = text.replace(*n)
		text = text.strip()
	return text

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split('&')
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
image = unquote_plus(params.get('image', ''))
pict = unquote_plus(params.get('pict', ''))
url = unquote_plus(params.get('url', ''))
plot = unquote_plus(params.get('plot', ''))
duration = unquote_plus(params.get('duration', ''))
begins = unquote_plus(params.get('begins', ''))
year = unquote_plus(params.get('year', ''))
genre = unquote_plus(params.get('genre', ''))
director = unquote_plus(params.get('director', ''))
cast = unquote_plus(params.get('cast', ''))
rating = unquote_plus(params.get('rating', ''))
mpaa = unquote_plus(params.get('mpaa', ''))
background = unquote_plus(params.get('background', ''))
banner = unquote_plus(params.get('banner', ''))
studio = unquote_plus(params.get('studio', ''))
mode = unquote_plus(params.get('mode', 'root'))
action = unquote_plus(params.get('action', ''))
extras = unquote_plus(params.get('extras', 'standard'))
