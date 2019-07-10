FROM ubuntu:18.04
MAINTAINER sinpcw

# Command
CMD ["echo", "Slackbot for KAMONOHASHI"]

RUN set -x && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y vim-common && \
    apt-get install -y git && \
    apt-get install -y ssh && \
    apt-get install -y curl && \
    apt-get install -y python3 python3-pip && \
    pip3 install absl-py && \
    pip3 install kamonohashi-cli && \
    git clone https://github.com/sinpcw/kamonohashi-slackbot.git
