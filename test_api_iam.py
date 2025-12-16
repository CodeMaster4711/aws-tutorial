#!/usr/bin/env python3
"""
Test-Script für API Gateway mit AWS_IAM Autorisierung.
Benötigt AWS Credentials und signiert die Requests.
"""

import json
import boto3
import os
from datetime import datetime
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests

# Load .env - muss VOR os.getenv() sein!
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env Datei geladen")
except ImportError:
    print("⚠️  python-dotenv nicht installiert, verwende OS Umgebungsvariablen")

def make_signed_request(url, method='POST', data=None):
    """
    Erstellt einen AWS Signature V4 signierten Request.
    """
    # AWS Session und Credentials
    session = boto3.Session()
    credentials = session.get_credentials()

    # Region aus URL extrahieren
    region = url.split('.')[2]  # eu-north-1 aus URL

    # Request vorbereiten
    headers = {
        'Content-Type': 'application/json'
    }

    # AWS Request erstellen
    request = AWSRequest(
        method=method,
        url=url,
        data=json.dumps(data) if data else None,
        headers=headers
    )

    # Request signieren
    SigV4Auth(credentials, 'execute-api', region).add_auth(request)

    # Signed Request ausführen
    return requests.request(
        method=request.method,
        url=request.url,
        headers=dict(request.headers),
        data=request.body
    )


def main():
    print("\n" + "="*60)
    print("  AWS API Gateway Test (mit IAM Autorisierung)")
    print("="*60 + "\n")

    # API URL aus .env
    api_url = os.getenv('API_GATEWAY_URL')

    # Debug: Zeige was geladen wurde
    print(f"🔍 Debug: API_GATEWAY_URL = {api_url}")
    print(f"🔍 Debug: S3_BUCKET_NAME = {os.getenv('S3_BUCKET_NAME')}")
    print(f"🔍 Debug: AWS_REGION = {os.getenv('AWS_REGION')}")
    print()

    if not api_url or 'xxxxxxxxxx' in api_url:
        print("❌ Bitte setze API_GATEWAY_URL in .env Datei!")
        print("💡 Aktueller Wert:", api_url)
        return

    print(f"📋 API URL: {api_url}\n")

    # Test-Daten
    test_data = {
        "event": "iam_test",
        "timestamp": datetime.now().isoformat(),
        "message": "Test mit AWS IAM Signatur",
        "source": "test_api_iam.py"
    }

    print("📤 Sende signierten Request...")
    print(json.dumps(test_data, indent=2))
    print()

    try:
        response = make_signed_request(api_url, method='POST', data=test_data)

        print("📥 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Body: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✅ Test erfolgreich!")
        else:
            print(f"\n⚠️  API returned Status {response.status_code}")

    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
