#    Copyright 2023 Atick Faisal

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# --------------- Setup Client -----------------
FROM node:21-slim as build
WORKDIR /app
COPY . ./
RUN npm install --prefix client
RUN npm run build --prefix client
# ----------------------------------------------

# ----------- Setup Flask Backend --------------
FROM python:3.12-slim
ENV PYTHONUNBUFFERED True
WORKDIR /app
COPY --from=build /app/ ./
RUN pip install --no-cache-dir -r requirements.txt
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
# -----------------------------------------------