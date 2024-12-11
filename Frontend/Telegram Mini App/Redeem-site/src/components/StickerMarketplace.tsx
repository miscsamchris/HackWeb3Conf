"use client"
import eruda from 'eruda'


import  { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useWallet } from "@aptos-labs/wallet-adapter-react"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "../components/ui/card"
import { Badge } from "../components/ui/badge"
import { Loader2, ShoppingCart, AlertCircle } from "lucide-react"

eruda.init()

interface NFTPack {
  title: string
  price: number
  id: number
  negative: string
  keywords: string
  imageUrl: string
  altText: string
}

interface StickerMarketplaceProps {
  communityId: string;
  userBalance: number; // Add this new prop
}

export default function StickerMarketplace({ communityId, userBalance }: StickerMarketplaceProps) {
  const { account } = useWallet()
  const [nftPacks, setNFTPacks] = useState<NFTPack[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const mintNftPack = async (pack: NFTPack) => {
    const data = {
      action: "Add Sticker",
      prompt: pack.keywords,
      wallet: account?.address.toString(),
      negative_prompt: pack.negative,
      price: pack.price,
      community_id: communityId
    }

    console.log("Minting NFT pack:", data)

    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.sendData(JSON.stringify(data))
      
    } else {
      console.error("Telegram WebApp is not available")
    }
  }

  useEffect(() => {
    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.ready()
    }
    
    const fetchAllNFTPacks = async (communityId: string) => {
      try {
        setLoading(true);
        setError(null);
    
        // Fetch NFT Superpacks
        const superpacksResponse = await fetch('https://telegage-server.onrender.com/api/nft-superpacks');
        if (!superpacksResponse.ok) {
          throw new Error('Failed to fetch NFT superpacks');
        }
        const superpacksData = await superpacksResponse.json();
    
        // Fetch Community NFT Packs
        const communityPacksResponse = await fetch('https://telegage-server.onrender.com/api/nft-packs', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ communityId: communityId.toString() }),
        });
        if (!communityPacksResponse.ok) {
          throw new Error('Failed to fetch community NFT packs');
        }
        const communityPacksData = await communityPacksResponse.json();
    
        // Combine the results
        const combinedNFTPacks = [...superpacksData, ...communityPacksData];
        
        // Update state with combined results
        setNFTPacks(combinedNFTPacks);
      } catch (error) {
        console.error("Error fetching NFT packs:", error);
        setError('Failed to load NFT packs. Please try again later.');
      } finally {
        setLoading(false);
      }
    };


    fetchAllNFTPacks(communityId)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen text-center p-4">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <p className="text-lg font-semibold text-red-500">{error}</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-1 py-2 max-w-screen-xl bg-gray-900">
      
      <div className="grid grid-cols-2 gap-1 sm:grid-cols-3 sm:gap-2 lg:grid-cols-4 xl:grid-cols-5">
        <AnimatePresence>
          {nftPacks.map((pack) => {
            const isAffordable = userBalance >= pack.price;
            return (
              <motion.div
                key={pack.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Card className={`bg-gray-800 overflow-hidden h-full flex flex-col rounded-lg shadow-md ${!isAffordable ? 'opacity-50' : ''}`}>
                  <CardHeader className="p-0">
                    <div className="aspect-square relative overflow-hidden">
                      <img
                        src={pack.imageUrl}
                        alt={pack.altText}
                        className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement
                          target.src = 'https://via.placeholder.com/400?text=Image+Not+Found'
                        }}
                      />
                    </div>
                  </CardHeader>
                  <CardContent className="p-2 flex-grow">
                    <CardTitle className="text-sm font-semibold mb-1 text-white truncate">{pack.title}</CardTitle>
                    <Badge variant="secondary" className="mb-1 text-xs px-1 py-0">
                      {pack.price} Tokens
                    </Badge>
                    <p className="text-xs text-gray-400 line-clamp-2" title={pack.keywords}>
                      {pack.keywords}
                    </p>
                  </CardContent>
                  <CardFooter className="p-2 pt-0">
                    <Button
                      className={`w-full text-white text-xs py-1 px-2 rounded ${
                        isAffordable ? 'bg-purple-600 hover:bg-purple-700' : 'bg-gray-500 cursor-not-allowed'
                      }`}
                      onClick={() => isAffordable && mintNftPack(pack)}
                      disabled={!isAffordable}
                    >
                      <ShoppingCart className="w-3 h-3 mr-1" />
                      {isAffordable ? 'Buy Pack' : 'Insufficient Balance'}
                    </Button>
                  </CardFooter>
                </Card>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  )
}