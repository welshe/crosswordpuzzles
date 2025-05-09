import pygame
import sys

# --- Constants ---
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Grid dimensions
GRID_SIZE = 10
CELL_SIZE = 50  # Increased for better visibility
MARGIN = 5
NUMBER_OFFSET = 3
GRID_WIDTH = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN
GRID_HEIGHT = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN

# Clue area dimensions
CLUE_AREA_HEIGHT = 200
INFO_AREA_HEIGHT = 50

# Screen dimensions
SCREEN_WIDTH = GRID_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT + CLUE_AREA_HEIGHT + INFO_AREA_HEIGHT

# Fonts
pygame.font.init() # Initialize font module
try:
    FONT_LETTER = pygame.font.SysFont('arial', 35)
    FONT_NUMBER = pygame.font.SysFont('arial', 15)
    FONT_CLUE = pygame.font.SysFont('arial', 20)
    FONT_INFO = pygame.font.SysFont('arial', 18)
except pygame.error as e:
    print(f"Warning: System font 'arial' not found. Using default font. Error: {e}")
    FONT_LETTER = pygame.font.Font(None, 45) # Default font if Arial is not found
    FONT_NUMBER = pygame.font.Font(None, 20)
    FONT_CLUE = pygame.font.Font(None, 25)
    FONT_INFO = pygame.font.Font(None, 22)


# --- Crossword Data ---
# (word, clue, start_row, start_col, direction ('A' or 'D'))
# Numbering will be assigned automatically
WORDS_DATA = [
    ("PYTHON", "Popular programming language", 0, 0, "A"),
    ("GRID", "Network of lines for the puzzle", 0, 0, "D"),
    ("LOOP", "Repeated execution of code", 2, 1, "A"),
    ("TEXT", "Written words or characters", 0, 3, "D"),
    ("EVENT", "Something that happens, in Pygame", 4, 3, "A"),
    ("ARRAY", "Ordered series or arrangement", 2, 6, "D"),
    ("TEN", "Number of rows/columns in this grid", 6, 0, "A"),
    ("SET", "To put or place something", 6, 0, "D"), # Shares 'T' with TEN
    ("INPUT", "Data entered into a system", 8, 2, "A"),
    ("MOUSE", "Computer pointing device", 4, 5, "D"), # Shares 'E' with EVENT
    ("CELL", "A single box in the grid", 0, 8, "D"),
    ("pygame", "Library used for this game", 6, 4, "A") #pygame word
]

class CrosswordGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("10x10 Crossword Puzzle")

        self.puzzle_grid = [['#' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)] # '#' for black, ' ' for white
        self.solution_grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.user_grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.number_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)] # Stores word numbers

        self.words = [] # Will store processed word objects
        self.active_cell = None # (row, col)
        self.active_direction = "A" # "A" for across, "D" for down
        self.current_word_highlight = [] # list of (r,c) tuples for the active word

        self._prepare_puzzle()

        self.across_clues_display = [] # (number, clue_text, word_obj)
        self.down_clues_display = []   # (number, clue_text, word_obj)
        self._prepare_clue_lists()

        self.active_clue_text = ""

    def _prepare_puzzle(self):
        """Populates the puzzle_grid, solution_grid, and number_grid based on WORDS_DATA."""
        word_starts = {} # (row, col) -> number
        current_word_number = 1

        # Sort words to assign numbers consistently (optional, but good for predictability)
        # Typically, words are numbered left-to-right, top-to-bottom.
        sorted_words_data = sorted(WORDS_DATA, key=lambda x: (x[2], x[3]))

        for word_str, clue, r_start, c_start, direction in sorted_words_data:
            word_obj = {
                "text": word_str.upper(),
                "clue": clue,
                "row": r_start,
                "col": c_start,
                "direction": direction,
                "number": 0, # Will be assigned
                "cells": [] # List of (r,c) tuples
            }

            # Assign word number if it's a new starting cell
            if (r_start, c_start) not in word_starts:
                word_starts[(r_start, c_start)] = current_word_number
                self.number_grid[r_start][c_start] = current_word_number
                word_obj["number"] = current_word_number
                current_word_number += 1
            else:
                word_obj["number"] = word_starts[(r_start, c_start)]


            for i, char_w in enumerate(word_str.upper()):
                if direction == "A": # Across
                    r, c = r_start, c_start + i
                else: # Down
                    r, c = r_start + i, c_start

                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    self.puzzle_grid[r][c] = ' ' # Mark as usable cell
                    self.solution_grid[r][c] = char_w
                    word_obj["cells"].append((r,c))
                else:
                    print(f"Error: Word '{word_str}' at ({r_start},{c_start}) goes out of bounds.")
                    # Handle error or skip word
                    continue
            self.words.append(word_obj)

    def _prepare_clue_lists(self):
        """Populates the lists of clues for display."""
        seen_numbers_across = set()
        seen_numbers_down = set()

        # Sort words by number for ordered clue list
        sorted_words = sorted(self.words, key=lambda w: w["number"])

        for word_obj in sorted_words:
            num = word_obj["number"]
            clue = word_obj["clue"]
            if word_obj["direction"] == "A" and num not in seen_numbers_across:
                self.across_clues_display.append((num, clue, word_obj))
                seen_numbers_across.add(num)
            elif word_obj["direction"] == "D" and num not in seen_numbers_down:
                self.down_clues_display.append((num, clue, word_obj))
                seen_numbers_down.add(num)
        
        # Further sort by number just in case (though primary sort should handle it)
        self.across_clues_display.sort(key=lambda x: x[0])
        self.down_clues_display.sort(key=lambda x: x[0])


    def _draw_grid(self):
        """Draws the crossword grid, numbers, and letters."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect_x = MARGIN + c * (CELL_SIZE + MARGIN)
                rect_y = MARGIN + r * (CELL_SIZE + MARGIN)
                cell_rect = pygame.Rect(rect_x, rect_y, CELL_SIZE, CELL_SIZE)

                # Cell color
                if self.puzzle_grid[r][c] == '#':
                    pygame.draw.rect(self.screen, BLACK, cell_rect)
                else:
                    pygame.draw.rect(self.screen, WHITE, cell_rect)
                    if self.active_cell and (r,c) == self.active_cell:
                        pygame.draw.rect(self.screen, YELLOW, cell_rect, 0) # Highlight active cell
                    elif (r,c) in self.current_word_highlight:
                         pygame.draw.rect(self.screen, LIGHT_BLUE, cell_rect, 0) # Highlight active word

                    # Draw cell border
                    pygame.draw.rect(self.screen, GRAY, cell_rect, 1)


                    # Draw word number
                    if self.number_grid[r][c] != 0:
                        num_surf = FONT_NUMBER.render(str(self.number_grid[r][c]), True, BLACK)
                        self.screen.blit(num_surf, (rect_x + NUMBER_OFFSET, rect_y + NUMBER_OFFSET))

                    # Draw user's letter
                    if self.user_grid[r][c] != '':
                        letter_surf = FONT_LETTER.render(self.user_grid[r][c].upper(), True, DARK_BLUE)
                        text_rect = letter_surf.get_rect(center=cell_rect.center)
                        self.screen.blit(letter_surf, text_rect)

    def _draw_clues(self):
        """Draws the clue lists and the active clue."""
        clue_area_rect = pygame.Rect(0, GRID_HEIGHT, SCREEN_WIDTH, CLUE_AREA_HEIGHT)
        pygame.draw.rect(self.screen, GRAY, clue_area_rect) # Background for clue area

        # Active Clue Display
        if self.active_clue_text:
            active_clue_surf = FONT_CLUE.render(f"Clue: {self.active_clue_text}", True, BLACK)
            active_clue_rect = active_clue_surf.get_rect(centerx=clue_area_rect.centerx, top=clue_area_rect.top + 10)
            self.screen.blit(active_clue_surf, active_clue_rect)

        # Column headers
        across_header_surf = FONT_CLUE.render("Across", True, BLACK)
        down_header_surf = FONT_CLUE.render("Down", True, BLACK)
        self.screen.blit(across_header_surf, (MARGIN + 20, clue_area_rect.top + 40))
        self.screen.blit(down_header_surf, (SCREEN_WIDTH // 2 + 20, clue_area_rect.top + 40))

        # Display Across Clues
        y_offset_clue = clue_area_rect.top + 65
        for num, clue, _ in self.across_clues_display:
            if y_offset_clue < clue_area_rect.bottom - 20: # Check if there's space
                clue_text = f"{num}. {clue}"
                clue_surf = FONT_CLUE.render(clue_text, True, BLACK)
                clue_width = clue_surf.get_width()
                # Simple wrapping (split by space)
                if MARGIN + 20 + clue_width > SCREEN_WIDTH // 2 - 10: # if wider than half screen
                    words_in_clue = clue_text.split(' ')
                    line1 = ""
                    line2_list = []
                    for i, w in enumerate(words_in_clue):
                        if FONT_CLUE.size(line1 + w)[0] < (SCREEN_WIDTH // 2 - 30):
                            line1 += w + " "
                        else:
                            line2_list = words_in_clue[i:]
                            break
                    
                    clue_surf_l1 = FONT_CLUE.render(line1.strip(), True, BLACK)
                    self.screen.blit(clue_surf_l1, (MARGIN + 20, y_offset_clue))
                    y_offset_clue += FONT_CLUE.get_height()
                    if line2_list and y_offset_clue < clue_area_rect.bottom - 20:
                         clue_surf_l2 = FONT_CLUE.render("   " + " ".join(line2_list), True, BLACK)
                         self.screen.blit(clue_surf_l2, (MARGIN + 20, y_offset_clue))

                else:
                    self.screen.blit(clue_surf, (MARGIN + 20, y_offset_clue))
                
                y_offset_clue += FONT_CLUE.get_height() + 2 # spacing
            else:
                break # Stop if no more space

        # Display Down Clues
        y_offset_clue = clue_area_rect.top + 65
        for num, clue, _ in self.down_clues_display:
            if y_offset_clue < clue_area_rect.bottom - 20:
                clue_text = f"{num}. {clue}"
                clue_surf = FONT_CLUE.render(clue_text, True, BLACK)
                clue_width = clue_surf.get_width()

                if SCREEN_WIDTH // 2 + 20 + clue_width > SCREEN_WIDTH - 10:
                    words_in_clue = clue_text.split(' ')
                    line1 = ""
                    line2_list = []
                    for i, w in enumerate(words_in_clue):
                        if FONT_CLUE.size(line1 + w)[0] < (SCREEN_WIDTH // 2 - 30):
                            line1 += w + " "
                        else:
                            line2_list = words_in_clue[i:]
                            break
                    clue_surf_l1 = FONT_CLUE.render(line1.strip(), True, BLACK)
                    self.screen.blit(clue_surf_l1, (SCREEN_WIDTH // 2 + 20, y_offset_clue))
                    y_offset_clue += FONT_CLUE.get_height()
                    if line2_list and y_offset_clue < clue_area_rect.bottom - 20:
                         clue_surf_l2 = FONT_CLUE.render("   " + " ".join(line2_list), True, BLACK)
                         self.screen.blit(clue_surf_l2, (SCREEN_WIDTH // 2 + 20, y_offset_clue))
                else:
                    self.screen.blit(clue_surf, (SCREEN_WIDTH // 2 + 20, y_offset_clue))

                y_offset_clue += FONT_CLUE.get_height() + 2
            else:
                break
    
    def _draw_info_bar(self):
        """Draws an info bar at the bottom."""
        info_area_rect = pygame.Rect(0, GRID_HEIGHT + CLUE_AREA_HEIGHT, SCREEN_WIDTH, INFO_AREA_HEIGHT)
        pygame.draw.rect(self.screen, DARK_BLUE, info_area_rect)
        
        info_text = "Click a cell or use arrows. Click cell again to toggle direction (Across/Down)."
        if self.active_cell:
            r, c = self.active_cell
            info_text = f"Selected: ({r},{c}) | Direction: {'Across' if self.active_direction == 'A' else 'Down'}"
            
        info_surf = FONT_INFO.render(info_text, True, WHITE)
        info_rect = info_surf.get_rect(center=info_area_rect.center)
        self.screen.blit(info_surf, info_rect)


    def _handle_click(self, pos):
        """Handles mouse clicks on the grid."""
        col = (pos[0] - MARGIN) // (CELL_SIZE + MARGIN)
        row = (pos[1] - MARGIN) // (CELL_SIZE + MARGIN)

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and self.puzzle_grid[row][col] != '#':
            if self.active_cell == (row, col): # Clicked same cell again
                # Toggle direction if the cell is part of both A and D words
                is_across_word = any(word for word in self.words if word["direction"] == "A" and (row,col) in word["cells"])
                is_down_word = any(word for word in self.words if word["direction"] == "D" and (row,col) in word["cells"])

                if is_across_word and is_down_word:
                    self.active_direction = "D" if self.active_direction == "A" else "A"
            else: # Clicked a new cell
                self.active_cell = (row, col)
                # Default to Across if possible, else Down
                is_across_word = any(word for word in self.words if word["direction"] == "A" and (row,col) in word["cells"])
                if is_across_word:
                    self.active_direction = "A"
                else: # If not part of any across word, try down
                    is_down_word = any(word for word in self.words if word["direction"] == "D" and (row,col) in word["cells"])
                    if is_down_word:
                        self.active_direction = "D"
                    else: # Not part of any word (should not happen if puzzle_grid is correct)
                        self.active_cell = None # Deselect

            self._update_active_word_highlight_and_clue()
        else: # Clicked outside grid or on black square
            self.active_cell = None
            self.current_word_highlight = []
            self.active_clue_text = ""


    def _update_active_word_highlight_and_clue(self):
        """Updates the highlighted word and current clue based on active_cell and active_direction."""
        self.current_word_highlight = []
        self.active_clue_text = ""
        if not self.active_cell:
            return

        r_active, c_active = self.active_cell
        found_word = None

        for word_obj in self.words:
            if word_obj["direction"] == self.active_direction and (r_active, c_active) in word_obj["cells"]:
                found_word = word_obj
                break
        
        # If no word in current direction, try to find one in the other direction
        if not found_word:
            other_direction = "D" if self.active_direction == "A" else "A"
            for word_obj in self.words:
                if word_obj["direction"] == other_direction and (r_active, c_active) in word_obj["cells"]:
                    found_word = word_obj
                    self.active_direction = other_direction # Switch to this direction
                    break
        
        if found_word:
            self.current_word_highlight = found_word["cells"]
            self.active_clue_text = f"{found_word['number']}{found_word['direction']}. {found_word['clue']}"
            # Ensure active cell is the start of the segment of this word for typing
            # For example, if you click in the middle of "PYTHON", typing should still fill "PYTHON"
            # The current active_cell is fine for this logic.

    def _move_active_cell(self, dr, dc):
        """Moves the active cell by dr, dc, skipping black cells."""
        if not self.active_cell:
            # Try to select the first available cell
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.puzzle_grid[r][c] != '#':
                        self.active_cell = (r,c)
                        self._update_active_word_highlight_and_clue()
                        return
            return # No valid cells

        r, c = self.active_cell
        
        # If moving along the current word's direction
        if self.active_direction == "A": # Across
            next_r, next_c = r, c + dc
        else: # Down
            next_r, next_c = r + dr, c

        # Check bounds and if it's a valid cell
        if 0 <= next_r < GRID_SIZE and 0 <= next_c < GRID_SIZE and \
           self.puzzle_grid[next_r][next_c] != '#':
            # Check if the new cell is part of the currently highlighted word
            if (next_r, next_c) in self.current_word_highlight:
                self.active_cell = (next_r, next_c)
            else: # Moved out of current word, try to find a new word at the new cell
                self.active_cell = (next_r, next_c)
                self._update_active_word_highlight_and_clue() # This will try to find a new word
                # If no word is found in current direction, it might switch or clear highlight
        else: # If out of bounds or black cell, try general movement
            # This part handles jumping to the next available cell if the direct move is blocked
            # or if not moving along the word.
            # For simplicity, this example will only move if the direct next cell in word is valid.
            # A more advanced version would "jump" to the next letter of the current word or next word.
            
            # Fallback: simple boundary-respecting move if not in a word context
            # This is a simpler arrow key navigation if not strictly following a word path
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < GRID_SIZE and 0 <= new_c < GRID_SIZE and self.puzzle_grid[new_r][new_c] != '#':
                self.active_cell = (new_r, new_c)
                self._update_active_word_highlight_and_clue()


    def _handle_keypress(self, event):
        """Handles keyboard input."""
        if not self.active_cell:
            return

        r, c = self.active_cell

        if event.key == pygame.K_BACKSPACE:
            self.user_grid[r][c] = ''
            # Optionally, move back one cell in the current word direction
            if self.active_direction == "A" and c > 0 :
                # Find previous cell in this word
                prev_cell_in_word = None
                current_word_cells = self.current_word_highlight
                if (r,c) in current_word_cells:
                    idx = current_word_cells.index((r,c))
                    if idx > 0:
                        prev_cell_in_word = current_word_cells[idx-1]
                
                if prev_cell_in_word and self.puzzle_grid[prev_cell_in_word[0]][prev_cell_in_word[1]] != '#':
                    self.active_cell = prev_cell_in_word
                # elif c > 0 and self.puzzle_grid[r][c-1] != '#': # Simple move left
                #     self.active_cell = (r, c - 1)

            elif self.active_direction == "D" and r > 0:
                prev_cell_in_word = None
                current_word_cells = self.current_word_highlight
                if (r,c) in current_word_cells:
                    idx = current_word_cells.index((r,c))
                    if idx > 0:
                        prev_cell_in_word = current_word_cells[idx-1]

                if prev_cell_in_word and self.puzzle_grid[prev_cell_in_word[0]][prev_cell_in_word[1]] != '#':
                    self.active_cell = prev_cell_in_word
                # elif r > 0 and self.puzzle_grid[r-1][c] != '#': # Simple move up
                #     self.active_cell = (r - 1, c)
            self._update_active_word_highlight_and_clue()


        elif event.unicode.isalpha() and len(event.unicode) == 1:
            self.user_grid[r][c] = event.unicode.upper()
            # Move to next cell in the current word direction
            if self.active_direction == "A":
                next_cell_in_word = None
                current_word_cells = self.current_word_highlight
                if (r,c) in current_word_cells:
                    idx = current_word_cells.index((r,c))
                    if idx < len(current_word_cells) - 1:
                        next_cell_in_word = current_word_cells[idx+1]
                
                if next_cell_in_word and self.puzzle_grid[next_cell_in_word[0]][next_cell_in_word[1]] != '#':
                     self.active_cell = next_cell_in_word
                # elif c + 1 < GRID_SIZE and self.puzzle_grid[r][c+1] != '#': # Simple move right
                #     self.active_cell = (r, c + 1)


            elif self.active_direction == "D":
                next_cell_in_word = None
                current_word_cells = self.current_word_highlight
                if (r,c) in current_word_cells:
                    idx = current_word_cells.index((r,c))
                    if idx < len(current_word_cells) - 1:
                        next_cell_in_word = current_word_cells[idx+1]
                
                if next_cell_in_word and self.puzzle_grid[next_cell_in_word[0]][next_cell_in_word[1]] != '#':
                     self.active_cell = next_cell_in_word
                # elif r + 1 < GRID_SIZE and self.puzzle_grid[r+1][c] != '#': # Simple move down
                #     self.active_cell = (r + 1, c)
            self._update_active_word_highlight_and_clue()


        elif event.key == pygame.K_LEFT:
            self._move_active_cell(0, -1)
        elif event.key == pygame.K_RIGHT:
            self._move_active_cell(0, 1)
        elif event.key == pygame.K_UP:
            self._move_active_cell(-1, 0)
        elif event.key == pygame.K_DOWN:
            self._move_active_cell(1, 0)
        elif event.key == pygame.K_TAB: # Use Tab to toggle direction
            if self.active_cell:
                is_across_word = any(word for word in self.words if word["direction"] == "A" and self.active_cell in word["cells"])
                is_down_word = any(word for word in self.words if word["direction"] == "D" and self.active_cell in word["cells"])
                if is_across_word and is_down_word:
                    self.active_direction = "D" if self.active_direction == "A" else "A"
                    self._update_active_word_highlight_and_clue()


    def run(self):
        """Main game loop."""
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left mouse button
                        # Check if click is within the grid area
                        if 0 <= event.pos[1] < GRID_HEIGHT:
                             self._handle_click(event.pos)
                        # Potentially handle clicks on clue list later to select word
                if event.type == pygame.KEYDOWN:
                    self._handle_keypress(event)

            self.screen.fill(BLACK) # Background for areas outside grid/clues
            self._draw_grid()
            self._draw_clues()
            self._draw_info_bar()

            pygame.display.flip() # Update the full screen
            clock.tick(30) # Limit to 30 FPS

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = CrosswordGame()
    game.run()
