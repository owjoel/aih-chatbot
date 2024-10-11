FROM python:3.10.12-alpine

WORKDIR /usr/src/app

COPY . .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "app.py"]