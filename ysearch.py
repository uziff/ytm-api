import random
import paths
import logging
from ytmusicapi import YTMusic

# taken by my old downloader.
# documentation: https://ytmusicapi.readthedocs.io/en/stable/
# github: https://github.com/sigma67/ytmusicapi

def lookup_ytmusic(query, limit=10):
    try:
        ytmusic = YTMusic(paths.getYTmusicAuth())
        results = ytmusic.search(query, filter='songs', limit=limit)
        return results
    except Exception as e:
        print(f"Error while lookup: {e}")
        web_logger.error(f"Error while lookup: {e}")
        return []