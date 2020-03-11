FROM buildpack-deps:buster

ENV DISCORD_TOKEN=
ENV DISCORD_ID=
ENV BOT_NAME=MegaBot
ENV LOG_URL=
ENV PANIC_WORD=
ENV PANIC_LOG_LEN=50

RUN apt-get update && \
DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip git && \
apt-get clean && \
mkdir /MegaBot && \
cd /MegaBot && \
git clone https://github.com/kdog31/MegaBot && \
chmod +x /MegaBot/MegaBot/pydependancysetup.sh && \
chmod +x /MegaBot/MegaBot/run.sh && \
cd /MegaBot/MegaBot && \
./pydependancysetup.sh

CMD /MegaBot/MegaBot/run.sh