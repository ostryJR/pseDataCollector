# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

ADD pseDataCollector.py .
ADD dbconnect.py .

RUN pip install requests
RUN pip install mysql.connector

CMD ["python3", "-u", "./pseDataCollector.py"]