import telebot
import csv

# Initialize the bot with your bot token
bot = telebot.TeleBot("7203587973:AAGEYfH-VaZB_pyNj0BECl0Z2nDiSArGSCo")

# Global dictionary to store team information
team_info = {}

# Function to handle the team leader's mobile number input
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Please enter the team leader's mobile number:")

@bot.message_handler(func=lambda message: True)
def get_mobile_number(message):
    mobile_number = message.text
    global team_info

    with open("C:/Users/USER/Desktop/Hunt/student.csv.csv", mode='r') as file:
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
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    
    # After confirmation, return the team_info to the main script
    return_team_info()

# Function to return team_info after confirmation (called from main.py)
def return_team_info():
    return team_info

if __name__ == "__main__":
    bot.polling()
