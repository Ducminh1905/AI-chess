"""
Neural Network Module for Chess AI
Implements a deep learning approach for chess position evaluation
"""

import numpy as np
import json
import os
from datetime import datetime
import chess

class ChessNeuralNetwork:
    """
    A neural network for chess position evaluation
    Architecture: Input Layer (773 nodes) -> Hidden Layers -> Output Layer (1 node)
    """
    
    def __init__(self, hidden_layers=[512, 256, 128], learning_rate=0.001):
        self.hidden_layers = hidden_layers
        self.learning_rate = learning_rate
        self.weights = {}
        self.biases = {}
        self.training_history = []
        
        # Network architecture
        layer_sizes = [773] + hidden_layers + [1]  # 773 input features, 1 output
        
        # Initialize weights and biases
        self.initialize_network(layer_sizes)
        
        # Load pre-trained weights if available
        self.load_model()
    
    def initialize_network(self, layer_sizes):
        """Initialize network weights and biases using Xavier initialization"""
        for i in range(len(layer_sizes) - 1):
            # Xavier initialization for better gradient flow
            fan_in = layer_sizes[i]
            fan_out = layer_sizes[i + 1]
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            
            self.weights[f'W{i+1}'] = np.random.uniform(-limit, limit, (fan_in, fan_out))
            self.biases[f'b{i+1}'] = np.zeros((1, fan_out))
    
    def relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        """Derivative of ReLU function"""
        return (x > 0).astype(float)
    
    def leaky_relu(self, x, alpha=0.01):
        """Leaky ReLU activation function"""
        return np.where(x > 0, x, alpha * x)
    
    def leaky_relu_derivative(self, x, alpha=0.01):
        """Derivative of Leaky ReLU function"""
        return np.where(x > 0, 1, alpha)
    
    def tanh(self, x):
        """Tanh activation function"""
        return np.tanh(x)
    
    def tanh_derivative(self, x):
        """Derivative of tanh function"""
        return 1 - np.tanh(x) ** 2
    
    def extract_features(self, board):
        """
        Extract comprehensive features from chess position
        Returns a 773-dimensional feature vector
        """
        features = []
        
        # 1. Piece placement (8x8x12 = 768 features)
        piece_features = np.zeros((8, 8, 12))
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            
            if piece:
                # Encode piece type and color
                piece_idx = (piece.piece_type - 1) * 2 + (0 if piece.color else 1)
                piece_features[rank, file, piece_idx] = 1
        
        features.extend(piece_features.flatten())
        
        # 2. Castling rights (4 features)
        features.append(1 if board.has_kingside_castling_rights(chess.WHITE) else 0)
        features.append(1 if board.has_queenside_castling_rights(chess.WHITE) else 0)
        features.append(1 if board.has_kingside_castling_rights(chess.BLACK) else 0)
        features.append(1 if board.has_queenside_castling_rights(chess.BLACK) else 0)
        
        # 3. En passant target (1 feature)
        features.append(1 if board.ep_square is not None else 0)
        
        return np.array(features).reshape(1, -1)
    
    def forward_pass(self, X):
        """Forward propagation through the network"""
        activations = {'A0': X}
        Z_values = {}
        
        for i in range(len(self.hidden_layers) + 1):
            layer_num = i + 1
            
            # Linear transformation
            Z = np.dot(activations[f'A{i}'], self.weights[f'W{layer_num}']) + self.biases[f'b{layer_num}']
            Z_values[f'Z{layer_num}'] = Z
            
            # Activation function
            if layer_num == len(self.hidden_layers) + 1:  # Output layer
                A = self.tanh(Z)  # Tanh for output in range [-1, 1]
            else:  # Hidden layers
                A = self.leaky_relu(Z)
            
            activations[f'A{layer_num}'] = A
        
        return activations, Z_values
    
    def backward_pass(self, X, y, activations, Z_values):
        """Backward propagation to compute gradients"""
        m = X.shape[0]  # Number of samples
        gradients = {}
        
        # Output layer gradient
        layer_num = len(self.hidden_layers) + 1
        dZ = activations[f'A{layer_num}'] - y
        
        for i in range(layer_num, 0, -1):
            # Compute gradients
            gradients[f'dW{i}'] = (1/m) * np.dot(activations[f'A{i-1}'].T, dZ)
            gradients[f'db{i}'] = (1/m) * np.sum(dZ, axis=0, keepdims=True)
            
            if i > 1:  # Not the first layer
                # Propagate error backwards
                dA_prev = np.dot(dZ, self.weights[f'W{i}'].T)
                
                # Apply activation derivative
                if i == layer_num:  # Output layer
                    dZ = dA_prev * self.tanh_derivative(Z_values[f'Z{i-1}'])
                else:  # Hidden layer
                    dZ = dA_prev * self.leaky_relu_derivative(Z_values[f'Z{i-1}'])
        
        return gradients
    
    def update_parameters(self, gradients):
        """Update network parameters using gradients"""
        for i in range(1, len(self.hidden_layers) + 2):
            self.weights[f'W{i}'] -= self.learning_rate * gradients[f'dW{i}']
            self.biases[f'b{i}'] -= self.learning_rate * gradients[f'db{i}']
    
    def train_batch(self, X_batch, y_batch):
        """Train the network on a single batch"""
        # Forward pass
        activations, Z_values = self.forward_pass(X_batch)
        
        # Backward pass
        gradients = self.backward_pass(X_batch, y_batch, activations, Z_values)
        
        # Update parameters
        self.update_parameters(gradients)
        
        # Calculate loss
        y_pred = activations[f'A{len(self.hidden_layers) + 1}']
        loss = np.mean((y_pred - y_batch) ** 2)
        
        return loss
    
    def predict(self, board):
        """Predict the evaluation of a chess position"""
        features = self.extract_features(board)
        activations, _ = self.forward_pass(features)
        prediction = activations[f'A{len(self.hidden_layers) + 1}'][0, 0]
        
        # Scale prediction to centipawns
        return prediction * 1000
    
    def train_from_games(self, training_data, epochs=100, batch_size=32):
        """
        Train the network from game data
        training_data: List of (board_fen, evaluation) tuples
        """
        print(f"Training neural network on {len(training_data)} positions...")
        
        # Prepare training data
        X_train = []
        y_train = []
        
        for fen, evaluation in training_data:
            try:
                board = chess.Board(fen)
                features = self.extract_features(board)
                X_train.append(features[0])
                # Normalize evaluation to [-1, 1]
                normalized_eval = np.tanh(evaluation / 1000.0)
                y_train.append([normalized_eval])
            except:
                continue
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        print(f"Training on {len(X_train)} valid positions")
        
        # Training loop
        for epoch in range(epochs):
            epoch_loss = 0
            num_batches = 0
            
            # Shuffle data
            indices = np.random.permutation(len(X_train))
            X_shuffled = X_train[indices]
            y_shuffled = y_train[indices]
            
            # Mini-batch training
            for i in range(0, len(X_train), batch_size):
                X_batch = X_shuffled[i:i+batch_size]
                y_batch = y_shuffled[i:i+batch_size]
                
                loss = self.train_batch(X_batch, y_batch)
                epoch_loss += loss
                num_batches += 1
            
            avg_loss = epoch_loss / num_batches
            self.training_history.append(avg_loss)
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}/{epochs}, Average Loss: {avg_loss:.6f}")
        
        print("Training completed!")
        self.save_model()
    
    def save_model(self, filepath=None):
        """Save the trained model to file"""
        if filepath is None:
            os.makedirs('data/models', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f'data/models/chess_nn_{timestamp}.json'
        
        model_data = {
            'weights': {},
            'biases': {},
            'hidden_layers': self.hidden_layers,
            'learning_rate': self.learning_rate,
            'training_history': self.training_history,
            'timestamp': datetime.now().isoformat()
        }
        
        # Convert numpy arrays to lists for JSON serialization
        for key, value in self.weights.items():
            model_data['weights'][key] = value.tolist()
        
        for key, value in self.biases.items():
            model_data['biases'][key] = value.tolist()
        
        try:
            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2)
            print(f"Model saved to {filepath}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self, filepath=None):
        """Load a pre-trained model from file"""
        if filepath is None:
            # Try to load the most recent model
            model_dir = 'data/models'
            if os.path.exists(model_dir):
                model_files = [f for f in os.listdir(model_dir) if f.startswith('chess_nn_') and f.endswith('.json')]
                if model_files:
                    model_files.sort(reverse=True)  # Most recent first
                    filepath = os.path.join(model_dir, model_files[0])
        
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    model_data = json.load(f)
                
                # Restore weights and biases
                for key, value in model_data['weights'].items():
                    self.weights[key] = np.array(value)
                
                for key, value in model_data['biases'].items():
                    self.biases[key] = np.array(value)
                
                self.training_history = model_data.get('training_history', [])
                print(f"Model loaded from {filepath}")
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        
        return False
    
    def evaluate_training_positions(self, test_data):
        """Evaluate the network on test positions"""
        if not test_data:
            return
        
        predictions = []
        actual_values = []
        
        for fen, actual_eval in test_data[:100]:  # Test on first 100 positions
            try:
                board = chess.Board(fen)
                predicted_eval = self.predict(board)
                predictions.append(predicted_eval)
                actual_values.append(actual_eval)
            except:
                continue
        
        if predictions:
            # Calculate metrics
            predictions = np.array(predictions)
            actual_values = np.array(actual_values)
            
            mse = np.mean((predictions - actual_values) ** 2)
            mae = np.mean(np.abs(predictions - actual_values))
            correlation = np.corrcoef(predictions, actual_values)[0, 1]
            
            print(f"Neural Network Evaluation Metrics:")
            print(f"Mean Squared Error: {mse:.2f}")
            print(f"Mean Absolute Error: {mae:.2f}")
            print(f"Correlation: {correlation:.3f}")

# Data collection and preprocessing
class TrainingDataCollector:
    """Collect and preprocess training data for the neural network"""
    
    def __init__(self):
        self.positions = []
    
    def add_position(self, board, evaluation, game_result=None):
        """Add a position to the training dataset"""
        position_data = {
            'fen': board.fen(),
            'evaluation': evaluation,
            'game_result': game_result,
            'material_balance': self.calculate_material_balance(board),
            'game_phase': self.determine_game_phase(board)
        }
        self.positions.append(position_data)
    
    def calculate_material_balance(self, board):
        """Calculate material balance for the position"""
        piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
                       chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
        
        white_material = sum(piece_values[piece.piece_type] 
                           for piece in board.piece_map().values() 
                           if piece.color == chess.WHITE)
        
        black_material = sum(piece_values[piece.piece_type] 
                           for piece in board.piece_map().values() 
                           if piece.color == chess.BLACK)
        
        return white_material - black_material
    
    def determine_game_phase(self, board):
        """Determine the game phase (opening, middlegame, endgame)"""
        piece_count = len(board.piece_map())
        
        if piece_count >= 24:
            return "opening"
        elif piece_count >= 12:
            return "middlegame"
        else:
            return "endgame"
    
    def save_training_data(self, filepath='data/training_positions.json'):
        """Save collected training data to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(self.positions, f, indent=2)
            print(f"Training data saved to {filepath}")
        except Exception as e:
            print(f"Error saving training data: {e}")
    
    def load_training_data(self, filepath='data/training_positions.json'):
        """Load training data from file"""
        try:
            with open(filepath, 'r') as f:
                self.positions = json.load(f)
            print(f"Loaded {len(self.positions)} training positions")
            return True
        except Exception as e:
            print(f"Error loading training data: {e}")
            return False
    
    def get_training_pairs(self):
        """Get (fen, evaluation) pairs for training"""
        return [(pos['fen'], pos['evaluation']) for pos in self.positions]

# Initialize global neural network
chess_nn = ChessNeuralNetwork()
training_collector = TrainingDataCollector()

# Try to load existing training data
training_collector.load_training_data()

print("Chess Neural Network module initialized!")