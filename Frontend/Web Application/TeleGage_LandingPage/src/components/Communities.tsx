import { useState, useEffect } from 'react';
import axios from 'axios';

interface Community {
  community_id: string;
  number_of_messages: number;
  points_earned: number;
  number_of_nfts_minted: number;
  users_to_be_kicked_out: string[];
  actions: Action[];
}

interface Action {
  timestamp: string;
  username: string;
  message: string;
}

export const Communities = () => {
  const [communities, setCommunities] = useState<Community[]>([]);

  useEffect(() => {
    const fetchCommunities = async () => {
      try {
        const response = await axios.get('https://telegage-server.onrender.com/api/communities');
        setCommunities(response.data);
      } catch (error) {
        console.error('Failed to fetch communities:', error);
      }
    };

    fetchCommunities();
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Your Communities</h2>
      {communities.map((community) => (
        <div key={community.community_id} className="mb-8 bg-gray-800 p-6 rounded-lg shadow-lg">
          <h3 className="text-xl font-semibold mb-4">Community ID: {community.community_id}</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-gray-700 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Messages</h4>
              <p>{community.number_of_messages}</p>
            </div>
            <div className="bg-gray-700 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Points Earned</h4>
              <p>{community.points_earned}</p>
            </div>
            <div className="bg-gray-700 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">NFTs ffffMinted</h4>
              <p>{community.number_of_nfts_minted}</p>
            </div>
          </div>
          <div className="mb-4">
            <h4 className="font-semibold mb-2">Users to be Kicked Out</h4>
            <ul className="list-disc list-inside">
              {community.users_to_be_kicked_out.map((user, index) => (
                <li key={index}>{user}</li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Recent Actions</h4>
            <ul className="space-y-2">
              {community.actions.slice(0, 5).map((action, index) => (
                <li key={index} className="bg-gray-700 p-2 rounded">
                  <p className="text-sm text-gray-300">{action.timestamp}</p>
                  <p><span className="font-semibold">{action.username}</span>: {action.message}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
};
