import telebot
import csv
import time

# Initialize the bot with your bot token
bot = telebot.TeleBot("6984563188:AAGCTJwsjeJnDclHTxI24H0D8twp5Tlr-JY")

# Global dictionary to store team information
team_info = {}
all_team_info = []

# Start the clock when the script is first run
start_time = time.time()

# Function to handle the team leader's mobile number input
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Please enter the team leader's mobile number:")

@bot.message_handler(func=lambda message: True)
def get_mobile_number(message):
    mobile_number = message.text
    global team_info  # Ensure that we're modifying the global team_info dictionary

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
                    "Member 3 Register Number": row[14],  # 15th column
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
                "Member 3 Register Number"
            ])
        
        # Write team information
        csv_writer.writerow([
            team_info.get("Team Name", ""),
            team_info.get("Team Leader Name", ""),
            team_info.get("Team Leader Register Number", ""),
            team_info.get("Member 1 Name", ""),
            team_info.get("Member 1 Register Number", ""),
            team_info.get("Member 3 Name", ""),
            team_info.get("Member 3 Register Number", "")
        ])

def handle_team_confirmation():
    """Handle a single team's confirmation and display their team number."""
    global team_info
    if team_info:
        all_team_info.append(team_info)  # Save team info details
        team_index = len(all_team_info)
        print(f"Team {team_index} is ready.")
        
        # Calculate elapsed time since the script started
        elapsed_time = time.time() - start_time
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        
        # Print the elapsed time to the console
        print(f"Elapsed Time: {formatted_time}")

if __name__ == "__main__":
    bot.polling()
