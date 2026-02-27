import httpx
import asyncio

async def test_register():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post('http://127.0.0.1:8000/auth/register', json={"email":"test5@example.com", "password":"password"}, timeout=3.0)
            print(response.status_code)
            print(response.text)
        except Exception as e:
            print("Error connecting:", type(e).__name__)

if __name__ == "__main__":
    asyncio.run(test_register())
