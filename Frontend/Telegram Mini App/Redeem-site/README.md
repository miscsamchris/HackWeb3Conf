
# TeleGage - AI-Generated Telegram Sticker NFT Platform

TeleGage is a React-based web application that allows users to mint AI-generated Telegram stickers as NFTs using community points. This project integrates with the Aptos blockchain and utilizes various wallets, including Mizu wallet, for seamless transactions.

## Features

- Connect to Aptos-compatible wallets
- View and manage NFTs
- Mint AI-generated stickers as NFTs
- Use community points for transactions
- Browse and purchase AI-generated sticker packs
- Responsive design with smooth animations

## Technologies Used

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Framer Motion for animations
- Aptos Blockchain
- Aptos Wallet Adapter
- Mizu Wallet
- Nodeit Indexer
- Shadcn UI components

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- npm or yarn

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/PawanAK/Redeem-site.git
   cd telegage
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`

## Project Structure

The main components of the project are:

- `src/App.tsx`: Main application component
- `src/components/Dashboard.tsx`: User dashboard displaying NFTs and marketplace
- `src/components/StickerMarketplace.tsx`: Marketplace for browsing and purchasing sticker packs
- `src/components/NFTCard.tsx`: Component for displaying individual NFTs
- `src/components/WalletConnector.tsx`: Wallet connection interface

## Configuration

The project uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

```
VITE_APTOS_NODE_URL=<Nodit aptos Indexer>
VITE_APTOS_NETWORK=testnet
VITE_CONTRACT_ADDRESS=0x...
```

## Mizu Wallet Integration

This project integrates Mizu wallet for Aptos blockchain transactions. Mizu wallet is configured in the `WalletProvider` component:

```typescript
import { WalletProvider } from '@manahippo/aptos-wallet-adapter';
import { MizuWallet } from '@mizu-wallet/sdk';

const wallets = [
  new MizuWallet(),
  // Add other wallet providers here
];

function App() {
  return (
    <WalletProvider wallets={wallets}>
      {/* Your app components */}
    </WalletProvider>
  );
}
```

## Nodeit Indexer Usage

We use the Nodeit indexer to fetch data from the Aptos blockchain. This is primarily used in the `Dashboard` component to retrieve NFT data and token balances:

```typescript
import { NodeitClient } from '@nodeit/client';

const nodeitClient = new NodeitClient({
  apiKey: process.env.NODEIT_API_KEY,
  network: 'testnet',
});

async function fetchUserNFTs(address: string) {
  const nfts = await nodeitClient.getNFTs(address);
  // Process and display NFTs
}
```
