FROM python:3.8-slim
RUN apt-get update && apt-get install -y libpq-dev build-essential
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
RUN chmod +x app/script.sh
