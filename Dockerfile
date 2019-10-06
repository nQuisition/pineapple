FROM python:3.5

ADD  . /pineapple-bot

WORKDIR /pineapple-bot

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]