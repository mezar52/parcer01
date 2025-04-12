FROM python:3.11-slim

WORKDIR /app


COPY ../../AppData/Local/Temp .

CMD ["python", "run_all.py"]
