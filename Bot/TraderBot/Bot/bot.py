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
import asyncio
import json
import time

from aptos_sdk.async_client import RestClient
from aptos_sdk.transactions import (
    TransactionArgument,
    TransactionPayload,
    EntryFunction,
    Serializer,
    StructTag,
    TypeTag,
    AccountAddress
)
from aptos_sdk.account import Account
from typing import Optional, List

bot_token = "7799557371:AAGkM0-1D1hW8kgrvLr-clPz5EK8SqtaUBM"
# Initialize Aptos client
aptos = RestClient("https://fullnode.testnet.aptoslabs.com/v1")

account = Account.load_key("0x78c13830e66f2685bd0c61c6cce6035ea66ca3ead544d857dce2336a7d55d741")
module_address = "0x880873652998d2cb0c63db5d7b11d7115a626f278c6d1bc56170aead9a8b00e4"


bot = AsyncTeleBot(bot_token, parse_mode=None)
def extract_arg(arg):
    return arg.split()[1:]

async def get_community_address(base_address: str, owner_address: str) -> str:
    """
    Get community address using the contract's view function
    
    Args:
        base_address: The address where the contract is deployed
        owner_address: The address of the community owner
    
    Returns:
        str: The community address
    """
    try:
        # Format the view request
        payload = {
            "function": f"{base_address}::communitySaver::get_community",
            "type_arguments": [],
            "arguments": [
                base_address,  # base_address parameter
                owner_address  # owner parameter
            ]
        }
        
        # Call view function using the correct method name
        response = await aptos.view(
            payload["function"],
            payload["type_arguments"],
            payload["arguments"]
        )
        
        return response[0]  # The response is typically a list with one item
        
    except Exception as error:
        print(f"Error getting community address: {str(error)}")
        raise error

async def sign_and_submit_create_community(
    account: Account, 
    module_address: str,
    owner_address: AccountAddress,
    community_id: str,
    community_name: str,
    community_prompt: str
) -> dict:
    """
    Specific sign and submit function for create_community with proper argument formatting
    """
    
    # Format the arguments properly
    arguments = [
        TransactionArgument(owner_address, Serializer.struct),  # address
        TransactionArgument(community_id, Serializer.str),  # String
        TransactionArgument(community_name, Serializer.str),  # String
        TransactionArgument(community_prompt, Serializer.str),  # String
    ]
    print(arguments)
    # Create entry function
    payload = EntryFunction.natural(
        f"{module_address}::communitySaver",
        "create_community",
        [],  # type arguments
        [TransactionArgument(owner_address, Serializer.struct), 
         TransactionArgument(community_id, Serializer.str), 
         TransactionArgument(community_name, Serializer.str), 
         TransactionArgument(community_prompt, Serializer.str)]
    )
    print(payload)

    # Create signed transaction
    signed_transaction = await aptos.create_bcs_signed_transaction(
        account,
        TransactionPayload(payload)
    )
    # Submit transaction
    response = await aptos.submit_bcs_transaction(signed_transaction)
    return response

async def create_community(account: Account, module_address: str, owner_address: str, 
                         community_id: str, community_name: str, community_prompt: str) -> bool:
    """
    Create a new community using the contract's create_community function
    """
    try:
        # Sign and submit transaction with properly formatted arguments
        response = await sign_and_submit_create_community(
            account,
            module_address,
            AccountAddress.from_str(owner_address),
            community_id,
            community_name,
            community_prompt
        )
        
        # Wait for transaction to complete
        await aptos.wait_for_transaction(response)
        
        return True
        
    except Exception as error:
        print(f"Error creating community: {str(error)}")
        raise error

async def fetch_list(account: Optional[Account], module_address: str) -> List[dict]:
    """
    Fetch todo list items from the account's resource
    
    Args:
        account: Aptos account
        module_address: Address where the module is deployed
    
    Returns:
        List of tasks
    """
    if not account:
        return []
        
    try:
        # Get the TodoList resource from the account
        todo_list_resource = await aptos.account_resource(
            account.address(),
            f"{module_address}::communitySaver::CommunityList"
        )
        #print(todo_list_resource)
        communities = todo_list_resource["data"]["communities"]["data"]
        values = [item["value"] for item in communities]
        print(values)
        
        return values
        
    except Exception as error:
        print(f"Error fetching list: {str(error)}")
        raise error

async def sign_and_submit_edit_community(
    account: Account, 
    module_address: str,
    owner_address: AccountAddress,
    community_prompt: str
) -> dict:
    """
    Specific sign and submit function for edit_community with proper argument formatting
    """
    
    # Format the arguments properly
    arguments = [
        TransactionArgument(owner_address, Serializer.struct),  # owner address
        TransactionArgument(community_prompt, Serializer.str),  # new community prompt
    ]
    
    # Create entry function
    payload = EntryFunction.natural(
        f"{module_address}::communitySaver",
        "edit_community",
        [],  # type arguments
        arguments
    )

    # Create signed transaction
    signed_transaction = await aptos.create_bcs_signed_transaction(
        account,
        TransactionPayload(payload)
    )
    
    # Submit transaction
    response = await aptos.submit_bcs_transaction(signed_transaction)
    return response

async def edit_community(
    account: Account, 
    module_address: str, 
    owner_address: str, 
    community_prompt: str
) -> bool:
    """
    Edit an existing community's prompt using the contract's edit_community function
    
    Args:
        account: Aptos account that will sign the transaction
        module_address: Address where the module is deployed
        owner_address: Address of the community owner
        community_prompt: New prompt for the community
    
    Returns:
        bool: True if edit was successful
    """
    try:
        # Sign and submit transaction with properly formatted arguments
        response = await sign_and_submit_edit_community(
            account,
            module_address,
            AccountAddress.from_str(owner_address),
            community_prompt
        )
        
        # Wait for transaction to complete
        await aptos.wait_for_transaction(response)
        
        return True
        
    except Exception as error:
        print(f"Error editing community: {str(error)}")
        raise error

@bot.message_handler(commands=["Register"])
async def redeemption(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    user_id = message.from_user.id
    markup.add(
                KeyboardButton(
                    f"Agent Bullseye - Register DAO",
                    web_app=WebAppInfo(
                        f"https://teledao.vercel.app/{user_id}/"
                    ),
                )
            )
    await bot.reply_to(
        message,
        "Hey There. You can use the following Register DAO button to register your DAO on Agent Bullseye",
        reply_markup=markup,
    )

@bot.message_handler(commands=['AddMember'])
async def add_member(message):
    community_id = extract_arg(message.text)
    if len(community_id)==1:
        user_id = message.from_user.id
        communities=await fetch_list(account, module_address)
        community=[community for community in communities if community.get("community_id")==community_id]
        if community!=[]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(
                KeyboardButton(
                    f"Agent Bullseye - Login",
                    web_app=WebAppInfo(
                        f"https://teledao.vercel.app/member/{community.get('owner')}/"
                    ),
                )
            )
            await bot.reply_to(
                message,
                "Hey There. You can use the following Login button to login to your DAO on Agent Bullseye",
                reply_markup=markup,
            )
        else:
            print("Community not found")
            await bot.send_message(message.chat.id, "Community not found")



@bot.message_handler(content_types=["web_app_data"])
async def web_app_data_manager(message):
    print(message.web_app_data.data)
    jsonObject = json.loads(message.web_app_data.data)
    user_id = message.from_user.id
    file_dir = f"./{user_id}"
    os.makedirs(file_dir, exist_ok=True)
    if jsonObject["action"] == "Register DAO":
        await bot.send_message(message.chat.id, f""" Welcome to Agent Bullseye.
                               
        Add Agent Bullseye to your DAO Telegram Group.
        
        Please provide the following to your members to register them:
        1. visit t.me/agentbullseye_bot
        2. Run the  /AddMember command as follows:
        """)
        await bot.send_message(message.chat.id, f"/AddMember {jsonObject['community_id']}")
    if jsonObject["action"] == "Modify DAO Rules":
        await bot.send_message(message.chat.id, f""" Modification of DAO Rules will start as soon as the poll is answered.""")
        sent_poll = await bot.send_poll(
            message.chat.id,
            f"Do you want to modify the DAO rules as follows: Rules: {jsonObject['new_rules']}",
            ["Yes", "No"],is_anonymous=False
        )
        await edit_community(account, module_address, jsonObject["owner"], jsonObject["new_rules"])

@bot.poll_answer_handler()
async def handle_poll_answer(poll_answer):
    """
    Handle poll answers from users
    poll_answer object contains:
    - poll_id
    - user
    - option_ids (list of selected options)
    """
    print(poll_answer)
    selected_options = poll_answer.option_ids
    user = poll_answer.user
    poll_id = poll_answer.poll_id
    print(selected_options, user, poll_id)
    if selected_options[0] == 0:  # User selected "Yes"
        # Handle "Yes" response
        await bot.send_message(user.id, "Great! Please provide the member's details...")
    else:  # User selected "No"
        await bot.send_message(user.id, "Okay, no problem!")






asyncio.run(bot.polling(skip_pending=True))
