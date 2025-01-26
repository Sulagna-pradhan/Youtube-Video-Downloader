from flask import Flask, request, send_file, jsonify, render_template
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
import os

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')

@app.route('/')
def home():
    return render_template('index.html')  # Serve the frontend HTML file

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    file_path = None  # Initialize file_path to avoid UnboundLocalError

    try:
        # Initialize YouTube object
        yt = YouTube(url)
        
        # Check for availability of the video
        if yt.check_availability() is False:
            return jsonify({"error": "Video is unavailable or restricted"}), 403
        
        # Get the highest resolution stream
        video_stream = yt.streams.get_highest_resolution()

        if video_stream is None:
            return jsonify({"error": "No available streams for download"}), 400
        
        # Download the video
        file_path = video_stream.download()

        # Return the video file
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=f"{yt.title}.mp4",
            mimetype="video/mp4"
        )
    except VideoUnavailable:
        return jsonify({"error": "Video unavailable on YouTube"}), 403
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        # Clean up downloaded file after sending response, if file_path is set
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
