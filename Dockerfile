# Dockerfile
FROM python:3.11-slim-buster
LABEL MAINTAINER="Raskitoma/EAJ"
LABEL VERSION="2.0"
LABEL LICENSE="GPLv3"
LABEL DESCRIPTION="Raskitoma - SorulloMachine Bot OpenAI"

# setting env vars
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# customizable env vars via docker-compose
ENV DISCORD_TOKEN=DISCORDTOKEN
ENV OPENAI_API_KEY=OPENAI_API_KEY
ENV OPENAI_MODEL=gpt-4o
ENV OPENAI_MODEL_IMG=dall-e-3

# create required folders
RUN mkdir -p /app

# setting workdir
WORKDIR /app

# copy requirements file
COPY requirements.txt /app/requirements.txt
# installing needed python libraries
RUN pip3 install -r requirements.txt

# copying required files
COPY *.py /app/

# Exposing main port
EXPOSE 8123

# Startup
CMD [ "python3", "sorullo.py" ]