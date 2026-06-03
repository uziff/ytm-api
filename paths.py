# paths for anything
import os
import random
import logging
# import syncFolders

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
WORK_DIR = BASE_DIR + '/'

# Commands
def getYtDlp():
    for p in [
        '/usr/local/bin/yt-dlp', '/usr/bin/yt-dlp',
        os.path.expanduser('~/.local/bin/yt-dlp'),
        '/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp',
        '/opt/homebrew/bin/yt-dlp',
    ]:
        if os.path.isfile(p):
            return p
    return 'yt-dlp'

# Utils
def getFFmpeg():
    for p in [
        '/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg',
        '/opt/homebrew/bin/ffmpeg',
    ]:
        if os.path.isfile(p):
            return p
    return 'ffmpeg'


# Cookies logic
def getCookiesDir():
    return os.path.join(BASE_DIR, 'cookies')

def getYTMusicAuthDir():
    return os.path.join(BASE_DIR, 'browser')

def getCookies():
    cookies_dir = getCookiesDir()
    if not os.path.isdir(cookies_dir):
        return None
    try:
        cookie_files = [f for f in os.listdir(cookies_dir) if os.path.isfile(os.path.join(cookies_dir, f))]
        if not cookie_files:
            logging.getLogger('spotdl').critical("Nessun cookie trovato nella cartella.")
            return None
    except OSError:
        return None

    random_cookie_file = random.choice(cookie_files)
    return os.path.join(cookies_dir, random_cookie_file)

def getIDs():
    return os.path.join(getKeys(), 'client_ids.txt')

def getSECRETs():
    return os.path.join(getKeys(), 'client_secrets.txt')

def getYTmusicAuth():
    return os.path.join(getYTMusicAuthDir(), 'browser.json')

def getKeys():
    return os.path.join(BASE_DIR, 'keys')


# Server
def getNavidromeURL():
    return 'http://127.0.0.1:4533/music'

