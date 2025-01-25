# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcaddon
PY2 = sys.version_info[0] == 2


def py2_enc(s, nom='utf-8', ign='ignore'):
	if PY2:
		if not isinstance(s, basestring):
			s = str(s)
		s = s.encode(nom, ign) if isinstance(s, unicode) else s
	return s

def translation(id):
	return py2_enc(xbmcaddon.Addon().getLocalizedString(id))


class Client(object):
	CONFIG_NETZKINO = {
		'url': 'https://api.netzkino.de.simplecache.net/capi-2.0a/{}',
		'index_entries': 'https://api.netzkino.de.simplecache.net/capi-2.0a/index.json?d=www&l=de-DE&g=DE',
		'category_entries': 'https://api.netzkino.de.simplecache.net/capi-2.0a/categories/{}.json?d=www&l=de-DE&g=DE',
		'movie_entries': 'https://api.netzkino.de.simplecache.net/capi-2.0a/movies/{}.json?d=www&l=de-DE&g=DE',
		'search_query': 'https://api.netzkino.de.simplecache.net/capi-2.0a/search?q={}&d=www&l=de-DE&g=DE',
		'parent': 0,
		'category_thumb': 'https://pmd.bilder.netzkino.de/bilder/categories_trans/{}.png',
		'category_fanart': 'https://pmd.bilder.netzkino.de/bilder/webseite/Genre/{}.jpg',
		'streaming_hls': 'https://nk_seite_hls-vh.akamaihd.net/i/{}.mp4/master.m3u8',
		'streaming_pmd': 'https://pmd.netzkino-seite.netzkino.de/{}.mp4',
		'WIDEVINE_LICENSE_URL': 'https://token.netzkino.de/token/wv/{}',
		'picks': [
		{
			'title': translation(30602),
			'slug': 'neu',
			'id': 81
		},
		{
			'title': translation(30603),
			'slug': 'frontpage-exklusiv',
			'id': 9471
		},
		{
			'title': translation(30604),
			'slug': 'filme_mit_auszeichnungen',
			'id': 6621
		},
		{
			'title': translation(30605),
			'slug': 'top-20-frontpage',
			'id': 10643
		},
		{
			'title': translation(30606),
			'slug': 'highlights',
			'id': 8
		},
		{
			'title': translation(30607),
			'slug': 'featured',
			'id': 161
		},
		{
			'title': translation(30608),
			'slug': 'meisgesehene_filme',
			'id': 6611
		},
		{
			'title': translation(30609),
			'slug': 'beste-bewertung',
			'id': 9431
		},
		{
			'title': translation(30610),
			'slug': 'empfehlungen_woche',
			'id': 6801
		},
		{
			'title': translation(30611),
			'slug': 'letzte-chance',
			'id': 10633
		}],
		'genres': [
		{
			'title': translation(30631),
			'slug': 'animekino',
			'id': 8951
		},
		{
			'title': translation(30632),
			'slug': 'actionkino',
			'id': 1
		},
		{
			'title': translation(30633),
			'slug': 'arthousekino',
			'id': 51
		},
		{
			'title': translation(30634),
			'slug': 'asiakino',
			'id': 10
		},
		{
			'title': translation(30635),
			'slug': 'dramakino',
			'id': 4
		},
		{
			'title': translation(30636),
			'slug': 'kinderkino',
			'id': 35
		},
		{
			'title': translation(30637),
			'slug': 'liebesfilmkino',
			'id': 18
		},
		{
			'title': translation(30638),
			'slug': 'horrorkino',
			'id': 5
		},
		{
			'title': translation(30639),
			'slug': 'scifikino',
			'id': 6
		},
		{
			'title': translation(30640),
			'slug': 'spasskino',
			'id': 3
		},
		{
			'title': translation(30641),
			'slug': 'thrillerkino',
			'id': 32
		},
		{
			'title': translation(30642),
			'slug': 'themenkino-genre',
			'id': 10333
		},
		{
			'title': translation(30643),
			'slug': 'kinoab18',
			'id': 71
		}],
		'header': {
			'Origin': 'https://www.netzkino.de',
			'Referer': 'https://www.netzkino.de/'
		}
	}

	def __init__(self, config):
		self._config = config

	def get_config(self):
		return self._config
