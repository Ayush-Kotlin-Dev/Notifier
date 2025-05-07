# GGU Notification Bot

A Telegram bot that monitors GGU notifications and forwards them to a Telegram channel.

## Deployment on Render.com

1. Create a free account on [Render.com](https://render.com)
2. Fork this repository to your GitHub account
3. In Render.com dashboard:
   - Click "New +"
   - Select "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` and deploy your bot

## Environment Variables

The bot uses the following configuration in `notifi.py`:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHANNEL_ID`: Your Telegram channel ID

Make sure these are properly set in your code before deploying.

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the bot:
```bash
python notifi.py 