FROM ubuntu:latest

WORKDIR /app

COPY requirements.txt /app/

RUN apt update && apt upgrade -y
RUN apt install python3 python3-venv python3-pip -y

RUN python3 -m venv venv
RUN . venv/bin/activate
RUN pip install -r requirements.txt

COPY . .

CMD [ "sh", "scripts/docker-cmd.sh" ]
