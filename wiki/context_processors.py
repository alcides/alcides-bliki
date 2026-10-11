import json
import logging
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from django.core.cache import cache

from .models import Page


logger = logging.getLogger(__name__)

LASTFM_USER = "alcidesfonseca"
BGG_USER = "alcides"


def _get_json(url):
    with urlopen(url, timeout=5) as response:
        return json.load(response)


def _recent_lastfm_tracks():
    api_key = os.environ.get("LASTFM_API_KEY")
    if not api_key:
        return None

    query = urlencode({
        "method": "user.getrecenttracks",
        "user": LASTFM_USER,
        "api_key": api_key,
        "format": "json",
        "limit": 100,
    })
    try:
        tracks = _get_json(f"https://ws.audioscrobbler.com/2.0/?{query}")
        tracks = tracks["recenttracks"]["track"]
        if not isinstance(tracks, list):
            tracks = [tracks]
        recent_tracks = []
        seen_tracks = set()
        for track in tracks:
            artist = track.get("artist", {}).get("#text", "")
            identity = (track["name"], artist)
            if identity in seen_tracks:
                continue
            seen_tracks.add(identity)
            recent_tracks.append({
                "name": track["name"],
                "artist": artist,
                "url": track.get("url"),
                "now_playing": track.get("@attr", {}).get("nowplaying") == "true",
            })
            if len(recent_tracks) == 13:
                break
        return recent_tracks
    except (ElementTree.ParseError, KeyError, OSError, ValueError) as error:
        logger.warning("Could not retrieve Last.fm activity: %s", error)
        return None


def _recent_bgg_plays():
    token = os.environ.get("BGG_API_TOKEN")
    if not token:
        return None

    request = Request(
        f"https://boardgamegeek.com/xmlapi2/plays?{urlencode({'username': BGG_USER, 'subtype': 'boardgame'})}",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            root = ElementTree.parse(response).getroot()
        collection_request = Request(
            f"https://boardgamegeek.com/xmlapi2/collection?{urlencode({'username': BGG_USER, 'stats': 1})}",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urlopen(collection_request, timeout=5) as response:
            collection = ElementTree.parse(response).getroot()
        ratings = {
            item.get("objectid"): item.find("stats/rating").get("value")
            for item in collection.findall("item")
            if item.find("stats/rating") is not None
            and item.find("stats/rating").get("value") != "N/A"
        }
        plays = []
        seen_games = set()
        for play in root.findall("./play"):
            item = play.find("item")
            if item is None or item.get("objectid") in seen_games:
                continue
            seen_games.add(item.get("objectid"))
            plays.append({
                "name": item.get("name"),
                "url": f"https://boardgamegeek.com/boardgame/{item.get('objectid')}/",
                "rating": ratings.get(item.get("objectid")),
            })
            if len(plays) == 13:
                break
        return plays
    except (ElementTree.ParseError, OSError, ValueError) as error:
        logger.warning("Could not retrieve BoardGameGeek activity: %s", error)
        return None


def _cached_activity(key, fetcher):
    value = cache.get(key)
    if value is None:
        value = fetcher() or False
        cache.set(key, value, 15 * 60)
    return value or None


def blogroll(request):
	"""Make the editable blog-roll page available to shared templates."""
	return {
		'blogroll_page': Page.objects.filter(
			slug__in=('blogroll', '/blogroll'),
		).first(),
	}


def current_activity(request):
    """Expose recent listening and playing activity to the shared footer."""
    return {
        "lastfm_tracks": _cached_activity("lastfm-recent-tracks", _recent_lastfm_tracks),
        "bgg_plays": _cached_activity("bgg-recent-plays", _recent_bgg_plays),
    }
