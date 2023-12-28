FROM python

WORKDIR /usr/src/tg-bot

COPY ./app /usr/src/tg-bot
COPY ./requirements.txt /usr/src/tg-bot

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3", "./main.py"]