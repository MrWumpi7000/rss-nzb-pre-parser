import feedparser
import re
import zipfile
import time
import requests
from datetime import datetime
from pathlib import Path

# Create the main directory if it doesn't exist
directory = Path("rss-nzb-pre-parser-saved_files")
if not directory.exists():
    directory.mkdir()

# Parse the RSS feed
parsed_feed = feedparser.parse(r'rss.xml')

# Process each entry in the feed
for entry in parsed_feed['entries']:
    release = entry.title
    print(f'Release: {release}')
    print(f'Link: {entry.link}')

    # Make the API request
    response = requests.get(f'https://api.predb.net/?type=pre&release=' + release)
    
    # Parse the JSON response
    try:
        r = response.json()
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        continue
    
    # Check the status and results
    if r.get('status') == 'success' and r.get('results') > 0:
        pretime = r['data'][0]['pretime']
        print(f'Pretime: {pretime}')
        
        # Convert the pretime (assuming it's a UNIX timestamp)
        pretime_datetime = datetime.fromtimestamp(pretime)
        print(f'Pretime (datetime): {pretime_datetime}')

        # Get the date as a string in the format YYYY-MM-DD
        date_str = pretime_datetime.strftime("%Y-%m-%d")

        # Define the directory path for this date
        date_directory = directory / date_str
        print(f'Checking directory: {date_directory}')

        # Create the directory if it doesn't exist
        if not date_directory.exists():
            date_directory.mkdir(parents=True, exist_ok=True)
            print(f'Directory created: {date_directory}')
        else:
            print(f'Directory already exists: {date_directory}')
        
        # Download the file from the link
        file_url = entry.link  # Assuming entry.link is the file URL
        file_response = requests.get(file_url, allow_redirects=True)
        
        # Extract file extension from URL
        file_extension = file_url.split('.')[-1]
        file_path = date_directory / f"{release}.{file_extension}"
        
        # Save the file with the correct extension
        with open(file_path, 'wb') as file:
            file.write(file_response.content)
        print(f'File saved: {file_path}')

        # Create a ZIP file for the release
        zip_file_path = date_directory / f"{release}.zip"
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, file_path.name)
        print(f'Directory zipped: {zip_file_path}')

        # Remove the original file
        file_path.unlink()
        print(f'Original file removed: {file_path}')
    else:
        print('No data found or request unsuccessful.')
    
    # Sleep to avoid hitting the API too frequently
    time.sleep(2.5)
