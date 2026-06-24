import os
import shutil

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

# py files
import ytsong
import ysearch

app = FastAPI(title="ytmAPI")

SESSIONS = {}


class StreamRequest(BaseModel):
    url: str


@app.post("/stream")
def start_stream(body: StreamRequest):
    session_id, output_dir, processes, error = ytsong.run(body.url)
    if error:
        raise HTTPException(status_code=500, detail=error)
    SESSIONS[session_id] = {"output_dir": output_dir, "processes": processes}
    return {"session_id": session_id, "playlist_url": f"/hls/{session_id}/playlist.m3u8"}


@app.get("/status/{session_id}")
def stream_status(session_id: str):
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    playlist = os.path.join(session["output_dir"], "playlist.m3u8")
    ready = os.path.isfile(playlist) and os.path.getsize(playlist) > 0
    return {"ready": ready}


@app.get("/hls/{session_id}/playlist.m3u8")
def serve_playlist(session_id: str):
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    playlist = os.path.join(session["output_dir"], "playlist.m3u8")
    if not os.path.isfile(playlist):
        raise HTTPException(status_code=404, detail="Playlist not ready")
    return FileResponse(playlist, media_type="application/vnd.apple.mpegurl")


@app.get("/hls/{session_id}/{segment}")
def serve_segment(session_id: str, segment: str):
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    seg_path = os.path.join(session["output_dir"], segment)
    if not os.path.isfile(seg_path):
        raise HTTPException(status_code=404, detail="Segment not found")
    media_type = "video/iso.segment" if segment.endswith(".m4s") else "video/mp2t"
    return FileResponse(seg_path, media_type=media_type)


@app.delete("/stream/{session_id}")
def stop_stream(session_id: str):
    session = SESSIONS.pop(session_id, None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    for proc in session.get("processes", ()):
        if proc.poll() is None:
            proc.terminate()
    shutil.rmtree(session["output_dir"], ignore_errors=True)
    return {"message": "Stream stopped"}


@app.get("/cdn")
def cdn_url(url: str = Query(..., description="YouTube URL")):
    cdn, error = ytsong.get_cdn_url(url)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return {"url": cdn}


@app.get("/download")
def download_track(background_tasks: BackgroundTasks, url: str = Query(..., description="YouTube URL")):
    file_path, error = ytsong.download(url)
    if error:
        raise HTTPException(status_code=500, detail=error)
    temp_dir = os.path.dirname(file_path)
    background_tasks.add_task(shutil.rmtree, temp_dir, True)
    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=os.path.basename(file_path),
    )


@app.get("/search/{query}")
def search(query: str):
    return ysearch.lookup_ytmusic(query, limit=10)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
