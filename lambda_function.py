import json
import boto3
import uuid
from datetime import datetime

# S3 Client initialisieren
s3_client = boto3.client('s3')

# S3 Bucket Name (wird als Umgebungsvariable gesetzt)
import os
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'your-bucket-name')


def lambda_handler(event, context):
    """
    Lambda Handler Funktion für API Gateway POST Requests.

    Args:
        event: API Gateway Event mit HTTP Request Daten
        context: Lambda Context Objekt

    Returns:
        HTTP Response mit Status Code und Body
    """

    try:
        # 1. Request Body parsen
        if 'body' in event:
            # Body kann als String kommen (von API Gateway)
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Kein Request Body vorhanden'
                })
            }

        # 2. Metadaten hinzufügen
        log_entry = {
            'id': str(uuid.uuid4()),  # Eindeutige UUID
            'timestamp': datetime.utcnow().isoformat() + 'Z',  # ISO 8601 Format
            'data': body  # Original Request Daten
        }

        # Optional: IP-Adresse und User-Agent hinzufügen
        if 'requestContext' in event:
            request_context = event['requestContext']
            if 'identity' in request_context:
                identity = request_context['identity']
                log_entry['source_ip'] = identity.get('sourceIp', 'unknown')
                log_entry['user_agent'] = identity.get('userAgent', 'unknown')

        # 3. Dateiname generieren (Timestamp-basiert für Organisation)
        timestamp_str = datetime.utcnow().strftime('%Y/%m/%d/%H')
        filename = f"logs/{timestamp_str}/{log_entry['id']}.json"

        # 4. In S3 speichern
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=json.dumps(log_entry, indent=2),
            ContentType='application/json'
        )

        # 5. Erfolgreiche Response zurückgeben
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # CORS aktivieren
            },
            'body': json.dumps({
                'message': 'Daten erfolgreich gespeichert',
                'log_id': log_entry['id'],
                's3_location': f"s3://{BUCKET_NAME}/{filename}"
            })
        }

    except json.JSONDecodeError as e:
        # Fehler beim JSON Parsing
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Ungültiges JSON Format',
                'details': str(e)
            })
        }

    except Exception as e:
        # Allgemeine Fehlerbehandlung
        print(f"Fehler: {str(e)}")  # CloudWatch Logs
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Interner Server Fehler',
                'details': str(e)
            })
        }
