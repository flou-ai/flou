FROM python:3.11

WORKDIR /code

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

COPY ./flou/requirements.txt /code/requirements.txt
COPY ./flou/pyproject.toml /code/pyproject.toml
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./flou /code/flou

WORKDIR /code/flou

RUN pip install -e .

ENV ENV=docker

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

WORKDIR /code/app

CMD ["uvicorn", "flou.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--timeout-graceful-shutdown=0"]