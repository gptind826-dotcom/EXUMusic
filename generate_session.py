import asyncio
import json
from pathlib import Path
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

API_ID = int(input("Enter your API_ID: "))
API_HASH = input("Enter your API_HASH: ")
PHONE = input("Enter your phone number (with country code): ").strip()
PHONE_CODE = input("Enter the OTP code: ").strip()
PASSWORD = input("Enter your 2FA password (leave blank if none): ").strip()

async def main():
    client = Client("session_gen", api_id=API_ID, api_hash=API_HASH, in_memory=True, no_updates=True)
    await client.connect()
    sent = await client.send_code(PHONE)
    try:
        await client.sign_in(PHONE, sent.phone_code_hash, PHONE_CODE)
    except SessionPasswordNeeded:
        if not PASSWORD:
            raise SystemExit("2FA password is required.")
        await client.check_password(PASSWORD)

    session = await client.export_session_string()
    await client.disconnect()
    env_path = Path(".env")
    lines = env_path.read_text().splitlines() if env_path.exists() else []
    out = []
    replaced = False
    for line in lines:
        if line.startswith("STRING_SESSION="):
            out.append(f"STRING_SESSION={session}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(f"STRING_SESSION={session}")
    env_path.write_text("\n".join(out) + "\n")
    print("\n✅ Login complete. Session saved to .env")

asyncio.run(main())
