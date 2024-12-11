import { useState, ChangeEvent, FormEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaHashtag, FaInfoCircle, FaList, FaPlus, FaTimes } from 'react-icons/fa';

interface Topic {
  topicName: string;
  topicRules: string;
  topicInstructions: string;
  id?: number;
  status?: string;
}

interface TopicFormProps {
  onSubmit: (data: Topic) => void;
  topics: Topic[];
  onRemove: (index: number) => void;
  onEdit: (index: number, updatedTopic: Topic) => void;
}

export const TopicForm = ({ onSubmit, topics, onRemove, onEdit }: TopicFormProps) => {
  const [formData, setFormData] = useState<Topic>({
    topicName: '',
    topicRules: '',
    topicInstructions: '',
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({ topicName: '', topicRules: '', topicInstructions: '' });
  };

  const handleEdit = (index: number, field: string, value: string) => {
    const updatedTopic = { ...topics[index], [field]: value };
    onEdit(index, updatedTopic);
  };

  return (
    <div className="space-y-4">
      <motion.form
        onSubmit={handleSubmit}
        className="space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="topicName" className="block text-sm font-semibold text-indigo-300 mb-1">
              <FaHashtag className="inline-block mr-2" />
              Name
            </label>
            <input
              type="text"
              name="topicName"
              id="topicName"
              value={formData.topicName}
              onChange={handleChange}
              required
              className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
              placeholder="Enter topic name"
            />
          </div>
          <div>
            <label htmlFor="topicRules" className="block text-sm font-semibold text-indigo-300 mb-1">
              <FaList className="inline-block mr-2" />
              Rules
            </label>
            <input
              type="text"
              name="topicRules"
              id="topicRules"
              value={formData.topicRules}
              onChange={handleChange}
              required
              className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
              placeholder="Topic rules"
            />
          </div>
          <div>
            <label htmlFor="topicInstructions" className="block text-sm font-semibold text-indigo-300 mb-1">
              <FaInfoCircle className="inline-block mr-2" />
              Instructions
            </label>
            <input
              type="text"
              name="topicInstructions"
              id="topicInstructions"
              value={formData.topicInstructions}
              onChange={handleChange}
              required
              className="w-full rounded-md bg-gray-800 border border-indigo-500 text-white shadow-sm focus:border-pink-500 focus:ring-1 focus:ring-pink-500 p-2 text-sm transition-all duration-300"
              placeholder="Topic instructions"
            />
          </div>
        </div>
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:opacity-90 transition-all duration-300 text-sm font-bold shadow-lg flex items-center justify-center"
          >
            <FaPlus className="mr-2" />
            Add Topic
          </button>
        </motion.div>
      </motion.form>

      {topics.length > 0 && (
        <div className="mt-4">
          <h3 className="text-lg font-semibold text-indigo-300 mb-2">Topics</h3>
          <div className="bg-gray-900 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-800">
                  <th className="px-2 py-1 text-left text-indigo-300">Name</th>
                  <th className="px-2 py-1 text-left text-indigo-300">Rules</th>
                  <th className="px-2 py-1 text-left text-indigo-300">Instructions</th>
                  <th className="px-2 py-1 text-left text-indigo-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                <AnimatePresence>
                  {topics.map((topic, index) => (
                    <motion.tr
                      key={topic.id || index}
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.3 }}
                      className="border-b border-gray-700"
                    >
                      <td className="px-2 py-1 text-white">{topic.topicName}</td>
                      <td className="px-2 py-1">
                        <input
                          type="text"
                          value={topic.topicRules}
                          onChange={(e) => handleEdit(index, 'topicRules', e.target.value)}
                          className="w-full bg-gray-800 text-white p-1 rounded border border-gray-700 focus:border-pink-500 focus:ring-1 focus:ring-pink-500"
                        />
                      </td>
                      <td className="px-2 py-1">
                        <input
                          type="text"
                          value={topic.topicInstructions}
                          onChange={(e) => handleEdit(index, 'topicInstructions', e.target.value)}
                          className="w-full bg-gray-800 text-white p-1 rounded border border-gray-700 focus:border-pink-500 focus:ring-1 focus:ring-pink-500"
                        />
                      </td>
                      <td className="px-2 py-1">
                        <button
                          onClick={() => onRemove(index)}
                          className="text-red-500 hover:text-red-600 transition-colors duration-300"
                        >
                          <FaTimes />
                        </button>
                      </td>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};