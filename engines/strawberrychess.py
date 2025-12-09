#!/usr/bin/env python3

import chess
import sys
import time

class BasicUCIEngine:
    def __init__(self):
        self.board = chess.Board()
        self.name = "StrawberryChess v1.0"
        self.author = "MK"
        self.depth_limit = None
        self.time_limit_ms = None

    def evaluate_board(self, board):
        if board.is_checkmate():
            return 100000 if board.turn == chess.BLACK else -100000
        if board.is_game_over(claim_draw=True):
            return 0
        piece_values = {'P': 100, 'N': 300, 'B': 320, 'R': 500, 'Q': 900, 'K': 0,
                        'p': -100, 'n': -300, 'b': -320, 'r': -500, 'q': -900, 'k': 0}
        score = sum(piece_values[piece.symbol()] for square in chess.SQUARES if (piece := board.piece_at(square)))
        return score

    def negaMax(board, depth, alpha, beta):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board) * (1 if board.turn == chess.WHITE else -1)

        max_score = float("-inf")
        for move in board.legal_moves:
            board.push(move)
            score = -self.negaMax(board, depth - 1, -beta, -alpha)
            board.pop()
            max_score = max(max_score, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Alpha-beta cutoff
        return max_score

        best_score = float('-inf') if self.board.turn == chess.WHITE else float('inf')
        best_move = legal_moves[0] 

        for move in legal_moves:
            self.board.push(move)
            score = self.evaluate_board(self.board)
            self.board.pop()
            
            if self.board.turn == chess.WHITE:
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
            
            if self.depth_limit is not None and self.depth_limit <= 1:
                break
            if self.time_limit_ms is not None and (time.time() - start_time) * 1000 >= self.time_limit_ms:
                break
        
        return f"bestmove {best_move.uci()}"

    def uci_loop(self):
        print("id name " + self.name)
        print("id author " + self.author)
        print("uciok")
        
        while True:
            try:
                line = sys.stdin.readline().strip()
                if not line:
                    continue
                parts = line.split()
                command = parts[0]

                if command == "uci":
                    print("id name " + self.name)
                    print("id author " + self.author)
                    print("uciok")
                elif command == "isready":
                    print("readyok")
                elif command == "ucinewgame":
                    self.board = chess.Board()
                elif command == "position":
                    self.board = chess.Board()
                    if parts[1] == "fen":
                        fen_string = " ".join(parts[2:8])
                        self.board = chess.Board(fen_string)
                        moves_index = 8
                    elif parts[1] == "startpos":
                        moves_index = 2
                
                    if len(parts) > moves_index and parts[moves_index] == "moves":
                        for move_uci in parts[moves_index+1:]:
                            move = chess.Move.from_uci(move_uci)
                            if move in self.board.legal_moves:
                                self.board.push(move)

                elif command == "go":
                    self.depth_limit = None
                    self.time_limit_ms = None
                    if "depth" in parts:
                        self.depth_limit = int(parts[parts.index("depth") + 1])
                    if "time" in parts:
                        self.time_limit_ms = int(parts[parts.index("movetime") + 1])
                
                    best_move_command = self.search_best_move()
                    print(best_move_command)

                elif command == "quit":
                    break
            
            except Exception as e:
                with open("engine_error.log", "a") as f:
                    f.write(f"Error at {time.ctime()}: {e}\n")
                    f.write(traceback.format_exc())
                print(f"info string Encountered error: {e}")

     

if __name__ == "__main__":
    engine = BasicUCIEngine()
    engine.uci_loop()

