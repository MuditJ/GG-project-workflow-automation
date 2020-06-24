FROM python:3.7-slim-buster
COPY . /src
WORKDIR /src
RUN pip install -r requirements.txt 
RUN chmod +x startup.sh
ENTRYPOINT /src/startup.sh