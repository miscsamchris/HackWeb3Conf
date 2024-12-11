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
import asyncio


# Initialize Aptos client
aptos = RestClient("https://fullnode.testnet.aptoslabs.com/v1")

async def sign_and_submit_transaction(account: Account, transaction: dict) -> dict:
    """Sign and submit a transaction using the Aptos SDK"""
    
    # Extract function parts from the transaction data
    function_id = transaction["data"]["function"]
    module_address, module_name, function_name = function_id.split("::")
    
    # Create entry function
    payload = EntryFunction.natural(
        module_address+"::"+module_name,
        function_name,
        [], # type arguments (empty in this case)
        [] # arguments (empty in this case)
    )
    
    # Create signed transaction
    signed_transaction = await aptos.create_bcs_signed_transaction(
        account,
        TransactionPayload(payload)
    )
    
    # Submit transaction
    response = await aptos.submit_bcs_transaction(signed_transaction)
    return response

async def add_new_list(account: Optional[Account], module_address: str) -> bool:
    if not account:
        return []
    
    transaction_in_progress = True
    
    try:
        # Create transaction data
        transaction = {
            "data": {
                "function": f"{module_address}::communitySaver::create_list",
                "function_arguments": []
            }
        }
        
        # Sign and submit transaction
        response = await sign_and_submit_transaction(account, transaction)
        
        # Wait for transaction to complete
        await aptos.wait_for_transaction(response)
        
        account_has_list = True
        
    except Exception as error:
        account_has_list = False
        raise error
    
    finally:
        transaction_in_progress = False
        
    return account_has_list

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

async def main():
    try:
        private_key = "0x78c13830e66f2685bd0c61c6cce6035ea66ca3ead544d857dce2336a7d55d741"  # Replace with your private key
        account = Account.load_key(private_key)
        
        # Your module address (replace with actual address)
        module_address = "0x880873652998d2cb0c63db5d7b11d7115a626f278c6d1bc56170aead9a8b00e4"
        
        print(f"Using account address: {account.address()}")
        print(f"Module address: {module_address}")
        
        # Create a new community
        owner_address = "0xf47369da744ab288e30427fbf1a6f563838e78d1964d837c9da53de4545bc9cd"  # Replace with desired owner address
        # result = await create_community(
        #     account,
        #     module_address,
        #     owner_address,
        #     "community123",  # community_id
        #     "My Test Community",  # community_name
        #     "This is a test community prompt"  # community_prompt
        # )
        new_prompt = "Updated community prompt"
        
        result = await edit_community(
            account,
            module_address,
            owner_address,
            new_prompt
        )
        if result:
            print("Successfully edited community!")
            
            # Fetch updated list to verify changes
            communities = await fetch_list(account, module_address)
            print("Updated communities:", communities)
        else:
            print("Failed to edit community")
        # if result:
        #     print("Successfully created new community!")
            
        #     # Get and verify the community address
        #     community_address = await get_community_address(module_address, owner_address)
        #     print(f"Community address: {community_address}")
        # else:
        #     print("Failed to create community")
        
        # Fetch the list
        tasks = await fetch_list(account, module_address)
        print(tasks)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
