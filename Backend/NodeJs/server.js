const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const mongoose = require('mongoose');
const crypto = require('crypto'); // Import Node.js crypto module
require('dotenv').config();
const { MongoClient } = require('mongodb');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(bodyParser.json());

// Create connections to both databases
const telegramCommunitiesConnection = mongoose.createConnection("<Add MongoDB URL for telegram_communities database here>");
const testConnection = mongoose.createConnection("<Add MongoDB URL for test database here>");

// User model (in test database)
const UserSchema = new mongoose.Schema({
  username: { type: String, unique: true, required: true },
  password: { type: String, required: true },
  walletAddress: { type: String, unique: true, sparse: true },
  has_community: { type: Boolean, default: false }
});

const User = testConnection.model('User', UserSchema);

// Community User model (in telegram_communities database)
const CommunityUserSchema = new mongoose.Schema({
  user_id: { type: String, required: true },
  user_name: { type: String },
  name: { type: String },
  TeleTokens_CustodialAddress: { type: String },
  data: { type: String },
  community_name: { type: String }
});

const CommunityUser = telegramCommunitiesConnection.model('CommunityUser', CommunityUserSchema, 'community_users');

// Community model (in telegram_communities database)
const CommunitySchema = new mongoose.Schema({
  _id: { type: String },
  category: { type: String },
  community_description: { type: String },
  community_id: { type: String },
  community_instructions: { type: String },
  community_name: { type: String },
  community_rules: { type: String },
  owner_id: { type: String },
  stats: { type: String },
  topics: [{ type: String }],
  users: [{ type: String }]
});

const Community = telegramCommunitiesConnection.model('Community', CommunitySchema, 'communities');

// NFT Pack model (in test database)
const NFTPackSchema = new mongoose.Schema({
  title: { type: String, required: true },
  price: { type: Number, required: true },
  id: { type: Number, unique: true },
  negative: { type: String },
  keywords: { type: String },
  imageUrl: { type: String },
  altText: { type: String },
  community_id: { type: String }
});

const NFTPack = testConnection.model('NFTPack', NFTPackSchema);

// Decryption function using Node.js crypto module
function decrypt(key, source, decode = true) {
  if (decode) {
    source = Buffer.from(source, 'base64');
  }

  const keyBuffer = crypto.createHash('sha256').update(key).digest();
  const iv = source.slice(0, 16);
  const encryptedText = source.slice(16);

  const decipher = crypto.createDecipheriv('aes-256-cbc', keyBuffer, iv);
  let decrypted = decipher.update(encryptedText);
  decrypted = Buffer.concat([decrypted, decipher.final()]);

  // Handle padding
  const padding = decrypted[decrypted.length - 1];
  if (padding > 0 && padding <= 16) {
    const padded = decrypted.slice(-padding);
    if (padded.equals(Buffer.alloc(padding, padding))) {
      decrypted = decrypted.slice(0, -padding);
    }
  }

  return decrypted.toString('utf8');
}

// Signup route
app.post('/api/signup', async (req, res) => {
  try {
    const { username, password, walletAddress } = req.body;
    if (!username || !password || !walletAddress) {
      return res.status(400).json({ message: 'All fields are required' });
    }
    const user = new User({ username, password, walletAddress });
    await user.save();
    res.status(201).json({ message: 'User created successfully' });
    console.log("User created successfully", user);
  } catch (error) {
    res.status(500).json({ message: 'Error creating user', error: error.message });
    console.error("Error creating user", error);
  }
});


app.get('/api/list-databases', async (req, res) => {
  try {
    const adminDb = mongoose.connection.useDb('admin');
    const result = await adminDb.db.admin().listDatabases();
    const databases = result.databases.map(db => db.name);
    const databaseCount = databases.length;
    res.json({
      count: databaseCount,
      databases: databases
    });
  } catch (error) {
    console.error('Error listing databases:', error);
    res.status(500).json({ message: 'Error listing databases', error: error.message });
  }
});

// Login route
app.post('/api/login', async (req, res) => {
  try {
    const { username, password, walletAddress } = req.body;
    let user;

    if (walletAddress) {
      user = await User.findOne({ walletAddress });
    } else if (username && password) {
      user = await User.findOne({ username });
      if (user && user.password !== password) {
        user = null;
      }
    } else {
      return res.status(400).json({ message: 'Invalid login credentials' });
    }

    if (!user) {
      return res.status(400).json({ message: 'User not found or invalid credentials' });
    }

    res.json({
      message: 'Login successful',
      userId: user._id,
      username: user.username,
      walletAddress: user.walletAddress,
      has_community: user.has_community
    });
    console.log("Login successful", user);
  } catch (error) {
    res.status(500).json({ message: 'Error logging in', error: error.message });
    console.error("Error logging in", error);
  }
});

// Fetch NFT Packs route
// app.get('/api/nft-packs', async (req, res) => {
//   try {
//     const nftPacks = await NFTPack.find();
//     res.json(nftPacks);
//   } catch (error) {
//     res.status(500).json({ message: 'Error fetching NFT packs', error: error.message });
//     console.error("Error fetching NFT packs", error);
//   }
// });

app.get('/api/nft-superpacks', async (req, res) => {
  try {
    const client = new MongoClient("<Add MongoDB URL for test database here>", {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    await client.connect();

    const coll = client.db('test').collection('superpack');
    const cursor = coll.find({});
    const nftPacks = await cursor.toArray();
    res.json(nftPacks);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching NFT packs', error: error.message });
    console.error("Error fetching NFT packs", error);
  }
});

// New route to fetch community user data
app.get('/api/community-user/:userId', async (req, res) => {
  try {
    const userId = req.params.userId;
    console.log('Searching for user with ID:', userId);

    const user = await CommunityUser.findOne(
      { user_id: userId },
      'TeleTokens_CustodialAddress data'
    );

    if (!user) {
      console.log('User not found:', userId);
      return res.status(404).json({ message: 'User not found' });
    }

    res.json({
      custodialAddress: user.TeleTokens_CustodialAddress,
      data: user.data
    });
  } catch (error) {
    res.status(500).json({ message: 'Error fetching community user data', error: error.message });
    console.error("Error fetching community user data", error);
  }
});

// Fetch all community users
app.get('/api/community-users', async (req, res) => {
  try {
    const communityUsers = await CommunityUser.find();
    res.json(communityUsers);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching community users', error: error.message });
    console.error("Error fetching community users", error);
  }
});

// New route to decrypt user data
app.get('/api/decrypt-user-data/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const key = userId; // Replace with your actual secret key

    // Fetch the community user data
    const user = await CommunityUser.findOne({ user_id: userId });

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Decrypt the data
    const decryptedData = decrypt(key, user.data);

    res.json({
      decryptedData
    });
  } catch (error) {
    res.status(500).json({ message: 'Error decrypting user data', error: error.message });
    console.error("Error decrypting user data", error);
  }
});

// New route to update user's has_community field
app.post('/update_user_community_status', async (req, res) => {
  try {
    const { walletAddress, has_community } = req.body;

    const user = await User.findOneAndUpdate(
      { walletAddress },
      { has_community },
      { new: true }
    );

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json({ message: 'User community status updated successfully', user });
  } catch (error) {
    res.status(500).json({ message: 'Error updating user community status', error: error.message });
    console.error("Error updating user community status", error);
  }
});

// New route to fetch communities for a wallet address
// New route to fetch communities for a wallet address
app.post('/api/communities', async (req, res) => {
  try {
    const client = new MongoClient("<Add MongoDB URL for telegram_communities database here>", {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    await client.connect();

    const { walletAddress } = req.body;
    console.log("Fetching communities for walletAddress:", walletAddress);
    const coll = client.db('telegram_communities').collection('telegram_community');
    const cursor = coll.find({ owner_id: walletAddress });
    const communities = await cursor.toArray();

    console.log("Communitiesss:", communities);

    if (!communities || communities.length === 0) {
      console.log("No communities found for walletAddress:", walletAddress);
      return res.json([]); // Return an empty array instead of 404
    }

    const formattedCommunities = communities.map(community => ({
      _id: community._id,
      community_name: community.community_name,
      category: community.category,
      community_description: community.community_description,
      community_rules: community.community_rules,
      community_instructions: community.community_instructions,
      community_id: community.community_id,
      topics: community.topics,
      owner_id: community.owner_id,
      users: community.users,
      stats: community.stats
    }));

    res.json(formattedCommunities);
  } catch (error) {
    console.error("Error in /api/communities:", error);
    res.status(500).json({
      message: 'Error fetching communities',
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

// New route to fetch community stats
app.post('/api/community-stats', async (req, res) => {
  try {
    const { walletAddress } = req.body;
    console.log("Fetching community stats for walletAddress:", walletAddress);

    // Attempt to connect to MongoDB
    const client = new MongoClient("<Add MongoDB URL for telegram_communities database here>", {
      serverSelectionTimeoutMS: 5000, // 5 second timeout
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    await client.connect();
    console.log("Connected to MongoDB successfully");

    const coll = client.db('telegram_communities').collection('telegram_community');
    const cursor = coll.find({ owner_id: walletAddress });
    const result = await cursor.toArray();

    if (result.length === 0) {
      console.log("No community found for walletAddress:", walletAddress);
      return res.status(404).json({ message: 'No community found for this wallet address' });
    }

    const communityId = result[0].community_id;
    console.log("Found communityId:", communityId);

    // Make a request to the external API to fetch community stats
    const response = await fetch('https://tegegageapplication.onrender.com/get_stats_by_community', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ telegram_channel_id: communityId }),
    });

    if (!response.ok) {
      throw new Error(`External API responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Received data from external API:", data);

    await client.close();
    res.json(data);
  } catch (error) {
    console.error("Error in /api/community-stats:", error);
    res.status(500).json({
      message: 'Error fetching community stats',
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

app.post('/api/create-nft-pack', async (req, res) => {
  try {
    console.log("Server - Received NFT Pack data:", JSON.stringify(req.body, null, 2));
    const { title, price, negative, keywords, imageUrl, altText, community_id } = req.body;
    if (!title || !price) {
      console.log("Missing required fields");
      return res.status(400).json({ message: 'Missing required fields' });
    }
    const newNFTPack = new NFTPack({
      title,
      price,
      id: Date.now(), // Generate a unique ID
      negative,
      keywords,
      imageUrl,
      altText,
      community_id
    });
    console.log("New NFT Pack:", JSON.stringify(newNFTPack, null, 2));
    await newNFTPack.save();
    res.status(201).json({ message: 'NFT Pack created successfully', nftPack: newNFTPack });
  } catch (error) {
    console.error("Error creating NFT Pack:", error);
    res.status(500).json({ message: 'Error creating NFT Pack', error: error.message });
  }
});

app.post('/api/nft-packs', async (req, res) => {
  try {
    const { communityId } = req.body;
    if (!communityId) {
      return res.status(400).json({ message: 'Community ID is required' });
    }
    // Ensure communityId is treated as a string
    const nftPacks = await NFTPack.find({ community_id: communityId.toString() });
    res.json(nftPacks);
  } catch (error) {
    console.error("Error fetching NFT packs for community:", error);
    res.status(500).json({ message: 'Error fetching NFT packs for community', error: error.message });
  }
});

// // Initialize NFT Packs
// async function initializeNFTPacks() {
//   const nftData = [
//     { 
//       title: "Good Pack", 
//       price: 50, 
//       id: 1, 
//       negative: "Evil Expression, Scowl, Frown, No beard,Sarcastic Smile,blurry images", 
//       keywords: "Cartoon, Exagerated,Handsome, Beautiful, Detailed Animation, Animated, No Background, Black Background, Happy, Long hair, Always bearded",
//       imageUrl: "https://res.cloudinary.com/dkewhgebd/image/upload/v1724837797/copsdqwxvevwbkvll2hy.jpg",
//       altText: "Good Pack NFT"
//     },
//     { 
//       title: "Evil Pack", 
//       price: 50, 
//       id: 2, 
//       negative: "Good Expression, Smile, blurry images", 
//       keywords: "Evil ,Cartoon, Exagerated,Handsome, Beautiful, Detailed Animation, Animated, No Background, Black Background, Happy, Long hair, Always bearded, Sarcastic smile",
//       imageUrl: "https://res.cloudinary.com/dkewhgebd/image/upload/v1724837806/qhyaseccdm25i8zhqsc8.jpg",
//       altText: "Evil Pack NFT"
//     },
//     {
//       "title": "Prince Pack",
//       "price": 50,
//       "id": 5,
//       "negative": "Princess elements, feminine features, blurry images, realistic, photograph",
//       "keywords": "Cartoon sticker, handsome prince character, royal attire, crown, sword, noble pose, charming smile, detailed 2D animation style, fairytale castle background, no background option, transparent, vibrant colors, heroic gestures, majestic aura",
//       "imageUrl": "https://res.cloudinary.com/dkewhgebd/image/upload/v1724932864/azbycespmcz7szyralcm.jpg",
//       "altText": "Prince Pack NFT Sticker"
//     },
//     {
//       "title": "Princess Pack",
//       "price": 50,
//       "id": 6,
//       "negative": "Prince elements, masculine features, blurry images, realistic, photograph",
//       "keywords": "Cartoon sticker, beautiful princess character, elegant gown, tiara, graceful pose, enchanting smile, detailed 2D animation style, fairytale castle background, no background option, transparent, pastel color palette, regal gestures, magical aura",
//       "imageUrl": "https://res.cloudinary.com/dkewhgebd/image/upload/v1724932864/mppucn34tpobdrrhwzc0.jpg",
//       "altText": "Princess Pack NFT Sticker"
//     },
//     {
//       "title": "Ethereum Pack",
//       "price": 50,
//       "id": 3,
//       "negative": "Bitcoin symbols, fiat currency, centralized systems, realistic photos, blurry images, confusion",
//       "keywords": "Cartoon sticker, Ethereum logo prominence, Black and White ,ETH symbol, cryptocurrency coin, blockchain visualization, smart contract illustration, decentralized network, animated ether particles, no background, transparent, vibrant blue and white palette, futuristic tech aesthetic, DeFi ecosystem symbols, gas fee representation, Ethereum 2.0 concept",
//       "imageUrl": "https://res.cloudinary.com/dkewhgebd/image/upload/v1724837803/jcqlnfvtjsvzlah4filf.jpg",
//       "altText": "Ethereum Cryptocurrency Sticker Pack"
//     },
//     {
//       "title": "Bitcoin Pack",
//       "price": 50,
//       "id": 4,
//       "negative": "Ethereum symbols, fiat currency, centralized banking, realistic photos, blurry images, bearish trends",
//       "keywords": "Cartoon sticker, Detailed animation,Gold,Bitcoin logo dominance, BTC symbol, cryptocurrency coin, blockchain structure, mining concept illustration, animated network connections, no background, transparent, vibrant orange and gold scheme, digital wallet visualization, halving event depiction, Lightning Network concept, bullish trend chart",
//       "imageUrl": "https://res.cloudinary.com/dkewhgebd/image/upload/v1724837804/bqmtrtvckxfqf4sad6aq.jpg",
//       "altText": "Bitcoin Cryptocurrency Sticker Pack"
//     }
//   ];


//   try {
//     for (const pack of nftData) {
//       await NFTPack.findOneAndUpdate({ id: pack.id }, pack, { upsert: true, new: true });
//     }
//     console.log("NFT Packs initialized successfully");
//   } catch (error) {
//     console.error("Error initializing NFT Packs:", error);
//   }
// }

// Connect to MongoDB and start the server
Promise.all([
  telegramCommunitiesConnection.asPromise(),
  testConnection.asPromise()
])
  .then(() => {
    console.log('Connected to MongoDB Atlas (telegram_communities and test databases)');
    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
  })
  .catch((err) => {
    console.error('Error connecting to MongoDB:', err);
  });