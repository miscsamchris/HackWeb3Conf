from TeleGage import (
    app,
    db_client,
    aptos_client,
    faucet_client,
    functions,
    types,
    uuid,
    topics_collection,
    community_collection,
    users_collection,
    Account,
    admin_wallet,
    encrypt,
    TelegramClient,
    name,
    api_id,
    api_hash,
)
from flask import url_for, render_template, request
import json
import pickle
import requests, traceback
from datetime import datetime
@app.route("/test")
def test():
    return "Hello World From Python app"


@app.route("/create_telegram_channel", methods=["POST"])
async def create_telegram_channel():
    if request.method == "POST":
        telegram_channel_title = request.json.get("telegram_channel_title", "NA")
        telegram_channel_description = request.json.get(
            "telegram_channel_description", "NA"
        )
        telegram_admin_id = request.json.get("telegram_admin_id", "NA")
        telegram_channel_rules = request.json.get("telegram_channel_rules", "NA")
        telegram_channel_owner = request.json.get("telegram_channel_owner", "NA")
        telegram_channel_instructions = request.json.get(
            "telegram_channel_instructions", "NA"
        )
        telegram_topics = request.json.get("topics", [])
        try:
            telethon_client = TelegramClient(name, api_id, api_hash)
            async with telethon_client:
                result = await telethon_client(
                    functions.channels.CreateChannelRequest(
                        telegram_channel_title,
                        telegram_channel_description,
                        megagroup=True,
                        forum=True,
                    )
                )
                channel = result.chats[0]
                result = await telethon_client(
                    functions.channels.InviteToChannelRequest(
                        channel, [telegram_admin_id]
                    )
                )
                await telethon_client.edit_admin(
                    channel,
                    telegram_admin_id,
                    is_admin=True,
                    add_admins=False,
                    anonymous=False,
                )

                topic_ids = []
                for topic in telegram_topics:
                    topic_name = topic.get("Name")
                    result = await telethon_client(
                        functions.channels.CreateForumTopicRequest(channel, topic_name)
                    )
                    topic_id = result.updates[-1].message.id
                    topic_item = {
                        "_id": str(uuid.uuid4()),
                        "topic_id": topic_id,
                        "topic_name": topic.get("Name"),
                        "topic_rules": topic.get("Rules"),
                        "topic_instructions": topic.get("Instructions"),
                    }
                    topic_ids.append(
                        topics_collection.insert_one(topic_item).inserted_id
                    )
                topic_name = "Activties"
                result = await telethon_client(
                    functions.channels.CreateForumTopicRequest(channel, topic_name)
                )
                topic_id = result.updates[-1].message.id
                activities_id=result.updates[-1].message.id
                topic_item = {
                    "_id": str(uuid.uuid4()),
                    "topic_id": topic_id,
                    "topic_name": topic_name,
                    "topic_rules": "For Bot User",
                    "topic_instructions": "For Bot Use",
                }
                topic_ids.append(topics_collection.insert_one(topic_item).inserted_id)

                result = await telethon_client(
                    functions.channels.EditForumTopicRequest(
                        channel=channel, topic_id=topic_id, closed=True
                    )
                )
                topic_name = "Announcements"
                result = await telethon_client(
                    functions.channels.CreateForumTopicRequest(channel, topic_name)
                )
                topic_id = result.updates[-1].message.id
                announcements_id = result.updates[-1].message.id
                topic_item = {
                    "_id": str(uuid.uuid4()),
                    "topic_id": topic_id,
                    "topic_name": topic_name,
                    "topic_rules": "For Bot User",
                    "topic_instructions": "For Bot Use",
                }
                topic_ids.append(topics_collection.insert_one(topic_item).inserted_id)

                result = await telethon_client(
                    functions.channels.EditForumTopicRequest(
                        channel=channel, topic_id=topic_id, closed=True
                    )
                )
                users = telethon_client.iter_participants(channel.id)
                user_ids = []
                async for i in users:
                    # print(i)
                    try:
                        print(i)
                        if i.bot == False:
                            user_account = Account.generate()
                            try:
                                await faucet_client.fund_account(
                                    user_account.address(), 20_000_000
                                )
                            except:
                                await faucet_client.fund_account(
                                    user_account.address(), 20_000_000
                                )
                            updateddata = str(user_account.private_key)
                            print(user_account.account_address)
                            encrypted = encrypt(
                                str(i.id).encode(), updateddata.encode()
                            )
                            user_item = {
                                "_id": str(uuid.uuid4()),
                                "user_id": str(i.id),
                                "user_name": i.username,
                                "name": f"{i.first_name if i.first_name!=None else '' } {i.last_name if i.last_name!=None else '' }",
                                "TeleTokens_CustodialAddress": str(
                                    user_account.account_address
                                ),
                                "data": str(encrypted),
                                "community_id": f"-100{channel.id}",
                            }
                            txn_hash = await aptos_client.register_coin(
                                admin_wallet.address(), user_account
                            )
                            await aptos_client.wait_for_transaction(txn_hash)
                            txn_hash = await aptos_client.mint_coin(
                                admin_wallet, user_account.address(), 1000
                            )
                            await aptos_client.wait_for_transaction(txn_hash)
                            user_ids.append(
                                users_collection.insert_one(user_item).inserted_id
                            )
                            balance = await aptos_client.get_balance(
                                admin_wallet.address(), user_account.address()
                            )
                            print(
                                f"Account for {i.username} : initial TeleGage balance: {balance}"
                            )
                    except:
                        print(traceback.format_exc())
                result = await telethon_client(
                    functions.channels.InviteToChannelRequest(
                        channel, ["TeleGageCommunityBot"]
                    )
                )
                await telethon_client(functions.channels.EditAdminRequest(
                    channel=channel,
                    user_id='TeleGageCommunityBot',
                    admin_rights=types.ChatAdminRights(
                        change_info=True,
                        post_messages=True,
                        edit_messages=True,
                        delete_messages=True,
                        ban_users=True,
                        invite_users=True,
                        pin_messages=True,
                        add_admins=True,
                        anonymous=True,
                        manage_call=True,
                        other=True,
                        manage_topics=True,
                        post_stories=True,
                        edit_stories=True,
                        delete_stories=True
                    ),
                    rank='Moderator'
                ))
                message=f"**Community Rules**:\n {telegram_channel_rules}\n\n\n Link to redeem: https://t.me/TeleGageCommunityBot?start=redeem"
                await telethon_client.send_message(channel,message,reply_to=announcements_id)
            test_community = {
                "_id": str(uuid.uuid4()),
                "community_name": telegram_channel_title,
                "category": "channel",
                "community_description": telegram_channel_description,
                "community_rules": telegram_channel_rules,
                "community_instructions": telegram_channel_instructions,
                "community_id": f"-100{channel.id}",
                "topics": topic_ids,
                "owner_id": telegram_channel_owner,
                "activities_id": activities_id,
                "announcements_id":announcements_id,
                "users": user_ids,
                "stats": {
                    "number_of_messages": "0",
                    "points_earned": "0",
                    "number_of_nfts_minted": "0",
                    "users_to_be_kicked_out": [],
                    "community_id": f"-100{channel.id}",
                    "actions": [],
                },
            }
            
            
            community_collection.insert_one(test_community)
            return {"code": 200, "Message": "Channel created Successfully"}
        except Exception as e:
            # Rollback changes if an error occurs
            print(traceback.format_exc())
    return {"code": 201}


@app.route("/get_stats_by_community", methods=["POST"])
async def get_stats_by_community():
    if request.method == "POST":
        print("JSON", request.json)
        print("fomr", request.form)
        telegram_channel_id = request.json.get("telegram_channel_id", "NA")
        try:
            community = community_collection.find_one(
                {"community_id": telegram_channel_id}   
            )
            stats = community.get("stats", {})
            return {"code": 200, "Stats": stats}
        except Exception as e:
            # Rollback changes if an error occurs
            print(traceback.format_exc())
    return {"code": 201}


@app.route("/get_topics_by_community", methods=["POST"])
async def get_topics_by_community():
    if request.method == "POST":
        print("JSON", request.json)
        print("fomr", request.form)
        telegram_channel_username = int(
            request.json.get("telegram_channel_username", "NA")
        )
        try:
            telethon_client = TelegramClient(name, api_id, api_hash)
            async with telethon_client:
                async for dialog in telethon_client.iter_dialogs():
                    print(dialog.entity)
                channel = await telethon_client.get_entity(telegram_channel_username)
                date, offset, offset_topic, total = 0, 0, 0, 0
                result = await telethon_client(
                    functions.channels.GetForumTopicsRequest(
                        channel, date, offset, offset_topic, 100, ""
                    )
                )
                topics = result.topics
                topics_list = []
                for i in topics:
                    tname = i.title
                    iden = i.id
                    topics_list.append({"Name": tname, "id": iden})
            return {"code": 200, "Topics": topics_list}
        except Exception as e:
            # Rollback changes if an error occurs
            print(traceback.format_exc())
    return {"code": 201}


@app.route("/kick_user_from_community", methods=["POST"])
async def kick_user_from_community():
    if request.method == "POST":
        print("JSON", request.json)
        telegram_channel_username = int(
            request.json.get("telegram_channel_username", "NA")
        )
        user_id = int(request.json.get("user_name", "NA"))
        community = community_collection.find_one({"community_id": str(telegram_channel_username)})
        user = users_collection.find_one({"user_id": str(user_id)})
        try:
            telethon_client = TelegramClient(name, api_id, api_hash)
            async with telethon_client:
                channel = await telethon_client.get_entity(telegram_channel_username)
                banned_rights = types.ChatBannedRights(
                    until_date=None, view_messages=False
                )
                
                community_collection.update_one(
                    {"community_id": str(telegram_channel_username)},  # Match the community by name
                    {"$pull": {"users": user.get("_id")}}  # Remove the topic_id from the topic_ids array
                )
                community_collection.update_one(
                    {"community_id": str(telegram_channel_username)},  # Match the community by name
                    {"$pull": {"users": user.get("_id")}}  # Remove the topic_id from the topic_ids array
                )
                community_collection.update_one(
                    {"community_id": str(telegram_channel_username)},
                    {"$pull": {"stats.users_to_be_kicked_out": {"user_id": str(user_id)}}}
                )
                community_collection.update_one(
                    {"community_id": str(telegram_channel_username)},
                    {
                        "$push": {
                            "stats.actions": {
                                "timestamp": str(datetime.now()),
                                "username": str(user.get("user_name")),
                                "message": f"{user.get('user_name')} has been Kicked out by the community manager",
                            }
                        }
                    },
                )
                result=await telethon_client.edit_permissions(channel, user_id, view_messages=False)
                print(result)
            return {"code": 200, "Message": "User Banned Successfully"}
        except Exception as e:
            # Rollback changes if an error occurs
            print(traceback.format_exc())
    return {"code": 201}


@app.route("/import_channel", methods=["POST"])
async def import_channel():
    if request.method == "POST":
        telegram_channel_username = request.json.get("telegram_channel_username", "NA")
        telegram_channel_rules = request.json.get("telegram_channel_rules", "NA")
        telegram_channel_owner = request.json.get("telegram_channel_owner", "NA")
        telegram_channel_instructions = request.json.get(
            "telegram_channel_instructions", "NA"
        )
        telegram_topics = request.json.get("topics", [])
        try:
            telethon_client = TelegramClient(name, api_id, api_hash)
            async with telethon_client:
                async for dialog in telethon_client.iter_dialogs():
                    print(dialog.entity)
                channel = await telethon_client.get_entity(
                    int(telegram_channel_username)
                )
                topic_ids = []
                for topic in telegram_topics:
                    topic_name = topic.get("Name")
                    topic_status = topic.get("Status")
                    if topic_status == "New":
                        result = await telethon_client(
                            functions.channels.CreateForumTopicRequest(
                                channel, topic_name
                            )
                        )
                        topic_id = result.updates[-1].message.id
                        topic_item = {
                            "_id": str(uuid.uuid4()),
                            "topic_id": topic_id,
                            "topic_name": topic.get("Name"),
                            "topic_rules": topic.get("Rules"),
                            "topic_instructions": topic.get("Instructions"),
                        }
                        topic_ids.append(
                            topics_collection.insert_one(topic_item).inserted_id
                        )
                    else:
                        topic_item = {
                            "_id": str(uuid.uuid4()),
                            "topic_id": topic.get("ID"),
                            "topic_name": topic.get("Name"),
                            "topic_rules": topic.get("Rules"),
                            "topic_instructions": topic.get("Instructions"),
                        }
                        topic_ids.append(
                            topics_collection.insert_one(topic_item).inserted_id
                        )
                topic_name = "Activties"
                result = await telethon_client(
                    functions.channels.CreateForumTopicRequest(channel, topic_name)
                )
                topic_id = result.updates[-1].message.id
                activities_id=result.updates[-1].message.id
                topic_item = {
                    "_id": str(uuid.uuid4()),
                    "topic_id": topic_id,
                    "topic_name": topic_name,
                    "topic_rules": "For Bot User",
                    "topic_instructions": "For Bot Use",
                }
                topic_ids.append(topics_collection.insert_one(topic_item).inserted_id)
                result = await telethon_client(
                    functions.channels.EditForumTopicRequest(
                        channel=channel, topic_id=topic_id, closed=True
                    )
                )
                topic_name = "Announcements"
                result = await telethon_client(
                    functions.channels.CreateForumTopicRequest(channel, topic_name)
                )
                topic_id = result.updates[-1].message.id
                announcements_id = result.updates[-1].message.id
                topic_item = {
                    "_id": str(uuid.uuid4()),
                    "topic_id": topic_id,
                    "topic_name": topic_name,
                    "topic_rules": "For Bot User",
                    "topic_instructions": "For Bot Use",
                }
                topic_ids.append(topics_collection.insert_one(topic_item).inserted_id)
                result = await telethon_client(
                    functions.channels.EditForumTopicRequest(
                        channel=channel, topic_id=topic_id, closed=True
                    )
                )
                users = telethon_client.iter_participants(channel.id)
                user_ids = []
                async for i in users:
                    # print(i)
                    try:
                        if i.bot == False:
                            user_account = Account.generate()
                            try:
                                await faucet_client.fund_account(
                                    user_account.address(), 20_000_000
                                )
                            except:
                                await faucet_client.fund_account(
                                    user_account.address(), 20_000_000
                                )
                            updateddata = str(user_account.private_key)
                            print(user_account.account_address)
                            encrypted = encrypt(
                                str(i.id).encode(), updateddata.encode()
                            )
                            print(encrypted)
                            user_item = {
                                "_id": str(uuid.uuid4()),
                                "user_id": str(i.id),
                                "user_name": i.username,
                                "name": f"{i.first_name if i.first_name!=None else '' } {i.last_name if i.last_name!=None else '' }",
                                "TeleTokens_CustodialAddress": str(
                                    user_account.account_address
                                ),
                                "data": str(encrypted),
                                "community_id": f"-100{channel.id}",
                            }
                            txn_hash = await aptos_client.register_coin(
                                admin_wallet.address(), user_account
                            )
                            await aptos_client.wait_for_transaction(txn_hash)
                            txn_hash = await aptos_client.mint_coin(
                                admin_wallet, user_account.address(), 1000
                            )
                            await aptos_client.wait_for_transaction(txn_hash)
                            user_ids.append(
                                users_collection.insert_one(user_item).inserted_id
                            )
                            balance = await aptos_client.get_balance(
                                admin_wallet.address(), user_account.address()
                            )
                            print(
                                f"Account for {i.username} : initial TeleGage balance: {balance}"
                            )
                    except:
                        pass
                result = await telethon_client(
                    functions.channels.InviteToChannelRequest(
                        channel, ["TeleGageCommunityBot"]
                    )
                )
                
                await telethon_client(functions.channels.EditAdminRequest(
                    channel=channel,
                    user_id='TeleGageCommunityBot',
                    admin_rights=types.ChatAdminRights(
                        change_info=True,
                        post_messages=True,
                        edit_messages=True,
                        delete_messages=True,
                        ban_users=True,
                        invite_users=True,
                        pin_messages=True,
                        add_admins=True,
                        anonymous=True,
                        manage_call=True,
                        other=True,
                        manage_topics=True,
                        post_stories=True,
                        edit_stories=True,
                        delete_stories=True
                    ),
                    rank='Moderator'
                ))
                message=f"**Community Rules**:\n {telegram_channel_rules}\n\n\n Link to redeem: https://t.me/TeleGageCommunityBot?start=redeem"
                await telethon_client.send_message(channel,message,reply_to=announcements_id)
            test_community = {
                "_id": str(uuid.uuid4()),
                "community_name": channel.title,
                "category": "channel",
                "community_description": "",
                "community_rules": telegram_channel_rules,
                "community_instructions": telegram_channel_instructions,
                "community_id": f"-100{channel.id}",
                "topics": topic_ids,
                "users": user_ids,
                "owner_id": telegram_channel_owner,
                "activities_id": activities_id,
                "stats": {
                    "number_of_messages": "0",
                    "points_earned": "0",
                    "number_of_nfts_minted": "0",
                    "users_to_be_kicked_out": [],
                    "community_id": f"-100{channel.id}",
                    "actions": [],
                },
            }
            community_collection.insert_one(test_community)
            return {"code": 200, "Message": "Channel Imported Successfully"}
        except Exception as e:
            # Rollback changes if an error occurs
            print(traceback.format_exc())
    return {"code": 201}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
