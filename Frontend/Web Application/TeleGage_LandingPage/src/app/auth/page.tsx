"use client";
import { useState } from "react";
import { AuthForm } from "@/components/AuthForm";
import { motion } from "framer-motion";
import Image from "next/image";
import logoImg from "@/assets/images/Telegage_logo.png";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="bg-black text-white min-h-screen flex items-center justify-center bg-[linear-gradient(to_bottom,#000,#200D42_34%,#4F21A1_65%,#A45EDB_82%)]">
      <motion.div 
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-gray-900 p-8 rounded-lg shadow-lg max-w-md w-full"
      >
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 260, damping: 20 }}
          className="flex justify-center mb-6"
        >
          <Image src={logoImg} alt="TeleGage Logo" width={80} height={80} />
        </motion.div>
        <div className="relative mb-8">
          <div className="flex bg-gray-800 p-1 rounded-full">
            <button
              className={`flex-1 py-2 px-4 rounded-full transition-all duration-300 relative z-10 ${
                isLogin ? 'text-white' : 'text-gray-400'
              }`}
              onClick={() => setIsLogin(true)}
            >
              Login
            </button>
            <button
              className={`flex-1 py-2 px-4 rounded-full transition-all duration-300 relative z-10 ${
                !isLogin ? 'text-white' : 'text-gray-400'
              }`}
              onClick={() => setIsLogin(false)}
            >
              Sign Up
            </button>
          </div>
          <motion.div
            className="absolute top-1 left-1 w-[calc(50%-0.25rem)] h-[calc(100%-0.5rem)] bg-indigo-600 rounded-full"
            animate={{ x: isLogin ? 0 : "100%" }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          />
        </div>
        <motion.div
          key={isLogin ? "login" : "signup"}
          initial={{ opacity: 0, x: isLogin ? -20 : 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: isLogin ? 20 : -20 }}
          transition={{ duration: 0.3 }}
        >
          <AuthForm isLogin={isLogin} />
        </motion.div>
      </motion.div>
    </div>
  );
}