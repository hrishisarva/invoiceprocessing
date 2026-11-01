FROM --platform=linux/amd64 python:3.12-slim
WORKDIR /app
COPY app.py seed.json ./
ENV PORT=10000 PYTHONUNBUFFERED=1
EXPOSE 10000
CMD ["python", "app.py"]
