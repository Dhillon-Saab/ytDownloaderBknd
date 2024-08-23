from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse
import subprocess
import os
from time import sleep
import re
import uvicorn

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def main_page():
    return """
        <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Running</h1>
        </body>
    </html>
    """ 

@app.get("/download_video")
async def download_video(url: str):
    # This block provides with location pointer and the command to be executed
    exePath = "yt-dlp.exe"
    cmd = [exePath, "-f", "best", "-o", "%(title)s.%(ext)s", url]

    # This runs the command in the cli using subprocess
    process = subprocess.run(cmd, capture_output=True, text=True)

    # Get the file name from the process
    output = process.stdout
    pattern = r"(\[.+?\]\s+)(.+)\.mp4"
    match = re.search(pattern, output)
    if match:
        file_name = match.group(2) + ".mp4"
        fileName = file_name.replace('Destination: ', '')

    else:
        print("Error: Unable to find file name in output")
        return Response(status_code=500, content="Error: Unable to find file name in output")

    filePath = os.path.join(os.getcwd(), fileName)

    while not os.path.exists(filePath):
        sleep(1)

    if(os.path.exists(filePath)):
        return Response(content=open(filePath, 'rb').read(), media_type=f'video/{fileName.split(".")[-1]}', headers={'Content-Disposition': f'attachment; filename="{fileName}"'})
    else:
        return Response(status_code=404, content="File not found")


# @app.get("/download_file")
# async def download_file():
#     file_path = "C:/pythonProjects/test.txt"
#     file_name = "test.txt"
#     response = Response(content=open(file_path, "rb").read(), media_type="application/octet-stream")
#     response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
#     return response


@app.get("/try_video")
async def download_video(video_id: str):
    yt_dlp_cmd = f"yt-dlp -f best -o - https://www.youtube.com/watch?v={video_id}"
    process = subprocess.Popen(yt_dlp_cmd, shell=True, stdout=subprocess.PIPE)
    return StreamingResponse(process.stdout, media_type="video/mp4")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)