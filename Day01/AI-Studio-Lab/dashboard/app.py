import os
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template
from google.cloud import bigquery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# BigQuery config from environment variables
PROJECT_ID = os.getenv("GCP_PROJECT")
DATASET_ID = os.getenv("BQ_DATASET", "document_processing")
TABLE_ID = os.getenv("BQ_TABLE", "processed_metadata")

# Rich mock dataset for fallback and local testing
MOCK_DOCUMENTS = [
    {
        "filename": "q2_financials_invoice.pdf",
        "date": "2026-06-15T21:10:00Z",
        "tags": ["finance", "invoice", "pdf", "q2"],
        "word_count": 1420
    },
    {
        "filename": "ocr_tesseract_scan.png",
        "date": "2026-06-15T20:30:15Z",
        "tags": ["image", "ocr", "scan", "raw"],
        "word_count": 350
    },
    {
        "filename": "employee_handbook_v4.txt",
        "date": "2026-06-15T18:45:12Z",
        "tags": ["hr", "handbook", "text", "official"],
        "word_count": 5420
    },
    {
        "filename": "marketing_strategy_draft.docx",
        "date": "2026-06-15T15:22:01Z",
        "tags": ["marketing", "draft", "strategy"],
        "word_count": 980
    },
    {
        "filename": "serverless_specifications.pdf",
        "date": "2026-06-15T09:12:44Z",
        "tags": ["technical", "serverless", "pdf", "gcp"],
        "word_count": 2150
    },
    {
        "filename": "confidential_meeting_notes.txt",
        "date": "2026-06-14T17:05:00Z",
        "tags": ["notes", "internal", "text", "confidential"],
        "word_count": 620
    }
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/documents")
def get_documents():
    """
    Fetches processed document metadata from BigQuery.
    Falls back to mock data if BQ is inaccessible.
    """
    documents = []
    use_fallback = False
    
    try:
        # Attempt to query BigQuery
        bq_client = bigquery.Client()
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}" if PROJECT_ID else f"{DATASET_ID}.{TABLE_ID}"
        
        query = f"""
            SELECT filename, date, tags, word_count 
            FROM `{table_ref}` 
            ORDER BY date DESC
        """
        
        logger.info(f"Querying BigQuery table: {table_ref}")
        query_job = bq_client.query(query)
        results = query_job.result()
        
        for row in results:
            # Convert timestamp to ISO format string
            date_str = row.date.isoformat() if hasattr(row.date, "isoformat") else str(row.date)
            # Row tags is a repeated field (list of strings)
            tags_list = list(row.tags) if row.tags else []
            
            documents.append({
                "filename": row.filename,
                "date": date_str,
                "tags": tags_list,
                "word_count": row.word_count
            })
            
        logger.info(f"Successfully loaded {len(documents)} rows from BigQuery.")
        
        # If the table exists but is empty, we still return empty, not fallback.
        # But if there are no records, return a JSON response.
        
    except Exception as e:
        logger.warning(f"Could not fetch metadata from BigQuery. Falling back to mock data. Reason: {e}")
        use_fallback = True
        
    if use_fallback:
        documents = MOCK_DOCUMENTS
        
    return jsonify({
        "status": "success",
        "source": "bigquery" if not use_fallback else "mock_data",
        "data": documents
    })

if __name__ == "__main__":
    # Run server on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
