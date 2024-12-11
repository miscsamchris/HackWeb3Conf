from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    WebAppInfo,
    InputSticker,
    MenuButtonWebApp,
    MenuButton,    
    InputFile,
)
from telebot import types
import json
import requests
import os
from PIL import Image
import random
from pymongo import MongoClient
import os
from datetime import datetime

# from openai import OpenAI
import asyncio
import json
import time
import base64
import requests
from aptos_sdk.account import Account
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.aptos_cli_wrapper import AptosCLIWrapper
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.bcs import Serializer
from aptos_sdk.package_publisher import PackagePublisher
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionArgument,
    TransactionPayload,
    RawTransactionWithData,
    RawTransaction,
)
from aptos_sdk.aptos_token_client import (
    AptosTokenClient,
    Collection,
    Object,
    PropertyMap,
    Property,
    ReadObject,
    Token,
)
from aptos_sdk.type_tag import StructTag, TypeTag
import uuid
import requests
import shutil
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="<Add Azure OpenAI API Key here>",
    api_version="2024-02-15-preview",
    azure_endpoint="<Add Azure OpenAI Endpoint here>",
)
deployment_name = "<Add Azure OpenAI Deployment Name here>"
bot_token = "<Add Telegram Bot Token here>"

bot = AsyncTeleBot(bot_token, parse_mode=None)

APTOS_CORE_PATH = os.getenv(
    "APTOS_CORE_PATH",
    os.path.abspath("./aptos-core"),
)
FAUCET_URL = os.getenv(
    "APTOS_FAUCET_URL",
    "https://faucet.testnet.aptoslabs.com",
)
INDEXER_URL = os.getenv(
    "APTOS_INDEXER_URL",
    "https://api.testnet.aptoslabs.com/v1/graphql",
)
NODE_URL = os.getenv("APTOS_NODE_URL", "https://api.testnet.aptoslabs.com/v1")

from telebot.apihelper import get_chat_member


class CoinClient(RestClient):
    async def register_coin(self, coin_address: AccountAddress, sender: Account) -> str:
        """Register the receiver account to receive transfers for the new coin."""

        payload = EntryFunction.natural(
            "0x1::managed_coin",
            "register",
            [
                TypeTag(
                    StructTag.from_str(f"{coin_address}::telegage_token::TeleGageToken")
                )
            ],
            [],
        )
        signed_transaction = await self.create_bcs_signed_transaction(
            sender, TransactionPayload(payload)
        )
        return await self.submit_bcs_transaction(signed_transaction)

    async def mint_coin(
        self, minter: Account, receiver_address: AccountAddress, amount: int
    ) -> str:
        """Mints the newly created coin to a specified receiver address."""

        payload = EntryFunction.natural(
            "0x1::managed_coin",
            "mint",
            [
                TypeTag(
                    StructTag.from_str(
                        f"{minter.address()}::telegage_token::TeleGageToken"
                    )
                )
            ],
            [
                TransactionArgument(receiver_address, Serializer.struct),
                TransactionArgument(amount, Serializer.u64),
            ],
        )
        signed_transaction = await self.create_bcs_signed_transaction(
            minter, TransactionPayload(payload)
        )
        return await self.submit_bcs_transaction(signed_transaction)

    async def get_balance(
        self,
        coin_address: AccountAddress,
        account_address: AccountAddress,
    ) -> str:
        """Returns the coin balance of the given account"""

        balance = await self.account_resource(
            account_address,
            f"0x1::coin::CoinStore<{coin_address}::telegage_token::TeleGageToken>",
        )
        return balance["data"]["coin"]["value"]


rest_client = CoinClient(NODE_URL)
faucet_client = FaucetClient(FAUCET_URL, rest_client)
admin_wallet = Account.load("admin")
token_client = AptosTokenClient(rest_client)  # <:!:section_1b
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import json


def encrypt(key, source, encode=True):
    key = SHA256.new(
        key
    ).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data


def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(
        key
    ).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[: AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size :])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if (
        data[-padding:] != bytes([padding]) * padding
    ):  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding


import cloudinary
import cloudinary.uploader
import cloudinary.api

# Configure Cloudinary with your credentials
cloudinary.config(
    cloud_name="<Add Cloudinary Cloud Name here>",  # Replace with your Cloudinary Cloud Name
    api_key="<Add Cloudinary API Key here>",  # Replace with your Cloudinary API Key
    api_secret="<Add Cloudinary API Secret here>",  # Replace with your Cloudinary API Secret
    secure=True,
)


def upload_to_cloudinary(image_path, public_id):
    try:
        # Upload the image to Cloudinary
        response = cloudinary.uploader.upload(image_path, public_id=public_id)
        # Return the URL of the uploaded image
        return response["secure_url"]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "<Add mongodb url here>"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client["telegram_communities"]


dbname = get_database()
community_collection = dbname["telegram_community"]
topics_collection = dbname["community_topics"]
users_collection = dbname["community_users"]


# :!:>section_6
async def get_collection_data(
    token_client: AptosTokenClient, collection_addr: AccountAddress
) -> dict[str, str]:
    collection = (await token_client.read_object(collection_addr)).resources[Collection]
    return {
        "creator": str(collection.creator),
        "name": str(collection.name),
        "description": str(collection.description),
        "uri": str(collection.uri),
    }  # <:!:section_6


# :!:>get_token_data
async def get_token_data(
    token_client: AptosTokenClient, token_addr: AccountAddress
) -> dict[str, str]:
    token = (await token_client.read_object(token_addr)).resources[Token]
    return {
        "collection": str(token.collection),
        "description": str(token.description),
        "name": str(token.name),
        "uri": str(token.uri),
        "index": str(token.index),
    }  # <:!:get_token_data


async def modify_tokens(user_id, community_id, action, amount):
    """Modify the TeleToken Balance of the User. This is an tool that needs to be used to update a users Token Balance"""
    user = users_collection.find_one({"user_id": user_id, "community_id": community_id})
    community = community_collection.find_one({"community_id": community_id})
    stats = community["stats"]
    if user == None:
        user_account = Account.generate()
        try:
            await faucet_client.fund_account(user_account.address(), 20_000_000)
        except:
            await faucet_client.fund_account(user_account.address(), 20_000_000)
        updateddata = str(user_account.private_key)
        print(user_account.account_address)
        encrypted = encrypt(str(user_id).encode(), updateddata.encode())
        print(encrypted)
        result = get_chat_member(bot_token, int(community_id), int(user_id))
        print(result)
        user_item = {
            "_id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "user_name": result.get("user", dict()).get("username", "NA"),
            "name": result.get("user", dict()).get("first_name", "NA"),
            "TeleTokens_CustodialAddress": str(user_account.account_address),
            "data": str(encrypted),
            "community_id": community_id,
        }
        txn_hash = await rest_client.register_coin(admin_wallet.address(), user_account)
        await rest_client.wait_for_transaction(txn_hash)
        txn_hash = await rest_client.mint_coin(
            admin_wallet, user_account.address(), 1000
        )
        await rest_client.wait_for_transaction(txn_hash)
        generated_id = users_collection.insert_one(user_item).inserted_id
        community_collection.update_one(
            {"community_id": community_id}, {"$push": {"users": generated_id}}
        )
        community_collection.update_one(
        {"community_id": str(community_id)},
        {
            "$push": {
                "stats.actions": {
                    "timestamp": str(datetime.now()),
                    "username": str(result.get("user", dict()).get("username", "NA")),
                    "message": f"{result.get('user', dict()).get('username', 'NA')} has joined the Community",
                }
            }
        },
        )
        balance = await rest_client.get_balance(
            admin_wallet.address(), user_account.address()
        )
        print(f"Account for user : initial TeleGage balance: {balance}")
        if community!=None:
            thread_id=int(community.get("activities_id",0))
            await bot.send_message(int(community_id),f"{result.get('user', dict()).get('username', 'NA')} has joined the Community",message_thread_id=thread_id)
            
    user = users_collection.find_one({"user_id": user_id, "community_id": community_id})
    print(user)
    data = decrypt(str(user_id).encode(), user.get("data"))
    print(data.decode())
    my_account = Account.load_key(data.decode())
    if action.lower() == "deduct":
        balance = await rest_client.get_balance(
            admin_wallet.address(), my_account.address()
        )
        print(f"{user.get('user_name') }'s updated TeleGage balance: {balance}")
        new_balance = int(balance) - amount
        community_collection.update_one(
            {"community_id": community_id},
            {
                "$set": {
                    "stats.points_earned": str(int(stats.get("points_earned")) - amount)
                }
            },
        )
        community_collection.update_one(
            {"community_id": community_id},
            {
                "$push": {
                    "stats.actions": {
                        "timestamp": str(datetime.now()),
                        "username": str(user.get("user_name")),
                        "message": f"{user.get('user_name')} has been deducted {amount} points",
                    }
                }
            },
        )
        if community!=None:
            thread_id=int(community.get("activities_id",0))
            await bot.send_message(int(community_id),f"{user.get('user_name')} has been deducted {amount} points",message_thread_id=thread_id)
        if new_balance < 0:
            to_transfer = amount + new_balance
            txn_hash = await rest_client.transfer_coins(
                my_account,
                admin_wallet.address(),
                f"{admin_wallet.address()}::telegage_token::TeleGageToken",
                to_transfer,
            )
            community_collection.update_one(
                {"community_id": community_id},
                {"$push": {"stats.users_to_be_kicked_out": {
                            "timestamp": str(datetime.now()),
                            "username": str(user.get("user_name")),
                            "user_id": str(user.get("user_id")),
                        }}},
            )
            community_collection.update_one(
                {"community_id": community_id},
                {
                    "$push": {
                        "stats.actions": {
                            "timestamp": str(datetime.now()),
                            "username": str(user.get("user_name")),
                            "message": f"{user.get('user_name')} has been marked as a user due for a ban",
                        }
                    }
                },
            )
            if community!=None:
                thread_id=int(community.get("activities_id",0))
                await bot.send_message(int(community_id),f"{user.get('user_name')} has been marked as a user due for a ban",message_thread_id=thread_id)
            await rest_client.wait_for_transaction(txn_hash)
        else:
            txn_hash = await rest_client.transfer_coins(
                my_account,
                admin_wallet.address(),
                f"{admin_wallet.address()}::telegage_token::TeleGageToken",
                amount,
            )
            await rest_client.wait_for_transaction(txn_hash)
    elif action.lower() == "award":
        txn_hash = await rest_client.mint_coin(
            admin_wallet, my_account.address(), amount
        )
        community_collection.update_one(
            {"community_id": community_id},
            {
                "$set": {
                    "stats.points_earned": str(int(stats.get("points_earned")) + amount)
                }
            },
        )
        community_collection.update_one(
            {"community_id": community_id},
            {
                "$push": {
                    "stats.actions": {
                        "timestamp": str(datetime.now()),
                        "username": str(user.get("user_name")),
                        "message": f"{user.get('user_name')} has been awarded {amount} points",
                    }
                }
            },
        )
        if community!=None:
            thread_id=int(community.get("activities_id",0))
            await bot.send_message(int(community_id),f"{user.get('user_name')} has been awarded {amount} points",message_thread_id=thread_id)
        await rest_client.wait_for_transaction(txn_hash)
    return "TeleTokens updated successfully"


async def invoke_ai(community_id, topic_id, message, user_id):
    print(community_id)
    community = community_collection.find_one({"community_id": str(community_id)})
    topic = topics_collection.find_one({"topic_id": topic_id})
    community_rules = community.get("community_instructions")
    if topic != None:
        topic_rules = topic.get("topic_instructions")
    else:
        topic_rules = community_rules
    print(topic_rules)
    messages = [
        {
            "role": "system",
            "content": f"""
                        You are a community manager bot for a community called {community.get("community_name")}. 
                        You are assigned the task of making sure that community members follow the overall community rules, Topic Specific Rules.
                        You should provide rewards to the users based on their message and the action that they do/follow.
                        You should also punish bad behaviour by dedcuting points from their token balance. 
                        Do not reply to the message. Your sole purpose is to award or deduct points.
                        ### Community Rules:
                        {community_rules}
                        
                        ### Topic Rules:
                        {topic_rules}
                        
                        ### User Interaction
                        User ID: "{user_id}"
                        Community ID: "{community_id}"
                        The user will now make a message. Use the tool modify_tokens to punsh or award them.
            """,
        },
        {
            "role": "user",
            "content": f""" User ID: {user_id} 
                            ### message: {message}""",
        },
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "modify_tokens",
                "description": "Modify the TeleToken Balance of the User. This is an tool that needs to be used to update a users Token Balance",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The User ID of the User that made the message",
                        },
                        "community_id": {
                            "type": "string",
                            "description": "The Community ID of the Community the user made the message.",
                        },
                        "action": {
                            "type": "string",
                            "enum": ["deduct", "award"],
                            "description": "The action to be performed on the user based on the message and rules.",
                        },
                        "amount": {
                            "type": "number",
                            "description": "The amount of tokens that needs to be either deducted or awarded. It must always be a positve number",
                        },
                    },
                    "required": ["user_id", "community_id", "action", "amount"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        tools=tools,
    )
    response_message = response.choices[0].message
    print(response_message)
    # Step 2: check if GPT wanted to call a function
    if response_message.tool_calls:
        print(response_message.content)
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "modify_tokens": modify_tokens,
        }  # only one function in this example, but you can have multiple
        function_name = response_message.tool_calls[0].function.name
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message.tool_calls[0].function.arguments)
        function_response = await fuction_to_call(
            user_id=function_args.get("user_id"),
            community_id=function_args.get("community_id"),
            action=function_args.get("action"),
            amount=function_args.get("amount"),
        )


def download_file(user_id, number, file_info, prompt, negative_prompt):
    file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_info}"
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        file_dir = f"./{user_id}"
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_path = f"{file_dir}/profile_pic_{user_id}_{number}.png"

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File saved to {file_path}")
        url = "https://87c1-35-247-188-138.ngrok-free.app/process_sticker"
        payload = {
            "negative_prompt": negative_prompt,
            "prompt": prompt,
        }
        files = [
            (
                "image",
                (
                    "myfile.jpg",
                    open(file_path, "rb"),
                    "image/jpeg",
                ),
            )
        ]
        headers = {}
        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files
        )
        with open(f"{file_dir}/new_{user_id}_{number}.png", "wb") as out_file:
            out_file.write(response.content)
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


@bot.message_handler(commands=["start", "redeem"])
async def redeemption(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    user_id = message.from_user.id
    user_accounts = users_collection.find({"user_id": str(user_id)})
    for user in user_accounts:
        community = community_collection.find_one(
            {"community_id": str(user.get("community_id"))}
        )
        print(user)
        if community!=None:
            print(community)
            markup.add(
                KeyboardButton(
                    f"{community.get('community_name')} Rewards",
                    web_app=WebAppInfo(
                        f"https://redeem-site.vercel.app/user/{user_id}/{community.get('community_id')}/"
                    ),
                )
            )
        print(
            f"https://redeem-site.vercel.app/user/{user_id}/{community.get('community_id')}/"
        )
    await bot.reply_to(
        message,
        "Hey There. You can use the following Rewards button to redeem your points",
        reply_markup=markup,
    )



@bot.message_handler(content_types=["new_chat_members"])
async def new_member_manager(message):
    new_user = message.new_chat_members[0]
    community_id = str(message.chat.id)
    if users_collection.find_one({"user_id": new_user.id, "community_id": community_id}) == None:
        user_account = Account.generate()
        try:
            await faucet_client.fund_account(user_account.address(), 20_000_000)
        except:
            await faucet_client.fund_account(user_account.address(), 20_000_000)
        updateddata = str(user_account.private_key)
        print(user_account.account_address)
        encrypted = encrypt(str(new_user.id).encode(), updateddata.encode())
        print(encrypted)
        user_item = {
            "_id": str(uuid.uuid4()),
            "user_id": str(new_user.id),
            "user_name": new_user.username,
            "name": f"{new_user.first_name if new_user.first_name!=None else '' } {new_user.last_name if new_user.last_name!=None else '' }",
            "TeleTokens_CustodialAddress": str(user_account.account_address),
            "data": str(encrypted),
            "community_id": community_id,
        }
        txn_hash = await rest_client.register_coin(admin_wallet.address(), user_account)
        await rest_client.wait_for_transaction(txn_hash)
        txn_hash = await rest_client.mint_coin(
            admin_wallet, user_account.address(), 1000
        )
        await rest_client.wait_for_transaction(txn_hash)
        user_id = users_collection.insert_one(user_item).inserted_id
        community_collection.update_one(
            {"community_id": community_id}, {"$push": {"users": user_id}}
        )
        community_collection.update_one(
        {"community_id": str(community_id)},
        {
            "$push": {
                "stats.actions": {
                    "timestamp": str(datetime.now()),
                    "username": str(new_user.username),
                    "message": f"{new_user.username} has joined the Community",
                }
            }
        },
        )
        community=community_collection.find_one({"community_id": str(community_id)})
        if community!=None:
            thread_id=int(community.get("activities_id",0))
            await bot.send_message(int(community_id),f"{new_user.username} has joined the Community",message_thread_id=thread_id)
        balance = await rest_client.get_balance(
            admin_wallet.address(), user_account.address()
        )
        print(f"Account for {new_user.username} : initial TeleGage balance: {balance}")


@bot.message_handler(func=lambda m: True)
async def moderate(message):
    # print(message)
    user_id = message.from_user.id
    chat_type=message.chat.type
    community_id=message.chat.id
    if chat_type=="supergroup":
        useronject=users_collection.find_one({"user_id": str(user_id), "community_id": str(community_id)})
        if useronject==None:
            user_account = Account.generate()
            try:
                await faucet_client.fund_account(user_account.address(), 20_000_000)
            except:
                await faucet_client.fund_account(user_account.address(), 20_000_000)
            updateddata = str(user_account.private_key)
            print(user_account.account_address)
            encrypted = encrypt(str(user_id).encode(), updateddata.encode())
            print(encrypted)
            result = get_chat_member(bot_token, int(community_id), int(user_id))
            print(result)
            user_item = {
                "_id": str(uuid.uuid4()),
                "user_id": str(user_id),
                "user_name": result.get("user", dict()).get("username", "NA"),
                "name": result.get("user", dict()).get("first_name", "NA"),
                "TeleTokens_CustodialAddress": str(user_account.account_address),
                "data": str(encrypted),
                "community_id": community_id,
            }
            txn_hash = await rest_client.register_coin(admin_wallet.address(), user_account)
            await rest_client.wait_for_transaction(txn_hash)
            txn_hash = await rest_client.mint_coin(
                admin_wallet, user_account.address(), 1000
            )
            await rest_client.wait_for_transaction(txn_hash)
            generated_id = users_collection.insert_one(user_item).inserted_id
            community_collection.update_one(
                {"community_id": community_id}, {"$push": {"users": generated_id}}
            )
            community_collection.update_one(
            {"community_id": str(community_id)},
            {
                "$push": {
                    "stats.actions": {
                        "timestamp": str(datetime.now()),
                        "username": str(result.get("user", dict()).get("username", "NA")),
                        "message": f"{result.get('user', dict()).get('username', 'NA')} has joined the Community",
                    }
                }
            },
            )
            balance = await rest_client.get_balance(
                admin_wallet.address(), user_account.address()
            )
            print(f"Account for user : initial TeleGage balance: {balance}")
            community=community_collection.find_one({"community_id": str(community_id)})
            if community!=None:
                thread_id=int(community.get("activities_id",0))
                await bot.send_message(int(community_id),f"{result.get('user', dict()).get('username', 'NA')} has joined the Community",message_thread_id=thread_id)
        user=await bot.get_chat_member(message.chat.id, user_id)
        if user.status!="creator":
            group_name = message.json.get("chat", {}).get("title", "Your Community")
            channel_id = message.json.get("chat", {}).get("id", "None")
            message_text = message.json.get("text", "None")
            community = community_collection.find_one({"community_id": str(channel_id)})
            # print(community)
            current_message_count = int(community["stats"]["number_of_messages"])
            new_message_count = current_message_count + 1
            print(new_message_count)
            community_collection.update_one(
                {"community_id": str(channel_id)},
                {"$set": {"stats.number_of_messages": str(new_message_count)}},
            )
            topic_id = 1
            if message.json.get("is_topic_message", False):
                topic_id = message.json.get("reply_to_message", {}).get("message_thread_id", 0)
            await invoke_ai(channel_id, topic_id, message_text, user_id)


@bot.message_handler(content_types=["web_app_data"])
async def web_app_data_manager(message):
    print(message.web_app_data.data)
    jsonObject = json.loads(message.web_app_data.data)
    await bot.send_message(message.chat.id, "Received The Data")
    user_id = message.from_user.id
    file_dir = f"./{user_id}"
    print(message)
    os.makedirs(file_dir, exist_ok=True)
    if jsonObject["action"] == "Add Sticker":
        pics = await bot.get_user_profile_photos(user_id)
        print(pics)
        user = users_collection.find_one({"user_id": str(user_id)})
        if user != None:
            data = decrypt(str(user_id).encode(), user.get("data"))
            print(data.decode())
            my_account = Account.load_key(data.decode())
            balance = await rest_client.get_balance(
                admin_wallet.address(), my_account.address()
            )
            print(f"{user.get('user_name')}'s updated Telegage balance: {balance}")
            txn_hash = await rest_client.transfer_coins(
                my_account,
                AccountAddress.from_str(
                    "0x23eb0d8f041a17f8060b017f0b75329d69a27a2b995e70cdeec3257583fbed80"
                ),
                f"{admin_wallet.address()}::telegage_token::TeleGageToken",
                jsonObject["price"],
            )
            balance = await rest_client.get_balance(
                admin_wallet.address(), my_account.address()
            )
            print(f"{user.get('user_name')}'s updated Telegage balance: {balance}")
            await rest_client.wait_for_transaction(txn_hash)
            if pics.total_count > 0:
                for id, pic in enumerate(pics.photos, start=1):
                    await bot.send_photo(
                        message.chat.id,
                        pic[-2].file_id,
                        caption="Profile Picture # " + str(id),
                    )
                    file_info = await bot.get_file(pic[-2].file_id)
                    download_file(
                        user_id,
                        id,
                        file_info.file_path,
                        jsonObject["prompt"],
                        jsonObject["negative_prompt"],
                    )
                sticker = InputSticker(
                    InputFile(f"{file_dir}/new_{user_id}_1.png"),
                    emoji_list=["🍩"],
                    format="static",
                )
                num = random.randrange(1, 10**4)
                num_with_zeros = "{:04}".format(num)
                await bot.create_new_sticker_set(
                    user_id,
                    f"mv_{num_with_zeros}_by_TeleGageCommunityBot",
                    "TeleGage Stickers",
                    stickers=[sticker],
                )
                print(
                    f"https://t.me/addstickers/mv_{num_with_zeros}_by_TeleGageCommunityBot"
                )

                txn_hash = await token_client.create_collection(
                    admin_wallet,
                    "TeleGage Stickers",
                    100,
                    f"TeleGage Stickers {num_with_zeros}",
                    "https://x.com/TeleGage_APT",
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    0,
                    1,
                )  # <:!:section_4
                await rest_client.wait_for_transaction(txn_hash)
                resp = await rest_client.account_resource(
                    admin_wallet.address(), "0x1::account::Account"
                )
                collection_addr = AccountAddress.for_named_collection(
                    admin_wallet.address(), "TeleGage Stickers"
                )
                pth = upload_to_cloudinary(
                    f"{file_dir}/new_{user_id}_1.png", f"new_{user_id}_1.png"
                )
                # :!:>section_5

                txn_hash = await token_client.mint_soul_bound_token(
                    admin_wallet,
                    f"TeleGage Stickers {num_with_zeros}",
                    f"Sticker # 1",
                    f"Sticker # 1",
                    pth,
                    PropertyMap([Property.string("Sticker #", "1")]),
                    AccountAddress.from_str(jsonObject["wallet"]),
                )  # <:!:section_5
                await rest_client.wait_for_transaction(txn_hash)
                print(txn_hash)
                minted_tokens = await token_client.tokens_minted_from_transaction(
                    txn_hash
                )
                print(minted_tokens)
                community_id=str(jsonObject["community_id"])
                print(community_id)
                community = community_collection.find_one(
                    {"community_id": community_id}
                )
                print(community)
                current_message_count = int(community["stats"]["number_of_nfts_minted"])
                new_message_count = current_message_count + 1
                print(new_message_count)
                community_collection.update_one(
                    {"community_id": str(community["community_id"])},
                    {"$set": {"stats.number_of_nfts_minted": str(new_message_count)}},
                )
                community_collection.update_one(
                    {"community_id": str(community["community_id"])},
                    {
                        "$push": {
                            "stats.actions": {
                                "timestamp": str(datetime.now()),
                                "username": str(user.get("user_name")),
                                "message": f"{user.get('user_name')} has Minted an NFT",
                            }
                        }
                    },
                )
                # collection_data = await get_collection_data(token_client, collection_addr)
                # print(collection_data)
                txn_ids = []
                photos_list = list(pics.photos)[1:]
                for id, pic in enumerate(photos_list, start=2):
                    sticker = InputSticker(
                        InputFile(f"{file_dir}/new_{user_id}_{id}.png"),
                        emoji_list=["🍩"],
                        format="static",
                    )
                    pth = upload_to_cloudinary(
                        f"{file_dir}/new_{user_id}_{id}.png", f"new_{user_id}_{id}.png"
                    )
                    txn_hash = await token_client.mint_soul_bound_token(
                        admin_wallet,
                        f"TeleGage Stickers {num_with_zeros}",
                        f"Sticker # {id}",
                        f"Sticker # {id}",
                        pth,
                        PropertyMap([Property.string("Sticker #", str(id))]),
                        AccountAddress.from_str(jsonObject["wallet"]),
                    )  # <:!:section_5
                    await rest_client.wait_for_transaction(txn_hash)
                    print(txn_hash)
                    minted_tokens = await token_client.tokens_minted_from_transaction(
                        txn_hash
                    )
                    print(minted_tokens)
                    community = community_collection.find_one(
                        {"community_id": str(jsonObject["community_id"])}
                    )
                    current_message_count = int(
                        community["stats"]["number_of_nfts_minted"]
                    )
                    new_message_count = current_message_count + 1
                    print(new_message_count)
                    community_collection.update_one(
                        {"community_id": str(community["community_id"])},
                        {
                            "$set": {
                                "stats.number_of_nfts_minted": str(new_message_count)
                            }
                        },
                    )
                    community_collection.update_one(
                        {"community_id": str(community["community_id"])},
                        {
                            "$push": {
                                "stats.actions": {
                                    "timestamp": str(datetime.now()),
                                    "username": str(user.get("user_name")),
                                    "message": f"{user.get('user_name')} has Minted an NFT",
                                }
                            }
                        },
                    )
                    await bot.add_sticker_to_set(
                        user_id,
                        f"mv_{num_with_zeros}_by_TeleGageCommunityBot",
                        emojis=["🍩"],
                        sticker=sticker,
                    )
                # collection_data = await get_collection_data(token_client, collection_addr)
                # print(collection_data)
                await bot.send_message(
                    message.chat.id,
                    f"Sticker set created successfully! You can add it here: https://t.me/addstickers/mv_{num_with_zeros}_by_TeleGageCommunityBot",
                )
                await bot.send_message(
                    message.chat.id,
                    f"Sticker Minted On Chain successfully! You View it here @: https://explorer.aptoslabs.com/account/{jsonObject['wallet']}/tokens?network=testnet",
                )
            else:
                await bot.send_message(
                    message.chat.id,
                    f"User Photos not found. Please Go to Settings > Privacy & Security > Privacy and Set Your Profile Picture setting to Everybody.",
                )

        else:
            await bot.send_message(
                message.chat.id,
                f"User Not Found",
            )

@bot.inline_handler(lambda query: query.query == 'mint_nft')
async def mintnft(message):
    print(message)
    jsonObject = json.loads(message.web_app_data.data)
    await bot.send_message(message.chat.id, "Received The Data")
    user_id = message.from_user.id
    file_dir = f"./{user_id}"
    print(message)
    os.makedirs(file_dir, exist_ok=True)
    if jsonObject["action"] == "Add Sticker":
        pics = await bot.get_user_profile_photos(user_id)
        print(pics)
        user = users_collection.find_one({"user_id": str(user_id)})
        if user != None:
            data = decrypt(str(user_id).encode(), user.get("data"))
            print(data.decode())
            my_account = Account.load_key(data.decode())
            balance = await rest_client.get_balance(
                admin_wallet.address(), my_account.address()
            )
            print(f"{user.get('user_name')}'s updated Telegage balance: {balance}")
            txn_hash = await rest_client.transfer_coins(
                my_account,
                AccountAddress.from_str(
                    "<Add TeleGage Token Address here>"
                ),
                f"{admin_wallet.address()}::telegage_token::TeleGageToken",
                jsonObject["price"],
            )
            balance = await rest_client.get_balance(
                admin_wallet.address(), my_account.address()
            )
            print(f"{user.get('user_name')}'s updated Telegage balance: {balance}")
            await rest_client.wait_for_transaction(txn_hash)
            if pics.total_count > 0:
                for id, pic in enumerate(pics.photos, start=1):
                    await bot.send_photo(
                        message.chat.id,
                        pic[-2].file_id,
                        caption="Profile Picture # " + str(id),
                    )
                    file_info = await bot.get_file(pic[-2].file_id)
                    download_file(
                        user_id,
                        id,
                        file_info.file_path,
                        jsonObject["prompt"],
                        jsonObject["negative_prompt"],
                    )
                sticker = InputSticker(
                    InputFile(f"{file_dir}/new_{user_id}_1.png"),
                    emoji_list=["🍩"],
                    format="static",
                )
                num = random.randrange(1, 10**4)
                num_with_zeros = "{:04}".format(num)
                await bot.create_new_sticker_set(
                    user_id,
                    f"mv_{num_with_zeros}_by_TeleGageCommunityBot",
                    "TeleGage Stickers",
                    stickers=[sticker],
                )
                print(
                    f"https://t.me/addstickers/mv_{num_with_zeros}_by_TeleGageCommunityBot"
                )

                txn_hash = await token_client.create_collection(
                    admin_wallet,
                    "TeleGage Stickers",
                    100,
                    f"TeleGage Stickers {num_with_zeros}",
                    "https://x.com/TeleGage_APT",
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    0,
                    1,
                )  # <:!:section_4
                await rest_client.wait_for_transaction(txn_hash)
                resp = await rest_client.account_resource(
                    admin_wallet.address(), "0x1::account::Account"
                )
                collection_addr = AccountAddress.for_named_collection(
                    admin_wallet.address(), "TeleGage Stickers"
                )
                pth = upload_to_cloudinary(
                    f"{file_dir}/new_{user_id}_1.png", f"new_{user_id}_1.png"
                )
                # :!:>section_5

                txn_hash = await token_client.mint_soul_bound_token(
                    admin_wallet,
                    f"TeleGage Stickers {num_with_zeros}",
                    f"Sticker # 1",
                    f"Sticker # 1",
                    pth,
                    PropertyMap([Property.string("Sticker #", "1")]),
                    AccountAddress.from_str(jsonObject["wallet"]),
                )  # <:!:section_5
                await rest_client.wait_for_transaction(txn_hash)
                print(txn_hash)
                minted_tokens = await token_client.tokens_minted_from_transaction(
                    txn_hash
                )
                print(minted_tokens)
                community_id=str(jsonObject["community_id"])
                print(community_id)
                community = community_collection.find_one(
                    {"community_id": community_id}
                )
                print(community)
                current_message_count = int(community["stats"]["number_of_nfts_minted"])
                new_message_count = current_message_count + 1
                print(new_message_count)
                community_collection.update_one(
                    {"community_id": str(community["community_id"])},
                    {"$set": {"stats.number_of_nfts_minted": str(new_message_count)}},
                )
                community_collection.update_one(
                    {"community_id": str(community["community_id"])},
                    {
                        "$push": {
                            "stats.actions": {
                                "timestamp": str(datetime.now()),
                                "username": str(user.get("user_name")),
                                "message": f"{user.get('user_name')} has Minted an NFT",
                            }
                        }
                    },
                )
                # collection_data = await get_collection_data(token_client, collection_addr)
                # print(collection_data)
                txn_ids = []
                photos_list = list(pics.photos)[1:]
                for id, pic in enumerate(photos_list, start=2):
                    sticker = InputSticker(
                        InputFile(f"{file_dir}/new_{user_id}_{id}.png"),
                        emoji_list=["🍩"],
                        format="static",
                    )
                    pth = upload_to_cloudinary(
                        f"{file_dir}/new_{user_id}_{id}.png", f"new_{user_id}_{id}.png"
                    )
                    txn_hash = await token_client.mint_soul_bound_token(
                        admin_wallet,
                        f"TeleGage Stickers {num_with_zeros}",
                        f"Sticker # {id}",
                        f"Sticker # {id}",
                        pth,
                        PropertyMap([Property.string("Sticker #", str(id))]),
                        AccountAddress.from_str(jsonObject["wallet"]),
                    )  # <:!:section_5
                    await rest_client.wait_for_transaction(txn_hash)
                    print(txn_hash)
                    minted_tokens = await token_client.tokens_minted_from_transaction(
                        txn_hash
                    )
                    print(minted_tokens)
                    community = community_collection.find_one(
                        {"community_id": str(jsonObject["community_id"])}
                    )
                    current_message_count = int(
                        community["stats"]["number_of_nfts_minted"]
                    )
                    new_message_count = current_message_count + 1
                    print(new_message_count)
                    community_collection.update_one(
                        {"community_id": str(community["community_id"])},
                        {
                            "$set": {
                                "stats.number_of_nfts_minted": str(new_message_count)
                            }
                        },
                    )
                    community_collection.update_one(
                        {"community_id": str(community["community_id"])},
                        {
                            "$push": {
                                "stats.actions": {
                                    "timestamp": str(datetime.now()),
                                    "username": str(user.get("user_name")),
                                    "message": f"{user.get('user_name')} has Minted an NFT",
                                }
                            }
                        },
                    )
                    await bot.add_sticker_to_set(
                        user_id,
                        f"mv_{num_with_zeros}_by_TeleGageCommunityBot",
                        emojis=["🍩"],
                        sticker=sticker,
                    )
                # collection_data = await get_collection_data(token_client, collection_addr)
                # print(collection_data)
                await bot.send_message(
                    message.chat.id,
                    f"Sticker set created successfully! You can add it here: https://t.me/addstickers/mv_{num_with_zeros}_by_TeleGageCommunityBot",
                )
                await bot.send_message(
                    message.chat.id,
                    f"Sticker Minted On Chain successfully! You View it here @: https://explorer.aptoslabs.com/account/{jsonObject['wallet']}/tokens?network=testnet",
                )
            else:
                await bot.send_message(
                    message.chat.id,
                    f"User Photos not found. Please Go to Settings > Privacy & Security > Privacy and Set Your Profile Picture setting to Everybody.",
                )

        else:
            await bot.send_message(
                message.chat.id,
                f"User Not Found",
            )

@bot.chat_join_request_handler()
async def make_some(message: types.ChatJoinRequest):
    bot.send_message(message.chat.id, "I accepted a new user!")
    bot.approve_chat_join_request(message.chat.id, message.from_user.id)


@bot.chat_member_handler()
def chat_m(message: types.ChatMemberUpdated):
    old = message.old_chat_member
    new = message.new_chat_member
    if new.status == "member":
        bot.send_message(
            message.chat.id, "Hello {name}!".format(name=new.user.first_name)
        )  # Welcome message


asyncio.run(bot.polling(skip_pending=True))