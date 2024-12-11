import React, { useState, useEffect } from "react";
import eruda from 'eruda'

import { useWallet } from "@aptos-labs/wallet-adapter-react";
import { motion } from "framer-motion";
import { useParams } from "react-router-dom";
import StickerMarketplace from "./StickerMarketplace";
import NFTCard from "./NFTCard";
import { Wallet } from "lucide-react";

eruda.init()

export const Dashboard: React.FC = () => {
  const { account } = useWallet();
  const { userId, communityId } = useParams<{ userId: string; communityId: string }>();
  const [balance, setBalance] = useState(0);
  const [activeTab, setActiveTab] = useState("my nfts");
  const [nfts, setNfts] = useState<any[]>([]);
  const [custodialAddress, setCustodialAddress] = useState<string | null>(null);

  useEffect(() => {
    console.log("custodialAddress", custodialAddress);
    const fetchCustodialAddress = async () => {
      const res = await fetch(`https://telegage-server.onrender.com/api/community-user/${userId}`);
      const data = await res.json();
      if (data.custodialAddress) {
        console.log("Custodial Address:", data.custodialAddress);
        setCustodialAddress(data.custodialAddress);

        const balanceQuery = `query MyQuery {
          current_fungible_asset_balances(
            where: {
              owner_address: {
                _eq: "${data.custodialAddress}"
              }
            }
          ) {
            amount
          }
        }`;
        try {
          const response = await fetch("https://aptos-testnet.nodit.io/<Add Aptos Node URL here>/v1/graphql", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ query: balanceQuery }),
          });

          const result = await response.json();
          const balances = result.data.current_fungible_asset_balances;
          console.log("token balance", balances[1].amount);
          setBalance(balances[1].amount);
        } catch (error) {
          console.error("Error fetching token balance:", error);
          setBalance(0); // Set balance to 0 if there's an error
        }
      }
    };

    const fetchAccountNFTs = async () => {
      if (account?.address) {
        const query = `
          query MyQuery {
            current_token_ownerships_v2(
              offset: 0
              where: {owner_address: {_eq: "${account.address}"}}
            ) {
              owner_address
              current_token_data {
                collection_id
                token_name
                current_collection {
                  collection_name
                }
                token_uri
              }
            }
          }
        `;

        try {
          const response = await fetch("https://aptos-testnet.nodit.io/<Add Aptos Node URL here>/v1/graphql", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ query }),
          });

          const result = await response.json();
          console.log("result nffff", result);
          const accountNFTs = result.data.current_token_ownerships_v2.reverse();

          console.log("Account NFTs:", accountNFTs);
          setNfts(accountNFTs);
        } catch (error) {
          console.error("Error fetching account NFTs:", error);
        }
      }
    };

    fetchAccountNFTs();
    fetchCustodialAddress();
  }, [account?.address, userId]);

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      <motion.header
        className="bg-gray-800 rounded-lg shadow-lg p-4 flex justify-between items-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center space-x-2">
          <Wallet className="text-purple-400 w-6 h-6" />
          <span className="text-white font-mono">
            {account?.address ? `${account.address.slice(0, 6)}...${account.address.slice(-4)}` : 'Not Connected'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-purple-400 font-bold">{balance.toFixed(2)}</span>
          <span className="text-gray-300">TELE</span>
        </div>
      </motion.header>

      <nav className="bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="flex">
          {["My NFTs", "Marketplace"].map((tab) => (
            <button
              key={tab}
              className={`flex-1 py-3 px-4 ${activeTab === tab.toLowerCase() ? "bg-purple-600 text-white" : "bg-gray-700 text-gray-300"} transition-colors duration-200`}
              onClick={() => setActiveTab(tab.toLowerCase())}
            >
              {tab}
            </button>
          ))}
        </div>
      </nav>

      <motion.div
        className="bg-gray-800 rounded-lg shadow-md p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {activeTab === "my nfts" ? (
          <div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {nfts.map((nft, index) => (
                <NFTCard
                  key={index}
                  collectionName={nft.current_token_data.current_collection.collection_name}
                  tokenUri={nft.current_token_data.token_uri}
                  tokenName={nft.current_token_data.token_name || `Sticker #${nft.current_token_data.token_properties?.['Sticker #']}`}
                />
              ))}
            </div>
          </div>
        ) : (
          <StickerMarketplace communityId={communityId || ""} userBalance={balance} />
        )}
      </motion.div>
    </div>
  );
};