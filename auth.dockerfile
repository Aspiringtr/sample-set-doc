FROM python:3.12-slim

WORKDIR /home_depot_supply

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "auth.auth:app", "--host", "0.0.0.0", "--port", "8001"]