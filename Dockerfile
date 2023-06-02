FROM ubuntu:latest

WORKDIR /app

COPY requirements.txt /app/

RUN apt update && apt upgrade -y
RUN apt install python3 python3-venv python3-pip -y

RUN python3 -m venv venv
RUN . venv/bin/activate
RUN pip install -r requirements.txt

COPY . .

# Be sure do set this to the domain you will be using!
# opensearch.xml WILL be generated using this domain.
# Uncomment when done.
# NOTE: You do not need to add a trailing '/'.
# NOTE: Use the example below as a reference on using the variable.
# ENV DOMAIN=https://www.yourdomain.com

RUN sh scripts/generate-opensearch.sh

ENV PORT=8000
EXPOSE ${PORT}

# Read the gunicorn docs on how exactly to use it,
# or change the server if need be.
CMD [ "gunicorn", "-w", "4", "-t", "1", "__init__:app" ]
