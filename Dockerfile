FROM python:alpine

COPY . .

RUN pip install -r requirements.txt

CMD ./start.sh

EXPOSE 2001
