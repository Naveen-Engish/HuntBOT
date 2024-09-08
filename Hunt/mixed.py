import telebot
import csv

# Initialize the bot with your bot token
bot = telebot.TeleBot("6984563188:AAGCTJwsjeJnDclHTxI24H0D8twp5Tlr-JY")

# Global variables to store team information, confirmed user IDs, and current riddle index for each user
team_info = {}
all_team_info = []
team_sets = {}
confirmed_users = set()
user_riddle_index = {}  # Dictionary to store current riddle index for each user

MAX_TEAMS = 4  # Maximum number of teams allowed

# Example riddles and their answers
riddles = [
    {"question": "I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?", "answer": "echo"},
    {"question": "I’m light as a feather, yet the strongest man can’t hold me for more than 5 minutes. What am I?", "answer": "breath"},
    {"question": "The more you take, the more you leave behind. What am I?", "answer": "footsteps"},
    {"question": "What has keys but can’t open locks?", "answer": "piano"},
    {"question": "What can travel around the world while staying in a corner?", "answer": "stamp"},
    {"question": "What has a head, a tail, but no body?", "answer": "coin"}
]

@bot.message_handler(commands=['start'])
def start(message):
    telegram_user_id = message.from_user.id

    # Check if the user is already registered
    team_name = get_team_name_by_user_id(telegram_user_id)
    if team_name:
        bot.send_message(message.chat.id, f"Welcome back! Your team name is '{team_name}'.")
    elif len(all_team_info) >= MAX_TEAMS:
        bot.send_message(message.chat.id, "Registration is closed as we already have 6 teams.")
    else:
        bot.send_message(message.chat.id, "Please enter the team leader's mobile number:")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    telegram_user_id = message.from_user.id
    
    # If the user is answering a riddle
    if telegram_user_id in user_riddle_index:
        check_answer(message)
    else:
        get_mobile_number(message)

def get_mobile_number(message):
    telegram_user_id = message.from_user.id
    team_name = get_team_name_by_user_id(telegram_user_id)
    if team_name:
        bot.send_message(message.chat.id, f"You're already registered! Welcome back, team '{team_name}'.")
        return

    if len(all_team_info) >= MAX_TEAMS:
        bot.send_message(message.chat.id, "Registration is closed as we already have 6 teams.")
        return

    mobile_number = message.text.strip()

    global team_info

    if is_team_already_registered(mobile_number):
        bot.send_message(message.chat.id, "This team is already registered.")
        return

    with open("student.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)

        for row in csv_reader:
            if row[5] == mobile_number:
                team_info = {
                    "Team Name": row[2],
                    "Team Leader Name": row[3],
                    "Team Leader Register Number": row[4],
                    "Member 1 Name": row[8],
                    "Member 1 Register Number": row[9],
                    "Member 3 Name": row[13],
                    "Member 3 Register Number": row[14],
                    "Mobile Number": mobile_number,
                    "Telegram User ID": telegram_user_id
                }
                break

    if team_info:
        message_text = (
            f"📋 *Team Information:*\n\n"
            f"*🏷️ Team Name:*\n{team_info['Team Name']}\n\n"
            f"*👤 Team Leader:*\n"
            f"- Name: {team_info['Team Leader Name']}\n"
            f"- Register Number: {team_info['Team Leader Register Number']}\n\n"
            f"*👥 Member 1:*\n"
            f"- Name: {team_info['Member 1 Name']}\n"
            f"- Register Number: {team_info['Member 1 Register Number']}\n\n"
            f"*👥 Member 3:*\n"
            f"- Name: {team_info['Member 3 Name']}\n"
            f"- Register Number: {team_info['Member 3 Register Number']}\n"
        )
        bot.send_message(message.chat.id, message_text, parse_mode='Markdown')

        markup = telebot.types.InlineKeyboardMarkup()
        confirm_button = telebot.types.InlineKeyboardButton("Confirm", callback_data="confirm")
        markup.add(confirm_button)
        bot.send_message(message.chat.id, "Please confirm the details:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Mobile number not found. Please try again.")

def is_team_already_registered(mobile_number):
    try:
        with open("players.csv", mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)

            for row in csv_reader:
                if row[7] == mobile_number:
                    return True
    except FileNotFoundError:
        return False
    return False

@bot.callback_query_handler(func=lambda call: call.data == "confirm")
def confirm_details(call):
    user_id = call.from_user.id

    # Check if the user has already confirmed
    if user_id in confirmed_users:
        bot.answer_callback_query(call.id, "You have already confirmed your details!")
        return

    bot.answer_callback_query(call.id)
    confirmed_users.add(user_id)  # Add the user to the set of confirmed users

    bot.send_message(call.message.chat.id, "Details confirmed. Thank you!")

    if call.message.reply_markup is not None:
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error while trying to edit message: {e}")

    save_team_info_to_csv()
    handle_team_confirmation()

def save_team_info_to_csv():
    global team_info
    with open("players.csv", mode='a+', newline='') as file:
        file.seek(0)
        is_empty = file.read(1) == ''

        csv_writer = csv.writer(file)

        if is_empty:
            csv_writer.writerow([
                "Team Name", 
                "Team Leader Name", 
                "Team Leader Register Number", 
                "Member 1 Name", 
                "Member 1 Register Number", 
                "Member 3 Name", 
                "Member 3 Register Number",
                "Mobile Number",
                "Telegram User ID"
            ])
        
        csv_writer.writerow([
            team_info.get("Team Name", ""),
            team_info.get("Team Leader Name", ""),
            team_info.get("Team Leader Register Number", ""),
            team_info.get("Member 1 Name", ""),
            team_info.get("Member 1 Register Number", ""),
            team_info.get("Member 3 Name", ""),
            team_info.get("Member 3 Register Number", ""),
            team_info.get("Mobile Number", ""),
            team_info.get("Telegram User ID", "")
        ])

def get_team_name_by_user_id(telegram_user_id):
    try:
        with open("players.csv", mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)

            for row in csv_reader:
                if row[8] == str(telegram_user_id):
                    return row[0]
    except FileNotFoundError:
        return None
    return None

def handle_team_confirmation():
    global team_info
    if team_info:
        all_team_info.append(team_info)

        if len(all_team_info) == MAX_TEAMS:
            create_and_display_team_sets()

def create_and_display_team_sets():
    global team_sets
    sets = [all_team_info[i:i+2] for i in range(0, len(all_team_info), 2)]

    for idx, team_set in enumerate(sets, start=1):
        set_key = f"Set {idx}"
        riddle = riddles[idx - 1]["question"] if idx <= len(riddles) else "No riddle assigned."
        team_sets[set_key] = {
            "teams": team_set,
            "riddle": riddle
        }

        for team in team_set:
            user_riddle_index[team["Telegram User ID"]] = 0  # Start at the first riddle
            try:
                bot.send_message(team["Telegram User ID"], f"🧩 *Your Riddle:* {riddle}", parse_mode='Markdown')
            except Exception as e:
                print(f"Error sending riddle to {team['Team Name']}: {e}")

def check_answer(message):
    user_id = message.from_user.id
    current_index = user_riddle_index.get(user_id, 0)

    if current_index < len(riddles):
        correct_answer = riddles[current_index]["answer"].lower()
        if message.text.strip().lower() == correct_answer:
            user_riddle_index[user_id] += 1
            next_index = user_riddle_index[user_id]

            if next_index < len(riddles):
                next_riddle = riddles[next_index]["question"]
                bot.send_message(message.chat.id, f"Correct! Here is your next riddle:\n\n🧩 *{next_riddle}*", parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "Congratulations! You have solved all the riddles!")
        else:
            bot.send_message(message.chat.id, "Incorrect! Please try again.")
    else:
        bot.send_message(message.chat.id, "You have completed all the riddles. Well done!")

if __name__ == "__main__":
    bot.polling()
