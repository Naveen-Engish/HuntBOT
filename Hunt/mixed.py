import telebot
import csv

# Initialize the bot with your bot token
bot = telebot.TeleBot("6984563188:AAGCTJwsjeJnDclHTxI24H0D8twp5Tlr-JY")

# Global dictionary to store team information
team_info = {}
all_team_info = []

MAX_TEAMS = 6  # Maximum number of teams allowed

# Function to handle the team leader's mobile number input
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
def get_mobile_number(message):
    # Check if the user is already registered
    telegram_user_id = message.from_user.id
    team_name = get_team_name_by_user_id(telegram_user_id)
    if team_name:
        bot.send_message(message.chat.id, f"You're already registered! Welcome back, team '{team_name}'.")
        return

    # Check if the maximum number of teams has been reached
    if len(all_team_info) >= MAX_TEAMS:
        bot.send_message(message.chat.id, "Registration is closed as we already have 6 teams.")
        return

    mobile_number = message.text

    global team_info  # Ensure that we're modifying the global team_info dictionary

    if is_team_already_registered(mobile_number):
        bot.send_message(message.chat.id, "This team is already registered.")
        return

    with open("student.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Skip the header

        # Iterate through rows to find the matching mobile number
        for row in csv_reader:
            if row[5] == mobile_number:  # 6th column is at index 5
                team_info = {
                    "Team Name": row[2],  # 3rd column
                    "Team Leader Name": row[3],  # 4th column
                    "Team Leader Register Number": row[4],  # 5th column
                    "Member 1 Name": row[8],  # 9th column
                    "Member 1 Register Number": row[9],  # 10th column
                    "Member 3 Name": row[13],  # 14th column
                    "Member 3 Register Number": row[14],  # 15th column,
                    "Mobile Number": mobile_number,
                    "Telegram User ID": telegram_user_id
                }
                break

    if team_info:
        # Create a neat and sectioned message with the team information
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
        # Send the neatly formatted and sectioned team information to the user
        bot.send_message(message.chat.id, message_text, parse_mode='Markdown')

        # Ask for confirmation
        markup = telebot.types.InlineKeyboardMarkup()
        confirm_button = telebot.types.InlineKeyboardButton("Confirm", callback_data="confirm")
        markup.add(confirm_button)
        bot.send_message(message.chat.id, "Please confirm the details:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Mobile number not found. Please try again.")

# Function to check if a team is already registered
def is_team_already_registered(mobile_number):
    try:
        with open("players.csv", mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header

            # Check if the mobile number already exists
            for row in csv_reader:
                if row[7] == mobile_number:  # Assuming mobile number is stored at index 7
                    return True
    except FileNotFoundError:
        # File not found, meaning no teams have been registered yet
        return False
    return False

# Handle the confirmation button click
@bot.callback_query_handler(func=lambda call: call.data == "confirm")
def confirm_details(call):
    bot.answer_callback_query(call.id)

    bot.send_message(call.message.chat.id, "Details confirmed. Thank you!")
    
    # Only attempt to edit the message if there is a reply markup to remove
    if call.message.reply_markup is not None:
        try:
            # Attempt to remove the reply markup
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except telebot.apihelper.ApiTelegramException as e:
            # Handle the exception if the message cannot be modified
            print(f"Error while trying to edit message: {e}")

    # Save the team info to a CSV file named 'players.csv'
    save_team_info_to_csv()

    # Handle team confirmation and print elapsed time
    handle_team_confirmation()

def save_team_info_to_csv():
    """Function to save the current team info to a CSV file."""
    global team_info
    with open("players.csv", mode='a+', newline='') as file:
        file.seek(0)  # Move to the start of the file
        is_empty = file.read(1) == ''  # Check if the file is empty
        
        csv_writer = csv.writer(file)
        
        # If file is empty, write the header first
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
        
        # Write team information
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
    """Function to get the team name by the user's Telegram ID."""
    try:
        with open("players.csv", mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header

            # Check if the user's Telegram ID already exists
            for row in csv_reader:
                if row[8] == str(telegram_user_id):  # Assuming Telegram user ID is at index 8
                    return None#row[0]  # Return the team name
    except FileNotFoundError:
        # File not found, meaning no teams have been registered yet
        return None
    return None

def handle_team_confirmation():
    """Handle a single team's confirmation and display their team number."""
    global team_info
    if team_info:
        all_team_info.append(team_info)  # Save team info details

        if len(all_team_info) == MAX_TEAMS:
            display_team_sets()

def display_team_sets():
    """Display sets of teams in both console and Telegram."""
    sets = [all_team_info[i:i+2] for i in range(0, len(all_team_info), 2)]
    sets_message = "Teams have been divided into sets:\n"

    for idx, team_set in enumerate(sets, start=1):
        sets_message += f"\nSet {idx}:\n"
        for team in team_set:
            sets_message += f" - {team['Team Name']}\n"

    print(sets_message)

    # Send the sets information to each team member via Telegram
    for team in all_team_info:
        bot.send_message(team["Telegram User ID"], sets_message)

if __name__ == "__main__":
    bot.polling()
