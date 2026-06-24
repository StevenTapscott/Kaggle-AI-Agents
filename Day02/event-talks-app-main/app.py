import os
import re
import time
import requests
import feedparser
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Cache configuration
FEED_URL = "https://docs.cloud.google.com/feeds/bigquery-release-notes.xml"
CACHE_TIMEOUT = 600  # 10 minutes cache duration in seconds
cache = {
    "data": None,
    "last_fetched": 0
}

def parse_release_notes(feed_content):
    """
    Parses the BigQuery release notes feed into individual update entries.
    Google feeds combine all updates for a single day into one <entry>.
    We parse and split these updates into separate granular items.
    """
    feed = feedparser.parse(feed_content)
    parsed_entries = []

    for entry in feed.entries:
        date_str = entry.title  # E.g., "June 15, 2026"
        updated_time = entry.get("updated", "")
        
        # Get HTML content
        content_val = ""
        if "content" in entry and len(entry.content) > 0:
            content_val = entry.content[0].value
        elif "summary" in entry:
            content_val = entry.summary
            
        if not content_val:
            continue

        # Split content by <h3> headers to isolate individual updates
        # e.g., <h3>Feature</h3>\n<p>...</p>\n<h3>Issue</h3>...
        parts = re.split(r'<h3>(.*?)</h3>', content_val)
        
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                update_type = parts[i].strip()
                update_html = parts[i+1].strip() if i+1 < len(parts) else ""
                
                # Create a unique ID based on date, type and contents
                update_id = f"{updated_time}_{update_type}_{i}"
                
                parsed_entries.append({
                    "id": update_id,
                    "date": date_str,
                    "timestamp": updated_time,
                    "type": update_type,
                    "html": update_html
                })
        else:
            # Fallback if no <h3> tags are found
            parsed_entries.append({
                "id": f"{updated_time}_general_0",
                "date": date_str,
                "timestamp": updated_time,
                "type": "General",
                "html": content_val
            })
            
    return parsed_entries

def get_feed_data(force_refresh=False):
    """
    Fetches the feed from the Google feed URL.
    Implements in-memory caching to avoid rate-limiting and ensure fast responses.
    """
    current_time = time.time()
    
    # Return cache if valid and not forcing a refresh
    if cache["data"] is not None and not force_refresh:
        if (current_time - cache["last_fetched"]) < CACHE_TIMEOUT:
            return cache["data"], False

    try:
        # Fetch the feed
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(FEED_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the feed data
        parsed_data = parse_release_notes(response.text)
        
        # Update cache
        cache["data"] = parsed_data
        cache["last_fetched"] = current_time
        return parsed_data, True
        
    except Exception as e:
        print(f"Error fetching feed: {e}")
        # Return stale cache if available in case of failure, otherwise raise
        if cache["data"] is not None:
            return cache["data"], False
        raise e

@app.route("/")
def index():
    """Serves the main application page."""
    return render_template("index.html")

@app.route("/api/notes")
def get_notes():
    """API endpoint to retrieve release notes, with optional force refresh."""
    force_refresh = request.args.get("refresh", "false").lower() == "true"
    try:
        notes, fetched_fresh = get_feed_data(force_refresh=force_refresh)
        return jsonify({
            "success": True,
            "notes": notes,
            "cached": not fetched_fresh,
            "last_fetched": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cache["last_fetched"]))
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
