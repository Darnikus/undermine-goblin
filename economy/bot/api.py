from dataclasses import dataclass
from typing import Literal, TypedDict

import aiohttp

from economy.bot.config import API_BASE_URL


class ItemData(TypedDict):
    id: str
    name: str
    display: str


@dataclass(frozen=True)
class OkResponse[T]:
    data: T
    success: Literal[True] = True

    def __bool__(self) -> Literal[True]:
        return True


@dataclass(frozen=True)
class FailResponse:
    message: str
    success: Literal[False] = False

    def __bool__(self) -> Literal[False]:
        return False


type ApiResponse[T] = OkResponse[T] | FailResponse


async def create_item(id: str) -> ApiResponse[tuple[ItemData, bool]]:
    api_url = f"{API_BASE_URL}items/"
    timeout = aiohttp.ClientTimeout(total=10.0)
    payload = {"id": id}

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 201:
                    data: ItemData = await response.json()
                    return OkResponse((data, True))

                elif response.status == 400:
                    error_payload: dict = await response.json()
                    message = error_payload.get("id", ["Invalid input."])[0]
                    return FailResponse(f"⚠️ {message}")

                elif response.status == 409:
                    async with session.get(
                        f"{api_url}{payload['id']}"
                    ) as get_item_response:
                        if get_item_response.status == 200:
                            item = await get_item_response.json()
                            return OkResponse((item, False))

                return FailResponse(
                    "❌ The backend server encountered an error. "
                    f"Status code: {response.status}"
                )
    except TimeoutError:
        return FailResponse("❌ The server took too long to respond.")
    except aiohttp.ClientConnectorError:
        return FailResponse("❌ Unable to reach the backend server.")


async def delete_item(id: str) -> ApiResponse[ItemData]:
    api_url = f"{API_BASE_URL}items/{id}/"
    timeout = aiohttp.ClientTimeout(total=10.0)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.delete(api_url) as response:
                if response.status == 200:
                    deleted_item: ItemData = await response.json()
                    return OkResponse(deleted_item)

                elif response.status == 404:
                    return FailResponse(f"⚠️ Item with ID: `{id}` was not found.")

                return FailResponse("❌ An error occurred while deleting the item.")

    except TimeoutError:
        return FailResponse("❌ The server took too long to respond.")
    except aiohttp.ClientConnectorError:
        return FailResponse("❌ Unable to reach the backend server.")


async def fetch_items() -> ApiResponse[list[ItemData]]:
    api_url = f"{API_BASE_URL}items/"
    timeout = aiohttp.ClientTimeout(total=10.0)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data: list[ItemData] = await response.json()
                    return OkResponse(data)

                elif response.status == 404:
                    return FailResponse("❌ No items are currently being tracked.")

                return FailResponse(
                    "❌ The backend server encountered an error. "
                    f"Status code: {response.status}"
                )

    except TimeoutError:
        return FailResponse("❌ The server took too long to respond.")

    except aiohttp.ClientConnectorError:
        return FailResponse("❌ Unable to reach the backend server.")
