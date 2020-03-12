echo MegaBot Docker Initializing.
echo Creating environment file.
echo DISCORD_TOKEN=$DISCORD_TOKEN\\nDISCORD_ID=$DISCORD_ID\\nBOT_NAME=$BOT_NAME\\nLOG_URL=$LOG_URL\\nPANIC_WORD=$PANIC_WORD\\nPANIC_LOG_LEN=$PANIC_LOG_LEN > /MegaBot/MegaBot/.env && echo Environment file created successfully
cd /MegaBot/MegaBot
echo Updating internal GIT repository
git reset --hard HEAD && git pull && echo Internal GIT repository up to date.
chmod +x /MegaBot/MegaBot/run.sh
echo Launching bot.
python3 bot.py
echo Bot Exited.