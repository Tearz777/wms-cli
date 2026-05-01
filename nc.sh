#!/bin/bash

echo "🗒️  Starting NotaCore ERP..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start backend
echo "⚡ Starting backend..."
cd "$SCRIPT_DIR/erp/backend"
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

# Start frontend
echo "🎨 Starting frontend..."
cd "$SCRIPT_DIR/erp/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ NotaCore is running!"
echo "   Backend  → http://localhost:8000"
echo "   Frontend → http://localhost:5173"
echo "   API Docs → http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID; echo 'NotaCore stopped.'" SIGINT
wait
