TSIS4 Snake Game
Snake Game with PostgreSQL leaderboard and advanced gameplay.

Features
PostgreSQL database integration
Username entry in Pygame
Auto-save result after game over
Top 10 leaderboard screen
Personal best during gameplay
Weighted food
Food disappears after timer
Poison food
Power-ups: speed boost, slow motion, shield
Obstacles starting from Level 3
Settings saved in settings.json
Main Menu, Game Over, Leaderboard, Settings screens
Files
main.py = starts the game and controls screens
game.py = snake gameplay logic
db.py = PostgreSQL functions
config.py = database connection settings
settings_manager.py = save/load settings.json
ui.py = buttons, text, username input
settings.json = user settings
PostgreSQL
Create database first:

CREATE DATABASE snake_db;
Then edit config.py password.

Tables are created automatically when you run main.py.
