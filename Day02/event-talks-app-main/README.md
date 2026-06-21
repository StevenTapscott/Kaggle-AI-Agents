# BigQuery Release Notes Dashboard

A premium web application built using **Python Flask** for the backend and **vanilla HTML/JavaScript/CSS** for the frontend. It fetches, parses, and formats Google Cloud's BigQuery Release Notes feed, allowing users to browse, search, filter, and share individual release items directly to Twitter/X.

## Features

- **Granular Updates**: Google's feed combines all release items for a day into a single feed entry. This application automatically parses and splits these entries into individual, category-tagged cards (e.g., *Feature*, *Issue*, *Deprecation*, *General*).
- **Premium User Interface**: Modern dark mode with glassmorphism layout, subtle ambient animations, and a responsive grid dashboard.
- **Instant Client-Side Filtering**:
  - Filter updates by category dynamically.
  - Search notes by keyword instantly.
  - Sort updates (Newest First vs. Oldest First).
- **Twitter/X Sharing**:
  - Select any release card to tweet about.
  - Customize the tweet inside a modal with an active character counter (280 characters limit).
  - Truncates long descriptions automatically to fit formatting and hashtags like `#BigQuery` and `#GoogleCloud`.
- **Feed Cache Control**: Server-side in-memory caching keeps the feed loading fast while the "Refresh Feed" button enables force-refreshing directly from the Google source feed.

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` package manager

### Installation

1. Navigate to the project directory:
   ```bash
   cd C:\Users\steve\bigquery_release_notes
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Run the Flask development server:
   ```bash
   python app.py
   ```

2. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## Project Structure

- `app.py`: Flask backend, feed fetcher, and parser logic.
- `templates/index.html`: Main Dashboard page template.
- `static/css/styles.css`: Dark mode styles, styling tokens, responsive grids, and modal styles.
- `static/js/app.js`: Interactive search, filtering, sorting, and modal tweet generation logic.
- `requirements.txt`: Python package dependencies.
