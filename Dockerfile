FROM python:3.13-slim

WORKDIR /app

COPY main.py /app/main.py
COPY img /app/img
COPY data /app/data

ENV HOST=0.0.0.0
ENV PORT=10000

EXPOSE 10000

CMD ["python3", "main.py"]
