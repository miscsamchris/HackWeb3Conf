import { useState, ChangeEvent, FormEvent } from 'react';

interface FormData {
  channelName: string;
  channelRules: string;
  rewards: string;
  consequences: string;
}

interface ChannelFormProps {
  onSubmit: (data: FormData) => void;
}

export const ChannelForm = ({ onSubmit }: ChannelFormProps) => {
  const [formData, setFormData] = useState<FormData>({
    channelName: '',
    channelRules: '',
    rewards: '',
    consequences: '',
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({
      channelName: '',
      channelRules: '',
      rewards: '',
      consequences: '',
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="channelName" className="block text-sm font-medium text-gray-300">
          Channel Name
        </label>
        <input
          type="text"
          name="channelName"
          id="channelName"
          value={formData.channelName}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md bg-gray-800 border-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label htmlFor="channelRules" className="block text-sm font-medium text-gray-300">
          Channel Rules
        </label>
        <textarea
          name="channelRules"
          id="channelRules"
          value={formData.channelRules}
          onChange={handleChange}
          required
          rows={3}
          className="mt-1 block w-full rounded-md bg-gray-800 border-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        ></textarea>
      </div>
      <div>
        <label htmlFor="rewards" className="block text-sm font-medium text-gray-300">
          Rewards for Positive Behavior
        </label>
        <input
          type="text"
          name="rewards"
          id="rewards"
          value={formData.rewards}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md bg-gray-800 border-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label htmlFor="consequences" className="block text-sm font-medium text-gray-300">
          Consequences for Rule Violations
        </label>
        <input
          type="text"
          name="consequences"
          id="consequences"
          value={formData.consequences}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md bg-gray-800 border-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>
      <div>
        <button
          type="submit"
          className="w-full bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:opacity-90 transition duration-300"
        >
          Add Channel
        </button>
      </div>
    </form>
  );
};