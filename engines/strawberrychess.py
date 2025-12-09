#!/usr/bin/env python3

import sys
import chess
import random

# --- Evaluation Function ---
# Piece values for material count
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

def evaluate_board(board):
    """
    Evaluates the board position based on material count.
    Positive score for White, negative for Black.
    """
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -float('inf') # Black wins
        else:
            return float('inf') # White wins
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    score = 0
    for piece_type in PIECE_VALUES:
        score += len(board.pieces(piece_type, chess.WHITE)) * PIECE_VALUES[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * PIECE_VALUES[piece_type]
    return score

# --- Search Algorithm (Alpha-Beta Pruning) ---
def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth=3):
    """Finds the best move using minimax with alpha-beta pruning."""
    best_move = None
    best_score = -float('inf') if board.turn == chess.WHITE else float('inf')

    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, -float('inf'), float('inf'), board.turn == chess.BLACK)
        board.pop()

        if board.turn == chess.WHITE:
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move
    return best_move

# --- UCI Protocol Implementation ---
def uci_protocol():
    board = chess.Board()
    while True:
        line = sys.stdin.readline().strip().split()
        if not line:
            continue

        command = line[0]

        if command == "uci":
            sys.stdout.write("id name StrawberryChess v1.0\n")
            sys.stdout.write("id author MK\n")
            sys.stdout.write("uciok\n")
        elif command == "isready":
            sys.stdout.write("readyok\n")
        elif command == "position":
            if "startpos" in line:
                board = chess.Board()
            elif "fen" in line:
                fen_index = line.index("fen") + 1
                fen = " ".join(line[fen_index:])
                board = chess.Board(fen)
            moves_index = next((i for i, x in enumerate(line) if x == "moves"), len(line))
            if moves_index < len(line):
                for move_uci in line[moves_index + 1:]:
                    move = chess.Move.from_uci(move_uci)
                    board.push(move)
        elif command == "go":
            best_move = find_best_move(board)
            if best_move:
                sys.stdout.write(f"bestmove {best_move.uci()}\n")
            else:
                # Handle game over or no moves
                sys.stdout.write("bestmove (none)\n")
        elif command == "quit":
            break

if __name__ == "__main__":
    uci_protocol()

