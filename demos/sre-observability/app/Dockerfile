FROM python:3.12-slim
WORKDIR /app
COPY orders_service.py .
# Run as an unprivileged user.
RUN useradd --uid 10001 --no-create-home appuser
USER 10001
EXPOSE 8081
HEALTHCHECK --interval=15s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/healthz')"
CMD ["python", "orders_service.py"]
