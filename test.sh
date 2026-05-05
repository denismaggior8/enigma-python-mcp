#!/bin/bash
curl -sN http://localhost:8000/sse > sse.log &
SSE_PID=$!
sleep 1
SESSION_ID=$(grep -o "session_id=[^&]*" sse.log | cut -d'=' -f2 | head -n 1)
curl -s -X POST "http://localhost:8000/messages/?session_id=$SESSION_ID" -H "Content-Type: application/json" -d @example_payload.json
sleep 2
kill $SSE_PID
cat sse.log
