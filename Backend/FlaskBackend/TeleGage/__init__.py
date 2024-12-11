from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
import os, sys
from logging.config import dictConfig
from dotenv import dotenv_values, load_dotenv
import datetime
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
    ReadObject,
    Token,
)
from aptos_sdk.type_tag import StructTag, TypeTag
from telethon.sync import TelegramClient
from telethon import functions, types
import time
from pymongo import MongoClient
import uuid
from flask_cors import CORS, cross_origin

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

config = dotenv_values(".env")
direc = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

datestamp = datetime.datetime.now().strftime("%Y-%m-%d")
log_folder = direc + "/static/logs"
os.makedirs(log_folder, exist_ok=True)

name = "<Add Telegram Bot Name here>"
api_id = "<Add Telegram API ID here>"
api_hash = "<Add Telegram API Hash here>"


def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "<Add MongoDB Connection String here>"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client["telegram_communities"]


db_client = get_database()
community_collection = db_client["telegram_community"]
topics_collection = db_client["community_topics"]
users_collection = db_client["community_users"]


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

    async def burn_coin(
        self, owner: Account, receiver_address: AccountAddress, amount: int
    ) -> str:
        """Mints the newly created coin to a specified receiver address."""

        payload = EntryFunction.natural(
            "0x1::managed_coin",
            "burn_from",
            [
                TypeTag(
                    StructTag.from_str(
                        f"{owner.address()}::telegage_token::TeleGageToken"
                    )
                )
            ],
            [
                TransactionArgument(receiver_address, Serializer.struct),
                TransactionArgument(amount, Serializer.u64),
            ],
        )
        signed_transaction = await self.create_bcs_signed_transaction(
            owner, TransactionPayload(payload)
        )

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


aptos_client = CoinClient(NODE_URL)
faucet_client = FaucetClient(FAUCET_URL, aptos_client)
admin_wallet = Account.load(direc + "/static/admin")

import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


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
