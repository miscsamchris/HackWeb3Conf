"use client";
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import logoImg from '../../assets/images/Telegage_logo.png';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Bell, LogOut, MessageSquare, Award, Zap, Users, Activity, User, Heart, Wallet, Copy, CodeSquare, ImageIcon, Minus, Plus, UserPlus, Trash2 } from 'lucide-react';
import NFTPackForm  from '@/components/NFTPackForm';
import AddNFTPackModal from '@/components/AddNFTPackModal';
import NFTPacksDisplay from '@/components/NFTPacksDisplay';
import { format, parseISO } from 'date-fns';
import React from 'react';

interface Community {
  _id: string;
  community_id: string;
  community_name: string;
  community_description: string;
  users: any[];
  title: string;  // Add this line
  memberCount: number;  // Add this line if it's used in the Communities component
}

interface Stats {
  number_of_messages: string;
  number_of_nfts_minted: string;
  points_earned: string;
  actions: Array<{
    message: string;
    timestamp: string;
    username: string;
  }>;
  users_to_be_kicked_out: UserToKick[];
}

interface ChartDataPoint {
  timestamp: Date;
  points: number;
  users: number;
  nfts: number;
}

const mockChartData = [
  { name: 'Jan', messages: 400, points: 240, nfts: 20 },
  { name: 'Feb', messages: 300, points: 139, nfts: 15 },
  { name: 'Mar', messages: 200, points: 980, nfts: 30 },
  { name: 'Apr', messages: 278, points: 390, nfts: 25 },
  { name: 'May', messages: 189, points: 480, nfts: 18 },
  { name: 'Jun', messages: 239, points: 380, nfts: 22 },
];


const CommunityStats = ({ stats }: { stats: Stats }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg flex items-center">
      <MessageSquare className="text-pink-500 w-8 h-8 mr-4" />
      <div>
        <h3 className="text-lg font-semibold mb-2 text-white/70">Messages</h3>
        <p className="text-3xl font-bold bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-transparent bg-clip-text">{stats.number_of_messages}</p>
      </div>
    </div>
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg flex items-center">
      <Award className="text-purple-500 w-8 h-8 mr-4" />
      <div>
        <h3 className="text-lg font-semibold mb-2 text-white/70">NFTs Minted</h3>
        <p className="text-3xl font-bold bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-transparent bg-clip-text">{stats.number_of_nfts_minted}</p>
      </div>
    </div>
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg flex items-center">
      <Zap className="text-indigo-500 w-8 h-8 mr-4" />
      <div>
        <h3 className="text-lg font-semibold mb-2 text-white/70">Points Earned</h3>
        <p className="text-3xl font-bold bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-transparent bg-clip-text">{stats.points_earned}</p>
      </div>
    </div>
  </div>
);

const CommunityInfo = ({ community }: { community: Community }) => (
  <div className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8 hover:shadow-xl transition-shadow duration-300">
    <div className="flex flex-row justify-center items-center mb-4">
      <h2 className="text-2xl font-bold text-white mr-4">Community Name:</h2>
      <h2 className="text-3xl font-bold bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-transparent bg-clip-text">
        {community.community_name}
      </h2>
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <div className="bg-gray-700 p-4 rounded-lg flex items-center">
        <Activity className="text-pink-500 w-8 h-8 mr-4" />
        <div>
          <h3 className="text-lg font-semibold mb-1 text-white/80">Community ID</h3>
          <p className="text-xl font-bold bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-transparent bg-clip-text">
            {community.community_id}
          </p>
        </div>
      </div>
      <div className="bg-gray-700 p-4 rounded-lg flex items-center">
        <Users className="text-purple-500 w-8 h-8 mr-4" />
        <div>
          <h3 className="text-lg font-semibold mb-1 text-white/80">Total Members</h3>
          <p className="text-xl font-bold bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-transparent bg-clip-text">
            {community.users.length}
          </p>
        </div>
      </div>
    </div>
    <div className="bg-gray-700 p-4 rounded-lg">
      <h3 className="text-lg font-semibold mb-2 text-white/80">Description </h3>
      <p className="text-white/80 leading-relaxed">{community.community_description}</p>
    </div>
  </div>
);


interface ChartDataPoint {
  timestamp: Date;
  points: number;
  users: number;
  nfts: number;
}
const ActivityChart = ({ actions, userCount }: { actions: Stats['actions'], userCount: number }) => {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

  useEffect(() => {
    const processedData = actions.reduce((acc: ChartDataPoint[], action, index) => {
      const timestamp = parseISO(action.timestamp);
      let pointChange = 0;
      let nftChange = 0;
      let userChange = 0;

      if (action.message.includes('awarded')) {
        pointChange = parseInt(action.message.match(/\d+/)?.[0] || '0', 10);
      } else if (action.message.includes('deducted')) {
        // Extract only the points deducted, not the user ID
        const match = action.message.match(/deducted (\d+) points/);
        if (match) {
          pointChange = -parseInt(match[1], 10);
        }
      } else if (action.message.includes('Minted')) {
        nftChange = 1;
      } else if (action.message.includes('joined the Community')) {
        userChange = 1;
      }

      const lastPoint = acc[acc.length - 1] || { points: 0, users: 0, nfts: 0 };
      acc.push({
        timestamp,
        points: lastPoint.points + pointChange,
        users: Math.min(lastPoint.users + userChange, userCount), // Ensure users don't exceed total
        nfts: lastPoint.nfts + nftChange
      });

      return acc;
    }, []);

    setChartData(processedData);
  }, [actions, userCount]);

  console.log("chartData:", chartData);

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8">
      <h2 className="text-2xl font-bold mb-4 text-white flex items-center">
        <Activity className="text-purple-500 w-6 h-6 mr-2" />
        Activity Overview
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis 
            dataKey="timestamp" 
            stroke="#888" 
            tickFormatter={(timestamp) => format(new Date(timestamp), 'MMM dd')}
          />
          <YAxis 
            stroke="#888"
            yAxisId="left"
            domain={['auto', 'auto']} // This allows for negative values
            tickFormatter={(value) => {
              if (Math.abs(value) >= 1000000) {
                return `${(value / 1000000).toFixed(1)}M`;
              } else if (Math.abs(value) >= 1000) {
                return `${(value / 1000).toFixed(1)}k`;
              }
              return value;
            }}
          />
          <YAxis 
            stroke="#888"
            yAxisId="right"
            orientation="right"
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#333', border: 'none' }}
            labelFormatter={(value) => format(new Date(value), 'MMM dd, yyyy HH:mm:ss')}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="points" 
            stroke="#8884d8" 
            strokeWidth={2}
            dot={false} 
            name="Points" 
            yAxisId="left"
          />
          <Line 
            type="monotone" 
            dataKey="users" 
            stroke="#82ca9d" 
            strokeWidth={2}
            dot={false} 
            name="Users" 
            yAxisId="right"
          />
          <Line 
            type="monotone" 
            dataKey="nfts" 
            stroke="#ffc658" 
            strokeWidth={2}
            dot={false} 
            name="NFTs" 
            yAxisId="right"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};


const RecentActivity = ({ actions }: { actions: Stats['actions'] }) => {
  const getActionIcon = (message: string) => {
    if (message.includes('deducted')) return <Minus className="text-red-500 w-6 h-6" />;
    if (message.includes('awarded')) return <Plus className="text-green-500 w-6 h-6" />;
    if (message.includes('Minted')) return <ImageIcon className="text-purple-500 w-6 h-6" />;
    if (message.includes('joined')) return <UserPlus className="text-blue-500 w-6 h-6" />;
    if (message.includes('Kicked')) return <Trash2 className="text-red-500 w-6 h-6" />;
    return <Activity className="text-blue-500 w-6 h-6" />;
  };

  const getActionColor = (message: string) => {
    if (message.includes('deducted')) return 'bg-red-900/30';
    if (message.includes('awarded')) return 'bg-green-900/30';
    if (message.includes('Minted')) return 'bg-purple-900/30';
    if (message.includes('joined')) return 'bg-blue-900/30';
    if (message.includes('kicked')) return 'bg-red-900/30';
    return 'bg-blue-900/30';
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8">
      <h2 className="text-2xl font-bold mb-4 text-white flex items-center">
        <Bell className="text-pink-500 w-6 h-6 mr-2" />
        Recent Activity
      </h2>
      <div className="max-h-80 overflow-y-auto">
        <ul className="space-y-4">
          {actions.slice().reverse().map((activity, index) => (
            <li key={index} className={`flex items-center p-3 rounded-lg ${getActionColor(activity.message)}`}>
              <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center mr-4">
                {getActionIcon(activity.message)}
              </div>
              <div className="flex-grow">
                <p className="text-white">{activity.message}</p>
                <p className="text-sm text-white/70">{format(new Date(activity.timestamp), 'PPpp')}</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center ml-4">
                <User className="text-white w-6 h-6" />
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

interface UserToKick {
  timestamp: string;
  username: string;
  user_id: string;
}

const UsersToBeKickedOut = ({ users, communityId }: { users: UserToKick[], communityId: string }) => {
  const handleKickUser = async (user: UserToKick) => {
    try {
      const response = await fetch('https://tegegageapplication.onrender.com/kick_user_from_community', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          telegram_channel_username: communityId,
          user_name: user.user_id,
        }),
      });
      console.log("body to kick out:", JSON.stringify({
        telegram_channel_username: communityId,
        user_name: user.user_id,
      }));

      if (response.ok) {
        console.log(`User ${user.username} kicked out successfully`);
        // You might want to update the UI or refetch the users list here
      } else {
        console.error('Failed to kick out user');
      }
    } catch (error) {
      console.error('Error kicking out user:', error);
    }
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8">
      <h2 className="text-2xl font-bold mb-4 text-white flex items-center">
        <Users className="text-red-500 w-6 h-6 mr-2" />
        Users to be Kicked Out
      </h2>
      <ul className="space-y-2">
        {users.map((user, index) => (
          <li key={index} className="bg-gray-700 p-2 rounded-lg text-white flex justify-between items-center">
            <div>
              <span>{user.username}</span>
              <span className="text-sm text-gray-400 ml-2">({user.user_id})</span>
            </div>
            <button
              onClick={() => handleKickUser(user)}
              className="bg-red-500 hover:bg-red-600 text-white p-2 rounded-full transition duration-300"
              title="Kick out user"
            >
              <Trash2 size={16} />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default function DashboardPage() {
  const [username, setUsername] = useState('');
  const [walletAddress, setWalletAddress] = useState('');
  const [communities, setCommunities] = useState<Community[]>([]);
  const [hasCommunity, setHasCommunity] = useState(false);
  const [communityStats, setCommunityStats] = useState<Stats | null>(null);
  const router = useRouter();
  const [isNFTPackModalOpen, setIsNFTPackModalOpen] = useState(false);
  const [showNFTs, setShowNFTs] = useState(false);
  const [isCommunityLoading, setIsCommunityLoading] = useState(true);

  const fetchCommunities = useCallback(async () => {
    try {
      const { walletAddress } = JSON.parse(localStorage.getItem('user') || '{}');
      const response = await fetch('https://telegage-server.onrender.com/api/communities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ walletAddress }),
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      
      if (Array.isArray(data)) {
        setCommunities(data);
        setHasCommunity(data.length > 0);
        if (data.length > 0) fetchCommunityStats(data[0].id);
        setIsCommunityLoading(false);
      } else {
        console.error('Fetched communities data is not an array:', data);
        setCommunities([]);
        setHasCommunity(false);
      }
    } catch (error) {
      console.error('Error fetching communities:', error);
      setCommunities([]);
      setHasCommunity(false);
    }
  }, []);

  const fetchCommunityStats = async (communityId: number) => {
    try {
      const { walletAddress } = JSON.parse(localStorage.getItem('user') || '{}');
      const response = await fetch('https://telegage-server.onrender.com/api/community-stats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ walletAddress, communityId }),
      });
      const data = await response.json();
      console.log("Community Statsssssssssss:", data);
      setCommunityStats(data.Stats);
    } catch (error) {
      console.error('Error fetching community stats:', error);
    }
  };

  useEffect(() => {
    const user = localStorage.getItem('user');
    setIsCommunityLoading(true);
    if (!user) {
      router.push('/auth');
    } else {
      const { username, has_community, walletAddress } = JSON.parse(user);
      setUsername(username);
      setWalletAddress(walletAddress);
      setHasCommunity(has_community);
      fetchCommunities();
    }
  }, [router, walletAddress, fetchCommunities]);

  const handleNFTPackSubmit = async (formData: any) => {
    console.log("Dashboard - Received form data:", JSON.stringify(formData));
  
    try {
      // Assuming communities is an array and the first community's id should be used
      const communityId = communities[0]?.community_id;
      if (!communityId) {
        throw new Error('No community found');
      }

      console.log("Dashboard - Community ID:", communityId);

      const formDataWithCommunityId = { ...formData, community_id: communityId.toString() };
      console.log("nft - Form data with community ID:", JSON.stringify(formDataWithCommunityId));

      const response = await fetch('https://telegage-server.onrender.com/api/create-nft-pack', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formDataWithCommunityId),
      });
      console.log("Response status:", response.status);
      if (response.ok) {
        const result = await response.json();
        console.log("NFT Pack created successfully:", result);
        // Handle success (e.g., show a success message, update UI)
      } else {
        console.error('Failed to create NFT Pack');
        // Handle error (e.g., show error message to user)
      }
    } catch (error) {
      console.error('Error creating NFT Pack:', error);
      // Handle error (e.g., show error message to user)
    }
  };

  return (
    <div className="bg-black text-white min-h-screen bg-[linear-gradient(to_bottom,#000,#200D42_34%,#4F21A1_65%,#A45EDB_82%)]">
      <header className="bg-gray-900 p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center">
            <Image src={logoImg} alt="TeleGage Logo" width={40} height={40} />
            <h1 className="text-2xl font-bold ml-2">TeleGage Dashboard</h1>
          </div>
          <div className="flex items-center space-x-4">
           
            <div className="flex items-center bg-gray-800 rounded-full px-3 py-2 hover:bg-gray-700 transition-colors duration-300">
              <Wallet size={18} className="mr-2 text-gray-300" />
              <span className="text-sm font-medium truncate max-w-[150px] text-gray-200">{walletAddress}</span>
              <button 
                onClick={() => navigator.clipboard.writeText(walletAddress)}
                className="ml-2 text-gray-400 hover:text-gray-200 focus:outline-none"
                title="Copy wallet address"
              >
                <Copy size={14} />
              </button>
            </div>
            <button 
              onClick={() => {
                localStorage.removeItem('user');
                router.push('/auth');
              }}
              className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white p-2 rounded-full hover:opacity-90 transition duration-300"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {isCommunityLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-primary"></div>
            </div>
          ) : (
            <>
              {!hasCommunity && (
                <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4 mb-8">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => router.push('/create_community')}
                    className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-3 px-6 rounded-lg hover:opacity-90 transition duration-300"
                  >
                    Create Your Community
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => router.push('/import_community')}
                    className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-3 px-6 rounded-lg hover:opacity-90 transition duration-300"
                  >
                    Import Your Community
                  </motion.button>
                </div>
              )}
              
              {hasCommunity && communityStats && (
                <>
                  <CommunityInfo community={communities[0]} />
                  <CommunityStats stats={communityStats} />
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <ActivityChart actions={communityStats.actions} userCount={communities[0]?.users.length || 0} />
                    <RecentActivity actions={communityStats.actions} />
                  </div>
                  {communityStats.users_to_be_kicked_out.length > 0 && (
                    <UsersToBeKickedOut 
                      users={communityStats.users_to_be_kicked_out} 
                      communityId={communities[0]?.community_id}
                    />
                  )}
                  <div className="mt-8 flex space-x-4">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setIsNFTPackModalOpen(true)}
                      className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:opacity-90 transition-all duration-300"
                    >
                      Add NFT Pack
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setShowNFTs(!showNFTs)}
                      className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:opacity-90 transition-all duration-300"
                    >
                      {showNFTs ? 'Hide NFTs' : 'Display NFTs'}
                    </motion.button>
                  </div>
                  <AddNFTPackModal
                    isOpen={isNFTPackModalOpen}
                    onClose={() => setIsNFTPackModalOpen(false)}
                    onSubmit={handleNFTPackSubmit}
                  />
                  {showNFTs && <NFTPacksDisplay communityId={communities[0]?.community_id}/>}
                </>
              )}
            </>
          )}
        </motion.div>
      </main>
    </div>
  );
}