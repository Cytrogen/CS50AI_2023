"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY]
    ]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Count number of X's and O's
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)

    # If X's and O's are equal, then it's X's turn
    if x_count == o_count:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    available = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] is EMPTY:
                available.add((i, j))
    return available


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if board[i][j] is not EMPTY:
        raise Exception("Invalid action")

    # Create a copy of the board, and make the move
    new_board = copy.deepcopy(board)
    new_board[i][j] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for row in board:
        # Check if all elements in the row are equal and not empty
        if len(set(row)) == 1 and row[0] != EMPTY:
            return row[0]

    # Check columns
    for col in range(len(board)):
        # Check if all elements in the column are equal and not empty
        if len(set(row[col] for row in board)) == 1 and board[0][col] != EMPTY:
            return board[0][col]

    # Check diagonal that goes from top left to bottom right
    if len(set([board[i][i] for i in range(len(board))])) == 1 and board[0][0] != EMPTY:
        return board[0][0]

    # Check diagonal that goes from top right to bottom left
    if len(set([board[i][len(board) - i - 1] for i in range(len(board))])) == 1 and board[0][len(board) - 1] != EMPTY:
        return board[0][len(board) - 1]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Game is over if there is a winner or there are no empty squares left
    if winner(board) is not None or not any(EMPTY in sublist for sublist in board):
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == X:
        # If it's X's turn, then we want to maximize the value
        best_move = max_value(board)[1]
    else:
        # If it's O's turn, then we want to minimize the value
        best_move = min_value(board)[1]

    return best_move


def max_value(board):
    """
    Returns the maximum value and the best action of the board
    """
    if terminal(board):
        return utility(board), None

    value = float('-inf')
    best_action = None

    for action in actions(board):
        future_board = result(board, action)

        # Get the minimum value of the next board
        minimum = min_value(future_board)[0]

        # If the minimum value is greater than the current value, update the value and the best action
        if minimum > value:
            value = minimum
            best_action = action

            # If the value is 1, then we have found the best move
            if value == 1:
                return value, best_action
    return value, best_action


def min_value(board):
    """
    Returns the minimum value and the best action of the board
    """
    if terminal(board):
        return utility(board), None

    value = float('inf')
    best_action = None

    for action in actions(board):
        future_board = result(board, action)

        # Get the maximum value of the next board
        maximum = max_value(future_board)[0]

        # If the maximum value is less than the current value, update the value and the best action
        if maximum < value:
            value = maximum
            best_action = action

            # If the value is -1, then we have found the best move
            if value == -1:
                return value, best_action
    return value, best_action
