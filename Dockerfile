FROM python
ENV PYTHONUNBUFFERED 1
RUN pip install poetry
WORKDIR /app
COPY . ./
RUN poetry install
EXPOSE 8000
