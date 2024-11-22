import subprocess
from flask import Flask, render_template, request, jsonify, send_file
from pytubefix import YouTube
from io import BytesIO
import json
from urllib.parse import unquote  # Import unquote to decode URL


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate_token", methods=["GET"])
def generate_token():
    try:
        # Run the Node.js script from Python
        result = subprocess.run(
            ["node", "generateToken.js"], capture_output=True, text=True, check=True
        )

        # Parse the generated output (expected to be a JSON string)
        tokens = result.stdout.strip()  # Get the output
        tokens_json = json.loads(tokens)  # Parse as JSON

        # Access visitor data and po_token from the parsed JSON
        visitor_data = tokens_json.get("visitorData")
        po_token = tokens_json.get("poToken")

        return jsonify({"visitorData": visitor_data, "poToken": po_token})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Subprocess failed: {e.stderr}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download", methods=["GET"])
def download_video():
    url = request.args.get("url")
    format = request.args.get("format")

    # Decode the URL to handle encoding properly
    url = unquote(url)  # Decode URL if it has been URL-encoded

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


if __name__ == "__main__":
    app.run(debug=True)
