FROM python:3.12

EXPOSE 8000/tcp

COPY hda-requirements.txt ./
RUN pip install --upgrade --no-cache-dir pip setuptools wheel
RUN pip install --no-cache-dir -r hda-requirements.txt

COPY . .

WORKDIR "/src"

CMD [ "uvicorn", "work_orchestration.main:app", "--host", "0.0.0.0", "--port", "8000"]
