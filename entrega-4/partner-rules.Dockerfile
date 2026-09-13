FROM python:3.12-slim

WORKDIR /app

COPY hda-requirements.txt .
RUN pip install --upgrade --no-cache-dir pip setuptools wheel \
    && pip install --no-cache-dir -r hda-requirements.txt

COPY src/seedwork ./seedwork
COPY src/published_language ./published_language
COPY src/partner_rules ./partner_rules

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "partner_rules.main:app", "--host", "0.0.0.0", "--port", "8000"]
