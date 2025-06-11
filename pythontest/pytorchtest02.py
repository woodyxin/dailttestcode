import torch

# 检查PyTorch版本
print(torch.__version__)

# 检查CUDA是否可用（GPU版本）
print(torch.cuda.is_available())

# 尝试简单张量运算
x = torch.rand(5, 3)
print(x)

# 测试pytorch

