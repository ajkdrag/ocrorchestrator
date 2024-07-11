FROM python:3.9

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

# install PDM
RUN pip install -U pip setuptools wheel

RUN useradd -u 999 --user-group --create-home --no-log-init --shell /bin/bash app 
ENV PATH=/home/app/.local/bin:$PATH

USER app

RUN pip install pdm==2.13.0

RUN mkdir /home/app/project
WORKDIR /home/app/project
COPY --chown=app pyproject.toml pdm.lock README.md ./

# install project files
RUN pdm install --frozen-lockfile --no-self

COPY --chown=app src/ ./src
RUN pdm sync

COPY --chown=app entrypoint.sh ./

RUN chmod u+x entrypoint.sh

EXPOSE 8181
ENTRYPOINT ["./entrypoint.sh"]
