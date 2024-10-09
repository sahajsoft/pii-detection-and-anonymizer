FROM python:3.11

WORKDIR /usr/src/app
RUN pip install poetry==1.8.3
RUN apt-get update && apt-get install -y tesseract-ocr
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_VIRTUALENVS_CREATE=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache
COPY poetry.toml .
COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR
RUN poetry run python -m spacy download en_core_web_sm
COPY src src
COPY tests tests

ENTRYPOINT [ "poetry", "run", "python", "src/cli.py" ]
