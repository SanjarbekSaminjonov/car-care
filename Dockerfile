FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

ARG REQUIREMENTS_FILE=production.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements ./requirements
RUN pip install --no-cache-dir -r requirements/${REQUIREMENTS_FILE}

COPY . .

RUN DJANGO_SECRET_KEY=build-time-secret \
    POSTGRES_DB=car_care \
    POSTGRES_USER=car_care \
    POSTGRES_PASSWORD=car_care \
    POSTGRES_HOST=localhost \
    python src/manage.py collectstatic --noinput

RUN addgroup --system app && adduser --system --ingroup app app \
    && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--chdir", "src", "--bind", "0.0.0.0:8000"]
