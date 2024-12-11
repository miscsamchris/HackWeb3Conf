import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent,  } from "../components/ui/card"
import { Badge } from "../components/ui/badge"


interface NFTCardProps {
  collectionName: string
  tokenUri: string
  tokenName: string
}

const NFTCard: React.FC<NFTCardProps> = ({ collectionName, tokenUri, tokenName }) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <Card className="overflow-hidden bg-gray-800 border-gray-700">
        <div className="relative">
          <img 
            src={tokenUri} 
            alt={tokenName} 
            className="w-full h-64 object-cover transition-transform duration-300 ease-in-out transform hover:scale-110"
          />
          {isHovered && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center"
            >
            </motion.div>
          )}
        </div>
        <CardContent className="p-4">
          <h3 className="text-lg font-semibold text-white mb-2 truncate" title={tokenName || 'Unnamed Token'}>
            {tokenName || 'Unnamed Token'}
          </h3>
          <Badge variant="secondary" className="text-xs font-normal">
            {collectionName}
          </Badge>
        </CardContent>
        
      </Card>
    </motion.div>
  )
}

export default NFTCard