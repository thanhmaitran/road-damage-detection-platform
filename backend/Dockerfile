FROM python:3.11-slim
WORKDIR /repo/backend
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" python-multipart sqlalchemy pillow "psycopg[binary]"
COPY backend/app app
COPY ml /repo/ml
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
