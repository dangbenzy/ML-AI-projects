"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x=0
    o=0
    Total= 9

    if board == [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]:
            return X

    for row in board:
        for cell in row:
            if cell == X:
                x += 1
            elif cell == O:
                o += 1

    if x > o :
       return O
    elif x == o:
        return X
    raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.add((i, j))
    return actions
    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Invalid action")

    new_board = [row[:] for row in board]  # Create a copy of the board
    i, j = action
    current_player = player(board)
    new_board[i][j] = current_player
    return new_board

    raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]
    # Check columns
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] and board[0][j] is not None:
            return board[0][j]
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    # No winner
    return None
    raise NotImplementedError

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if there is a winner
    if winner(board) is not None:
        return True
    # Check if the board is full
    for row in board:
        if EMPTY in row:
            return False
    return True

    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    current_player = player(board)

    if current_player == X:
        _, action = max_value(board)
    else:
        _, action = min_value(board)

    return action

def max_value(board):
    if terminal(board):
        return utility(board), None

    v = -math.inf
    best_action = None

    for action in actions(board):
        new_v, _ = min_value(result(board, action))
        if new_v > v:
            v = new_v
            best_action = action
            if v == 1:  # Early return if found winning move
                break

    return v, best_action

def min_value(board):
    if terminal(board):
        return utility(board), None

    v = math.inf
    best_action = None

    for action in actions(board):
        new_v, _ = max_value(result(board, action))
        if new_v < v:
            v = new_v
            best_action = action
            if v == -1:  # Early return if found winning move
                break

    return v, best_action
