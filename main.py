import random
from pathlib import Path
from datetime import datetime
import chess
import chess.engine
import chess.svg
import time

# For PNG conversion
try:
    import cairosvg
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False
    print("⚠️  Install cairosvg for PNG export: pip install cairosvg")

# ===== CONFIGURATION =====
STOCKFISH_PATH = Path("stockfish.exe")  # Stockfish in same folder
OUTPUT_DIR = Path("generated_puzzles")
EXPORT_PNG = True
NUM_PUZZLES = 200  # Number of puzzles to generate

# Stockfish analysis settings
ANALYSIS_TIME = 2.0  # seconds per position
MATE_DEPTH = 10  # depth to search for mates

# ===== HELPER FUNCTIONS =====
def get_title_text(board, mate_in):
    """Generate puzzle title"""
    color = "White" if board.turn == chess.WHITE else "Black"
    if mate_in:
        return f"{color} to move and mate in {mate_in}"
    return f"{color} to move and win"

def svg_to_png(svg_file, png_file):
    """Convert SVG to PNG for social media"""
    if not HAS_CAIRO:
        return False
    
    try:
        cairosvg.svg2png(url=str(svg_file), write_to=str(png_file), scale=2)
        return True
    except Exception as e:
        print(f"    ❌ PNG conversion failed: {e}")
        return False

def create_board_svg_with_title(board, title, last_move=None, orientation=chess.WHITE, size=400):
    """Create SVG with title above the board"""
    board_svg = chess.svg.board(
        board,
        size=size,
        lastmove=last_move,
        orientation=orientation,
        colors={"square light": "#f0d9b5", "square dark": "#b58863"}
    )
    
    svg_with_title = f'''<svg width="{size}" height="{size + 40}" xmlns="http://www.w3.org/2000/svg">
  <text x="{size//2}" y="25" text-anchor="middle" font-size="18"
        font-family="Arial, sans-serif" fill="white" font-weight="bold">
    {title}
  </text>
  
  <g transform="translate(0,40)">
    {board_svg}
  </g>
</svg>'''
    return svg_with_title

def generate_random_game(max_moves=40):
    """Generate a random chess game to create puzzle positions"""
    board = chess.Board()
    moves_played = 0
    
    while not board.is_game_over() and moves_played < max_moves:
        # Play semi-random moves (weighted towards center and development)
        legal_moves = list(board.legal_moves)
        
        if not legal_moves:
            break
        
        # Weight moves by basic heuristics
        move_scores = []
        for move in legal_moves:
            score = random.random()
            
            # Prefer captures
            if board.is_capture(move):
                score += 1.0
            
            # Prefer center moves in opening
            if moves_played < 10:
                to_square = move.to_square
                if chess.square_file(to_square) in [3, 4] and chess.square_rank(to_square) in [3, 4]:
                    score += 0.5
            
            move_scores.append((score, move))
        
        # Choose move with some randomness
        move_scores.sort(reverse=True)
        top_moves = move_scores[:min(5, len(move_scores))]
        chosen_move = random.choice(top_moves)[1]
        
        board.push(chosen_move)
        moves_played += 1
    
    return board

def analyze_for_mate(engine, board, max_mate=3):
    """Check if position has mate in 2 or 3"""
    try:
        info = engine.analyse(board, chess.engine.Limit(depth=MATE_DEPTH))
        score = info.get("score")
        
        if score and score.white().is_mate():
            mate_in = abs(score.white().mate())
            if mate_in <= max_mate:
                # Get the principal variation (solution)
                pv = info.get("pv", [])
                if len(pv) >= mate_in * 2 - 1:  # Enough moves for mate
                    return mate_in, pv[:mate_in * 2]
        
        return None, None
    except Exception as e:
        return None, None

def find_puzzle_position(engine, max_attempts=50):
    """Generate random positions until we find one with mate in 2 or 3"""
    for attempt in range(max_attempts):
        # Generate random game
        board = generate_random_game(random.randint(15, 35))
        
        # Skip if game is over
        if board.is_game_over():
            continue
        
        # Analyze position
        mate_in, solution = analyze_for_mate(engine, board)
        
        if mate_in and solution:
            return board, mate_in, solution
    
    return None, None, None

def save_puzzle(puzzle_data, puzzle_number, output_dir, export_png=True):
    """Save puzzle to files"""
    board = puzzle_data['board']
    mate_in = puzzle_data['mate_in']
    solution = puzzle_data['solution']
    
    # Create puzzle directory
    base_name = f"day{puzzle_number:03d}_generated"
    puzzle_dir = output_dir / base_name
    puzzle_dir.mkdir(exist_ok=True)
    
    # Determine orientation
    board_orientation = board.turn
    
    # Get title
    title_text = get_title_text(board, mate_in)
    
    # Save FEN and solution
    fen_file = puzzle_dir / "puzzle_data.txt"
    with open(fen_file, "w", encoding="utf-8") as f:
        f.write(f"FEN: {board.fen()}\n")
        f.write(f"Mate in: {mate_in}\n")
        f.write(f"Solution (UCI): {' '.join([m.uci() for m in solution])}\n\n")
    
    # === GENERATE PUZZLE IMAGE ===
    puzzle_svg = puzzle_dir / "puzzle.svg"
    puzzle_png = puzzle_dir / "puzzle.png"
    
    puzzle_svg_content = create_board_svg_with_title(
        board,
        title_text,
        last_move=None,
        orientation=board_orientation,
        size=400
    )
    
    with open(puzzle_svg, "w", encoding="utf-8") as f:
        f.write(puzzle_svg_content)
    
    if export_png and HAS_CAIRO:
        svg_to_png(puzzle_svg, puzzle_png)
    
    # === GENERATE STEP-BY-STEP SOLUTION IMAGES ===
    solution_san = []
    solve_board = board.copy()
    
    for i, move in enumerate(solution):
        try:
            san_notation = solve_board.san(move)
            solution_san.append(san_notation)
            
            move_color = "White" if solve_board.turn == chess.WHITE else "Black"
            solve_board.push(move)
            
            step_num = i + 1
            is_checkmate = solve_board.is_checkmate()
            
            if is_checkmate:
                step_title = f"Step {step_num}: {move_color} plays {san_notation} - Checkmate! ✓"
            elif solve_board.is_check():
                step_title = f"Step {step_num}: {move_color} plays {san_notation} +"
            else:
                step_title = f"Step {step_num}: {move_color} plays {san_notation}"
            
            step_svg_content = create_board_svg_with_title(
                solve_board,
                step_title,
                last_move=move,
                orientation=board_orientation,
                size=400
            )
            
            step_svg = puzzle_dir / f"solution_step{step_num}.svg"
            step_png = puzzle_dir / f"solution_step{step_num}.png"
            
            with open(step_svg, "w", encoding="utf-8") as f:
                f.write(step_svg_content)
            
            if export_png and HAS_CAIRO:
                svg_to_png(step_svg, step_png)
                
        except Exception as e:
            print(f"    ⚠️  Error at move {i+1}: {e}")
            break
    
    # === GENERATE TWEET TEXT ===
    solution_text = " ".join(solution_san)
    tweet_file = puzzle_dir / "tweet.txt"
    
    with open(tweet_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("TWEET 1: PUZZLE (Main Tweet)\n")
        f.write("=" * 60 + "\n")
        f.write(f"Attach: puzzle.png\n\n")
        f.write(f"🧩 Daily Chess Puzzle #{puzzle_number}\n\n")
        f.write(f"{title_text}\n")
        f.write(f"Generated by Stockfish AI ⭐\n\n")
        f.write("Can you solve it? 🤔\n\n")
        f.write("#ChessPuzzle #Chess #Tactics\n\n")
        
        f.write("=" * 60 + "\n")
        f.write("TWEET 2: SOLUTION SUMMARY\n")
        f.write("=" * 60 + "\n")
        f.write(f"✅ Solution: {solution_text}\n\n")
        f.write("See step-by-step images below! 👇\n\n")
        
        f.write("=" * 60 + "\n")
        f.write("TWEETS 3+: STEP-BY-STEP THREAD\n")
        f.write("=" * 60 + "\n")
        for i, san in enumerate(solution_san):
            step_num = i + 1
            move_color = "White" if i % 2 == 0 else "Black"
            is_checkmate = "#" in san
            
            f.write(f"\nTweet {step_num + 2}:\n")
            if is_checkmate:
                f.write(f"✓ {move_color}: {san} - Checkmate!\n")
            else:
                f.write(f"{move_color}: {san}\n")
            
            f.write(f"[Attach: solution_step{step_num}.png]\n\n")
    
    return {
        'success': True,
        'mate_in': mate_in,
        'solution_moves': len(solution_san),
        'folder': puzzle_dir
    }

# ===== MAIN EXECUTION =====
def main():
    print("="*70)
    print("🚀 CHESS PUZZLE GENERATOR - STOCKFISH ENGINE MODE")
    print(f"📊 Generating {NUM_PUZZLES} puzzles using Stockfish")
    print("="*70)
    
    # Check if Stockfish exists
    if not STOCKFISH_PATH.exists():
        print(f"\n❌ ERROR: Stockfish not found at {STOCKFISH_PATH.absolute()}")
        print("Please download Stockfish and place stockfish.exe in the same folder.")
        return
    
    start_time = time.time()
    
    # Setup output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Initialize Stockfish
    print(f"\n🔧 Initializing Stockfish engine...")
    try:
        engine = chess.engine.SimpleEngine.popen_uci(str(STOCKFISH_PATH))
        print(f"✅ Stockfish initialized: {engine.id.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Failed to initialize Stockfish: {e}")
        return
    
    # Generate puzzles
    print(f"\n🔄 Starting puzzle generation...\n")
    
    results = {
        'success': [],
        'failed': []
    }
    
    puzzle_count = 0
    attempts = 0
    max_total_attempts = NUM_PUZZLES * 100  # Prevent infinite loop
    
    while puzzle_count < NUM_PUZZLES and attempts < max_total_attempts:
        attempts += 1
        
        print(f"[{puzzle_count + 1}/{NUM_PUZZLES}] Searching for puzzle position (attempt {attempts})...")
        
        try:
            # Find a puzzle position
            board, mate_in, solution = find_puzzle_position(engine, max_attempts=50)
            
            if board and mate_in and solution:
                puzzle_count += 1
                
                print(f"    ✅ Found mate in {mate_in}!")
                
                # Save the puzzle
                puzzle_data = {
                    'board': board,
                    'mate_in': mate_in,
                    'solution': solution
                }
                
                result = save_puzzle(
                    puzzle_data=puzzle_data,
                    puzzle_number=puzzle_count,
                    output_dir=OUTPUT_DIR,
                    export_png=EXPORT_PNG
                )
                
                results['success'].append(result)
                print(f"    📁 Saved to: {result['folder'].name}/")
                
                # Progress indicator
                if puzzle_count % 10 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / puzzle_count
                    remaining = (NUM_PUZZLES - puzzle_count) * avg_time
                    print(f"\n📊 Progress: {puzzle_count}/{NUM_PUZZLES} ({puzzle_count/NUM_PUZZLES*100:.1f}%)")
                    print(f"⏱️  Elapsed: {elapsed:.1f}s | Estimated remaining: {remaining:.1f}s")
                    print(f"🎲 Total attempts: {attempts}\n")
            else:
                print(f"    ⏭️  No puzzle found, trying again...")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results['failed'].append({'error': str(e)})
    
    # Close engine
    engine.quit()
    
    # Final summary
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "="*70)
    print("🎉 GENERATION COMPLETE!")
    print("="*70)
    print(f"✅ Successfully generated: {len(results['success'])} puzzles")
    print(f"❌ Failed attempts: {len(results['failed'])}")
    print(f"🎲 Total position attempts: {attempts}")
    print(f"⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
    
    # Generate master index
    index_file = OUTPUT_DIR / "puzzle_index.txt"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write("STOCKFISH GENERATED PUZZLE COLLECTION\n")
        f.write("="*70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Puzzles: {len(results['success'])}\n")
        f.write(f"Engine: Stockfish\n\n")
        f.write("="*70 + "\n")
        f.write("PUZZLE LIST:\n")
        f.write("="*70 + "\n\n")
        
        for i, result in enumerate(results['success'], start=1):
            f.write(f"Day {i:03d}:\n")
            f.write(f"  Mate in: {result['mate_in']}\n")
            f.write(f"  Solution Moves: {result['solution_moves']}\n")
            f.write(f"  Folder: {result['folder'].name}\n\n")
    
    print(f"\n📋 Master index saved to: {index_file}")
    print(f"\n✅ All done! Ready for {len(results['success'])} days of Twitter posts! 🐦♟️")

if __name__ == "__main__":
    main()