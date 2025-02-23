#!/bin/bash

set -e

cd backend
# check if venv exists
if [ ! -d "venv" ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  echo "venv created and requirements installed"
else
  source venv/bin/activate
fi

uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
echo "FastAPI started"

cd ../frontend
# check if node_modules exists
if [ ! -d "node_modules" ]; then
  npm install
  echo "npm install success"
fi

npm run dev
echo "Next.js started"
