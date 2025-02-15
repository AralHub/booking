# --------- requirements ---------

FROM python:3.12 as requirements-stage

WORKDIR /tmp

RUN pip install "poetry==1.8.4"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


# --------- final image build ---------
FROM python:3.12

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install black  

COPY ./src/app /code/app

#copy migrations
COPY ./src/migrations /code/migrations  
COPY ./src/alembic.ini /code/alembic.ini 
# Добавляем /code в PYTHONPATH
ENV PYTHONPATH=/code
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]

CMD python app/run.py
