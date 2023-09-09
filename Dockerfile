FROM node:16-slim as build
WORKDIR /app
COPY . ./
RUN npm install --prefix client
RUN npm run build --prefix client

FROM python:3.11-slim
ENV PYTHONUNBUFFERED True
WORKDIR /app
COPY --from=build /app/ ./
RUN pip install --no-cache-dir -r requirements.txt
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app