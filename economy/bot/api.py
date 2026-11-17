import aiohttp

from economy.bot.config import API_BASE_URL


async def create_item(id: str):
    api_url = f"{API_BASE_URL}items/"
    timeout = aiohttp.ClientTimeout(total=10.0)
    payload = {"id": id}

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    return {"success": True, "data": data, "created": True}

                elif response.status == 400:
                    error_payload: dict = await response.json()
                    message = error_payload.get("id", ["Invalid input."])[0]
                    return {
                        "success": False,
                        "message": f"⚠️ {message}",
                    }

                elif response.status == 409:
                    async with session.get(
                        f"{api_url}{payload['id']}"
                    ) as get_item_response:
                        if get_item_response.status == 200:
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
    api_url = f"{API_BASE_URL}items/{id}/"
    timeout = aiohttp.ClientTimeout(total=10.0)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.delete(api_url) as response:
                if response.status == 200:
                    deleted_item = await response.json()
                    return {"success": True, "data": deleted_item}

                elif response.status == 404:
                    return {
                        "success": False,
                        "message": f"⚠️ Item with ID: `{id}` was not found.",
                    }

                return {
                    "success": False,
                    "message": "❌ An error occurred while deleting the item.",
                }

    except TimeoutError:
        return {
            "success": False,
            "message": "The server took too long to respond.",
        }
    except aiohttp.ClientConnectorError:
        return {"succe>ss": False, "message": "Unable to reach the backend server."}


async def fetch_items():
    api_url = f"{API_BASE_URL}items/"
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
                        "message": "No items are currently being tracked.",
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
