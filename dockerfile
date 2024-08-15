FROM --platform=linux/amd64 python:3.9-slim-buster

WORKDIR /storm-docker

COPY api /storm-docker
COPY requirements.txt requirements.txt
COPY secrets.toml secrets.toml
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5001", "-w", "2"]