# TeleGage Community Bot

TeleGage Community Bot is a Telegram bot designed to manage and enhance community engagement using blockchain technology and AI-powered moderation. This bot integrates with the Aptos blockchain to manage tokens, create NFTs, and provide a rewarding experience for community members.

## Features

1. Token Management: Users can earn and spend TeleTokens within the community.
2. AI-powered Moderation: Automatically moderates messages and awards or deducts points based on community rules.
3. NFT Sticker Creation: Users can create custom NFT stickers from their profile pictures.
4. Community Statistics: Tracks various community metrics and activities.
5. User Management: Handles new member joins and chat join requests.

## Setup

### Prerequisites

- Python 3.7+
- MongoDB
- Aptos CLI and SDK
- Telegram Bot API Token
- Azure OpenAI API Key
- Cloudinary Account

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/telegage-community-bot.git
   cd telegage-community-bot
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - `APTOS_NODE_URL`: Aptos node URL
   - `APTOS_FAUCET_URL`: Aptos faucet URL
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
   - `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
   - `CLOUDINARY_API_KEY`: Your Cloudinary API key
   - `CLOUDINARY_API_SECRET`: Your Cloudinary API secret
   - `MONGODB_CONNECTION_STRING`: Your MongoDB connection string

4. Set up the Aptos admin wallet:
   - Create a file named `admin` in the project root directory
   - Add the admin wallet details in JSON format (see the provided `admin` file)

5. Configure the bot:
   Update the following variables in the `bot.py` file:
   ```python:Bot/bot.py
   startLine: 57
   endLine: 62
   ```

### Running the Bot

Run the bot using the following command: