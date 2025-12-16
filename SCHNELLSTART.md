# Schnellstart Guide

## 1. Python Virtual Environment einrichten

### Erstelle ein neues venv:
```bash
python -m venv venv
```

### Aktiviere das venv:

**Auf macOS/Linux:**
```bash
source venv/bin/activate
```

**Auf Windows:**
```bash
venv\Scripts\activate
```

Du siehst dann `(venv)` vor deinem Terminal-Prompt.

### Installiere Dependencies:
```bash
pip install -r requirements.txt
```

## 2. .env Datei erstellen (für lokales Testen)

### Kopiere die Vorlage:
```bash
cp .env.example .env
```

### Bearbeite .env und fülle aus:
```bash
# S3 Bucket Name (nach Schritt 1 von AWS Setup)
S3_BUCKET_NAME=mein-logging-bucket-2024

# AWS Region
AWS_REGION=eu-central-1

# API Gateway URL (nach Schritt 4 von AWS Setup)
API_GATEWAY_URL=https://xxxxxxxxxx.execute-api.eu-central-1.amazonaws.com/prod/log
```

**Wichtig:** Die `.env` Datei ist in `.gitignore` und wird NICHT commited!

## 3. Teste lokal:
```bash
python test_lambda.py
```

## 4. Deaktiviere venv (wenn fertig):
```bash
deactivate
```

## AWS Setup (Die 4 Schritte)

### 1. S3 Bucket
- Gehe zu: https://console.aws.amazon.com/s3/
- Erstelle Bucket mit eindeutigem Namen (z.B. `logging-bucket-12345`)

### 2. IAM Rolle
- Gehe zu: https://console.aws.amazon.com/iam/
- Erstelle Rolle für Lambda mit S3-Zugriff (siehe README.md)

### 3. Lambda-Funktion
- Gehe zu: https://console.aws.amazon.com/lambda/
- Erstelle Funktion, kopiere Code aus `lambda_function.py`
- Setze Umgebungsvariable: `S3_BUCKET_NAME`

### 4. API Gateway
- Gehe zu: https://console.aws.amazon.com/apigateway/
- Erstelle REST API mit POST /log Route
- Verbinde mit Lambda (Proxy-Integration!)
- Deploye zu Stage "prod"

## Testen

```bash
curl -X POST https://DEINE-API-URL/prod/log \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "message": "Hello"}'
```

Oder mit Python:
```bash
python test_lambda.py https://DEINE-API-URL/prod/log
```

## Fertig!

Prüfe S3 Bucket → logs/ Ordner für gespeicherte Daten.
