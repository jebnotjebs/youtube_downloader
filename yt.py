from flask import Flask, render_template, request, jsonify, send_file
from pytubefix import YouTube
from io import BytesIO

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_title", methods=["GET"])
def get_title():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        yt = YouTube(url, use_po_token=True)
        title = yt.title
        return jsonify({"title": title})
    except ValueError as ve:  # Handle specific library errors
        return jsonify({"error": f"Invalid URL: {str(ve)}"}), 400
    except Exception as e:  # Catch all other exceptions
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route("/download", methods=["GET"])
def download_video():
    url = request.args.get("url")
    format = request.args.get("format")

    try:
        yt = YouTube(url)
        title = yt.title.replace(" ", "_")  # Replace spaces with underscores
        file_extension = "mp4" if format == "mp4" else "mp3"

        if format == "mp4":
            video_stream = yt.streams.filter(
                progressive=True, file_extension="mp4"
            ).first()
            if video_stream:
                buffer = BytesIO()
                video_stream.stream_to_buffer(buffer)
                buffer.seek(0)
                return send_file(
                    buffer,
                    as_attachment=True,
                    download_name=f"{title}.{file_extension}",
                    mimetype="video/mp4",
                )
        else:  # MP3
            audio_stream = yt.streams.filter(
                only_audio=True, file_extension="mp4"
            ).first()
            if audio_stream:
                buffer = BytesIO()
                audio_stream.stream_to_buffer(buffer)
                buffer.seek(0)
                return send_file(
                    buffer,
                    as_attachment=True,
                    download_name=f"{title}.{file_extension}",
                    mimetype="audio/mpeg",
                )

        return jsonify({"status": "error", "message": "Stream not available"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
