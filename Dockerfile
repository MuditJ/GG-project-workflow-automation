FROM python:3.7-buster
COPY . /src
WORKDIR /src
RUN pip install -r requirements.txt 
RUN chmod +x startup.sh
CMD ["sh"]