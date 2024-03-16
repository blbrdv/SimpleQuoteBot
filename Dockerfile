FROM debian:bookworm-slim@sha256:6bdbd579ba71f6855deecf57e64524921aed6b97ff1e5195436f244d2cb42b12 as chrome

RUN sed -i 's/deb.debian.org/debian.anexia.at/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y wget
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i ./google-chrome*.deb; exit 0  # fixing deps on next line
RUN apt-get install -y -f

FROM bitnami/python:3.9.18-debian-12-r29@sha256:607688045123fb4d60d6894ab64f297e51624883b51c340da1842dc5c8585411

COPY --from=chrome /opt/google/chrome /opt/google/chrome
COPY --from=chrome /usr/share /usr/share
COPY --from=chrome /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu
COPY --from=chrome /etc/fonts /etc/fonts

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot ./bot
COPY files ./files
COPY main.py .

CMD ["python", "main.py", "/opt/google/chrome"]
