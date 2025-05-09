#include <iostream>
#include <vector>
#include <string>
#include <iomanip> // For std::setw

// Structure to hold all information about a word in the crossword
struct WordInfo {
    std::string word;    // The actual word
    std::string clue;    // The clue for the word
    int row;             // Starting row (0-indexed)
    int col;             // Starting column (0-indexed)
    char direction;      // 'A' for Across, 'D' for Down
    int number;          // The number assigned to this word in the puzzle
};

class Crossword {
public:
    // Constructor initializes the crossword grid
    Crossword(int r, int c) : rows(r), cols(c), currentWordNumber(0) {
        // Initialize solutionGrid with '#' (representing blocked cells)
        solutionGrid.resize(rows, std::vector<char>(cols, '#'));
        // Initialize playerGrid (what the player sees) also with '#'
        // Fillable cells will be changed to '_' when words are added
        playerGrid.resize(rows, std::vector<char>(cols, '#'));
        // Initialize numberedPlayerGrid (for displaying clues with numbers)
        // Each cell will be a 3-character string for formatting
        numberedPlayerGrid.resize(rows, std::vector<std::string>(cols, "###"));
    }

    // Adds a word to the crossword
    void addWord(const std::string& w, const std::string& cl, int r, int c, char dir) {
        if (r >= rows || c >= cols || r < 0 || c < 0) {
            std::cerr << "Warning: Word '" << w << "' starting position (" << r << "," << c << ") is out of bounds." << std::endl;
            return;
        }

        currentWordNumber++; // Assign a new number to this word
        words.push_back({w, cl, r, c, dir, currentWordNumber});

        for (size_t i = 0; i < w.length(); ++i) {
            if (dir == 'A') { // Across
                if ((c + i) < cols) {
                    // Check for conflicts before placing
                    if (solutionGrid[r][c + i] != '#' && solutionGrid[r][c + i] != w[i]) {
                        std::cerr << "Conflict for word " << w << " at (" << r << "," << c + i << ") with existing char " << solutionGrid[r][c+i] << std::endl;
                        // Potentially handle error or skip word
                    }
                    solutionGrid[r][c + i] = w[i];
                    playerGrid[r][c + i] = '_'; // Mark as a fillable cell for the player
                } else {
                    std::cerr << "Warning: Word '" << w << "' (Across) goes out of bounds." << std::endl;
                    break; 
                }
            } else { // Down
                if ((r + i) < rows) {
                     // Check for conflicts before placing
                    if (solutionGrid[r + i][c] != '#' && solutionGrid[r + i][c] != w[i]) {
                        std::cerr << "Conflict for word " << w << " at (" << r + i << "," << c << ") with existing char " << solutionGrid[r+i][c] << std::endl;
                        // Potentially handle error or skip word
                    }
                    solutionGrid[r + i][c] = w[i];
                    playerGrid[r + i][c] = '_'; // Mark as a fillable cell for the player
                } else {
                     std::cerr << "Warning: Word '" << w << "' (Down) goes out of bounds." << std::endl;
                    break;
                }
            }
        }
    }
    
    // Prepares the player grid with numbers at the start of each word
    void preparePlayerGridWithNumbers() {
        // Initialize with blocks or spaces for letters based on playerGrid
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                if (playerGrid[i][j] == '#') {
                    numberedPlayerGrid[i][j] = "###"; // Represents a blocked cell
                } else {
                    numberedPlayerGrid[i][j] = " _ "; // Represents an empty fillable cell
                }
            }
        }

        // Add numbers to the starting cells of words
        for (const auto& wordInfo : words) {
            if (wordInfo.row < rows && wordInfo.col < cols) {
                std::string numStr = std::to_string(wordInfo.number);
                
                // Format number to fit in the cell (e.g., "1  ", "12 ", " 1_")
                // This simple version just puts the number.
                // A more sophisticated version might handle overlapping numbers (e.g. 1A and 1D start same cell)
                if (playerGrid[wordInfo.row][wordInfo.col] == '_') { // Only if it's a fillable cell
                    if (numStr.length() == 1) {
                        numberedPlayerGrid[wordInfo.row][wordInfo.col] = " " + numStr + " ";
                    } else if (numStr.length() == 2) {
                        numberedPlayerGrid[wordInfo.row][wordInfo.col] = numStr + " ";
                    } else { // For numbers > 99, just take first 3 chars.
                        numberedPlayerGrid[wordInfo.row][wordInfo.col] = numStr.substr(0,3);
                    }
                }
            }
        }
    }

    // Displays the player's grid (empty cells with numbers)
    void displayPlayerGridWithNumbers() const {
        std::cout << "Crossword Puzzle (10x10):" << std::endl;
        // Print column headers (0-9)
        std::cout << "   "; // Space for row numbers
        for (int j = 0; j < cols; ++j) {
            std::cout << std::setw(3) << j;
        }
        std::cout << std::endl;
        std::cout << "   "; // Space for row numbers
        for (int j = 0; j < cols; ++j) {
            std::cout << "---"; // Separator line
        }
        std::cout << std::endl;

        for (int i = 0; i < rows; ++i) {
            std::cout << std::setw(2) << i << "|"; // Print row header
            for (int j = 0; j < cols; ++j) {
                std::cout << numberedPlayerGrid[i][j]; // Print cell content (number or placeholder)
            }
            std::cout << std::endl;
        }
        std::cout << std::endl;
    }

    // Displays the solution grid
    void displaySolution() const {
        std::cout << "Solution:" << std::endl;
        // Print column headers
        std::cout << "   "; 
        for (int j = 0; j < cols; ++j) {
            std::cout << std::setw(2) << j;
        }
        std::cout << std::endl;
        std::cout << "   ";
         for (int j = 0; j < cols; ++j) {
            std::cout << "--";
        }
        std::cout << std::endl;


        for (int i = 0; i < rows; ++i) {
            std::cout << std::setw(2) << i << "| "; // Print row header
            for (int j = 0; j < cols; ++j) {
                std::cout << solutionGrid[i][j] << " ";
            }
            std::cout << std::endl;
        }
        std::cout << std::endl;
    }

    // Displays all clues
    void displayClues() const {
        std::cout << "Clues:" << std::endl;
        std::cout << "------" << std::endl;
        
        std::cout << "Across:" << std::endl;
        for (const auto& word : words) {
            if (word.direction == 'A') {
                std::cout << std::setw(2) << word.number << ". " << word.clue 
                          << " (" << word.word.length() << " letters)" << std::endl;
            }
        }
        std::cout << std::endl;
        
        std::cout << "Down:" << std::endl;
        for (const auto& word : words) {
            if (word.direction == 'D') {
                 std::cout << std::setw(2) << word.number << ". " << word.clue 
                           << " (" << word.word.length() << " letters)" << std::endl;
            }
        }
        std::cout << std::endl;
    }

private:
    int rows, cols;
    std::vector<std::vector<char>> solutionGrid;       // Stores the solution characters
    std::vector<std::vector<char>> playerGrid;         // Stores '_' for fillable, '#' for blocked
    std::vector<std::vector<std::string>> numberedPlayerGrid; // Stores formatted strings for display
    std::vector<WordInfo> words;                       // List of all words and their info
    int currentWordNumber;                             // Counter for assigning numbers to words
};

int main() {
    // Create a 10x10 crossword puzzle
    Crossword game(10, 10);

    // Add words to the puzzle:
    // Format: game.addWord("WORD", "Clue for the word", row, col, 'A' or 'D');
    
    // Word 1
    game.addWord("CPU", "Central Processing Unit", 1, 1, 'A');
    // Word 2
    game.addWord("RAM", "Volatile memory", 3, 1, 'A');
    // Word 3
    game.addWord("API", "Interface for software interaction", 0, 5, 'D');
    // Word 4
    game.addWord("BUG", "An error in code", 5, 3, 'A');
    // Word 5
    game.addWord("GIT", "Version control system", 3, 7, 'D');
    // Word 6
    game.addWord("LINKER", "Combines object files", 0, 8, 'D');
    // Word 7
    game.addWord("CODE", "Set of program instructions", 7, 0, 'A');
     // Word 8
    game.addWord("NULL", "Represents no value or address", 7,5,'A');


    // After all words are added, prepare the grid for display
    game.preparePlayerGridWithNumbers();

    // Display the empty puzzle grid with numbers
    game.displayPlayerGridWithNumbers();

    // Display the clues
    game.displayClues();

    // Optionally, display the solution
    std::cout << "\nWould you like to see the solution? (y/n): ";
    char choice;
    std::cin >> choice;
    if (choice == 'y' || choice == 'Y') {
       game.displaySolution();
    }

    return 0;
}

