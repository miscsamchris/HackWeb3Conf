import React from "react";

import { motion } from "framer-motion";
import { WalletSelector as ShadcnWalletSelector } from "./WalletSelector"

export const WalletConnector: React.FC = () => {
  return (
    <motion.div 
      className="bg-gray-900 p-8 rounded-2xl shadow-lg max-w-md w-full mx-auto text-center"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h1 
        className="text-4xl font-bold mb-4 bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 text-transparent bg-clip-text"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        Welcome to TeleGage
      </motion.h1>
      <motion.p
        className="text-gray-300 mb-6"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        Mint AI-generated Telegram stickers as NFTs using your community points!
      </motion.p>
      <motion.ul
        className="text-left text-gray-400 mb-8"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <li>✨ Create unique stickers with AI</li>
        <li>🏆 Use community points to mint</li>
        <li>🎨 Own your stickers as NFTs</li>
      </motion.ul>
      <motion.div
        className="wallet-button-wrapper"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <ShadcnWalletSelector />
      </motion.div>
    </motion.div>
  );
};