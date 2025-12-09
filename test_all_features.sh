#!/bin/bash
set -e

echo "=== Contract Analyzer v0.3.0 - Vollständiger Test ==="
echo ""

echo "1. Health Check (öffentlich)"
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
echo ""

echo "2. Upload MIT API-Key"
UPLOAD_RESULT=$(curl -s -H "X-API-Key: demo-key-123" -F "file=@testvertrag.pdf" http://127.0.0.1:8000/contracts/upload)
echo "$UPLOAD_RESULT" | python3 -m json.tool
CONTRACT_ID=$(echo "$UPLOAD_RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['contract_id'])")
echo "Contract ID: $CONTRACT_ID"
echo ""

echo "3. Analyse Employment"
curl -s -H "X-API-Key: demo-key-123" -X POST "http://127.0.0.1:8000/contracts/$CONTRACT_ID/analyze" -H "Content-Type: application/json" -d '{"contract_type": "employment", "language": "de"}' | python3 -m json.tool | head -n 50
echo ""

echo "4. Export JSON"
curl -s -H "X-API-Key: demo-key-123" "http://127.0.0.1:8000/contracts/$CONTRACT_ID/export/json" -o test_export.json
echo "✓ Exportiert nach test_export.json"
head -c 200 test_export.json
echo ""

echo "5. Export CSV"
curl -s -H "X-API-Key: demo-key-123" "http://127.0.0.1:8000/contracts/$CONTRACT_ID/export/csv" -o test_export.csv
echo "✓ Exportiert nach test_export.csv"
head -n 3 test_export.csv
echo ""

echo "6. Feedback geben"
curl -s -H "X-API-Key: demo-key-123" -X POST "http://127.0.0.1:8000/contracts/$CONTRACT_ID/feedback" -H "Content-Type: application/json" -d '{"is_correct": true, "comment": "Perfekt!"}' | python3 -m json.tool
echo ""

echo "7. Test OHNE API-Key (sollte 401 geben)"
curl -s http://127.0.0.1:8000/contracts | python3 -m json.tool
echo ""

echo "8. Test FALSCHER API-Key (sollte 403 geben)"
curl -s -H "X-API-Key: invalid" http://127.0.0.1:8000/contracts | python3 -m json.tool
echo ""

echo "✅ Alle Tests abgeschlossen!"
echo ""
echo "📊 Dashboard: http://127.0.0.1:8000/dashboard"
echo "📖 Swagger:   http://127.0.0.1:8000/docs"
