import aiohttp
from bot.config import API_BASE_URL


async def create_item(id: str):
    api_url = f"{API_BASE_URL}/items/"
    timeout = aiohttp.ClientTimeout(total=10.0)
    payload = {"id": id}

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    return {"success": True, "data": data, "created": True}

                elif response.status == 409:
                    async with session.get(
                        f"{api_url}/{payload['id']}"
                    ) as get_item_response:
                        if get_item_response == 200:
                            item = await get_item_response.json()
                            return {
                                "success": True,
                                "data": item,
                                "created": False,
                            }

                return {
                    "success": False,
                    "message": "The backend server encountered an error. "
                    f"Status code: {response.status}",
                }
    except TimeoutError:
        return {
            "success": False,
            "message": "The server took too long to respond.",
        }
    except aiohttp.ClientConnectorError:
        return {"success": False, "message": "Unable to reach the backend server."}


async def delete_item(id: str):
    api_url = f"{API_BASE_URL}/items/"
    timeout = aiohttp.ClientTimeout(total=10.0)
    payload = {"id": id}

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.delete(api_url, json=payload) as response:
                if response.status == 200:
                    deleted_item = await response.json()
                    return {"success": True, "data": deleted_item}

                elif response.status == 404:
                    return {
                        "success": False,
                        "message": "Item not found.",
                    }

                return {
                    "success": False,
                    "message": "The backend server encountered an error. "
                    f"Status code: {response.status}",
                }

    except TimeoutError:
        return {
            "success": False,
            "message": "The server took too long to respond.",
        }
    except aiohttp.ClientConnectorError:
        return {"succe>ss": False, "message": "Unable to reach the backend server."}


async def fetch_items():
    api_url = f"{API_BASE_URL}/items/"
    timeout = aiohttp.ClientTimeout(total=10.0)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "data": data}

                elif response.status == 404:
                    return {
                        "success": False,
                        "message": "No items found on the server.",
                    }

                return {
                    "success": False,
                    "message": "The backend server encountered an error. "
                    f"Status code: {response.status}",
                }

    except TimeoutError:
        return {
            "success": False,
            "message": "The server took too long to respond.",
        }
    except aiohttp.ClientConnectorError:
        return {"success": False, "message": "Unable to reach the backend server."}
