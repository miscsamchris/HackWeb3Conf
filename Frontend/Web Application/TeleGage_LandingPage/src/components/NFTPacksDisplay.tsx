"use client"

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Dialog, DialogContent, DialogClose } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { X } from 'lucide-react'

interface NFTPack {
  _id: string
  imageUrl: string
  altText: string
  title: string
  price: number
  keywords: string
  id: string
  communityId: string
}

export default function NFTPacksGallery({ communityId }: { communityId: string }) {
  const [packs, setPacks] = useState<NFTPack[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPack, setSelectedPack] = useState<NFTPack | null>(null)

  useEffect(() => {
    const fetchAllNFTPacks = async () => {
      if (!communityId) {
        console.log("Waiting for communityId...");
        return;
      }

      console.log("Community ID:", communityId);
      
      try {
        setIsLoading(true);
        setError(null);
    
        // Fetch NFT Superpacks
        const superpacksResponse = await fetch('https://telegage-server.onrender.com/api/nft-superpacks');
        if (!superpacksResponse.ok) {
          throw new Error('Failed to fetch NFT superpacks');
        }
        const superpacksData = await superpacksResponse.json();
        console.log("Superpacks Data:", superpacksData);
    
        // Wait for 4 seconds before making the second API call
        // await new Promise(resolve => setTimeout(resolve, 1000));

        // Fetch Community NFT Packs
        const communityPacksResponse = await fetch('https://telegage-server.onrender.com/api/nft-packs', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ communityId: communityId }),
        });
        if (!communityPacksResponse.ok) {
          throw new Error('Failed to fetch community NFT packs');
        }
        const communityPacksData = await communityPacksResponse.json();
        console.log("Community Packs Data:", communityPacksData);
        
        // Combine the results
        const combinedNFTPacks = [...superpacksData, ...communityPacksData];
        
        // Update state with combined results
        setPacks(combinedNFTPacks);
      } catch (error) {
        console.error("Error fetching NFT packs:", error);
        setError('Failed to load NFT packs. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllNFTPacks();
  }, [communityId])

  if (!communityId) {
    return <div className="text-center py-10">Loading community information...</div>
  }

  if (isLoading) return (
    <div className="flex justify-center items-center h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-primary"></div>
    </div>
  )

  if (error) return <div className="text-center py-10 text-red-500">Error: {error}</div>

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">NFT Packs Gallery</h1>
      <motion.div 
        className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {packs.map((pack) => (
          <motion.div
            key={pack._id}
            className="relative aspect-square cursor-pointer overflow-hidden rounded-lg"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelectedPack(pack)}
          >
            <img
              src={pack.imageUrl}
              alt={pack.altText}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
              <h2 className="text-white text-lg font-semibold mb-2">{pack.title}</h2>
              <p className="text-white font-bold">${pack.price.toFixed(2)}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      <Dialog open={!!selectedPack} onOpenChange={(open) => !open && setSelectedPack(null)}>
        <DialogContent className="max-w-3xl">
          <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </DialogClose>
          {selectedPack && (
            <motion.div 
              className="grid gap-4 py-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="relative aspect-video">
                <img
                  src={selectedPack.imageUrl}
                  alt={selectedPack.altText}
                  className="w-full h-full object-contain"
                />
              </div>
              <h2 className="text-2xl font-bold">{selectedPack.title}</h2>
              <p className="text-xl font-semibold">Price: ${selectedPack.price.toFixed(2)}</p>
              <div className="flex flex-wrap gap-2">
                {selectedPack.keywords.split(',').map((keyword, index) => (
                  <Badge key={index} variant="secondary">{keyword.trim()}</Badge>
                ))}
              </div>
              <p className="text-sm text-muted-foreground">ID: {selectedPack.id}</p>
            </motion.div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}