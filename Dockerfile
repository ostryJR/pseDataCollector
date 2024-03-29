# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

ADD pseDataCollector.py

RUN pip install requests mysql

CMD ['python3', './pseDataCollector.py']