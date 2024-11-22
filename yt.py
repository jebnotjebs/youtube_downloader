import subprocess
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
    except ValueError as ve:
        print(f"ValueError: {ve}")  # Logs for debugging
        return jsonify({"error": f"Invalid URL: {str(ve)}"}), 400
    except Exception as e:
        print(f"Exception: {e}")  # Logs for debugging
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


@app.route("/generate_token", methods=["GET"])
def generate_token():
    try:
        # Run the Node.js script from Python
        result = subprocess.run(
            ["node", "generateToken.js"], capture_output=True, text=True
        )
        # Return the generated token as a JSON response
        return jsonify({"token": result.stdout})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
