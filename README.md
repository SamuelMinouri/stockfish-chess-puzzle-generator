stockfish-chess-puzzle-generator

A fully automated chess puzzle generator built in Python that uses the Stockfish engine to create, analyze, and export daily puzzles — complete with SVG and PNG boards and ready-made Twitter threads.



♟ Features Deep Dive

This project is designed to streamline the entire workflow from raw chess position generation to social media deployment.

Position Generation

The script utilizes a semi-randomized process to simulate partial chess games. This ensures that the generated positions are not only legal but also aesthetically plausible as tactical puzzles, avoiding overly contrived or early-game setups.





Game Simulation: A position is reached by playing a set number of random, legal moves from the starting position (rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1).



Depth Control: The simulation depth is controlled to ensure the position is complex enough for a tactical solution, usually around 8 to 15 ply.

Stockfish Engine Integration

The core intelligence comes from the Stockfish engine, leveraging its deep search capabilities for precise tactical calculation.





Mate Finding: Stockfish is queried specifically to find forced checkmates of short depth: Mate in 2 (M2) or Mate in 3 (M3). This targeted search dramatically improves the quality and relevance of the generated puzzles.



Evaluation Parameters: The engine is typically configured with high search depth (e.g., depth 25+) and aggressive pruning to quickly confirm forced lines.

Automated Export Pipeline

Once a valid mating line is found, the generator automates the creation of all necessary assets for publication.

Asset TypeFormat(s)PurposePuzzle BoardSVG, PNGThe initial position presented to the solver. SVG is scalable; PNG is immediately usable.Solution StepsPNGA sequence of images showing each move of the forced line to clearly illustrate the solution.Social Media Texttweet.txtA formatted text file containing the puzzle title, challenge, and relevant hashtags, optimized for Twitter/X.Metadatapuzzle_data.txtStores FEN, solution moves (in UCI format), and engine evaluation for internal tracking.

File Structure Management

The system maintains organization by creating a dedicated, timestamped (or day-numbered) directory for every successful puzzle generation.

/generated_puzzles/
├── day001_generated/
│   ├── 001_puzzle_start.svg        (Initial board)
│   ├── 001_puzzle_start.png
│   ├── 001_solution_step1.png      (White's 1st move)
│   ├── 001_solution_step2.png      (Black's reply)
│   ├── 001_solution_step3.png      (White's Mating move)
│   ├── 001_tweet.txt               (Ready-to-post text)
│   └── 001_puzzle_data.txt         (Internal FEN/UCI data)
└── puzzle_index.txt                (Master log linking to all generated puzzles)


The puzzle_index.txt acts as a crucial manifest, allowing users or subsequent scripts to easily catalog or access previously generated content.



🧠 How It Works: The Technical Workflow

The generation process follows a structured loop designed for efficiency and verification.

Step 1: Position Initialization

The script initializes a chess.Board() object, starting from the initial position. It then enters a random move loop.

[
\text{Position} \leftarrow \text{Start Position} ] [ \text{For } i = 1 \text{ to } N_{\text{sim}}: ] [ \quad \text{Move} \leftarrow \text{Random Legal Move from Position} ] [ \quad \text{Position} \leftarrow \text{Position after Move} ] [ \text{End For} ]

Step 2: Engine Analysis (Mate Verification)

The resulting FEN string is passed to Stockfish via the python-chess library, specifically requesting a forced mate line up to depth 3.

The primary command sent to Stockfish is often a combination of setoption and go movetime X or go depth Y, focusing on mate search:

position fen "..."
go depth 30 mate 3 


If Stockfish returns an evaluation showing a definitive mate (e.g., info depth 3 seldepth 15 score cp +M180 for M2, or +M270 for M3), the position is accepted as a valid puzzle candidate.

Step 3: Board Rendering and Labeling

For an accepted position (e.g., White to move and mate in 2), the generator uses a library (like chess.svg integration or a custom drawing function) to render the SVG board.

The rendered board is explicitly labeled:

White to move and mate in 2


Step 4: Solution Tracing and Image Generation

The engine provides the UCI notation for the optimal line, for example: e7e8q, b8c6, f8h6#.

For each half-move in the solution line, a new board state is created, and an image is rendered, representing the state after the engine’s recommended move. This produces the sequential step-by-step guide.

Step 5: Final Packaging

All generated assets (images, text files) are organized into the new dated folder, and the puzzle_index.txt file is updated to register the new entry.



⚙️ Requirements Checklist

To run the stockfish-chess-puzzle-generator successfully, you need both software components and specific Python dependencies.

Python Libraries (Installation via )

These libraries handle board manipulation, FEN operations, and image vector conversion.

pip install python-chess cairosvg






python-chess: The essential library for interfacing with chess logic, move generation, and communicating with UCI engines like Stockfish.



cairosvg: Used to convert the intermediate SVG board representations into static PNG files for easy use online. (Note: cairosvg often requires the underlying Cairo graphics library installed on your operating system.)

Stockfish Engine

The engine executable must be present for the Python script to communicate with it via standard input/output (stdin/stdout).





Download: Obtain the latest stable version of the Stockfish engine from the official repository: https://stockfishchess.org/.



Placement: Place the downloaded executable (e.g., stockfish.exe for Windows or just stockfish for Linux/macOS) directly into the root directory of your puzzle generator project, alongside main.py.



🧩 Example Output Structure Walkthrough

After a successful run generating the first few puzzles, your file system should reflect this organized structure:

stockfish-chess-puzzle-generator/
├── main.py
├── stockfish.exe
├── generated_puzzles/
│   ├── day001_generated/
│   │   ├── 001_puzzle_start.svg
│   │   ├── 001_puzzle_start.png
│   │   ├── 001_solution_step1.png  <- W: 1. Qh7+
│   │   ├── 001_solution_step2.png  <- B: ... Kxh7
│   │   ├── 001_solution_step3.png  <- W: 2. Rg7# (Mate)
│   │   ├── 001_tweet.txt
│   │   └── 001_puzzle_data.txt
│   ├── day002_generated/
│   └── puzzle_index.txt            <- Master index file


This structure ensures that every piece of content needed for a post—the visual, the solution steps, and the text—is contained within its own logical directory.



▶️ Running the Bot

Execution is straightforward, relying on the configuration set within main.py.

Execution Command

Navigate to the project root directory in your terminal or command prompt and execute:

python main.py


Default Configuration

By default, the script is set to generate a predetermined quantity of puzzles in a single batch execution.





Number of Puzzles: The constant NUM_PUZZLES (configurable within main.py) typically defaults to 200. This means the script will attempt to find 200 unique, valid mate-in-2 or mate-in-3 puzzles before terminating.



Output Location: All results are funneled into the /generated_puzzles/ directory.



📱 Tweet Template Example ()

The generator populates a standardized text file to eliminate manual drafting of social media posts. This template is designed to maximize engagement by clearly presenting the challenge.

Content Example:

🧩 Daily Chess Puzzle #42
White to move and mate in 3
Generated by Stockfish AI ⭐

Position FEN: r4rk1/1bpq1ppp/p1n2n2/1p2p3/1P1bP3/P1N2N2/1BP2PPP/R2QKB1R w KQ - 1 12

Can you solve it? 🤔
Type your first move below!
#Chess #Puzzle #Stockfish #ChessPuzzle




📦 Repository Structure Summary

A clean, standard structure ensures maintainability and easy setup.

stockfish-chess-puzzle-generator/
├── main.py                 # Core generator logic (Position simulation, engine comms, file I/O)
├── stockfish.exe            # (The downloaded Stockfish engine executable)
├── generated_puzzles/       # Directory housing all daily puzzle output folders
├── requirements.txt         # List of required pip packages
├── README.md                # This comprehensive documentation file
└── LICENSE                  # The project's open-source license




🧾 License

This project is released under the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



💡 Credits and Acknowledgment

This project is a collaboration leveraging powerful open-source tools:





Engine Power: The core tactical strength is derived entirely from the Stockfish Engine, the world's leading open-source chess engine.



Python Interface: The interaction layer is built upon the robust python-chess library.



Development: Developed by Majid Vaghari (@sakhaleta), combining AI techniques with practical content generation needs.



🐦 Launch Tweet (Promotional Template)

This is the suggested text for announcing the release of the stockfish-chess-puzzle-generator on social media platforms like X (Twitter):

NEW PROJECT LAUNCH! 📣

♟️ Introducing: stockfish-chess-puzzle-generator

An open-source Python tool that automates daily tactical puzzle creation using Stockfish. Find mate-in-2/3 problems, generate board images (SVG/PNG), and get ready-to-post tweet threads automatically.

Run it, post it, challenge the world.
🔗 [Link to GitHub Repo]
#Chess #Stockfish #AI #Python #OpenSource
