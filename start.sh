#!/bin/bash

cd src

(
    cd backend
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
) &

# 2. Ejecutar Frontend (Ruta: src/frontend)
(
    cd frontend
    python3 -m http.server 3000
) &

wait
