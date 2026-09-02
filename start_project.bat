@echo off
title RAG Pipeline Startup

cd /d D:\Project\Rag_Project\rag-pipeline

echo ==========================================
echo       RAG PIPELINE STARTING
echo ==========================================
echo.

REM ==========================================
REM PostgreSQL
REM ==========================================

echo [1/4] Checking PostgreSQL...

sc query postgresql-x64-18 | findstr "RUNNING" >nul

if %errorlevel% equ 0 (
    echo PostgreSQL is already running.
) else (
    net start postgresql-x64-18
)

echo.

REM ==========================================
REM Redis
REM ==========================================

echo [2/4] Checking Redis...

docker ps --filter "name=redis" --filter "status=running" | findstr "redis" >nul

if %errorlevel% equ 0 (
    echo Redis is already running.
) else (
    docker start redis
)

echo.

REM ==========================================
REM Celery
REM ==========================================

echo [3/4] Starting Celery Worker...

start "Celery Worker" cmd /k "D:\Project\Rag_Project\env\Scripts\python.exe -m celery -A app.worker.celery_app.celery_app worker --loglevel=info --pool=solo"

timeout /t 5 /nobreak >nul

REM ==========================================
REM FastAPI
REM ==========================================

echo [4/4] Starting FastAPI...

start "FastAPI Server" cmd /k "D:\Project\Rag_Project\env\Scripts\python.exe -m uvicorn app.main:app --reload"

echo.
echo ==========================================
echo       RAG PIPELINE STARTED
echo ==========================================
echo.
echo FastAPI: http://127.0.0.1:8000
echo Swagger: http://127.0.0.1:8000/docs
echo Redis:   localhost:6379
echo PostgreSQL: localhost:5432
echo.
echo ==========================================