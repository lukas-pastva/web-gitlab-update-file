import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration - Read from environment variables
GITLAB_API_URL = os.getenv('GITLAB_API_URL', 'https://gitlab.com/api/v4')
PERSONAL_ACCESS_TOKEN = os.getenv('PERSONAL_ACCESS_TOKEN')
PROJECT_ID = os.getenv('PROJECT_ID')
FILE_PATH = os.getenv('FILE_PATH')  # e.g., 'path/to/your/file.ext'
BRANCH = os.getenv('BRANCH', 'main')

HEADERS = {
    'PRIVATE-TOKEN': PERSONAL_ACCESS_TOKEN,
    'Content-Type': 'application/json'
}

def get_filename(file_path):
    """Extracts the filename from the file path."""
    return os.path.basename(file_path)

@app.route('/')
def index():
    filename = get_filename(FILE_PATH)
    return render_template('index.html', filename=filename)

@app.route('/api/get_file', methods=['GET'])
def get_file():
    try:
        # Encode the file path for URL
        encoded_file_path = quote(FILE_PATH, safe='')
        url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/repository/files/{encoded_file_path}/raw"
        params = {'ref': BRANCH}
        response = requests.get(url, headers={'PRIVATE-TOKEN': PERSONAL_ACCESS_TOKEN}, params=params)

        if response.status_code == 200:
            return jsonify({'content': response.text}), 200
        else:
            return jsonify({'error': f"Error fetching file: {response.status_code} {response.reason}"}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_file', methods=['POST'])
def save_file():
    try:
        data = request.get_json()
        new_content = data.get('content', '')

        # Get the latest commit ID
        encoded_file_path = quote(FILE_PATH, safe='')
        info_url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/repository/files/{encoded_file_path}"
        info_params = {'ref': BRANCH}
        info_response = requests.get(info_url, headers=HEADERS, params=info_params)

        if info_response.status_code != 200:
            return jsonify({'error': f"Error fetching file info: {info_response.status_code} {info_response.reason}"}), info_response.status_code

        file_info = info_response.json()
        last_commit_id = file_info.get('last_commit_id')

        # Prepare payload for updating the file
        payload = {
            'branch': BRANCH,
            'content': new_content,
            'commit_message': 'Update file via web editor',
            'last_commit_id': last_commit_id
        }

        # Update the file
        update_url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/repository/files/{encoded_file_path}"
        update_response = requests.put(update_url, headers=HEADERS, json=payload)

        if update_response.status_code in [200, 201]:
            return jsonify({'message': 'File saved successfully!'}), 200
        else:
            error_data = update_response.json()
            error_message = error_data.get('message', 'Unknown error')
            return jsonify({'error': f"Error saving file: {update_response.status_code} {update_response.reason} - {error_message}"}), update_response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the app on port 5000 and make it accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
