FROM debian:bookworm-slim@sha256:6bdbd579ba71f6855deecf57e64524921aed6b97ff1e5195436f244d2cb42b12 as chrome

RUN sed -i 's/deb.debian.org/debian.anexia.at/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y wget gnupg
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get install -f -y curl fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0
RUN apt-get install -f -y libcairo2 libcups2 libdbus-1-3 libdrm2 libexpat1 libgbm1 libglib2.0-0 libgtk-3-0 libgtk-4-1
RUN apt-get install -f -y libpango-1.0-0 libu2f-udev libvulkan1 libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6
RUN apt-get install -f -y libxkbcommon0 libxrandr2 xdg-utils libglib2.0-dev libnspr4 libnss3 libxfixes3 libc-bin libc6
RUN apt-get install -f -y locales
RUN curl -O https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb

FROM bitnami/python:3.9.18-debian-12-r29@sha256:607688045123fb4d60d6894ab64f297e51624883b51c340da1842dc5c8585411

COPY --from=chrome /opt/google/chrome /opt/google/chrome
COPY --from=chrome /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu
COPY --from=chrome /etc/fonts /etc/fonts

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot ./bot
COPY files ./files
COPY main.py .

CMD ["python", "main.py", "/opt/google/chrome"]
