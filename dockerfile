FROM python:3.9-slim-buster

WORKDIR /storm-docker

COPY api /storm-docker
COPY requirements.txt requirements.txt
COPY secrets.toml secrets.toml
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]