using System;
using System.Collections.Generic;
using System.Linq;

class CrosswordGenerator
{
    private const int SIZE = 10;
    private char[,] grid = new char[SIZE, SIZE];
    private List<string> words = new List<string>
    {
        "ALGORITHM", "COMPUTER", "DATABASE", "FUNCTION", "VARIABLE",
        "ABSTRACT", "KEYBOARD", "NETWORK", "SOFTWARE", "STORAGE",
        "INTERFACE", "PROGRAM", "CONSOLE", "DEBUG", "METHOD",
        "ARRAY", "CODE", "LOOP", "CLASS", "DATA"
    };
    
    private Random random = new Random();
    private List<string> usedWords = new List<string>();
    private List<WordPlacement> placements = new List<WordPlacement>();
    
    public void Generate()
    {
        // Initialize grid with empty cells
        for (int i = 0; i < SIZE; i++)
        {
            for (int j = 0; j < SIZE; j++)
            {
                grid[i, j] = ' ';
            }
        }
        
        // Shuffle the word list
        words = words.OrderBy(x => random.Next()).ToList();
        
        // Try to place first word horizontally in the middle
        int startRow = SIZE / 2;
        int startCol = random.Next(0, SIZE - words[0].Length + 1);
        PlaceWord(words[0], startRow, startCol, true);
        
        // Try to place remaining words
        for (int i = 1; i < words.Count; i++)
        {
            if (!TryPlaceWord(words[i]))
            {
                // Couldn't place this word
                continue;
            }
        }
        
        // Fill in remaining spaces with random letters
        FillEmptyCells();
        
        // Display the generated crossword
        DisplayCrossword();
        
        // Display the word list with clues
        DisplayWordList();
    }
    
    private bool TryPlaceWord(string word)
    {
        // Try to find intersections with existing words
        foreach (var placement in placements)
        {
            for (int i = 0; i < word.Length; i++)
            {
                for (int j = 0; j < placement.Word.Length; j++)
                {
                    if (word[i] == placement.Word[j])
                    {
                        // Potential intersection found
                        if (placement.Horizontal)
                        {
                            // Try to place the new word vertically
                            int row = placement.Row - i;
                            int col = placement.Col + j;
                            
                            if (row >= 0 && row + word.Length <= SIZE && CanPlaceWord(word, row, col, false))
                            {
                                PlaceWord(word, row, col, false);
                                return true;
                            }
                        }
                        else
                        {
                            // Try to place the new word horizontally
                            int row = placement.Row + j;
                            int col = placement.Col - i;
                            
                            if (col >= 0 && col + word.Length <= SIZE && CanPlaceWord(word, row, col, true))
                            {
                                PlaceWord(word, row, col, true);
                                return true;
                            }
                        }
                    }
                }
            }
        }
        
        return false;
    }
    
    private bool CanPlaceWord(string word, int row, int col, bool horizontal)
    {
        if (horizontal)
        {
            if (col > 0 && grid[row, col - 1] != ' ') return false; // Check before start
            if (col + word.Length < SIZE && grid[row, col + word.Length] != ' ') return false; // Check after end
            
            for (int i = 0; i < word.Length; i++)
            {
                if (col + i >= SIZE) return false;
                
                if (grid[row, col + i] != ' ' && grid[row, col + i] != word[i])
                    return false;
                
                // Check for adjacent words (except at intersection points)
                if (grid[row, col + i] == ' ')
                {
                    if (row > 0 && grid[row - 1, col + i] != ' ') return false;
                    if (row < SIZE - 1 && grid[row + 1, col + i] != ' ') return false;
                }
            }
        }
        else // Vertical
        {
            if (row > 0 && grid[row - 1, col] != ' ') return false; // Check before start
            if (row + word.Length < SIZE && grid[row + word.Length, col] != ' ') return false; // Check after end
            
            for (int i = 0; i < word.Length; i++)
            {
                if (row + i >= SIZE) return false;
                
                if (grid[row + i, col] != ' ' && grid[row + i, col] != word[i])
                    return false;
                
                // Check for adjacent words (except at intersection points)
                if (grid[row + i, col] == ' ')
                {
                    if (col > 0 && grid[row + i, col - 1] != ' ') return false;
                    if (col < SIZE - 1 && grid[row + i, col + 1] != ' ') return false;
                }
            }
        }
        
        return true;
    }
    
    private void PlaceWord(string word, int row, int col, bool horizontal)
    {
        usedWords.Add(word);
        placements.Add(new WordPlacement { Word = word, Row = row, Col = col, Horizontal = horizontal });
        
        for (int i = 0; i < word.Length; i++)
        {
            if (horizontal)
                grid[row, col + i] = word[i];
            else
                grid[row + i, col] = word[i];
        }
    }
    
    private void FillEmptyCells()
    {
        for (int i = 0; i < SIZE; i++)
        {
            for (int j = 0; j < SIZE; j++)
            {
                if (grid[i, j] == ' ')
                {
                    grid[i, j] = (char)('A' + random.Next(0, 26));
                }
            }
        }
    }
    
    private void DisplayCrossword()
    {
        Console.WriteLine("10x10 Crossword Puzzle:\n");
        
        // Print top border
        Console.Write("   ");
        for (int j = 0; j < SIZE; j++)
        {
            Console.Write($" {j} ");
        }
        Console.WriteLine();
        
        Console.Write("   ");
        for (int j = 0; j < SIZE; j++)
        {
            Console.Write("---");
        }
        Console.WriteLine();
        
        // Print grid with row numbers
        for (int i = 0; i < SIZE; i++)
        {
            Console.Write($"{i} |");
            for (int j = 0; j < SIZE; j++)
            {
                Console.Write($" {grid[i, j]} ");
            }
            Console.WriteLine("|");
        }
        
        // Print bottom border
        Console.Write("   ");
        for (int j = 0; j < SIZE; j++)
        {
            Console.Write("---");
        }
        Console.WriteLine();
    }
    
    private void DisplayWordList()
    {
        Console.WriteLine("\nWord List and Clues:");
        
        int across = 1;
        int down = 1;
        
        Console.WriteLine("\nACROSS:");
        foreach (var placement in placements.OrderBy(p => p.Row * 100 + p.Col))
        {
            if (placement.Horizontal)
            {
                Console.WriteLine($"{across}. ({placement.Row},{placement.Col}) {GetClue(placement.Word)}");
                across++;
            }
        }
        
        Console.WriteLine("\nDOWN:");
        foreach (var placement in placements.OrderBy(p => p.Row * 100 + p.Col))
        {
            if (!placement.Horizontal)
            {
                Console.WriteLine($"{down}. ({placement.Row},{placement.Col}) {GetClue(placement.Word)}");
                down++;
            }
        }
    }
    
    private string GetClue(string word)
    {
        Dictionary<string, string> clues = new Dictionary<string, string>
        {
            {"ALGORITHM", "Step-by-step procedure for calculations"},
            {"COMPUTER", "Electronic device that processes data"},
            {"DATABASE", "Organized collection of data"},
            {"FUNCTION", "Subroutine that returns a value"},
            {"VARIABLE", "Storage location paired with a name"},
            {"ABSTRACT", "Conceptual rather than concrete"},
            {"KEYBOARD", "Input device with keys"},
            {"NETWORK", "Group of interconnected computers"},
            {"SOFTWARE", "Programs and data that run on a computer"},
            {"STORAGE", "Retention of retrievable data"},
            {"INTERFACE", "Connection between systems or users"},
            {"PROGRAM", "Set of instructions for a computer"},
            {"CONSOLE", "Text input/output environment"},
            {"DEBUG", "Find and fix errors in code"},
            {"METHOD", "Function that belongs to a class"},
            {"ARRAY", "Collection of elements of the same type"},
            {"CODE", "Instructions written in a programming language"},
            {"LOOP", "Structure that repeats a sequence of instructions"},
            {"CLASS", "Blueprint for creating objects"},
            {"DATA", "Information processed by a computer"}
        };
        
        if (clues.ContainsKey(word))
            return clues[word];
        else
            return "Clue not found";
    }
    
    class WordPlacement
    {
        public string Word { get; set; }
        public int Row { get; set; }
        public int Col { get; set; }
        public bool Horizontal { get; set; }
    }
    
    static void Main(string[] args)
    {
        Console.WriteLine("Generating 10x10 Crossword Puzzle...\n");
        CrosswordGenerator generator = new CrosswordGenerator();
        generator.Generate();
        Console.WriteLine("\nPress any key to exit.");
        Console.ReadKey();
    }
}
