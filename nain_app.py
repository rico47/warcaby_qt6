# main_app.py
# This file contains the graphical user interface for the checkers game.

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel,
    QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout,
    QDialog, QComboBox, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QColor, QBrush, QPainter
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer

# Import the game logic from the separate file
from game_logic import CheckersGameLogic


# Class representing a single square on the board
class CheckersSquare(QLabel):
    # Signal emitted when the square is clicked
    clicked = pyqtSignal(int, int)

    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setFixedSize(60, 60)  # Square size
        self.setMouseTracking(True)  # Enable mouse tracking for hover/leave events
        # 0: empty, 1: white pawn, 2: black pawn, 3: white king, 4: black king
        self.piece_type = 0
        self.is_selected = False  # True if this square's piece is selected
        self.is_highlighted = False  # True if this square is a possible move destination
        # Colors for light and dark squares (using Hex for ease)
        self.original_color = QColor("#D18B47") if (row + col) % 2 == 0 else QColor("#FFCE9E")

        self.update_background()

    def update_background(self):
        """Updates the square's background color based on its state."""
        if self.is_selected:
            self.setStyleSheet(f"background-color: lightblue;")  # Selection color
        elif self.is_highlighted:
            self.setStyleSheet(f"background-color: #A3D900;")  # Highlight color for possible moves
        else:
            self.setStyleSheet(f"background-color: {self.original_color.name()};")

    def set_piece(self, piece_type):
        """Sets the type of piece on this square and triggers a repaint."""
        self.piece_type = piece_type
        self.update()  # Force repaint

    def mousePressEvent(self, event):
        """Handles mouse clicks on the square."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.row, self.col)

    def enterEvent(self, event):
        """Event for mouse entering the square."""
        if not self.is_selected and not self.is_highlighted:
            # Slightly darker hover color
            self.setStyleSheet(f"background-color: {self.original_color.darker(120).name()};")

    def leaveEvent(self, event):
        """Event for mouse leaving the square."""
        self.update_background()  # Restore original color

    def select(self):
        """Marks the square as selected."""
        self.is_selected = True
        self.update_background()

    def deselect(self):
        """Marks the square as not selected."""
        self.is_selected = False
        self.update_background()

    def highlight(self):
        """Marks the square as highlighted (possible move)."""
        self.is_highlighted = True
        self.update_background()

    def unhighlight(self):
        """Marks the square as not highlighted."""
        self.is_highlighted = False
        self.update_background()

    def paintEvent(self, event):
        """Custom painting for pieces on the square."""
        super().paintEvent(event)  # Draw QLabel background first
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Drawing pawns and kings
        if self.piece_type == 1:  # White pawn
            painter.setBrush(QBrush(QColor(255, 255, 255)))  # White
            painter.drawEllipse(5, 5, 50, 50)  # Draw circle
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QColor(100, 100, 100))  # Grey outline
            painter.drawEllipse(5, 5, 50, 50)
        elif self.piece_type == 2:  # Black pawn
            painter.setBrush(QBrush(QColor(0, 0, 0)))  # Black
            painter.drawEllipse(5, 5, 50, 50)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QColor(150, 150, 150))  # Lighter grey outline
            painter.drawEllipse(5, 5, 50, 50)
        elif self.piece_type == 3:  # White king
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(5, 5, 50, 50)
            painter.setPen(QColor(100, 100, 100))
            painter.drawEllipse(5, 5, 50, 50)
            # Draw star for king
            painter.setPen(QColor(255, 215, 0))  # Gold color
            font = painter.font()
            font.setPointSize(24)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "★")
        elif self.piece_type == 4:  # Black king
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawEllipse(5, 5, 50, 50)
            painter.setPen(QColor(150, 150, 150))
            painter.drawEllipse(5, 5, 50, 50)
            painter.setPen(QColor(255, 215, 0))  # Gold color
            font = painter.font()
            font.setPointSize(24)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "★")


# Main application window class
class CheckersGameGUI(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize game logic with default settings
        self.game_logic = CheckersGameLogic(ai_difficulty="Średni", player_color=1)
        self.setWindowTitle("Warcaby PyQt6")
        self.setGeometry(100, 100, 8 * 60 + 80, 8 * 60 + 120)

        self.board_size = 8
        self.board_widgets = {}
        self.selected_square = None
        self.possible_moves_for_selected = []

        self.ai_timer = QTimer(self)
        self.ai_timer.setSingleShot(True)
        self.ai_timer.timeout.connect(self.make_ai_move)

        self.init_ui()
        self.update_board_display()
        self.update_status()

    def init_ui(self):
        """Initializes the main UI layout and widgets."""
        main_layout = QVBoxLayout()
        board_layout = QGridLayout()
        board_layout.setSpacing(0)

        # Column labels (A-H) at the top
        col_labels_top = QHBoxLayout()
        col_labels_top.addSpacing(40)
        for i in range(self.board_size):
            label_text = chr(ord('A') + i)
            col_labels_top.addWidget(QLabel(f"<b>{label_text}</b>", alignment=Qt.AlignmentFlag.AlignCenter))
        col_labels_top.addSpacing(40)
        main_layout.addLayout(col_labels_top)

        # Board layout with row labels
        board_with_row_labels = QHBoxLayout()

        # Row labels (8-1) on the left
        row_labels_left = QVBoxLayout()
        for r in range(self.board_size):
            row_labels_left.addWidget(
                QLabel(f"<b>{8 - r}</b>", alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
        board_with_row_labels.addLayout(row_labels_left)

        # Add board squares
        for row in range(self.board_size):
            for col in range(self.board_size):
                square = CheckersSquare(row, col, self)
                square.clicked.connect(self.square_clicked)
                board_layout.addWidget(square, row, col)
                self.board_widgets[(row, col)] = square
        board_with_row_labels.addLayout(board_layout)

        # Row labels (8-1) on the right
        row_labels_right = QVBoxLayout()
        for r in range(self.board_size):
            row_labels_right.addWidget(
                QLabel(f"<b>{8 - r}</b>", alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
        board_with_row_labels.addLayout(row_labels_right)

        main_layout.addLayout(board_with_row_labels)

        # Column labels (A-H) at the bottom
        col_labels_bottom = QHBoxLayout()
        col_labels_bottom.addSpacing(40)
        for i in range(self.board_size):
            label_text = chr(ord('A') + i)
            col_labels_bottom.addWidget(QLabel(f"<b>{label_text}</b>", alignment=Qt.AlignmentFlag.AlignCenter))
        col_labels_bottom.addSpacing(40)
        main_layout.addLayout(col_labels_bottom)

        # Additional UI elements
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(self.status_label)

        reset_button = QPushButton("Nowa Gra")
        reset_button.clicked.connect(self.show_new_game_dialog)
        reset_button.setFixedSize(120, 40)
        reset_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 10px; font-weight: bold;")

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(reset_button)
        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def update_board_display(self):
        """Updates the visual state of the board based on the game logic's board state."""
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece_type = self.game_logic.get_board_state()[row][col]
                self.board_widgets[(row, col)].set_piece(piece_type)

    def update_status(self):
        """Updates the status label text and color."""
        self.status_label.setText(self.game_logic.get_message())
        # Change status label color based on current player's turn
        if self.game_logic.get_current_player() == 1:  # White player
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px; color: blue;")
        else:  # Black player
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px; color: red;")

        # Special styling for game over message
        if "Koniec gry!" in self.game_logic.get_message():
            self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px; color: purple;")

    def clear_highlights(self):
        """Removes highlights from all squares."""
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.board_widgets[(row, col)].unhighlight()

    def highlight_possible_moves(self, moves):
        """Highlights the squares specified in the 'moves' list."""
        for r, c in moves:
            self.board_widgets[(r, c)].highlight()

    def square_clicked(self, row, col):
        """Handles a click event on a game square."""
        clicked_pos = (row, col)

        # If the game is over, do not allow moves
        if "Koniec gry!" in self.game_logic.get_message():
            QMessageBox.information(self, "Koniec Gry", self.game_logic.get_message())
            return

        # Determine if it's the human player's turn
        is_human_turn = False
        if self.game_logic.get_current_player() == self.game_logic.get_player_color():
            is_human_turn = True

        if not is_human_turn:
            self.game_logic.message = "Czekaj na ruch AI..."
            self.update_status()
            return

        # Handle forced captures - if a piece is forced to capture, only that piece can be selected
        if self.game_logic.forced_capture_piece:
            if self.selected_square is None:  # First click in a forced capture sequence
                if clicked_pos == self.game_logic.forced_capture_piece:
                    self.selected_square = self.board_widgets[clicked_pos]
                    self.selected_square.select()
                    self.game_logic.selected_piece_pos = clicked_pos
                    # Highlight possible further captures for this piece
                    possible_captures, _ = self.game_logic.get_possible_moves(row, col)
                    self.possible_moves_for_selected = possible_captures
                    self.highlight_possible_moves(self.possible_moves_for_selected)
                    self.update_status()
                    return  # Wait for the next click (the destination for the capture)
                else:
                    self.game_logic.message = "Musisz kontynuować bicie tym samym pionkiem!"
                    self.update_status()
                    return

        if self.selected_square is None:
            # First click - select a piece
            if self.game_logic.is_player_piece(row, col, player_type=self.game_logic.get_player_color()):
                # Check for any forced captures for the current player across the whole board
                all_possible_moves, has_forced_captures = self.game_logic.get_all_possible_moves_for_player(
                    board=self.game_logic.get_board_state(),
                    player_type=self.game_logic.get_player_color(),
                    forced_capture_piece=None  # Check all pieces initially
                )

                if has_forced_captures and clicked_pos not in all_possible_moves:
                    self.game_logic.message = "Musisz wykonać bicie innym pionkiem!"
                    self.update_status()
                    return

                self.selected_square = self.board_widgets[clicked_pos]
                self.selected_square.select()
                self.game_logic.selected_piece_pos = clicked_pos

                # Highlight possible moves/captures for the selected piece
                moves_for_selected_piece, _ = self.game_logic.get_possible_moves(row, col,
                                                                                 board=self.game_logic.get_board_state(),
                                                                                 player_type=self.game_logic.get_player_color())
                self.possible_moves_for_selected = moves_for_selected_piece
                self.highlight_possible_moves(self.possible_moves_for_selected)

                self.game_logic.message = (
                    f"Wybrano pionek na polu: ({chr(ord('A') + col)}{8 - row}). Wybierz pole docelowe."
                )
                self.update_status()
            else:
                self.game_logic.message = "Na wybranym polu nie ma twojego pionka."
                self.update_status()
        else:
            # Second click - attempt to make a move
            start_pos = self.game_logic.selected_piece_pos

            # If the same piece is clicked again, deselect it
            if clicked_pos == start_pos:
                self.selected_square.deselect()
                self.selected_square = None
                self.game_logic.selected_piece_pos = None
                self.clear_highlights()
                self.game_logic.message = "Anulowano wybór."
                self.update_status()
                return

            # Validate the move using game logic
            if self.game_logic.is_move_valid(start_pos, clicked_pos):
                self.game_logic.make_move(start_pos, clicked_pos)  # Make move in logic
                self.update_board_display()  # Refresh board view

                # Check for game over conditions first, then update status
                game_over = self.game_logic.check_game_over()
                self.update_status()  # Update status to reflect any new game over message

                if game_over:
                    # Game is over, clear selection
                    if self.selected_square:  # Ensure selected_square is not None before calling deselect
                        self.selected_square.deselect()
                    self.selected_square = None
                    self.game_logic.selected_piece_pos = None
                    self.clear_highlights()
                    QMessageBox.information(self, "Koniec Gry", self.game_logic.get_message())
                elif self.game_logic.forced_capture_piece:
                    # If there's a forced capture, the piece remains selected
                    # and we update highlights for next possible jumps.
                    self.game_logic.selected_piece_pos = self.game_logic.forced_capture_piece
                    # Re-select the piece for the next jump.
                    # We might need to deselect the previous selected_square if it's different.
                    if self.selected_square and self.selected_square != self.board_widgets[
                        self.game_logic.forced_capture_piece]:
                        self.selected_square.deselect()
                    self.selected_square = self.board_widgets[self.game_logic.forced_capture_piece]
                    self.selected_square.select()

                    # Update highlights for the remaining captures
                    r, c = self.game_logic.forced_capture_piece
                    remaining_moves, _ = self.game_logic.get_possible_moves(r, c,
                                                                            board=self.game_logic.get_board_state(),
                                                                            player_type=self.game_logic.get_current_player())
                    self.possible_moves_for_selected = remaining_moves
                    self.clear_highlights()
                    self.highlight_possible_moves(self.possible_moves_for_selected)

                else:
                    # No more forced captures, or it was a normal move, so clear selection.
                    if self.selected_square:  # Ensure selected_square is not None before calling deselect
                        self.selected_square.deselect()
                    self.selected_square = None
                    self.game_logic.selected_piece_pos = None
                    self.clear_highlights()  # Remove highlights

                    # If game not over, and it's AI's turn
                    if self.game_logic.get_current_player() == self.game_logic.get_ai_color():
                        self.ai_timer.start(1000)  # Start AI after 1 second delay
            else:
                self.game_logic.message = "Niepoprawny ruch: " + self.game_logic.get_message()
                self.update_status()

    def make_ai_move(self):
        """Executes the AI's move."""
        # print("make_ai_move called.")
        if self.game_logic.get_current_player() == self.game_logic.get_ai_color():  # Ensure it's AI's turn
            self.game_logic.message = "AI myśli..."
            self.update_status()
            QApplication.processEvents()  # Process events to update UI immediately

            ai_start_pos, ai_end_pos = self.game_logic.get_ai_move()
            # print(f"AI returned: start={ai_start_pos}, end={ai_end_pos}")

            if ai_start_pos is not None and ai_end_pos is not None:
                # Simulate selection and move on GUI for better feedback
                # Ensure the previously selected square (if any) is deselected
                if self.selected_square:
                    self.selected_square.deselect()
                self.selected_square = self.board_widgets[ai_start_pos]
                self.selected_square.select()
                self.game_logic.selected_piece_pos = ai_start_pos
                QApplication.processEvents()  # Process events to show selection

                # Small delay before executing AI move
                QTimer.singleShot(500, lambda: self._execute_ai_move_on_gui(ai_start_pos, ai_end_pos))
            else:
                # print("AI could not find a move.")
                # This block is for when AI explicitly cannot find a move.
                game_over = self.game_logic.check_game_over()  # Check for game over (if AI couldn't move, it might be game over for it)
                self.update_status()  # Update status with any new game over message
                if game_over:
                    QMessageBox.information(self, "Koniec Gry", self.game_logic.get_message())
                else:  # This path means AI had moves according to logic, but get_ai_move returned None unexpectedly
                    self.game_logic.message = "AI napotkało problem w znalezieniu ruchu. Spróbuj ponownie."
                    self.update_status()

    def _execute_ai_move_on_gui(self, start_pos, end_pos):
        """Helper to execute AI move on GUI after a short delay."""
        self.game_logic.make_move(start_pos, end_pos)
        self.update_board_display()

        # After a move, check if the current piece needs to continue capturing.
        # The game_logic.make_move method already updates self.forced_capture_piece.
        if self.game_logic.forced_capture_piece:
            # If AI just captured and needs to continue capturing, trigger AI again
            # We don't need to update selected_square for AI, as its moves are programmatic.
            # However, we must ensure game_logic.selected_piece_pos reflects the piece
            # that needs to continue capturing for consistency in game_logic.
            self.game_logic.selected_piece_pos = self.game_logic.forced_capture_piece
            # Ensure the selected_square in GUI reflects the new forced_capture_piece
            if self.selected_square:
                self.selected_square.deselect()  # Deselect old square if it was selected
            self.selected_square = self.board_widgets[self.game_logic.forced_capture_piece]
            self.selected_square.select()  # Select the piece that must continue capturing

            self.clear_highlights()  # Clear previous highlights
            r, c = self.game_logic.forced_capture_piece
            remaining_moves, _ = self.game_logic.get_possible_moves(r, c,
                                                                    board=self.game_logic.get_board_state(),
                                                                    player_type=self.game_logic.get_current_player())
            self.highlight_possible_moves(remaining_moves)  # Highlight new possible captures

            self.ai_timer.start(500)  # Shorter delay for subsequent captures
            # print("AI: Continuing forced capture.")
        else:
            # No more forced captures for AI, clear selection and highlights
            if self.selected_square:  # Ensure selected_square is not None before calling deselect
                self.selected_square.deselect()
            self.selected_square = None
            self.game_logic.selected_piece_pos = None
            self.clear_highlights()

            # After AI move, check game over
            game_over = self.game_logic.check_game_over()
            self.update_status()  # Update status with any new game over message

            if game_over:
                QMessageBox.information(self, "Koniec Gry", self.game_logic.get_message())
            # If game not over and AI's turn is done, human's turn starts, no timer.

    def show_new_game_dialog(self):
        """Shows a dialog to choose AI difficulty and player color."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Nowa Gra - Ustawienia")
        dialog.setFixedSize(300, 250)  # Fixed size for the dialog
        dialog_layout = QVBoxLayout()
        dialog_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialog.setStyleSheet("background-color: #F0F0F0; border-radius: 10px;")

        # Difficulty selection
        difficulty_label = QLabel("Wybierz trudność AI:")
        difficulty_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        dialog_layout.addWidget(difficulty_label)

        difficulty_combo = QComboBox()
        difficulty_combo.addItems(list(CheckersGameLogic.AI_SEARCH_DEPTH_MAP.keys()))
        # Set default selection based on current game difficulty
        current_difficulty_index = list(CheckersGameLogic.AI_SEARCH_DEPTH_MAP.keys()).index(
            self.game_logic.ai_difficulty)
        difficulty_combo.setCurrentIndex(current_difficulty_index)
        difficulty_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
                background: white;
                selection-background-color: #A3D900;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
        """)
        dialog_layout.addWidget(difficulty_combo)
        dialog_layout.addSpacing(20)

        # Player color selection
        color_label = QLabel("Wybierz kolor gracza:")
        color_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        dialog_layout.addWidget(color_label)

        color_radio_layout = QHBoxLayout()
        color_radio_group = QButtonGroup(dialog)

        white_radio = QRadioButton("Białe (pierwszy ruch)")
        white_radio.setStyleSheet("color: blue;")
        white_radio.setChecked(self.game_logic.get_player_color() == 1)
        color_radio_group.addButton(white_radio, 1)  # Value 1 for white
        color_radio_layout.addWidget(white_radio)

        black_radio = QRadioButton("Czarne")
        black_radio.setStyleSheet("color: red;")
        black_radio.setChecked(self.game_logic.get_player_color() == 2)
        color_radio_group.addButton(black_radio, 2)  # Value 2 for black
        color_radio_layout.addWidget(black_radio)

        dialog_layout.addLayout(color_radio_layout)
        dialog_layout.addSpacing(30)

        # Buttons
        button_box = QHBoxLayout()
        ok_button = QPushButton("Rozpocznij Grę")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; /* Blue */
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0B7CD8;
            }
        """)
        ok_button.clicked.connect(dialog.accept)
        button_box.addStretch()
        button_box.addWidget(ok_button)
        button_box.addStretch()

        dialog_layout.addLayout(button_box)
        dialog.setLayout(dialog_layout)

        # Execute dialog and handle result
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_difficulty = difficulty_combo.currentText()
            selected_color = color_radio_group.checkedId()
            self.start_new_game(selected_difficulty, selected_color)

    def start_new_game(self, ai_difficulty, player_color):
        """Starts a new game with the chosen settings."""
        self.ai_timer.stop()  # Stop any pending AI moves
        self.game_logic.reset_game(ai_difficulty, player_color)  # Reset game logic with new settings

        self.update_board_display()
        if self.selected_square:
            self.selected_square.deselect()
            self.selected_square = None
        self.possible_moves_for_selected = []
        self.clear_highlights()
        self.update_status()

        QMessageBox.information(self, "Nowa Gra", "Rozpoczęto nową grę z wybranymi ustawieniami!")

        # If AI is black (player 2) and is the current player, AI should make the first move
        # (This handles the case where human chooses Black, so AI is White and moves first)
        if self.game_logic.get_current_player() == self.game_logic.get_ai_color():
            self.ai_timer.start(1000)  # Give a short delay before AI moves


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game_gui = CheckersGameGUI()
    game_gui.show()
    sys.exit(app.exec())
