# MegaBot
## Overview
A discord bot for logging and monitoring. Has the ability to make logs public and detect a 'panic word' to create a separate log file for administrators to review. MegaBot is available in a docker container and takes environment variables to determine bot name, bot id, url for logs to be published etc.

## Docker
It is recommended to use a Docker container to run MegaBot to improve bot restart times and keep MegaBot running the latest version.
### Docker-Compose
Here is an example docker-compose file
```
version: '3'
services:
    MegaBot:
        image: kdog31/megabot
        volumes:
            - ./logs:/MegaBot/logs
        env_file:
            - .env
        restart: always
        tty: true
```
example .env file
```
DISCORD_TOKEN=YOUR_DISCORD_TOKEN
DISCORD_ID=YOUR_BOT_ID
BOT_NAME=YOUR_BOT_NAME
LOG_URL=https://logs.somewebsite.com
PANIC_WORD=PANIC
PANIC_LOG_LEN=50
SUPER_ADMIN=
MC_SERVERS=
```
Alternatively you can include your environment variables in the docker-compose.yml file. This can be helpful if you are using a Docker frontend, such as Portainer.
```
version: '3'
services:
    MegaBot:
        image: kdog31/megabot
        volumes:
            - ./logs:/MegaBot/logs
            - ./optouts:/MegaBot/optouts
        environment:
            - DISCORD_TOKEN=YOUR_DISCORD_TOKEN
            - DISCORD_ID=YOUR_BOT_ID
            - BOT_NAME=YOUR_BOT_NAME
            - LOG_URL=https://logs.somewebsite.com
            - PANIC_WORD=PANIC
            - PANIC_LOG_LEN=50
            - SUPER_ADMIN=
            - MC_SERVERS=
        restart: always
        tty: true
```
#### Environment breakdown
```
DISCORD_TOKEN=
```
This is your discord token, you obtain this by creating a bot in the Discord Developer portal.
```
DISCORD_ID=
```
This is the ID of the bot, it is required as the bot is configured to respond to pings, I.E. @MegaBot some_command
```
BOT_NAME=
```
This is how the bot will refer to itself in logs and in chat, excluding the use of the source command. MegaBot will always refer to its official name when referencing source.
```
LOG_URL=
```
This is the URL MegaBot will use as the root for the panic log links and log links. this variable is not required, however the panic and log linking functionality is disabled without it.
Should you choose to enable log linking your web root should point to the ./logs mount in the docker-compose.yml file. this is what MegaBot expects the base link to be pointed at, otherwise automatically generated URLs will be malformed.
```
PANIC_WORD=
```
This is the word that MegaBot will look for in chat to create a panic log, anybody can say this word and a panic will be triggered. This variable is also optional, however without it the panic functionality is disabled.
```
PANIC_LOG_LEN=
```
This defines the number of messages the panic log should contain. This can be as high as you would like in theory, however larger numbers slow down the creation of the panic log. has been tested working with 200 messages. If undefined this variable defaults to 50.
```
SUPER_ADMIN=
```
This is a space separated list of users who will be considered administrators over the bot, even if they do not have the administrator role. This is an optional list and not required.
```
MC_SERVERS=
```
This is a space separated list of Minecraft servers for the mstatus cog to monitor. This is an optional list and not required.