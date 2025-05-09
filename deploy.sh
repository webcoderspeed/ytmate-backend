#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Kill any running uvicorn processes on port 8000
PID=$(lsof -ti:8000)
if [ ! -z "$PID" ]; then
  kill -9 $PID
fi

# Start FastAPI app in the background
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# Reload nginx to apply config changes
sudo nginx -s reload

echo "Deployment complete. FastAPI running in background, Nginx reloaded."