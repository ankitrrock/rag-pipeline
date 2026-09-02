@echo off
title RAG Pipeline Health Check

cd /d "%~dp0"

echo.
echo ============================================================
echo                 RAG PIPELINE HEALTH CHECK
echo ============================================================
echo.

REM ============================================================
REM 1. PostgreSQL
REM ============================================================

echo [1/6] PostgreSQL
echo ------------------------------------------------------------

sc query postgresql-x64-18 | findstr /I "RUNNING" >nul

if %errorlevel% equ 0 (
    echo [OK] PostgreSQL service is RUNNING
) else (
    echo [FAIL] PostgreSQL service is NOT running
)

echo.


REM ============================================================
REM 2. Redis
REM ============================================================

echo [2/6] Redis
echo ------------------------------------------------------------

docker ps --filter "name=redis" --filter "status=running" | findstr /I "redis" >nul

if %errorlevel% equ 0 (
    echo [OK] Redis Docker container is RUNNING
) else (
    echo [FAIL] Redis Docker container is NOT running
)

docker exec redis redis-cli ping 2>nul | findstr /I "PONG" >nul

if %errorlevel% equ 0 (
    echo [OK] Redis connection: PONG
) else (
    echo [FAIL] Redis connection failed
)

echo.


REM ============================================================
REM 3. Celery Worker
REM ============================================================

echo [3/6] Celery Worker
echo ------------------------------------------------------------

tasklist | findstr /I "python.exe" >nul

if %errorlevel% equ 0 (
    echo [OK] Python process detected
) else (
    echo [FAIL] Python process not detected
)

echo.
echo Checking Celery configuration...

"%~dp0env\Scripts\python.exe" -c "from app.worker.celery_app import celery_app; print('[OK] Celery application loaded'); print('Broker:', celery_app.conf.broker_url); print('Registered tasks:'); [print('  -', t) for t in celery_app.tasks if not t.startswith('celery.')]"

echo.


REM ============================================================
REM 4. FastAPI
REM ============================================================

echo [4/6] FastAPI
echo ------------------------------------------------------------

curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://127.0.0.1:8000/docs

curl -s http://127.0.0.1:8000/openapi.json | findstr /I "openapi" >nul

if %errorlevel% equ 0 (
    echo [OK] FastAPI is responding
) else (
    echo [FAIL] FastAPI is NOT responding
)

echo.


REM ============================================================
REM 5. FAISS
REM ============================================================

echo [5/6] FAISS Vector Store
echo ------------------------------------------------------------

"%~dp0env\Scripts\python.exe" -c "from app.embeddings.vector_store import vector_store; vector_store.load(); print('[OK] FAISS index loaded'); print('Vectors:', vector_store.index.ntotal); print('Chunk IDs:', vector_store.chunk_ids)"

echo.


REM ============================================================
REM 6. Database / Document API
REM ============================================================

echo [6/6] Document API
echo ------------------------------------------------------------

curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://127.0.0.1:8000/api/v1/documents

echo.


REM ============================================================
REM SUMMARY
REM ============================================================

echo ============================================================
echo                    HEALTH CHECK COMPLETE
echo ============================================================
echo.
echo PostgreSQL : Check above
echo Redis      : Check above
echo Celery     : Check above
echo FastAPI    : Check above
echo FAISS      : Check above
echo Documents  : Check above
echo.
echo Swagger:
echo http://127.0.0.1:8000/docs
echo.
echo ============================================================

pause