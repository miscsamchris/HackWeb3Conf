import { NextRequest, NextResponse } from 'next/server';
import { MongoClient } from 'mongodb';

// IMPORTANT: In a real application, use environment variables for sensitive information
const uri = "<Add MongoDB URL for test database here>";

export async function GET(request: NextRequest) {
  const client = new MongoClient(uri, {
    serverSelectionTimeoutMS: 5000,
  });

  try {
    await client.connect();
    console.log("Connected to MongoDB successfully");

    const db = client.db('test');
    const coll = db.collection('nftpacks');
    console.log("Collection selected successfully");

    const nftPacks = await coll.find({}).toArray();

    return NextResponse.json(nftPacks, { status: 200 });
  } catch (error) {
    console.error('Error fetching NFT packs:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  } finally {
    await client.close();
  }
}