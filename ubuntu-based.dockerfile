FROM ubuntu:latest

# LABEL can be used to attach metadata to the container.
LABEL title="Araa Search" \
      description="A privacy-respecting, ad-free, self-hosted Google metasearch engine with strong security and full API support." \
      git_repo="https://github.com/TEMtheLEM/araa-search" \
      authors="https://github.com/Extravi/araa-search/contributors" \
      maintainer="TEMtheLEM <temthelem@duck.com>" \
      image="https://hub.docker.com/r/temthelem/araa-search"

WORKDIR /app

COPY requirements.txt /app/

RUN apt update && apt upgrade -y
RUN apt install python3 python3-venv python3-pip --no-install-recommends -y

# We will only be running our own python app in a container,
# so this shouldn't be terrible.
RUN pip install --break-system-packages -r requirements.txt

COPY . .

ENV ORIGIN_REPO=https://github.com/TEMtheLEM/araa-search

CMD [ "sh", "scripts/docker-cmd.sh" ]
