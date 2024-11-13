# Chatbot using OpenAI and Telegram

This project is a chatbot powered by OpenAI and deployed on Telegram, designed to help users with various conversational needs. It includes both a locator bot and a journaller bot.

## Prerequisites

1. **Python Environment**: Ensure Python 3.8+ is installed.
2. **OpenAI Account**: Set up an OpenAI account and obtain an API key.
3. **Telegram Bot**: Create a bot on Telegram to get the required access token and bot username.

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

### 2. Create environment
Set up a virtual environment to manage dependencies
```bash
python -m venv env
# On Windows Powershell:
./env/Scripts/activate
```

### 3. Install packages
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
```text
# TELEGRAM
TELEGRAM_ACCESS_TOKEN=<Telegram Access Token>
TELEGRAM_BOT_USERNAME=<Telegram Bot Username>

# OPENAI
OPENAI_API_KEY=<Your OpenAI API Key>
OPENAI_LOCATOR_ID=<OpenAI Model ID for Locator>
OPENAI_JOURNALLER_ID=<OpenAI Assistant ID for Journaller>
```

### 5. Run chatbot
```bash
python app.py
```

### Usage
With the bot running, send messages to Telegram bot username to start interacting. The bot will use OpenAI API to generate responses based on conversation type