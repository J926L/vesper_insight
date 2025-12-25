import torch
import os
from dotenv import load_dotenv
from icecream import ic
from river import anomaly

# 显存限制逻辑 (针对 RTX 3060 6GB)
def setup_cuda_limits():
    load_dotenv()
    max_vram = int(os.getenv("MAX_VRAM_GB", 6))
    limit_vram = 4 # 硬限制 4GB
    
    if torch.cuda.is_available():
        # 强制限制显存占用为 60% (约为 3.6GB / 6GB)，保护系统显存
        torch.cuda.set_per_process_memory_fraction(0.6, 0)
        ic(f"CUDA detected. VRAM limit set to 60%")
        torch.cuda.set_device(0)
    else:
        ic("CUDA not available. Falling back to CPU.")

class AnomalyDetector:
    def __init__(self):
        # 使用 Half-Space Trees (HST) 进行流式无监督异常检测
        # 减小 window_size 以便在测试阶段更快看到评分变化
        self.model = anomaly.HalfSpaceTrees(
            n_trees=25,
            height=15,
            window_size=50, 
            seed=42
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        ic(f"Model initialized on {self.device} with window_size=50")

    def learn_one(self, features: dict):
        # River 模型在 CPU 上处理逻辑，特征工程可利用 Torch/CUDA
        self.model.learn_one(features)

    def score_one(self, features: dict) -> float:
        # 返回异常评分 (0 to 1, 越高越可疑)
        return self.model.score_one(features)
