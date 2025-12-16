# AWS Lambda + API Gateway + S3 Tutorial

Ein minimalistisches Tutorial für ein Logging-System mit AWS.

## Was wird gebaut?

```
HTTP POST Request → API Gateway → Lambda Function → S3 Bucket
                                        ↓
                              (fügt UUID + Timestamp hinzu)
```

## Dateien im Projekt

- `lambda_function.py` - Die Lambda-Funktion (Python Code)
- `example_request.json` - Beispiel-Daten zum Testen
- `test_lambda.py` - Test-Script
- `requirements.txt` - Python Abhängigkeiten

## Setup - Schritt für Schritt

### 1. S3 Bucket erstellen

1. Öffne [S3 Console](https://console.aws.amazon.com/s3/)
2. Klicke "Bucket erstellen"
3. Name: `mein-logging-bucket-2024` (muss weltweit eindeutig sein!)
4. Region: `eu-central-1` (Frankfurt)
5. Klicke "Bucket erstellen"

### 2. IAM Rolle erstellen

1. Öffne [IAM Console](https://console.aws.amazon.com/iam/)
2. "Rollen" → "Rolle erstellen"
3. Wähle "AWS-Service" → "Lambda"
4. Füge Policies hinzu:
   - `AWSLambdaBasicExecutionRole`
5. Klicke "Weiter" → Name: `lambda-s3-role`
6. Rolle erstellen

**Custom Policy für S3 hinzufügen:**
1. Öffne die erstellte Rolle
2. "Berechtigungen hinzufügen" → "Inline-Richtlinie erstellen"
3. JSON:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::mein-logging-bucket-2024/*"
        }
    ]
}
```
4. Name: `S3Access` → Erstellen

### 3. Lambda-Funktion erstellen

1. Öffne [Lambda Console](https://console.aws.amazon.com/lambda/)
2. "Funktion erstellen"
3. Name: `TrafficLoggingFunction`
4. Runtime: `Python 3.12`
5. Rolle: "Vorhandene Rolle verwenden" → `lambda-s3-role`
6. Funktion erstellen

**Code hochladen:**
1. Kopiere den Code aus `lambda_function.py`
2. Füge ihn im Lambda Code-Editor ein
3. Klicke "Deploy"

**Umgebungsvariable setzen:**
1. Tab "Konfiguration" → "Umgebungsvariablen"
2. Bearbeiten → Hinzufügen:
   - Key: `S3_BUCKET_NAME`
   - Value: `mein-logging-bucket-2024`
3. Speichern

### 4. API Gateway erstellen

1. Öffne [API Gateway Console](https://console.aws.amazon.com/apigateway/)
2. "API erstellen" → **REST API** → "Erstellen"
3. Name: `LoggingAPI`

**Route erstellen:**
1. "Aktionen" → "Ressource erstellen"
   - Ressourcenname: `log`
2. Ressource `/log` wählen → "Aktionen" → "Methode erstellen"
3. Wähle `POST`
4. Integration:
   - Typ: Lambda-Funktion
   - Funktion: `TrafficLoggingFunction`
   - **Proxy-Integration**: ✓ (wichtig!)
5. Speichern

**API bereitstellen:**
1. "Aktionen" → "API bereitstellen"
2. Stage: "Neue Stage" → Name: `prod`
3. Bereitstellen

**API URL kopieren:**
```
https://XXXXXXXXXX.execute-api.eu-central-1.amazonaws.com/prod/log
```

## Testen

### Mit curl:
```bash
curl -X POST https://DEINE-API-URL/prod/log \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "message": "Hello AWS"}'
```

### Mit Python:
```bash
python test_lambda.py https://DEINE-API-URL/prod/log
```

## Ergebnis in S3

Nach erfolgreichem Request findest du in deinem S3 Bucket:

```
logs/
└── 2024/
    └── 12/
        └── 16/
            └── 10/
                └── abc-123-xyz.json
```

JSON-Datei Inhalt:
```json
{
  "id": "abc-123-xyz",
  "timestamp": "2024-12-16T10:30:45.123456Z",
  "source_ip": "203.0.113.42",
  "user_agent": "curl/7.68.0",
  "data": {
    "event": "test",
    "message": "Hello AWS"
  }
}
```

## Python Virtual Environment

### Erstellen:
```bash
python -m venv venv
```

### Aktivieren:

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Dependencies installieren:
```bash
pip install boto3 requests
```

### Deaktivieren:
```bash
deactivate
```

## Kosten

Mit AWS Free Tier: **Praktisch kostenlos** für Lernzwecke!
- API Gateway: 1M Requests/Monat gratis
- Lambda: 1M Requests/Monat gratis
- S3: 5 GB Speicher gratis

## Löschen (Cleanup)

1. Lambda-Funktion löschen
2. API Gateway löschen
3. S3 Bucket leeren und löschen
4. IAM Rolle löschen

## Troubleshooting

**Fehler "Access Denied":**
→ Prüfe IAM Rolle und S3 Bucket-Name in Lambda Umgebungsvariablen

**Fehler 502:**
→ Schaue in CloudWatch Logs der Lambda-Funktion

**Lambda Logs ansehen:**
1. Lambda Console → deine Funktion → Tab "Überwachen"
2. "CloudWatch-Logs anzeigen"
