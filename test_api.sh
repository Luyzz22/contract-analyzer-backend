#!/bin/bash
set -e

cd ~/contract-analyzer-backend
source .venv/bin/activate

echo "Stoppe alte Server..."
pkill -9 -f "uvicorn app.main:app" 2>/dev/null || true
sleep 2

echo "Installiere Dependencies..."
pip install -q pydantic-settings python-dotenv

echo "Starte Server..."
uvicorn app.main:app --reload > /tmp/backend.log 2>&1 &
sleep 4

echo "=== 1. Health Check ==="
curl -s http://127.0.0.1:8000/health | python3 -m json.tool

echo ""
echo "=== 2. Upload mit Auth ==="
curl -s -H "X-API-Key: demo-key-123" -F "file=@testvertrag.pdf" http://127.0.0.1:8000/contracts/upload > /tmp/upload.json
cat /tmp/upload.json | python3 -m json.tool
CONTRACT_ID=$(python3 -c "import json; print(json.load(open('/tmp/upload.json'))['contract_id'])")
echo "Contract ID: $CONTRACT_ID"

echo ""
echo "=== 3. Analyse mit Auth ==="
curl -s -H "X-API-Key: demo-key-123" -X POST "http://127.0.0.1:8000/contracts/$CONTRACT_ID/analyze" -H "Content-Type: application/json" -d '{"contract_type": "employment", "language": "de"}' | python3 -m json.tool

echo ""
echo "=== 4. Export JSON ==="
curl -s -H "X-API-Key: demo-key-123" "http://127.0.0.1:8000/contracts/$CONTRACT_ID/export/json" -o analysis_export.json
echo "Exportiert: analysis_export.json"

echo ""
echo "=== 5. Export CSV ==="
curl -s -H "X-API-Key: demo-key-123" "http://127.0.0.1:8000/contracts/$CONTRACT_ID/export/csv" -o analysis_export.csv
echo "Exportiert: analysis_export.csv"
head -n 3 analysis_export.csv

echo ""
echo "=== 6. Feedback ==="
curl -s -H "X-API-Key: demo-key-123" -X POST "http://127.0.0.1:8000/contracts/$CONTRACT_ID/feedback" -H "Content-Type: application/json" -d '{"is_correct": true, "comment": "Gut!"}' | python3 -m json.tool

echo ""
echo "=== 7. Test ohne Key (401) ==="
curl -s http://127.0.0.1:8000/contracts/upload | python3 -m json.tool

echo ""
echo "=== 8. Test falscher Key (403) ==="
curl -s -H "X-API-Key: falsch" http://127.0.0.1:8000/contracts | python3 -m json.tool

echo ""
echo "✅ Alle Tests OK!"
echo "Dashboard: http://127.0.0.1:8000/dashboard"
