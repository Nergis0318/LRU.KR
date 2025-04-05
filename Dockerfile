FROM python:alpine

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 2001

CMD ["./start.sh"]
