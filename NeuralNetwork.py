# NeuralNetwork.py
import os
import argparse
import numpy as np
from numba import njit
import chess


class ChessNeuralNetwork:
    """
    Lớp neural network để đánh giá thế cờ, dùng dữ liệu .npz chứa 'weights' và 'biases'.
    """
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        data = np.load(model_path, allow_pickle=True)
        self.weights = data['weights']
        self.biases  = data['biases']

    def extract_features(self, board: chess.Board) -> np.ndarray:
        """
        Trích xuất vector feature từ đối tượng chess.Board.
        Bạn cần implement phần này dựa trên logic hiện tại.
        """
        # TODO: cài đặt trích xuất đặc trưng
        raise NotImplementedError("extract_features chưa được implement")

    @staticmethod
    @njit
    def _fast_forward(weights, biases, X):
        """JIT-compiled forward pass với ReLU activation"""
        for W, b in zip(weights, biases):
            X = W.dot(X) + b
            for i in range(X.shape[0]):
                if X[i] < 0:
                    X[i] = 0
        return X

    def predict_fast(self, board: chess.Board) -> float:
        """Inference nhanh: trích xuất feature + forward-pass"""
        X = self.extract_features(board)
        return ChessNeuralNetwork._fast_forward(self.weights, self.biases, X)


def load_npz_models(models_dir: str) -> dict:

    models = {}
    for fname in os.listdir(models_dir):
        if fname.lower().endswith('.npz'):
            name = os.path.splitext(fname)[0]
            path = os.path.join(models_dir, fname)
            try:
                models[name] = ChessNeuralNetwork(path)
            except Exception as e:
                print(f"Không load được {fname}: {e}")
    return models


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Load and inspect all .npz chess models in a directory'
    )
    parser.add_argument('models_dir', help='Thư mục chứa file .npz')
    args = parser.parse_args()

    nets = load_npz_models(args.data)
    print(f"Đã load {len(nets)} mô hình:\n")
    for name, net in nets.items():
        w_shapes = [w.shape for w in net.weights]
        b_shapes = [b.shape for b in net.biases]
        print(f"- {name}: weights shapes={w_shapes}, biases shapes={b_shapes}")
