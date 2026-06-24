import os
import subprocess
import tempfile
import uuid
import logging
import paths

ytdlp_logger = logging.getLogger('youtube')

# ytdlp engine (taken from my yt downloader, revisited to work with ffmpeg)

def run(ytlink):
    # this is the main thing: takes the cookies, sets arguments for both ytdlp and fmpeg 
    cookies = paths.getCookies()
    if not cookies:
        ytdlp_logger.error("No cookie file found.")
        return None, None, None, "Cookie loading error."

    sessionId = str(uuid.uuid4())
    tempOut = tempfile.mkdtemp()

    ytdlp = [
        paths.getYtDlp(), ytlink,
        '-f', 'bestaudio',
        '--cookies', cookies,
        '--ffmpeg-location', paths.getFFmpeg(),
        '--no-playlist',
        '--quiet',
        '-o', '-',
    ]

    ffmpeg = [
        paths.getFFmpeg(),
        '-i', 'pipe:0',
        '-c:a', 'copy', # to not recode any audio
        '-hls_playlist_type', 'vod',
        # this line is important: the video fetching will be faster than the stream can load, 
        # by adding this line the player will treat everything as on-demand, starting from the beginning.
        '-f', 'hls',
        '-hls_segment_type', 'fmp4', 
        '-hls_time', '4',
        '-hls_list_size', '0',
        '-hls_segment_filename', os.path.join(tempOut, 'seg%03d.m4s'),
        os.path.join(tempOut, 'playlist.m3u8'),
    ]

    try:
        dlpProcess = subprocess.Popen(ytdlp, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) # starts ytdlp and outputs the song data to stdout
        FfmpegPRocess = subprocess.Popen(ffmpeg, stdin=dlpProcess.stdout, stdout=subprocess.DEVNULL,  stderr=subprocess.DEVNULL,) #starts ffmpeg to listen to ytdlp's stdout
        
        dlpProcess.stdout.close()
        return sessionId, tempOut, (dlpProcess, FfmpegPRocess), None
    except Exception as e:
        ytdlp_logger.error(f"HLS error: {e}")
        return None, None, None, str(e)


# the way ytdlp works is it gets the cdn link for the youtube track and then it downloads the audio/video via ffmpeg.
# this function returns the cdn link for that video/audio.
# this is very good to make large amount of users act as proxies instead of buying them.

def getCDNLink(ytlink):
    cookies = paths.getCookies()
    if not cookies:
        return None, "Cookie loading error."

    ytdlp = [
        paths.getYtDlp(), ytlink,
        '-f', 'bestaudio',
        '--cookies', cookies,
        '--no-playlist',
        '--quiet',
        '-g',
    ]

    try:
        result = subprocess.run(ytdlp, capture_output=True, text=True, timeout=30)
        url = result.stdout.strip()
        if not url:
            return None, "Could not extract CDN URL."
        return url, None
    except subprocess.TimeoutExpired:
        return None, "Timed out extracting URL."
    except Exception as e:
        return None, str(e)



# yay downlods
def download(ytlink):
    cookies = paths.getCookies()
    if not cookies:
        ytdlp_logger.error("No cookie file found.")
        return None, "Cookie loading error."

    tempDir = tempfile.mkdtemp()
    outTemplate = os.path.join(tempDir, '%(title)s.%(ext)s')

    ytdlp = [
        paths.getYtDlp(), ytlink,
        '-f', 'bestaudio',
        '--cookies', cookies,
        '--ffmpeg-location', paths.getFFmpeg(),
        '--no-playlist',
        '--quiet',
        '-x',
        '--audio-format', 'mp3',
        '--embed-thumbnail',
        '--embed-metadata',
        '-o', outTemplate,
    ]

    try:
        subprocess.run(ytdlp, check=True, stderr=subprocess.DEVNULL)
        files = os.listdir(tempDir)
        if not files:
            return None, "No output file found."
        return os.path.join(tempDir, files[0]), None
    except subprocess.CalledProcessError as e:
        ytdlp_logger.error(f"Download failed: {e}")
        return None, f"Download failed (exit {e.returncode})."
    except Exception as e:
        ytdlp_logger.error(f"Download error: {e}")
        return None, str(e)

# yay