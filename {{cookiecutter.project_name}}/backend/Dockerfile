FROM python:3.11
LABEL maintainer="lpdswing"

RUN pip install uvicorn[standard] gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

WORKDIR /app

# Install Poetry
RUN pip install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple && \
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