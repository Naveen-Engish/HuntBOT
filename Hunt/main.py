import threading
import regi

# Assuming your script file is named your_script_name.py

# List to store all team information dictionaries
all_team_info = []

def handle_team_info():
    while True:
        team_info = regi.return_team_info()
        if team_info:
            all_team_info.append(team_info)
            team_index = len(all_team_info)
            print(f"Team {team_index} is ready.")

def submit_event():
    print("Submit button pressed. Please wait for event to begin.")
    while True:
        user_input = input()
        if user_input == '0':
            print("Starting now")
            break

if __name__ == "__main__":
    # Start the bot in a separate thread to handle the team info
    threading.Thread(target=regi.bot.polling, daemon=True).start()
    
    # Continuously handle team info as they confirm
    handle_team_info_thread = threading.Thread(target=handle_team_info, daemon=True)
    handle_team_info_thread.start()
    
    # Wait for all teams to confirm and then show the submit button
    while True:
        if len(all_team_info) > 0:  # Wait until at least one team confirms
            print("All teams confirmed. Press submit to continue.")
            input("Press Enter to display the submit button...")

            # Simulate submit button pressed (in reality, you'd trigger this in the bot)
            submit_event()
            break
