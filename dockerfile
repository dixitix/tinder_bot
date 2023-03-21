FROM python:3.8-slim

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8888

CMD ["python", "main.py"]