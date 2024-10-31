FROM squidfunk/mkdocs-material

COPY ./docs/user-requirements.txt .
RUN pip install -U -r user-requirements.txt

COPY ./docs /docs

CMD ["serve", "--dev-addr=0.0.0.0:8002"]
