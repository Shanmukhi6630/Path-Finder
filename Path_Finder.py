import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from PIL import Image, ImageTk
import random
from queue import Queue, LifoQueue
import pygame

class GridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grid Path Finder")

        self.root.attributes("-fullscreen", True)
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.grid_size = 7
        self.images = []
        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.used_positions = set()
        self.start_position = None
        self.end_position = None

        self.image_paths = {
            "tree": "C:/Users/Dell/OneDrive/Desktop/treegiffff.gif",
            "hotel": "C:/Users/Dell/OneDrive/docunments/hotel.png",
            "hospital": "C:/Users/Dell/Downloads/hospital.png",
            "home": "C:/Users/Dell/OneDrive/docunments/home.png",
            "police station": "C:/Users/Dell/OneDrive/docunments/police station.png",
            "supermarket": "C:/Users/Dell/OneDrive/Desktop/super market.png",
            "pet store": "C:/Users/Dell/OneDrive/docunments/pet store.png",
            "food court": "C:/Users/Dell/OneDrive/docunments/food stalls.png",
            "park": "C:/Users/Dell/Downloads/park.png",
            "stationery": "C:/Users/Dell/OneDrive/docunments/stationery.png",
            "university": "C:/Users/Dell/OneDrive/docunments/university.png",
            "carnival": "C:/Users/Dell/OneDrive/docunments/carnival.png"
        }
        self.dead_end_path = "C:/Users/Dell/Downloads/dead end.png"
        self.locations = list(self.image_paths.keys())

        self.start_location = tk.StringVar(value=self.locations[0])
        self.end_location = tk.StringVar(value=self.locations[1])

        self.sound_click = "C:/Users/Dell/Downloads/switch-light-04-82204.mp3"
        self.background_music = "C:/Users/Dell/Downloads/DRIVE(chosic.com).mp3"
        self.reached_audio_path = "C:/Users/Dell/Downloads/reached_audio.mp3"

        self.init_pygame()
        self.setup_home_page()

    def init_pygame(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(self.background_music)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            messagebox.showerror("Pygame Error", f"Error initializing Pygame: {e}")

    def play_sound(self, sound_path):
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.play()
        except pygame.error as e:
            messagebox.showerror("Pygame Error", f"Error playing sound: {e}")

    def setup_home_page(self):
        self.home_frame = tk.Frame(self.root)
        self.home_frame.pack(fill='both', expand=True)

        bg_image_path = "C:/Users/Dell/OneDrive/Desktop/deadendppt.png"
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((self.width, self.height), Image.LANCZOS)
        bg_image = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(self.home_frame, width=self.width, height=self.height)
        canvas.pack(fill='both', expand=True)
        canvas.create_image(0, 0, image=bg_image, anchor='nw')
        canvas.image = bg_image  # keep a reference to prevent garbage collection

        start_button = tk.Button(self.home_frame, text="Start", bg="yellow", font=("Helvetica", 16), relief="solid", width=10, height=1, command=self.navigate_to_input_page)
        start_button.place(relx=0.5, rely=0.5, anchor='center')

    def navigate_to_input_page(self):
        self.home_frame.pack_forget()
        self.setup_input_page()

    def setup_input_page(self):
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.BOTH, expand=True)

        self.bg_image_path = "C:/Users/Dell/Downloads/b g 2 [MConverter.eu].png"
        self.bg_image = ImageTk.PhotoImage(Image.open(self.bg_image_path).resize((self.width, self.height), Image.LANCZOS))
        self.bg_label = tk.Label(self.input_frame, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)

        self.content_frame = tk.Frame(self.input_frame, bg='white', bd=10)
        self.content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.content_frame, text="Select Location and Destination", font=('Helvetica', 18, 'bold'), bg='white').pack(pady=20)

        self.create_dropdown(self.content_frame, "Select Start Point", self.start_location, self.locations)
        self.create_dropdown(self.content_frame, "Select End Point", self.end_location, self.locations)

        start_button = tk.Button(self.content_frame, text="Start", command=lambda: [self.play_sound(self.sound_click), self.setup_grid_page()], bg="yellow")
        start_button.pack(pady=20)

    def create_dropdown(self, parent, label_text, variable, options):
        tk.Label(parent, text=label_text, font=('Helvetica', 16, 'bold'), bg='white').pack(pady=10)
        dropdown = tk.OptionMenu(parent, variable, *options, command=lambda _: self.play_sound(self.sound_click))
        dropdown.config(bg="#DE3163", fg="white")
        dropdown.pack(pady=10)

    def setup_grid_page(self):
        self.input_frame.pack_forget()
        self.create_grid_page()

    def create_grid_page(self):
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.grid_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.resize)

        self.status_bar = ttk.Label(self.grid_frame, text="Status: Running", relief=tk.SUNKEN, anchor='w')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Add Back and Exit buttons at the bottom
        self.back_button = tk.Button(self.grid_frame, text="Back", command=self.navigate_to_input_page)
        self.exit_button = tk.Button(self.grid_frame, text="Exit", command=self.root.quit)
        self.back_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.exit_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.images = []
        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.used_positions = set()

        cell_width = self.width // self.grid_size
        cell_height = self.height // self.grid_size

        self.load_images(cell_width, cell_height)
        self.place_images_randomly()

        start_idx, end_idx = self.locations.index(self.start_location.get()), self.locations.index(self.end_location.get())
        self.place_start_end_points(start_idx, end_idx)
        self.draw_grid()

    def resize(self, event):
        self.width = event.width
        self.height = event.height
        self.draw_grid()
        self.redraw_grid()

    def draw_grid(self):
        self.canvas.delete("grid_line")
        for i in range(self.grid_size + 1):
            x = i * self.width // self.grid_size
            self.canvas.create_line(x, 0, x, self.height, fill="black", width=3, tags="grid_line")
            self.canvas.create_line(0, y, self.width, y, fill="black", width=3, tags="grid_line")

    def redraw_grid(self):
        cell_width = self.width // self.grid_size
        cell_height = self.height // self.grid_size
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cell = self.grid[i][j]
                if cell and "window" in cell:
                    self.canvas.coords(cell["window"], j * cell_width + cell_width // 2, i * cell_height + cell_height // 2)

    def load_and_resize_image(self, image_path, w, h):
        try:
            img = Image.open(image_path)
            img = img.resize((w, h), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            messagebox.showerror("Image Error", f"Error loading image {image_path}: {e}")
            return None

    def load_images(self, cell_width, cell_height):
        for image_name, image_path in self.image_paths.items():
            img = self.load_and_resize_image(image_path, cell_width, cell_height)
            if img:
                self.images.append((image_name, img))

    def place_images_randomly(self):
        positions = random.sample([(i, j) for i in range(self.grid_size) for j in range(self.grid_size)], len(self.images))

        for pos, (image_name, img) in zip(positions, self.images):
            i, j = pos
            image_window = self.canvas.create_image(j * self.width // self.grid_size + self.width // self.grid_size // 2, i * self.height // self.grid_size + self.height // self.grid_size // 2, image=img, tags="image")
            self.grid[i][j] = {"image_name": image_name, "image": img, "window": image_window}
            self.used_positions.add((i, j))

    def place_start_end_points(self, start_idx, end_idx):
        self.start_position = self.find_location_index(self.locations[start_idx])
        self.end_position = self.find_location_index(self.locations[end_idx])

        if self.start_position is None or self.end_position is None:
            messagebox.showerror("Error", "Start or End position not found")
            self.setup_input_page()
            return

        self.place_point(self.start_position, self.image_paths[self.locations[start_idx]])
        self.place_point(self.end_position, self.image_paths[self.locations[end_idx]])

        shortest_path = self.find_path(self.start_position, self.end_position)
        longest_path = self.find_longest_path(self.start_position, self.end_position)
        alt_longest_path = self.find_alternative_longest_path(self.start_position, self.end_position)

        if self.is_adjacent(self.start_position, self.end_position) and alt_longest_path:
            self.blink_path(alt_longest_path)
        elif shortest_path and longest_path:
            if shortest_path != longest_path:
                self.show_path_options(shortest_path, longest_path)
            else:
                self.blink_path(shortest_path)
        elif shortest_path:
            self.blink_path(shortest_path)
        else:
            self.handle_no_path()

    def place_point(self, position, image_path):
        x, y = position
        cell_width = self.width // self.grid_size
        cell_height = self.height // self.grid_size

        img = self.load_and_resize_image(image_path, cell_width, cell_height)
        if img:
            self.grid[x][y] = {"image": img, "window": self.canvas.create_image(y * cell_width + cell_width // 2, x * cell_height + cell_height // 2, image=img, tags="image")}

    def handle_no_path(self):
        self.status_bar.config(text="Status: No path found.")
        try_again_button = tk.Button(self.grid_frame, text="Try Again", command=self.navigate_to_input_page)
        try_again_button.pack(side=tk.BOTTOM, pady=20)

        cell_width = self.width // self.grid_size
        cell_height = self.height // self.grid_size
        dead_end_img = self.load_and_resize_image(self.dead_end_path, cell_width, cell_height)

        current_position = self.start_position
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while current_position:
            next_position = None
            for direction in directions:
                next_x, next_y = current_position[0] + direction[0], current_position[1] + direction[1]
                if 0 <= next_x < self.grid_size and 0 <= next_y < self.grid_size and (next_x, next_y) not in self.used_positions:
                    next_position = (next_x, next_y)
                    break
            if not next_position:
                break
            current_position = next_position

        if current_position:
            self.canvas.create_image(current_position[1] * cell_width + cell_width // 2, current_position[0] * cell_height + cell_height // 2, image=dead_end_img, tags="dead_end")

    def find_location_index(self, location_name):
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell and "image_name" in cell and cell["image_name"] == location_name:
                    return (i, j)
        return None

    def find_path(self, start_position, end_position):
        def is_valid_move(x, y):
            return 0 <= x < self.grid_size and 0 <= y < self.grid_size and ((x, y) not in self.used_positions or (x, y) == self.start_position or (x, y) == self.end_position)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = Queue()
        queue.put((start_position, [start_position]))
        visited = set()
        visited.add(start_position)

        while not queue.empty():
            current, path = queue.get()
            if current == end_position:
                return path

            for direction in directions:
                next_x, next_y = current[0] + direction[0], current[1] + direction[1]
                if is_valid_move(next_x, next_y) and (next_x, next_y) not in visited:
                    new_path = path + [(next_x, next_y)]
                    queue.put(((next_x, next_y), new_path))
                    visited.add((next_x, next_y))

        return None

    def find_longest_path(self, start_position, end_position):
        def is_valid_move(x, y):
            return 0 <= x < self.grid_size and 0 <= y < self.grid_size and ((x, y) not in self.used_positions or (x, y) == self.start_position or (x, y) == self.end_position)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        stack = LifoQueue()
        stack.put((start_position, [start_position]))
        longest_path = []
        visited = set()
        visited.add(start_position)

        while not stack.empty():
            current, path = stack.get()
            if current == end_position and len(path) > len(longest_path):
                longest_path = path

            for direction in directions:
                next_x, next_y = current[0] + direction[0], current[1] + direction[1]
                if is_valid_move(next_x, next_y) and (next_x, next_y) not in visited:
                    new_path = path + [(next_x, next_y)]
                    stack.put(((next_x, next_y), new_path))
                    visited.add((next_x, next_y))

        return longest_path

    def find_alternative_longest_path(self, start_position, end_position):
        all_longest_paths = []
        def is_valid_move(x, y):
            return 0 <= x < self.grid_size and 0 <= y < self.grid_size and ((x, y) not in self.used_positions or (x, y) == self.start_position or (x, y) == self.end_position)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        stack = LifoQueue()
        stack.put((start_position, [start_position]))
        visited = set()
        visited.add(start_position)

        while not stack.empty():
            current, path = stack.get()
            if current == end_position:
                all_longest_paths.append(path)
            for direction in directions:
                next_x, next_y = current[0] + direction[0], current[1] + direction[1]
                if is_valid_move(next_x, next_y) and (next_x, next_y) not in visited:
                    new_path = path + [(next_x, next_y)]
                    stack.put(((next_x, next_y), new_path))
                    visited.add((next_x, next_y))
        if all_longest_paths:
            all_longest_paths.sort(key=len, reverse=True)
            return all_longest_paths[1] if len(all_longest_paths) > 1 else all_longest_paths[0]
        return None

    def is_adjacent(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2) == 1

    def show_path_options(self, shortest_path, longest_path):
        self.path_selection_window = tk.Toplevel(self.root)
        self.path_selection_window.title("Select Path")
        self.path_selection_window.geometry("300x200")
        self.path_selection_window.transient(self.root)
        self.path_selection_window.grab_set()

        label = tk.Label(self.path_selection_window, text="Select Path Option", font=('Helvetica', 14, 'bold'))
        label.pack(pady=20)

        shortest_button = tk.Button(self.path_selection_window, text="Shortest Path", command=lambda: self.display_selected_path(shortest_path))
        longest_button = tk.Button(self.path_selection_window, text="Longest Path", command=lambda: self.display_selected_path(longest_path))
        shortest_button.pack(pady=10)
        longest_button.pack(pady=10)

    def display_selected_path(self, path):
        self.path_selection_window.destroy()
        self.blink_path(path)

    def blink_path(self, path):
        for i, step in enumerate(path[1:-1]):  # Skip the first and last elements
            rect_x = step[1] * self.width // self.grid_size
            rect_y = step[0] * self.height // self.grid_size
            self.canvas.create_rectangle(rect_x, rect_y, rect_x + self.width // self.grid_size, rect_y + self.height // self.grid_size, fill="grey", tags="path")

            if i > 0:
                prev_step = path[i]
                prev_rect_x = prev_step[1] * self.width // self.grid_size
                prev_rect_y = prev_step[0] * self.height // self.grid_size
                self.canvas.create_rectangle(prev_rect_x, prev_rect_y, prev_rect_x + self.width // self.grid_size, prev_rect_y + self.height // self.grid_size, fill="white", tags="path")

            # Play audio when reaching the cell before the endpoint
            if step == path[-2]:
                self.play_sound(self.reached_audio_path)
                self.show_reached_message()

            self.root.update()
            self.root.after(500)  # Pause for 500 milliseconds

        self.status_bar.config(text="Status: Path found!")

    def show_reached_message(self):
        message_label = tk.Label(self.grid_frame, text="REACHED THE DESTINATION", font=('Helvetica', 24, 'bold'), fg="red")
        message_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.root.after(1000, message_label.destroy)  # Remove message after 1 second

if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    root.mainloop()
