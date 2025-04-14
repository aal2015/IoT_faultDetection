FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r mysite/requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "python manage.py clear_faults && python manage.py runserver 0.0.0.0:8000"]
