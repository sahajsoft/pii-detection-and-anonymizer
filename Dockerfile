FROM python:3.11

WORKDIR /usr/src/app
RUN pip install poetry==1.8.3
ENV POETRY_NO_INTERACTION=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache
COPY poetry.toml .
COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install && rm -rf $POETRY_CACHE_DIR
COPY pii_detection_and_anonymizer pii_detection_and_anonymizer

ENTRYPOINT [ "poetry", "run", "python", "-m", "pii_detection_and_anonymizer" ]
