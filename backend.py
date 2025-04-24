import tkinter as tk
from tkinter import messagebox
import sqlite3
import json
from PIL import Image, ImageTk
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Database setup
def setup_database():
    conn = sqlite3.connect('adventure_game.db')
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS enemies")
    c.execute('''CREATE TABLE enemies
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  health INTEGER, 
                  attack_power INTEGER)''')

    enemy_data = [
        ("goblin", 50, 10),
    ]
    c.executemany("INSERT INTO enemies (name, health, attack_power) VALUES (?, ?, ?)", enemy_data)

    c.execute('''CREATE TABLE IF NOT EXISTS players
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  progress TEXT, 
                  inventory TEXT, 
                  health INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS story
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  scene TEXT, 
                  description TEXT, 
                  choice1 TEXT, 
                  choice2 TEXT, 
                  result1 TEXT, 
                  result2 TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  description TEXT, 
                  effect TEXT)''')

    c.execute("SELECT COUNT(*) FROM story")
    if c.fetchone()[0] == 0:
        story_data = [
            ("start", "Welcome to the Adventure Game! Enter your name to begin.", "", "", "", ""),
            ("forest", "You find yourself in a dark forest. Do you go 'left' or 'right'?", "left", "right", "cave", "village"),
            ("cave", "You find a cave. Do you 'enter' or 'continue'?", "enter", "continue", "treasure", "forest"),
            ("treasure", "You discover a treasure chest!", "go-back", "open-it", "death", "treasure-2"),
            ("village", "You arrive at a village. Do you 'talk' to the villagers or 'explore'?", "talk", "explore", "quest", "forest"),
            ("quest", "A villager asks you to find a 'sword'. Do you accept?", "yes", "no", "find_sword", "village"),
            ("find_sword", "You search for the sword. Do you 'search' the forest or 'buy' it?", "search", "buy", "sword_found", "village"),
            ("sword_found", "You found the sword! Return to the village.", "return", "explore", "village", "battle"),
            ("battle", "A wild goblin appears! Do you 'attack' or 'run'?", "attack", "run", "battle_result", "forest"),
        ]

        # Insert the new story data here
        story_data.extend([
            ("hidden_lab", "You stumble upon a hidden research lab. Do you 'enter' cautiously or 'scan' from outside?", "enter", "scan", "ai_core", "lab_scan"),
            ("ai_core", "Inside, an AI wakes up and asks for help. Do you 'assist' it or 'disable' it?", "assist", "disable", "ai_friend", "ai_shutdown"),
            ("ai_friend", "The AI gives you access to its database and maps to alien tech. You win!", "", "", "", ""),
            ("ai_shutdown", "Disabling the AI triggers a self-destruct timer! Do you 'run' or 'override'?", "run", "override", "escape", "override_success"),
            ("escape", "You barely escape as the lab explodes behind you.", "", "", "", ""),
            ("override_success", "You stop the self-destruct and salvage rare tech. You win!", "", "", "", ""),
            ("lab_scan", "You detect radiation inside. Do you 'enter' anyway or 'leave'?", "enter", "leave", "ai_core", "camp"),
            ("forest_planet", "You land on a lush forest planet. Do you 'collect samples' or 'search ruins'?", "collect samples", "search ruins", "sample_poison", "temple_entrance"),
            ("sample_poison", "The plant samples are toxic. Do you 'treat' or 'quarantine'?", "treat", "quarantine", "recovery", "safe_lab"),
            ("recovery", "You are treated successfully. Mission continues.", "", "", "", ""),
            ("safe_lab", "Quarantine works. The base remains safe.", "", "", "", ""),
            ("temple_entrance", "You find an overgrown alien temple. Do you 'enter' or 'scan'?", "enter", "scan", "puzzle_room", "secret_passage"),
            ("puzzle_room", "You face a puzzle of lights and glyphs. Do you 'solve' or 'force door'?", "solve", "force door", "treasure_room", "alarm"),
            ("alarm", "Forcing the door triggers an alarm. Security bots attack!", "", "", "", ""),
            ("treasure_room", "Inside you find ancient alien treasure. You win!", "", "", "", ""),
            ("secret_passage", "You discover a hidden route to a control room. Do you 'explore' or 'leave'?", "explore", "leave", "control_room", "temple_entrance"),
            ("control_room", "The control room activates a holographic map of the galaxy. Do you 'record' or 'broadcast'?", "record", "broadcast", "new_mission", "attention"),
            ("new_mission", "You receive coordinates to a mysterious new system. To be continued...", "", "", "", ""),
            ("attention", "Broadcasting alerts unknown beings... a ship is approaching!", "", "", "", ""),
            ("asteroid_field", "Your ship drifts into an asteroid field. Do you 'navigate' or 'wait'?", "navigate", "wait", "safe_passage", "ambush"),
            ("safe_passage", "You make it through the asteroids unharmed.", "", "", "", ""),
            ("ambush", "Space pirates ambush you! Do you 'fight' or 'escape'?", "fight", "escape", "win_battle", "damaged"),
            ("win_battle", "You defeat the pirates and salvage their tech. You win!", "", "", "", ""),
            ("damaged", "Your ship is badly damaged. Do you 'repair' or 'send signal'?", "repair", "send signal", "fix_ship", "rescue_arrives"),
            ("fix_ship", "You repair the ship and continue your mission.", "", "", "", ""),
            ("rescue_arrives", "A friendly ship arrives and rescues you. You're safe!", "", "", "", ""),
        ])

        # Add the new space mission story data
        story_data.extend([
            ("start", "Welcome aboard the Starship Orion! Enter your name to begin your space mission.", "", "", "", ""),
            ("orbit", "You are now orbiting an unknown planet. Do you 'scan' the surface or 'land' immediately?", "scan", "land", "scan_result", "landing_site"),
            ("scan_result", "Scans show energy signals and a suitable landing site. Do you 'investigate' the signals or 'land' at the site?", "investigate", "land", "alien_signal", "landing_site"),
            ("alien_signal", "You trace the signal to an alien structure. Do you 'enter' or 'report' back to base?", "enter", "report", "ancient_ruins", "orbit"),
            ("landing_site", "You safely land on the planet. Do you 'explore' the nearby cave or 'set up' camp?", "explore", "set up", "crystal_cave", "camp"),
            ("ancient_ruins", "Inside, you find an ancient alien computer. Do you try to 'activate' it or 'leave'?", "activate", "leave", "artifact_found", "orbit"),
            ("artifact_found", "You discover a powerful alien artifact! Do you 'take' it or 'secure' the site?", "take", "secure", "return_home", "alien_signal"),
            ("crystal_cave", "The cave is filled with glowing crystals. Do you 'collect' samples or 'go deeper'?", "collect", "go deeper", "camp", "underground_lake"),
            ("underground_lake", "You find a hidden underground lake with bioluminescent lifeforms. You win!", "", "", "", ""),
            ("camp", "Your team rests safely. Suddenly, sensors detect movement. Do you 'investigate' or 'stay' alert?", "investigate", "stay", "alien_creature", "camp_safe"),
            ("alien_creature", "You find a peaceful alien creature. It gives you a map to secret ruins. You win!", "", "", "", ""),
            ("camp_safe", "The night passes quietly. Mission success without incident.", "", "", "", ""),
            ("return_home", "You return to Earth with the alien artifact. Humanity celebrates your discovery!", "", "", "", ""),
        ])

        c.executemany("INSERT INTO story (scene, description, choice1, choice2, result1, result2) VALUES (?, ?, ?, ?, ?, ?)", story_data)

    conn.commit()
    conn.close()


def save_progress(player_name, progress, inventory, health):
    conn = sqlite3.connect('adventure_game.db')
    c = conn.cursor()
    c.execute("INSERT INTO players (name, progress, inventory, health) VALUES (?, ?, ?, ?)", 
              (player_name, progress, json.dumps(inventory), health))
    conn.commit()
    conn.close()


def load_progress(player_name):
    conn = sqlite3.connect('adventure_game.db')
    c = conn.cursor()
    c.execute("SELECT progress, inventory, health FROM players WHERE name=?", (player_name,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0], json.loads(result[1]), result[2]
    return None, [], 100


def load_scene(scene_id):
    conn = sqlite3.connect('adventure_game.db')
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM story WHERE scene=?", (scene_id,))
        result = c.fetchone()
        if result is None:
            raise sqlite3.OperationalError("Scene not found in the database.")
        print(f"Loaded scene: {result}")  # Debug print
    except sqlite3.OperationalError as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        result = None
    conn.close()
    return result


def load_enemy(enemy_name):
    conn = sqlite3.connect('adventure_game.db')
    c = conn.cursor()
    c.execute("SELECT * FROM enemies WHERE name=?", (enemy_name,))
    result = c.fetchone()
    conn.close()
    return result


class AdventureGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Trails of Felwinter")
        self.player_name = ""
        self.current_scene = "start"
        self.inventory = []
        self.health = 100
        self.enemy = None

        # Title label
        self.label = tk.Label(root, text="Welcome to the Trails of Felwinter!", font=("Arial", 20))
        self.label.pack(pady=20)

        # Image label (move this above the text area)
        self.images = {}  # Dictionary to store images
        self.image_label = tk.Label(root)  # Label to display images
        self.image_label.pack(pady=10)  # Place it above the text area

        # Text area for messages
        self.text_area = tk.Text(root, height=10, width=50, wrap=tk.WORD)
        self.text_area.pack(pady=10)

        # Input entry box
        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=10)

        # Submit button
        self.button = tk.Button(root, text="Submit", command=self.process_input)
        self.button.pack(pady=10)

        self.load_images()  # Load images
        self.start_game()

    def load_images(self):
        try:
            self.images["start"] = ImageTk.PhotoImage(Image.open("images/start_image.png"))
            print("Loaded start.png successfully!")
        except Exception as e:
            print(f"Error loading start.png: {e}")
            messagebox.showerror("Image Load Error", f"Error loading images: {e}")

    def type_text(self, text, delay=30):
        if not text:
            text = "No text available.\n"
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)  # Clear the text area

        def animate(i=0):
            if i < len(text):
                self.text_area.insert(tk.END, text[i])  # Insert one character at a time
                self.text_area.see(tk.END)
                self.text_area.after(delay, animate, i+1)
            else:
                self.text_area.insert(tk.END, "\n")  # Add a newline at the end

        animate()

    def start_game(self):
        self.display_scene(self.current_scene)
        self.root.mainloop()

    def display_scene(self, scene_id):
        scene = load_scene(scene_id)
        if not scene:
            self.type_text("Error: Scene not found.\n")
            return

        text = scene[2] + "\n"  # Scene description
        if scene[3] and scene[4]:  # Add choices if available
            text += f"Choices: {scene[3]} or {scene[4]}\n"

        if scene_id == "battle" and self.enemy:
            text += f"Your health: {self.health}\n"
            text += f"{self.enemy[1]}'s health: {self.enemy[2]}\n"
            text += "Type 'attack' to attack or 'run' to run away.\n"

        # Display the image for the current scene
        if scene_id in self.images:
            self.image_label.config(image=self.images[scene_id])
        else:
            self.image_label.config(image="")  # Clear the label if no image exists

        print(f"Current scene: {self.current_scene}")
        print(f"Player name: {self.player_name}")

        self.type_text(text)

    def process_input(self):
        user_input = self.entry.get().strip()  # Get and strip whitespace from input
        self.entry.delete(0, tk.END)  # Clear the input box

        if self.current_scene == "start":
            if user_input:  # Ensure the player enters a name
                self.player_name = user_input
                self.type_text(f"Welcome, {self.player_name}! Your adventure begins now.\n")
                self.current_scene = "forest"  # Transition to the next scene
                self.display_scene(self.current_scene)
            else:
                self.type_text("Please enter your name to begin.\n")
        elif self.current_scene == "battle":
            self.handle_battle(user_input)
        else:
            scene = load_scene(self.current_scene)
            if scene:
                if user_input.lower() == scene[3]:  # Choice 1
                    self.current_scene = scene[5]
                elif user_input.lower() == scene[4]:  # Choice 2
                    self.current_scene = scene[6]
                else:
                    self.type_text("Invalid choice. Try again.\n")
                    return

                if scene[2] == 'You found the sword! Return to the village.':
                    self.inventory = ['sword']

                if self.current_scene == "battle":
                    self.enemy = load_enemy("goblin")
                    self.display_scene(self.current_scene)
                else:
                    self.display_scene(self.current_scene)

    def handle_battle(self, user_input):
        if user_input.lower() == "attack":
            self.attack_enemy()
        elif user_input.lower() == "run":
            self.type_text("You ran away!\n")
            self.current_scene = "forest"
            self.display_scene(self.current_scene)
        else:
            self.type_text("Invalid choice. Type 'attack' or 'run'.\n")

    def attack_enemy(self):
        player_attack = 10
        if "sword" in self.inventory:
            player_attack += 5

        self.enemy = (self.enemy[0], self.enemy[1], self.enemy[2] - player_attack, self.enemy[3])
        self.type_text(f"You attacked the {self.enemy[1]} for {player_attack} damage!\n")

        if self.enemy[2] <= 0:
            self.type_text(f"You defeated the {self.enemy[1]}!\n")
            self.current_scene = "forest"
            self.display_scene(self.current_scene)
        else:
            self.enemy_attack()

    def enemy_attack(self):
        enemy_attack_power = self.enemy[3]
        self.health -= enemy_attack_power

        if self.health <= 0:
            self.type_text("You died!\n")
            self.end_game("death")
        else:
            self.type_text(f"The {self.enemy[1]} attacked you for {enemy_attack_power} damage!\n"
                           f"Your health: {self.health}\n"
                           f"{self.enemy[1]}'s health: {self.enemy[2]}\n"
                           "Type 'attack' to attack or 'run' to run away.\n")

    def end_game(self, outcome):
        if outcome == "death":
            self.type_text("Game over! You have been defeated.\n")
        else:
            self.type_text("Congratulations! You have won the game.\n")
        save_progress(self.player_name, outcome, self.inventory, self.health)
        messagebox.showinfo("Game Over", "The game has ended.")
        self.root.quit()


if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    game = AdventureGame(root)
