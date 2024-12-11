"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { TopicForm } from '@/components/TopicForm';
import { motion, AnimatePresence } from 'framer-motion';
import { FaArrowLeft, FaCheck, FaTelegram } from 'react-icons/fa';

interface Topic {
  topicName: string;
  topicRules: string;
  topicInstructions: string;
  id?: number;
  status?: string;
}

export default function ImportCommunityPage() {
  const [step, setStep] = useState(1);
  const [groupLink, setGroupLink] = useState('');
  const [topics, setTopics] = useState<Topic[]>([]);
  const [showModal, setShowModal] = useState(true); // Set this to true initially
  const [communityRules, setCommunityRules] = useState('');
  const [communityInstructions, setCommunityInstructions] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [nextId, setNextId] = useState(1000); // Start from 1000 to avoid conflicts with existing IDs
  const router = useRouter();

  const handleGroupLinkSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsValidating(true);
  
    // Extract the channel ID from the URL
    const channelIdMatch = groupLink.match(/\/c\/(\d+)/);
    const channelId = channelIdMatch ? channelIdMatch[1] : null;
  
    if (!channelId) {
      console.error('Invalid group link format');
      setShowModal(true);
      setIsValidating(false);
      return;
    }
  
    console.log(channelId);
  
    try {
      const response = await fetch('https://tegegageapplication.onrender.com//get_topics_by_community', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_channel_username: channelId }),
      });

      const data = await response.json();
      console.log(data);

      if (data.code === 200) {
        const initialTopics = data.Topics.map((topic: any) => ({
          topicName: topic.Name,
          topicRules: '',
          topicInstructions: '',
          id: topic.id,
          status: 'Old'
        }));
        setTopics(initialTopics);
        setStep(2);
      } else {
        setShowModal(true);
      }
    } catch (error) {
      console.error('Error validating group:', error);
      setShowModal(true);
    } finally {
      setIsValidating(false);
    }
  };
  
  const handleTopicSubmit = (data: Topic) => {
    const newTopic = {
      ...data,
      id: nextId,
      status: 'New'
    };
    setTopics([...topics, newTopic]);
    setNextId(nextId + 1);
  };

  const handleTopicRemove = (index: number) => {
    setTopics(topics.filter((_, i) => i !== index));
  };

  const handleTopicEdit = (index: number, updatedTopic: Topic) => {
    const newTopics = [...topics];
    newTopics[index] = updatedTopic;
    setTopics(newTopics);
  };

  const handleFinish = async () => {
    const channelIdMatch = groupLink.match(/\/c\/(\d+)/);
    const channelId = channelIdMatch ? channelIdMatch[1] : null;
    const { walletAddress } = JSON.parse(localStorage.getItem('user') || '{}');

    const requestData = {
      telegram_channel_username: channelId,
      telegram_channel_rules: communityRules,
      telegram_channel_owner: walletAddress,
      telegram_channel_instructions: communityInstructions,
      topics: topics.map(topic => ({
        Name: topic.topicName,
        Status: topic.status || 'New',
        ID: topic.id || undefined, // Use undefined for new topics without an ID
        Rules: topic.topicRules,
        Instructions: topic.topicInstructions,
      })),
    };

    console.log("Request Data:", requestData);
    try {
      const response = await fetch('https://tegegageapplication.onrender.com//import_channel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        console.log('Telegram channel updated successfully');

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
        console.error('Failed to update Telegram channel');
        // Handle error (e.g., show error message to user)
      }
    } catch (error) {
      console.error('Error updating Telegram channel:', error);
      // Handle error (e.g., show error message to user)
    }
  };

  const progressPercentage = step === 1 ? 50 : 100;

  const Modal = ({ onClose }: { onClose: () => void }) => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full">
        <h2 className="text-xl font-bold mb-4 text-indigo-300">Important!</h2>
        <p className="text-white mb-6">Add @telegageman to your community and transfer ownership rights to him.</p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onClose}
          className="w-full bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:opacity-90 transition-all duration-300 text-sm font-bold shadow-lg"
        >
          Done
        </motion.button>
      </div>
    </motion.div>
  );

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
          className="text-2xl font-bold mb-4 text-center bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-transparent bg-clip-text"
        >
          {step === 1 ? 'Import Your Community' : 'Add Topics'}
        </motion.h1>
        <AnimatePresence>
          {showModal && <Modal onClose={() => setShowModal(false)} />}
        </AnimatePresence>
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
              <form onSubmit={handleGroupLinkSubmit} className="space-y-4">
                <div>
                  <label htmlFor="groupLink" className="block text-sm font-semibold text-indigo-300 mb-1">
                    <FaTelegram className="inline-block mr-2" />
                    Paste Your Group Link
                  </label>
                  <input
                    type="text"
                    name="groupLink"
                    id="groupLink"
                    value={groupLink}
                    onChange={(e) => setGroupLink(e.target.value)}
                    required
                    className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
                    placeholder="https://t.me/your_group_link"
                  />
                </div>
                <div>
                  <label htmlFor="communityRules" className="block text-sm font-semibold text-indigo-300 mb-1">
                    Community Rules
                  </label>
                  <textarea
                    name="communityRules"
                    id="communityRules"
                    value={communityRules}
                    onChange={(e) => setCommunityRules(e.target.value)}
                    required
                    rows={3}
                    className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
                    placeholder="Enter community rules"
                  />
                </div>
                <div>
                  <label htmlFor="communityInstructions" className="block text-sm font-semibold text-indigo-300 mb-1">
                    Community Instructions
                  </label>
                  <textarea
                    name="communityInstructions"
                    id="communityInstructions"
                    value={communityInstructions}
                    onChange={(e) => setCommunityInstructions(e.target.value)}
                    required
                    rows={3}
                    className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
                    placeholder="Enter community instructions"
                  />
                </div>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <button
                    type="submit"
                    disabled={isValidating}
                    className="w-full bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:opacity-90 transition-all duration-300 text-sm font-bold shadow-lg"
                  >
                    {isValidating ? 'Validating...' : 'Validate'}
                  </button>
                </motion.div>
              </form>
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