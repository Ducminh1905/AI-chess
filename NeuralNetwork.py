# NeuralNetwork.py
import numpy as np
from numba import njit

class ChessNeuralNetwork:
    def __init__(self, model_path):
        # Tải trọng số và hệ số bias đã huấn luyện từ file .npz
        data = np.load(model_path)
        self.weights = data['weights']
        self.biases  = data['biases']

    def extract_features(self, board):
        # TODO: giữ nguyên code trích xuất đặc trưng hiện tại
        # Trả về vector numpy 1 chiều có shape (N,)
        ...

    @staticmethod
    @njit
    def _fast_forward(weights, biases, X):
        # Forward-pass đã được JIT biên dịch, dùng hàm kích hoạt ReLU
        for W, b in zip(weights, biases):
            X = W.dot(X) + b
            # ReLU tại chỗ
            for i in range(X.shape[0]):
                if X[i] < 0:
                    X[i] = 0
        return X

    def predict_fast(self, board):
        # Chỉ inference nhanh: trích xuất đặc trưng + 1 lần forward pass
        X = self.extract_features(board)
        return ChessNeuralNetwork._fast_forward(self.weights, self.biases, X)
