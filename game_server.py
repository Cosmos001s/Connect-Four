# Server Code
import socket
import threading
import pickle

# Global variables to track game state
board_state = [[0 for _ in range(7)] for _ in range(6)]  # 6x7 board
current_player = 1

# Lock to synchronize threads
lock = threading.Lock()

def check_win(board, row, col, player):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        x, y = col + dx, row + dy
        while 0 <= x < 7 and 0 <= y < 6 and board[y][x] == player:
            count += 1
            x, y = x + dx, y + dy
        x, y = col - dx, row - dy
        while 0 <= x < 7 and 0 <= y < 6 and board[y][x] == player:
            count += 1
            x, y = x - dx, y - dy
        if count >= 4:
            return True
    return False

def handle_client(conn, player_id):
    global current_player, board_state
    conn.send(pickle.dumps((board_state, player_id)))

    while True:
        try:
            col = pickle.loads(conn.recv(1024))
            with lock:
                if current_player != player_id:
                    conn.send(pickle.dumps(("not_your_turn", None)))
                    continue

                # Place the token
                for row in range(5, -1, -1):
                    if board_state[row][col] == 0:
                        board_state[row][col] = player_id
                        if check_win(board_state, row, col, player_id):
                            conn.send(pickle.dumps(("win", board_state)))
                            broadcast(pickle.dumps(("loss", board_state)), conn)
                        else:
                            current_player = 3 - player_id
                            broadcast(pickle.dumps(("update", board_state)))
                        break
                else:
                    conn.send(pickle.dumps(("invalid", None)))
        except:
            break

    conn.close()

def broadcast(message, exclude_conn=None):
    for conn in clients:
        if conn != exclude_conn:
            try:
                conn.send(message)
            except:
                pass

# Server setup
HOST = "0.0.0.0"
PORT = 65432
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

clients = []

print(f"Server started, listening on {HOST}:{PORT}. Waiting for players...")

while len(clients) < 2:
    conn, addr = server.accept()
    clients.append(conn)
    print(f"Player {len(clients)} connected from {addr}")
    threading.Thread(target=handle_client, args=(conn, len(clients))).start()
