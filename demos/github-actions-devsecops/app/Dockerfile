# Multi-stage is unnecessary for a stdlib-only app; one slim stage keeps the
# image small and the attack surface low.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY inventory_api.py .
RUN useradd --uid 10001 --no-create-home appuser
USER 10001
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz')"
CMD ["python", "inventory_api.py"]
