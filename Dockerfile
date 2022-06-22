FROM python:3.10.2-slim-buster
RUN pip install -U python-dotenv

RUN mkdir /app
WORKDIR /app/
RUN apt-get install -y tzdata

RUN apt-get update && apt-get install -y wget
RUN apt-get install -y build-essential \
    libpq-dev
RUN rm -rf /var/lib/apt/lists/*

ENV DOCKERIZE_VERSION v0.6.1
ENV TZ America/Sao_Paulo

RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#CMD ["bash"]