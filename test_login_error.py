import httpx
import asyncio
import sys

async def test():
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post("http://127.0.0.1:8000/auth/login", data={"username": "test@example.com", "password": "password"})
            print(res.status_code, res.text)
    except Exception as e:
        print(e)

asyncio.run(test())
