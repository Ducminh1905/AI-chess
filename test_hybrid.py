#!/usr/bin/env python3
"""
Quick Test Script cho Hybrid Chess AI
Chạy để kiểm tra performance và tính năng
"""

import sys
import os
import time
import chess

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import Bot
    from Board import GUI_Board
    print("✅ Modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_hybrid_evaluation():
    """Test hybrid evaluation performance"""
    print("\n🧪 Testing Hybrid Evaluation Performance...")
    
    # Test positions
    test_positions = [
        chess.Board(),  # Starting position
        chess.Board("rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2"),  # After 1.e4 Nf6
        chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4"),  # Italian Game
    ]
    
    modes = ["fast", "balanced", "adaptive", "accurate"]
    iterations = 50
    
    print(f"Testing each mode with {iterations} evaluations per position...")
    
    for mode in modes:
        print(f"\n🎯 Testing {mode.upper()} mode:")
        Bot.set_performance_mode(mode)
        
        total_time = 0
        for i, board in enumerate(test_positions):
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                evaluation = Bot.get_board_val(board)
            
            elapsed = time.perf_counter() - start_time
            avg_time = (elapsed / iterations) * 1000  # ms per evaluation
            
            total_time += elapsed
            print(f"   Position {i+1}: {avg_time:.2f}ms per eval (total: {evaluation})")
        
        avg_per_eval = (total_time / (len(test_positions) * iterations)) * 1000
        print(f"   📊 Average: {avg_per_eval:.2f}ms per evaluation")
        
        # Show performance stats
        stats = Bot.get_performance_stats()
        print(f"   🧠 NN usage: {stats['nn_usage_rate']:.1f}%")

def test_hybrid_search():
    """Test hybrid search performance"""
    print("\n🔍 Testing Hybrid Search Performance...")
    
    board = GUI_Board(600, 600, player_color=chess.WHITE)
    
    search_configs = [
        ("Fast", "fast", 3, 1.0),
        ("Balanced", "balanced", 3, 2.0),  
        ("Adaptive", "adaptive", 4, 3.0),
        ("Accurate", "accurate", 4, 4.0),
    ]
    
    for name, mode, depth, time_limit in search_configs:
        print(f"\n🎯 Testing {name} search (depth {depth}, {time_limit}s limit):")
        
        Bot.set_performance_mode(mode)
        
        start_time = time.perf_counter()
        move = Bot.minimax_search(board, depth, False, True, time_limit)
        elapsed = time.perf_counter() - start_time
        
        print(f"   ⏱️ Time: {elapsed:.2f}s")
        print(f"   🎲 Move: {move}")
        
        stats = Bot.get_performance_stats()
        print(f"   🧠 NN usage: {stats['nn_usage_rate']:.1f}%")
        print(f"   📊 Evaluations: {stats['total_evaluations']}")

def test_learning_capability():
    """Test learning from game data"""
    print("\n🧠 Testing Learning Capability...")
    
    # Mock game data
    sample_games = [
        {
            'move_history': ['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5'],
            'result': 'AI Win',
            'final_fen': 'r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3'
        },
        {
            'move_history': ['d2d4', 'd7d5', 'c2c4', 'e7e6'],
            'result': 'Draw',
            'final_fen': 'rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3'
        },
        {
            'move_history': ['e2e4', 'e7e5', 'f2f4'],
            'result': 'AI Loss',
            'final_fen': 'rnbqkbnr/pppp1ppp/8/4p3/4PP2/8/PPPP2PP/RNBQKBNR b KQkq - 0 2'
        }
    ]
    
    print(f"Testing learning from {len(sample_games)} sample games...")
    
    for i, game_data in enumerate(sample_games):
        print(f"\n📚 Learning from game {i+1} (result: {game_data['result']}):")
        
        success = Bot.train_from_game(game_data)
        
        if success:
            print("   ✅ Learning successful!")
        else:
            print("   ⚠️ Learning failed or limited")

def benchmark_against_traditional():
    """Benchmark hybrid vs traditional AI"""
    print("\n⚡ Benchmarking Hybrid vs Traditional AI...")
    
    test_board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4")
    iterations = 100
    
    # Test traditional only
    print("🤖 Testing Traditional AI...")
    Bot.set_performance_mode("fast")  # Pure traditional
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        eval_traditional = Bot.get_board_val(test_board)
    traditional_time = time.perf_counter() - start_time
    
    # Test hybrid
    print("🧠 Testing Hybrid AI...")
    Bot.set_performance_mode("adaptive")  # Hybrid mode
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        eval_hybrid = Bot.get_board_val(test_board)
    hybrid_time = time.perf_counter() - start_time
    
    # Results
    speedup_factor = hybrid_time / traditional_time
    
    print(f"\n📊 Benchmark Results:")
    print(f"   🤖 Traditional: {traditional_time/iterations*1000:.2f}ms per eval")
    print(f"   🧠 Hybrid:      {hybrid_time/iterations*1000:.2f}ms per eval")
    print(f"   ⚡ Speed ratio: {speedup_factor:.2f}x")
    print(f"   📈 Traditional eval: {eval_traditional}")
    print(f"   📈 Hybrid eval:      {eval_hybrid}")
    print(f"   📊 Difference:       {abs(eval_hybrid - eval_traditional)}")
    
    if speedup_factor < 1.5:
        print("   ✅ Excellent performance! Hybrid is very fast.")
    elif speedup_factor < 2.0:
        print("   🟡 Good performance. Moderate slowdown.")
    else:
        print("   🔴 Significant slowdown. Consider optimizations.")

def interactive_mode():
    """Interactive mode để test manual"""
    print("\n🎮 Interactive Hybrid AI Test Mode")
    print("Commands:")
    print("  eval <fen> - Evaluate position")
    print("  mode <fast/balanced/adaptive/accurate> - Set mode")
    print("  stats - Show performance stats")
    print("  search <depth> - Search from current position")
    print("  quit - Exit")
    
    current_board = chess.Board()
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command == "quit":
                break
            elif command == "stats":
                Bot.print_performance_stats()
            elif command.startswith("mode "):
                mode = command.split()[1]
                Bot.set_performance_mode(mode)
                print(f"🎯 Mode set to: {mode}")
            elif command.startswith("eval "):
                fen = command[5:]
                try:
                    board = chess.Board(fen)
                    evaluation = Bot.get_board_val(board)
                    print(f"📊 Evaluation: {evaluation}")
                except:
                    print("❌ Invalid FEN")
            elif command.startswith("search "):
                try:
                    depth = int(command.split()[1])
                    gui_board = GUI_Board(600, 600)
                    gui_board.chess_board = current_board.copy()
                    
                    print(f"🔍 Searching depth {depth}...")
                    move = Bot.minimax_search(gui_board, depth, current_board.turn == chess.WHITE)
                    print(f"🎯 Best move: {move}")
                except:
                    print("❌ Invalid depth or search failed")
            else:
                print("❌ Unknown command")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def main():
    """Main test function"""
    print("🚀 Hybrid Chess AI Test Suite")
    print("=" * 50)
    
    # Quick system check
    stats = Bot.get_performance_stats()
    print(f"🧠 Neural Network Available: {stats['nn_available']}")
    print(f"⚙️ Current Mode: {stats['performance_mode']}")
    
    print("\n🧪 Available Tests:")
    print("1. 🧪 Evaluation Performance Test")
    print("2. 🔍 Search Performance Test")  
    print("3. 🧠 Learning Capability Test")
    print("4. ⚡ Hybrid vs Traditional Benchmark")
    print("5. 🎮 Interactive Test Mode")
    print("6. 🏃 Quick Performance Check")
    print("7. ❌ Exit")
    
    while True:
        try:
            choice = input("\nSelect test (1-7): ").strip()
            
            if choice == "1":
                test_hybrid_evaluation()
            elif choice == "2":
                test_hybrid_search()
            elif choice == "3":
                test_learning_capability()
            elif choice == "4":
                benchmark_against_traditional()
            elif choice == "5":
                interactive_mode()
            elif choice == "6":
                # Quick check
                print("\n⚡ Quick Performance Check...")
                Bot.set_performance_mode("adaptive")
                board = chess.Board()
                
                start = time.perf_counter()
                evaluation = Bot.get_board_val(board)
                elapsed = (time.perf_counter() - start) * 1000
                
                print(f"   📊 Evaluation: {evaluation}")
                print(f"   ⏱️ Time: {elapsed:.2f}ms")
                
                if elapsed < 10:
                    print("   ✅ Excellent speed!")
                elif elapsed < 25:
                    print("   🟡 Good speed")
                else:
                    print("   🔴 Consider Fast mode")
                    
                Bot.print_performance_stats()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice!")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()