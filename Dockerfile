FROM python:latest
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]

