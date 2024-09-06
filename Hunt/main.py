import regi

# List to store all team information dictionaries
all_team_info = []

def handle_team_confirmation(team_info):
    """Handle a single team's confirmation and display their team number."""
    if team_info:
        all_team_info.append(team_info)
        team_index = len(all_team_info)
        print(f"Team {team_index} is ready.")

def confirm_callback(message):
    """Callback function for handling confirmation messages from teams."""
    # Assume that regi has a method to get team info from the message.
    team_info = regi.return_team_info(message)  # Adjust if necessary based on regi's implementation
    
    # Handle team confirmation
    handle_team_confirmation(team_info)
    
    # Send confirmation message back to the team
    regi.bot.send_message(message.chat.id, f"Your team is confirmed as Team {len(all_team_info)}!")

if __name__ == "__main__":
    # Register the confirm callback to handle when the confirm button is clicked
    regi.bot.callback_query_handler(func=lambda call: call.data == "confirm")(confirm_callback)
    
    # Start the bot to handle team info
    regi.bot.polling()
