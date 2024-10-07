FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install flask pandas scikit-learn joblib

EXPOSE 5001

CMD ["python", "main.py"]