FROM python:3.11
LABEL maintainer="lpdswing"
ARG INDEX_URL=https://pypi.org/simple
RUN pip install uvicorn[standard] gunicorn -i $INDEX_URL

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY ./worker-start.sh /worker-start.sh
RUN chmod +x /worker-start.sh

WORKDIR /app

# Install Poetry
RUN pip install poetry -i $INDEX_URL && \
    poetry config virtualenvs.create false
# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/
# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY ./ /app/


ENV PYTHONPATH=/app

EXPOSE 80

CMD ["/start.sh"]
