FROM python:alpine

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 2001

ENTRYPOINT ["python3", "-m", "hypercorn", "main:app", "--bind", "0.0.0.0:2001", "-w", "10"]
