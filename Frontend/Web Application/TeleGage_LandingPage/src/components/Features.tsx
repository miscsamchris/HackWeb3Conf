"use client"

import React from 'react'
import { Shield, Zap, MessageCircle } from 'lucide-react'
import { Feature } from "./Feature"

const features = [
  {
    title: "Automated Moderation",
    description:
      "Keep your community clean and on-topic with advanced AI-powered moderation.",
    icon: <Shield className="h-12 w-12 mb-4 text-[#F87AFF]" />
  },
  {
    title: "Engagement Boosting",
    description:
      "Increase participation with gamification and Web3 token rewards for active members.",
    icon: <Zap className="h-12 w-12 mb-4 text-[#FFDD99]" />
  },
  {
    title: "Customizable Rewards",
    description:
      "Create unique NFT stickers as rewards to incentivize and recognize community contributions.",
    icon: <MessageCircle className="h-12 w-12 mb-4 text-[#C3F0B2]" />
  },
]

export const Features = () => {
  return (
    <div className="bg-black text-white py-[72px] sm:py-24">
      <div className="container mx-auto px-4">
        <h2 className="text-center font-bold text-5xl sm:text-6xl tracking-tighter">Powerful Features</h2>
        <div className="max-w-xl mx-auto">
          <p className="text-center mt-5 text-xl text-white/70">
            TeleGage provides everything you need to manage and grow your Telegram community effectively.
          </p>
        </div>
        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Feature key={index} title={feature.title} description={feature.description} icon={feature.icon} />
          ))}
        </div>
      </div>
    </div>
  )
}
