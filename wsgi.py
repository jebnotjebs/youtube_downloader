from waitress import serve
from yt import app

if __name__ == "__main__":
    # For production use Waitress
    serve(app, host="0.0.0.0", port=8080)
