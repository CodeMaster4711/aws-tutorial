#!/usr/bin/env python3
"""
Test-Script für die Lambda-Funktion.

Dieses Script simuliert einen API Gateway Request und testet die Lambda-Funktion lokal.
Du kannst es auch verwenden, um die Live-API zu testen.
"""

import json
import sys
import os
import requests
from datetime import datetime

# Lade .env Datei falls vorhanden
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv nicht installiert, verwende OS Umgebungsvariablen


def test_local():
    """Teste die Lambda-Funktion lokal (ohne AWS)"""
    print("🧪 Lokaler Test der Lambda-Funktion\n")
    print("Hinweis: Für echtes S3-Upload benötigst du AWS-Credentials!")
    print("-" * 60)

    # Import der Lambda-Funktion
    try:
        from lambda_function import lambda_handler
    except ImportError:
        print("❌ Fehler: lambda_function.py nicht gefunden!")
        sys.exit(1)

    # Simuliere ein API Gateway Event
    test_event = {
        "body": json.dumps({
            "event": "page_view",
            "page": "/home",
            "user_id": "test-user-123",
            "session_id": "session-xyz"
        }),
        "requestContext": {
            "identity": {
                "sourceIp": "203.0.113.42",
                "userAgent": "Python Test Script/1.0"
            }
        }
    }

    # Dummy Context
    class Context:
        function_name = "TrafficLoggingFunction"
        request_id = "test-request-id"

    print("\n📤 Sende Test-Event:")
    print(json.dumps(json.loads(test_event["body"]), indent=2))
    print()

    try:
        # Lambda-Funktion aufrufen
        response = lambda_handler(test_event, Context())

        print("\n📥 Response:")
        print(f"Status Code: {response['statusCode']}")
        print(f"Body: {json.dumps(json.loads(response['body']), indent=2)}")

        if response['statusCode'] == 200:
            print("\n✅ Test erfolgreich!")
        else:
            print("\n⚠️  Test abgeschlossen mit Fehler")

    except Exception as e:
        print(f"\n❌ Fehler beim Test: {str(e)}")
        import traceback
        traceback.print_exc()


def test_api(api_url):
    """Teste die Live-API auf AWS"""
    print(f"🌐 Teste Live-API: {api_url}\n")
    print("-" * 60)

    # Test-Daten
    test_data = {
        "event": "api_test",
        "timestamp_local": datetime.now().isoformat(),
        "message": "Test von Python Script",
        "user_id": "test-12345",
        "metadata": {
            "source": "test_script",
            "version": "1.0"
        }
    }

    print("\n📤 Sende Request:")
    print(json.dumps(test_data, indent=2))
    print()

    try:
        # POST Request an API
        response = requests.post(
            api_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"\n📥 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✅ API Test erfolgreich!")
            result = response.json()
            if 's3_location' in result:
                print(f"📁 Daten gespeichert in: {result['s3_location']}")
        else:
            print(f"\n⚠️  API returned Status {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Netzwerk-Fehler: {str(e)}")
    except json.JSONDecodeError:
        print(f"\n❌ Ungültige JSON Response: {response.text}")
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")


def main():
    """Hauptfunktion"""
    print("\n" + "="*60)
    print("  AWS Lambda + API Gateway Test Script")
    print("="*60 + "\n")

    if len(sys.argv) > 1:
        # API URL wurde übergeben - teste Live-API
        api_url = sys.argv[1]
        test_api(api_url)
    else:
        # Prüfe ob .env existiert und API_GATEWAY_URL gesetzt ist
        api_url_from_env = os.getenv('API_GATEWAY_URL')

        if api_url_from_env:
            print(f"📋 API URL aus .env gefunden: {api_url_from_env}\n")
            choice = input("Möchtest du (1) Live API oder (2) Lokal testen? (1/2): ")
            if choice == "1":
                test_api(api_url_from_env)
            elif choice == "2":
                test_local()
            else:
                print("\nAbgebrochen.")
        else:
            # Kein Argument - teste lokal
            print("Verwendung:")
            print("  Lokal testen:     python test_lambda.py")
            print("  Live API testen:  python test_lambda.py https://your-api-url/prod/log")
            print("  Oder setze API_GATEWAY_URL in .env Datei")
            print()

            user_input = input("Möchtest du die Lambda-Funktion lokal testen? (j/n): ")
            if user_input.lower() in ['j', 'ja', 'y', 'yes']:
                test_local()
            else:
                print("\nAbgebrochen.")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
