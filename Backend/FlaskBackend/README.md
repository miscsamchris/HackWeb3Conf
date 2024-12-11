# TeleGage Web Application

TeleGage Web Application is a Flask-based backend service that integrates with Telegram, Aptos blockchain, and MongoDB to manage community engagement and token-based interactions.

## Features

1. Telegram Channel Management: Create and import Telegram channels/groups.
2. Token Management: Manage TeleTokens on the Aptos blockchain.
3. NFT Sticker Creation: Create and mint NFT stickers for users.
4. Community Statistics: Track and update community engagement metrics.
5. User Management: Handle user registrations and token balances.

## Prerequisites

- Python 3.7+
- MongoDB
- Aptos CLI and SDK
- Telegram API credentials
- Cloudinary account

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/telegage-web-app.git
   cd telegage-web-app
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   APTOS_NODE_URL=https://api.testnet.aptoslabs.com/v1
   APTOS_FAUCET_URL=https://faucet.testnet.aptoslabs.com
   TELEGRAM_API_ID=your_telegram_api_id
   TELEGRAM_API_HASH=your_telegram_api_hash
   MONGODB_CONNECTION_STRING=your_mongodb_connection_string
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret
   ```

4. Set up the Aptos admin wallet:
   - Create a file named `admin` in the `TeleGageApplication/TeleGage/static/` directory
   - Add the admin wallet details in the appropriate format

5. Configure the application:
   Update the following variables in the `__init__.py` file:
   ```python:TegeGageApplication/TeleGage/__init__.py
   startLine: 63
   ```

## Running the Application

```bash
python app.py
```
## API Endpoints

1. Create Telegram Channel:
   ```python:TegeGageApplication/app.py
   startLine: 30
   ```

2. Get Community Statistics:
   ```python:TegeGageApplication/app.py
   startLine: 238
   ```

3. Get Community Topics:
   ```python:TegeGageApplication/app.py
   startLine: 256
   ```

4. Import Existing Channel:
   ```python:TegeGageApplication/app.py
   startLine: 340
   ```

## How It Works

1. **Channel Creation/Import**: The application can create new Telegram channels or import existing ones. It sets up the channel structure, including topics and admin rights.

2. **User Management**: When users join a channel, the application creates a custodial wallet for them on the Aptos blockchain and manages their TeleTokens.

3. **Token Management**: The application handles minting, transferring, and burning of TeleTokens based on user actions and community rules.

4. **NFT Sticker Creation**: Users can create custom NFT stickers from their profile pictures. These are minted as soul-bound tokens on the Aptos blockchain and added as Telegram sticker sets.

5. **Community Statistics**: The application tracks various metrics such as message count, points earned, and NFTs minted. These are stored in MongoDB for easy retrieval and analysis.

## Security Considerations

- User private keys are encrypted before being stored in the database.
- Sensitive information is stored in environment variables.
- The application uses secure connections for all API interactions.