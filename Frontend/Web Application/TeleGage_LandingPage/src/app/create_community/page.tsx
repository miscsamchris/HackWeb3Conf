"use client";
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CommunityForm } from '@/components/CommunityForm';
import { TopicForm } from '@/components/TopicForm';
import { motion, AnimatePresence } from 'framer-motion';
import { FaArrowLeft, FaCheck } from 'react-icons/fa';


export default function CreateCommunityPage() {
  const [step, setStep] = useState(1);
  const [communityData, setCommunityData] = useState<any>({});
  const [topics, setTopics] = useState<any[]>([]);
  const router = useRouter();

  const handleCommunitySubmit = (data: any) => {
    setCommunityData(data);
    setStep(2);
  };

  const handleTopicSubmit = (data: any) => {
    console.log(data);
    setTopics([...topics, data]);
  };

  const handleTopicRemove = (index: number) => {
    setTopics(topics.filter((_, i) => i !== index));
  };

  const handleTopicEdit = (index: number, updatedTopic: any) => {
    const newTopics = [...topics];
    newTopics[index] = updatedTopic;
    setTopics(newTopics);
  };

  const handleFinish = async () => {
    const { walletAddress } = JSON.parse(localStorage.getItem('user') || '{}');
    const requestData = {
      telegram_channel_title: communityData.communityName,
      telegram_channel_description: communityData.communityDescription,
      telegram_admin_id: communityData.telegramUsername,
      telegram_channel_rules: communityData.communityRules,
      telegram_channel_instructions: communityData.communityInstructions,
      telegram_channel_owner: walletAddress,
      topics: topics.map(topic => ({
        Name: topic.topicName,
        Rules: topic.topicRules,
        Instructions: topic.topicInstructions
      }))
    };

    console.log(requestData);
    try {
      const response = await fetch('https://tegegageapplication.onrender.com/create_telegram_channel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        console.log('Telegram channel created successfully');
        
        // Update the user's has_community field
        try {
          await fetch('https://telegage-server.onrender.com/update_user_community_status', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ walletAddress: localStorage.getItem('petraAddress'), has_community: true }),
          });
        } catch (error) {
          console.error('Error updating user community status:', error);
        }

        router.push('/dashboard');
      } else {
        console.error('Failed to create Telegram channel');
        // Handle error (e.g., show error message to user)
      }
    } catch (error) {
      console.error('Error creating Telegram channel:', error);
      // Handle error (e.g., show error message to user)
    }
  };

  useEffect(() => {
    console.log('Topics updated:', topics);
  }, [topics]);

  const progressPercentage = step === 1 ? 50 : 100;

  return (
    <div className="bg-black text-white min-h-screen bg-[linear-gradient(to_bottom,#000,#200D42_34%,#4F21A1_65%,#A45EDB_82%)]">
      <div className="container mx-auto px-4 py-6 max-w-2xl">
        <motion.div
          initial={{ width: "0%" }}
          animate={{ width: `${progressPercentage}%` }}
          className="h-1 bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 rounded-full mb-4"
        />
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-3xl font-bold mb-4 text-center bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-transparent bg-clip-text"
        >
          {step === 1 ? 'Create Your Community' : 'Add Topics'}
        </motion.h1>
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="bg-gray-800 p-4 rounded-lg shadow-lg"
          >
            {step === 1 ? (
              <CommunityForm onSubmit={handleCommunitySubmit} />
            ) : (
              <>
                <TopicForm 
                  onSubmit={handleTopicSubmit} 
                  topics={topics} 
                  onRemove={handleTopicRemove} 
                  onEdit={handleTopicEdit}
                />
                <div className="mt-4 flex justify-between">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setStep(1)}
                    className="flex items-center bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition duration-300 text-sm"
                  >
                    <FaArrowLeft className="mr-2" />
                    Back
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleFinish}
                    className="flex items-center bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:opacity-90 transition duration-300 text-sm"
                  >
                    Finish
                    <FaCheck className="ml-2" />
                  </motion.button>
                </div>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}