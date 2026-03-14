FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir uploads audio images jobs outputs

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]