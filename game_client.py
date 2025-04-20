# Client Code
import socket
import pickle
import threading
import tkinter as tk
from tkinter import messagebox
  
# Connect to server
HOST = "127.0.0.1"
PORT = 65432
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Receive initial game state
board_state, player_id = pickle.loads(client.recv(1024))

# Tkinter setup
root = tk.Tk()
root.title(f"Connect 4 - Player {player_id}")
canvas = tk.Canvas(root, width=420, height=360, bg="blue", highlightthickness=0)
canvas.pack()

def draw_board():
    canvas.delete("all")
    for row in range(6):
        for col in range(7):
            color = "white"
            if board_state[row][col] == 1:
                color = "green"
            elif board_state[row][col] == 2:
                color = "orange"
            canvas.create_oval(col * 60 + 10, row * 60 + 10, col * 60 + 50, row * 60 + 50, fill=color, outline="black", width=2)

def handle_click(event):
    col = event.x // 60
    client.send(pickle.dumps(col))

def listen_to_server():
    global board_state
    while True:
        try:
            message = pickle.loads(client.recv(1024))
            if message[0] == "update":
                board_state = message[1]
                draw_board()
            elif message[0] == "win":
                board_state = message[1]
                draw_board()
                messagebox.showinfo("Game Over", "You win!")
                root.quit()
            elif message[0] == "loss":
                board_state = message[1]
                draw_board()
                messagebox.showinfo("Game Over", "You lose!")
                root.quit()
            elif message[0] == "not_your_turn":
                messagebox.showwarning("Warning", "Not your turn!")
            elif message[0] == "invalid":
                messagebox.showwarning("Warning", "Invalid move!")
                
        except:
            break

canvas.bind("<Button-1>", handle_click)
th = threading.Thread(target=listen_to_server, daemon=True)
th.start()

draw_board()
root.mainloop()