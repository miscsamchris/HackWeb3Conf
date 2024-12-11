"use client"
import { useState } from "react";
import clsx from "clsx";

import PlusIcon from "../assets/icons/plus.svg";
import MinusIcon from "../assets/icons/minus.svg"
import { AnimatePresence, motion } from "framer-motion";

const items = [
  {
    question: "How does TeleGage's automated moderation work?",
    answer:
      "TeleGage uses advanced AI algorithms to automatically filter out spam, off-topic content, and inappropriate messages. This helps keep discussions on track and maintains a high-quality interaction environment in your Telegram community.",
  },
  {
    question: "Can I customize the reward system for my community?",
    answer:
      "Yes, TeleGage allows you to create a customized reward mechanism. You can define rules for earning tokens and design unique NFT stickers as rewards for active participation and contributions to your community.",
  },
  {
    question: "Is TeleGage compatible with existing Telegram communities?",
    answer:
      "Absolutely! TeleGage is designed to seamlessly integrate with existing Telegram communities. Our easy onboarding process allows you to quickly set up and start benefiting from TeleGage's features without disrupting your current community structure.",
  },
  {
    question: "What kind of analytics does TeleGage provide?",
    answer:
      "TeleGage offers an advanced analytics dashboard that provides insights into community engagement, member activity, popular topics, and the effectiveness of your reward system. This data helps you make informed decisions to grow and improve your community.",
  },
];

const AccordionItem = ({ question, answer }: { question: string, answer: string }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="py-7 border-b border-white/30 cursor-pointer" onClick={() => setIsOpen(!isOpen)}>
      <div className="flex items-center">
        <span className="flex-1 sm:text-xl font-bold select-none">
          {question}
        </span>
        {
          isOpen ? <MinusIcon /> : <PlusIcon />
        }
      </div>
      <AnimatePresence>
        {isOpen &&
          <motion.div
            className={clsx("mt-4", { hidden: !isOpen, "": isOpen })}
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: "auto", marginTop: 16 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
          >
            {answer}
          </motion.div>
        }
      </AnimatePresence>
    </div>
  )
}

export const FAQs = () => {
  return (
    <div className="bg-black text-white bg-gradient-to-b from-[#5D2CA8] to-black py-[72px] sm:py-24">
      <div className="container">
        <h2 className="text-center text-5xl sm:text-6xl font-bold tracking-tighter">Frequently asked questions</h2>
        <div className="mt-12 max-w-5xl mx-auto">
          {
            items.map((item, index) => (
              <AccordionItem key={index} question={item.question} answer={item.answer} />
            ))
          }
        </div>
      </div>
    </div>
  );
};
