try:
    from pyrogram import Client, filters
    from pyrogram.types import Message
except Exception as e:
    print(e)
    print("\nInstall pyrogram: pip3 install pyrogram")
    exit(1)

print("Required pyrogram V2 or greater.")

# Set up your bot's API credentials
BOT_API_KEY = "6749453240:AAGFKXhD8_Y7dax0cmCkvs9tZ_WXQ4usK34"

# Initialize the bot client
app = Client("bot", bot_token=BOT_API_KEY)

# Command handler for /start
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply("Hello, this is a simple Pyrogram string session generator bot made by @The_Bots_Wallah. Send /create to create a string session.")

# Dictionary to store user states and data
user_data = {}

# Command handler for /create
@app.on_message(filters.command("create"))
async def create_command(client: Client, message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {"state": "api_id"}
    await message.reply("Please send your API ID.")

# Function to handle messages in different states
@app.on_message(filters.text & ~filters.command)
async def handle_input(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        return
    
    state = user_data[user_id].get("state")
    
    if state == "api_id":
        try:
            user_data[user_id]["api_id"] = int(message.text)
            user_data[user_id]["state"] = "api_hash"
            await message.reply("Please send your API HASH.")
        except ValueError:
            await message.reply("Invalid API ID. Please enter a valid number.")
        
    elif state == "api_hash":
        user_data[user_id]["api_hash"] = message.text
        user_data[user_id]["state"] = "phone_number"
        await message.reply("Please send your phone number.")
        
    elif state == "phone_number":
        user_data[user_id]["phone_number"] = message.text
        user_data[user_id]["state"] = "otp"
        
        try:
            # Create a temporary client to send the code
            temp_client = Client(
                "temp",
                api_id=user_data[user_id]["api_id"],
                api_hash=user_data[user_id]["api_hash"]
            )
            async with temp_client:
                sent_code = await temp_client.send_code(phone_number=user_data[user_id]["phone_number"])
                user_data[user_id]["phone_code_hash"] = sent_code.phone_code_hash
            
            await message.reply("Please send the OTP you received.")
        except Exception as e:
            await message.reply(f"Error sending code: {e}")
        
    elif state == "otp":
        user_data[user_id]["otp"] = message.text
        user_data[user_id]["state"] = "2fa"
        await message.reply("If you have 2FA enabled, please send your password. Otherwise, send 'None'.")
        
    elif state == "2fa":
        user_data[user_id]["password"] = message.text if message.text.lower() != "none" else None
        
        api_id = user_data[user_id]["api_id"]
        api_hash = user_data[user_id]["api_hash"]
        phone_number = user_data[user_id]["phone_number"]
        otp = user_data[user_id]["otp"]
        password = user_data[user_id]["password"]
        phone_code_hash = user_data[user_id]["phone_code_hash"]
        
        try:
            # Create a client to generate the session string
            async with Client(
                "generate_session",
                api_id=api_id,
                api_hash=api_hash
            ) as gen_client:
                await gen_client.sign_in(phone_number=phone_number, phone_code_hash=phone_code_hash, phone_code=otp)
                if password:
                    await gen_client.check_password(password)
                session_string = await gen_client.export_session_string()
                await message.reply(f"Your session string is: \n\n{session_string}")
        except Exception as e:
            await message.reply(f"Error generating session string: {e}")
        
        # Clear user data after session generation
        del user_data[user_id]

# Run the bot
app.run()
