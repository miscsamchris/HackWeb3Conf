# Community NFT Server

This is the backend server for the Community NFT application, which manages user authentication, community data, and NFT packs.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Endpoints](#api-endpoints)
7. [Database Structure](#database-structure)
8. [User Flow](#user-flow)

## Features

- User authentication (signup and login)
- Community management
- NFT pack creation and retrieval
- Integration with MongoDB Atlas
- Decryption of user data

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)
- MongoDB Atlas account

## Installation

1. Clone the repository
2. Navigate to the server directory:
   ```
   cd server
   ```
3. Install dependencies:
   ```
   npm install
   ```

## Configuration

1. Create a `.env` file in the server directory
2. Add the following environment variables:
   ```
   PORT=3001
   MONGODB_URI_TELEGRAM=your_telegram_communities_mongodb_uri
   MONGODB_URI_TEST=your_test_mongodb_uri
   ```

## Usage

To start the server, run:

```
npm start
```

The server will start on the port specified in the `.env` file (default is 3001).

## API Endpoints

- POST `/api/signup`: Create a new user account
- POST `/api/login`: Authenticate a user
- GET `/api/list-databases`: List all MongoDB databases
- GET `/api/nft-superpacks`: Fetch all NFT super packs
- GET `/api/community-user/:userId`: Fetch community user data
- GET `/api/community-users`: Fetch all community users
- GET `/api/decrypt-user-data/:userId`: Decrypt user data
- POST `/update_user_community_status`: Update user's community status
- POST `/api/communities`: Fetch communities for a wallet address
- POST `/api/community-stats`: Fetch community stats
- POST `/api/create-nft-pack`: Create a new NFT pack
- POST `/api/nft-packs`: Fetch NFT packs for a community

## Database Structure

The application uses two MongoDB databases:

1. `telegram_communities`:
   - `community_users` collection
   - `communities` collection

2. `test`:
   - `users` collection
   - `nftpacks` collection

## User Flow

1. User signs up or logs in using their username, password, or wallet address.
2. Upon successful authentication, the user can:
   - View their community data
   - Create or manage NFT packs
   - Fetch community statistics
   - Update their community status

3. For community owners:
   - They can create new NFT packs associated with their community
   - View and manage their community's data and statistics

4. Users can browse and purchase NFT packs from various communities

5. The server handles data encryption/decryption for sensitive user information

This application provides a seamless integration between user authentication, community management, and NFT pack creation/distribution within a decentralized ecosystem.

