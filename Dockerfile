FROM python:3.10
COPY ./requirements.txt /app/
RUN apt-get update && apt upgrade -y

WORKDIR /app/

RUN pip install -r requirements.txt

CMD python main.py