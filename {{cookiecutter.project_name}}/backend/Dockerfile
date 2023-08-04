FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
LABEL authors="lpdswing"

WORKDIR /app/

# Install Poetry
RUN pip install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"


COPY ./ /app
ENV PYTHONPATH=/app
