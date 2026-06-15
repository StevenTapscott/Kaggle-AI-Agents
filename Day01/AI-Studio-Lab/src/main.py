import base64
import json
import os
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from google.cloud import storage
from google.cloud import bigquery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GCS Event-Driven OCR Processor")

# BigQuery details from environment variables
PROJECT_ID = os.getenv("GCP_PROJECT")
DATASET_ID = os.getenv("BQ_DATASET", "document_processing")
TABLE_ID = os.getenv("BQ_TABLE", "processed_metadata")

# Pub/Sub Payload Pydantic Models
class PubSubMessage(BaseModel):
    attributes: Optional[dict] = None
    data: Optional[str] = None
    messageId: Optional[str] = None
    publishTime: Optional[str] = None

class PubSubPayload(BaseModel):
    message: PubSubMessage
    subscription: str

def simulate_ocr(file_content: bytes, filename: str) -> dict:
    """
    Simulates OCR. For text files, counts words and extracts long words as tags.
    For other file types, simulates OCR based on size and extension.
    """
    word_count = 0
    tags = []
    
    ext = os.path.splitext(filename.lower())[1]
    
    if ext == ".txt":
        try:
            text = file_content.decode("utf-8")
            words = text.split()
            word_count = len(words)
            # Use unique words longer than 5 chars as tags
            candidate_tags = [w.strip(".,!?;:()\"'").lower() for w in words if len(w) > 5]
            tags = list(set(candidate_tags))[:5]
        except Exception as e:
            logger.warning(f"Failed to decode text file {filename}: {e}")
            word_count = 0
    elif ext == ".pdf":
        word_count = max(10, len(file_content) // 50)
        tags = ["pdf_document", "extracted_text", "pdf"]
    elif ext in [".png", ".jpg", ".jpeg"]:
        word_count = max(5, len(file_content) // 1000)
        tags = ["image_ocr", "image", ext[1:]]
    else:
        word_count = max(1, len(file_content) // 100)
        tags = ["generic_document", ext[1:] if ext else "unknown"]
        
    tags.append("serverless-pipeline")
    # Clean tags list
    tags = list(set([t for t in tags if t]))
    
    return {"word_count": word_count, "tags": tags}

@app.post("/webhook", status_code=status.HTTP_200_OK)
async def receive_event(payload: PubSubPayload):
    """
    Receives Pub/Sub messages pushed to this endpoint when files are uploaded to GCS.
    """
    message = payload.message
    attributes = message.attributes or {}
    
    event_type = attributes.get("eventType")
    bucket_id = attributes.get("bucketId")
    object_id = attributes.get("objectId")
    
    # Fallback to decode data if attributes are missing
    if not bucket_id or not object_id:
        if message.data:
            try:
                decoded_data = base64.b64decode(message.data).decode("utf-8")
                gcs_event = json.loads(decoded_data)
                bucket_id = gcs_event.get("bucket")
                object_id = gcs_event.get("name")
                event_type = "OBJECT_FINALIZE"
            except Exception as e:
                logger.error(f"Failed to decode data payload: {e}")
                
    if not bucket_id or not object_id:
        logger.error(f"GCS event details not found in message. Attributes: {attributes}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Missing GCS event details (bucketId or objectId)"
        )
        
    # GCS Notification event for creation is OBJECT_FINALIZE
    if event_type and event_type != "OBJECT_FINALIZE":
        logger.info(f"Ignoring non-upload event type: {event_type} for file: {object_id}")
        return {"status": "ignored", "reason": f"Event type {event_type} is not OBJECT_FINALIZE"}
        
    logger.info(f"Processing file {object_id} from bucket {bucket_id}")
    
    try:
        # Initialize Google Cloud Storage Client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_id)
        blob = bucket.blob(object_id)
        
        # Check if blob exists
        if not blob.exists():
            logger.error(f"File {object_id} does not exist in bucket {bucket_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {object_id} not found in bucket {bucket_id}"
            )
            
        # Download file content
        file_content = blob.download_as_bytes()
        
        # Run Simulated OCR
        ocr_result = simulate_ocr(file_content, object_id)
        word_count = ocr_result["word_count"]
        tags = ocr_result["tags"]
        
        logger.info(f"Simulated OCR complete. Word count: {word_count}, Tags: {tags}")
        
        # Stream Metadata to BigQuery
        bq_client = bigquery.Client()
        
        # If PROJECT_ID is not set in env, BigQuery client will use default project from credentials
        dataset_ref = bq_client.dataset(DATASET_ID, project=PROJECT_ID)
        table_ref = dataset_ref.table(TABLE_ID)
        
        row_to_insert = {
            "filename": object_id,
            "date": datetime.now(timezone.utc).isoformat(),
            "tags": tags,
            "word_count": word_count
        }
        
        errors = bq_client.insert_rows_json(table_ref, [row_to_insert])
        if errors:
            logger.error(f"Failed to insert row to BigQuery: {errors}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"BigQuery streaming insert failed: {errors}"
            )
            
        logger.info(f"Successfully recorded metadata for {object_id} in BigQuery")
        return {
            "status": "success",
            "file": object_id,
            "word_count": word_count,
            "tags": tags
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@app.get("/healthz")
def health_check():
    return {"status": "healthy"}
