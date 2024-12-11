import { useState, ChangeEvent, FormEvent } from 'react';
import { motion } from 'framer-motion';
import { FaTelegram, FaUsers, FaInfoCircle, FaBook, FaClipboardList } from 'react-icons/fa';

interface FormData {
  telegramUsername: string;
  communityName: string;
  communityDescription: string;
  communityRules: string;
  communityInstructions: string;
}

interface CommunityFormProps {
  onSubmit: (data: FormData) => void;
}

export const CommunityForm = ({ onSubmit }: CommunityFormProps) => {
  const [formData, setFormData] = useState<FormData>({
    telegramUsername: '',
    communityName: '',
    communityDescription: '',
    communityRules: '',
    communityInstructions: '',
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div>
        <label htmlFor="telegramUsername" className="block text-sm font-semibold text-indigo-300 mb-1">
          <FaTelegram className="inline-block mr-2" />
          Your Telegram Username
        </label>
        <input
          type="text"
          name="telegramUsername"
          id="telegramUsername"
          value={formData.telegramUsername}
          onChange={handleChange}
          required
          className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
          placeholder="yourusername"
        />
      </div>

      <div>
        <label htmlFor="communityName" className="block text-sm font-semibold text-indigo-300 mb-1">
          <FaUsers className="inline-block mr-2" />
          Community Name
        </label>
        <input
          type="text"
          name="communityName"
          id="communityName"
          value={formData.communityName}
          onChange={handleChange}
          required
          className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
          placeholder="Enter your community name"
        />
      </div>

      <div>
        <label htmlFor="communityDescription" className="block text-sm font-semibold text-indigo-300 mb-1">
          <FaInfoCircle className="inline-block mr-2" />
          Community Description
        </label>
        <textarea
          name="communityDescription"
          id="communityDescription"
          value={formData.communityDescription}
          onChange={handleChange}
          required
          rows={3}
          className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
          placeholder="Describe your community..."
        ></textarea>
      </div>

      <div>
        <label htmlFor="communityRules" className="block text-sm font-semibold text-indigo-300 mb-1">
          <FaBook className="inline-block mr-2" />
          Community Rules
        </label>
        <textarea
          name="communityRules"
          id="communityRules"
          value={formData.communityRules}
          onChange={handleChange}
          required
          rows={4}
          className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
          placeholder="Enter community rules (e.g., Be respectful, No spam, etc.)"
        ></textarea>
      </div>

      <div>
        <label htmlFor="communityInstructions" className="block text-sm font-semibold text-indigo-300 mb-1">
          <FaClipboardList className="inline-block mr-2" />
          Community Instructions
        </label>
        <textarea
          name="communityInstructions"
          id="communityInstructions"
          value={formData.communityInstructions}
          onChange={handleChange}
          required
          rows={4}
          className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
          placeholder="Enter instructions for new members (e.g., How to join, What to do first, etc.)"
        ></textarea>
      </div>

      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <button
          type="submit"
          className="w-full bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:opacity-90 transition-all duration-300 text-sm font-bold shadow-lg"
        >
          Add Topics
        </button>
      </motion.div>
    </motion.form>
  );
};