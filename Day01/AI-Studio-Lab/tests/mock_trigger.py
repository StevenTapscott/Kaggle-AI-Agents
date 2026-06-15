import argparse
import json
import urllib.request
import base64
from datetime import datetime, timezone

def send_mock_payload(url: str, bucket: str, filename: str):
    # Construct the mock GCS notification payload
    payload = {
        "message": {
            "attributes": {
                "bucketId": bucket,
                "objectId": filename,
                "eventType": "OBJECT_FINALIZE"
            },
            "data": base64.b64encode(json.dumps({"bucket": bucket, "name": filename}).encode("utf-8")).decode("utf-8"),
            "messageId": "mock-message-id-12345",
            "publishTime": datetime.now(timezone.utc).isoformat()
        },
        "subscription": "projects/mock-project/subscriptions/mock-subscription"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    print(f"Sending mock Pub/Sub GCS upload notification to {url}...")
    print(f"Bucket: {bucket}")
    print(f"File: {filename}")
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            print(f"\nResponse Code: {response.status}")
            print(f"Response Body:\n{res_body}")
    except urllib.error.HTTPError as e:
        print(f"\nHTTP Error: {e.code}")
        print(f"Response Body:\n{e.read().decode('utf-8')}")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send mock Pub/Sub GCS trigger payload to local webhook")
    parser.add_argument("--url", default="http://localhost:8080/webhook", help="Webhook URL to target")
    parser.add_argument("--bucket", default="my-test-bucket", help="GCS Bucket name to mock")
    parser.add_argument("--file", default="sample.txt", help="File name/path in bucket to mock")
    
    args = parser.parse_args()
    send_mock_payload(args.url, args.bucket, args.file)
