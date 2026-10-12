from flask import Flask, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)

PHOTO_DIR = os.path.expanduser("~/smart-doorbell/photos")


@app.route("/photos/<path:filename>")
def photos(filename):
    return send_from_directory(PHOTO_DIR, filename)


@app.route("/")
def home():
    photos = []

    if os.path.exists(PHOTO_DIR):
        photos = [
            f for f in os.listdir(PHOTO_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

    # Newest photos first
    photos.sort(
        key=lambda f: os.path.getmtime(os.path.join(PHOTO_DIR, f)),
        reverse=True
    )

    cards = ""

    for photo in photos:
        path = os.path.join(PHOTO_DIR, photo)

        timestamp = datetime.fromtimestamp(
            os.path.getmtime(path)
        ).strftime("%B %d, %Y at %I:%M:%S %p")

        cards += f"""
        <div class="card">
            <img src="/photos/{photo}">
            <div class="info">
                <strong>{timestamp}</strong>
                <p>{photo}</p>
            </div>
        </div>
        """

    if not photos:
        cards = "<p>No visitors recorded yet.</p>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>

        <title>Smart Doorbell</title>

        <!-- Automatically refresh every 5 seconds -->
        <meta http-equiv="refresh" content="5">

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
            }}

            header {{
                background: #222;
                color: white;
                padding: 25px;
                text-align: center;
            }}

            .container {{
                max-width: 900px;
                margin: auto;
                padding: 25px;
            }}

            .status {{
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 25px;
            }}

            .online {{
                color: green;
                font-weight: bold;
            }}

            .card {{
                background: white;
                margin-bottom: 25px;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}

            .card img {{
                width: 100%;
                display: block;
            }}

            .info {{
                padding: 15px;
            }}

            .info p {{
                color: #777;
            }}

        </style>

    </head>

    <body>

        <header>
            <h1>Smart Doorbell</h1>
            <p>Raspberry Pi Visitor Monitor</p>
        </header>

        <div class="container">

            <div class="status">
                System:
                <span class="online">● ONLINE</span>

                <br><br>

                Visitors recorded: {len(photos)}
            </div>

            <h2>Visitor History</h2>

            {cards}

        </div>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
