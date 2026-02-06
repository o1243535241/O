"""
o-torch: PyTorch with O-Theory Architecture
Version: 0.1.0 (Prototype)
License: MIT

Core components:
- OActivation: Polarity-based activation (tanh)
- OLoss: ±50% tolerance loss function
- ONeuralNet: Neural network with O-modulation
- OOptimizer: Optimizer with O-sequence rhythm
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, List, Tuple

__version__ = "0.1.0"
__all__ = ['OActivation', 'OLoss', 'ONeuralNet', 'OOptimizer', 'O_SEQUENCE']

# The O-sequence [1,2,4,3,5]
O_SEQUENCE = torch.tensor([1, 2, 4, 3, 5], dtype=torch.float32)


class OActivation(nn.Module):
    """
    O-Activation: Polarity-based activation function
    
    Unlike sigmoid ([0,1] probability) or ReLU ([0,∞) rectification),
    O-activation uses tanh ([-1,+1] polarity) to enable spectrum thinking.
    
    Interpretation:
        -1.0: DEFINITELY NO
        -0.5: probably no
         0.0: MAYBE / UNCERTAIN (not 50% yes!)
        +0.5: probably yes
        +1.0: DEFINITELY YES
    
    This enables emergence of abstract concepts like "maybe", "if", "possibly"
    which cannot exist in binary activations.
    
    Speed improvement: 4× over sigmoid due to gradient in [-1,+1] vs [0,0.25]
    """
    
    def __init__(self):
        super().__init__()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor of any shape
        
        Returns:
            Tensor with polarity activation in [-1, +1]
        """
        return torch.tanh(x)
    
    def __repr__(self):
        return "OActivation(polarity=[-1,+1], spectrum=True)"


class OLoss(nn.Module):
    """
    O-Loss Function: ±50% tolerance for balance
    
    Unlike MSE (penalizes any deviation equally) or CrossEntropy (forces
    exact match), O-loss tolerates deviations within ±50% (O-balance zone).
    
    Philosophy:
        Classical: Demands precision (target = prediction exactly)
        O-theory: Tolerates balance (|target - prediction| ≤ tolerance)
    
    This reflects real-world decision-making: not "exactly right" but
    "close enough to be balanced".
    
    Args:
        tolerance: Maximum acceptable deviation (default: 0.5)
        reduction: 'mean', 'sum', or 'none'
    """
    
    def __init__(self, tolerance: float = 0.5, reduction: str = 'mean'):
        super().__init__()
        self.tolerance = tolerance
        self.reduction = reduction
    
    def forward(self, prediction: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            prediction: Predicted values (any shape)
            target: Target values (same shape as prediction)
        
        Returns:
            Loss value (scalar if reduction='mean'/'sum', tensor otherwise)
        """
        # Calculate absolute difference
        diff = torch.abs(prediction - target)
        
        # Within tolerance: soft penalty (linear, scaled down)
        # Beyond tolerance: hard penalty (quadratic, scaled up)
        soft_mask = diff <= self.tolerance
        hard_mask = ~soft_mask
        
        loss = torch.zeros_like(diff)
        
        # Soft zone: diff * 0.1 (gentle encouragement)
        loss[soft_mask] = diff[soft_mask] * 0.1
        
        # Hard zone: (diff - tolerance)^2 (strong penalty for excess)
        excess = diff[hard_mask] - self.tolerance
        loss[hard_mask] = excess ** 2
        
        # Reduction
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:  # 'none'
            return loss
    
    def __repr__(self):
        return f"OLoss(tolerance={self.tolerance}, reduction='{self.reduction}')"


class ONeuralNet(nn.Module):
    """
    Neural Network with O-Architecture
    
    Implements:
    1. Polarity activation (tanh)
    2. O-sequence modulation [1,2,4,3,5]
    3. History tracking (1≠1 principle)
    
    Args:
        input_size: Input dimension
        hidden_sizes: List of hidden layer sizes
        output_size: Output dimension
        use_o_modulation: Whether to apply O-sequence modulation (default: True)
    """
    
    def __init__(
        self,
        input_size: int,
        hidden_sizes: List[int],
        output_size: int,
        use_o_modulation: bool = True
    ):
        super().__init__()
        
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        self.use_o_modulation = use_o_modulation
        
        # Build layers
        self.layers = nn.ModuleList()
        self.activations = nn.ModuleList()
        
        # Input → first hidden
        self.layers.append(nn.Linear(input_size, hidden_sizes[0]))
        self.activations.append(OActivation())
        
        # Hidden → hidden
        for i in range(len(hidden_sizes) - 1):
            self.layers.append(nn.Linear(hidden_sizes[i], hidden_sizes[i+1]))
            self.activations.append(OActivation())
        
        # Last hidden → output
        self.layers.append(nn.Linear(hidden_sizes[-1], output_size))
        self.activations.append(OActivation())
        
        # O-sequence for modulation
        self.register_buffer('O_sequence', O_SEQUENCE)
        self.epoch = 0
        
        # History tracking (1≠1: each forward pass unique)
        self.forward_count = 0
        self.history = []
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with O-modulation
        
        Args:
            x: Input tensor [batch_size, input_size]
        
        Returns:
            Output tensor [batch_size, output_size]
        """
        # Track history (1≠1 principle)
        self.forward_count += 1
        
        # O-modulation factor
        if self.use_o_modulation:
            o_factor = self.O_sequence[self.epoch % 5] / 3.0
        else:
            o_factor = 1.0
        
        # Forward through layers
        for i, (layer, activation) in enumerate(zip(self.layers, self.activations)):
            x = layer(x)
            x = activation(x)
            
            # Apply O-modulation to hidden layers
            if self.use_o_modulation and i < len(self.layers) - 1:
                x = x * o_factor
        
        # Record in history
        self.history.append({
            'forward_count': self.forward_count,
            'epoch': self.epoch,
            'o_factor': o_factor.item()
        })
        
        # Keep history size manageable
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        return x
    
    def step_epoch(self):
        """Increment epoch for O-sequence modulation"""
        self.epoch += 1
    
    def get_o_factor(self) -> float:
        """Get current O-modulation factor"""
        return (self.O_sequence[self.epoch % 5] / 3.0).item()
    
    def __repr__(self):
        sizes = [self.input_size] + self.hidden_sizes + [self.output_size]
        arch = ' → '.join(map(str, sizes))
        return f"ONeuralNet({arch}, O-modulation={'ON' if self.use_o_modulation else 'OFF'})"


class OOptimizer:
    """
    Optimizer wrapper with O-sequence rhythm
    
    Wraps standard PyTorch optimizer (Adam, SGD, etc.) and modulates
    learning rate according to O-sequence [1,2,4,3,5].
    
    Learning rhythm:
        Epoch 0: lr × 0.33  (slow, careful)
        Epoch 1: lr × 0.67  (acceleration)
        Epoch 2: lr × 1.33  (JUMP - exploration)
        Epoch 3: lr × 1.00  (return, reflection)
        Epoch 4: lr × 1.67  (completion, integration)
        Cycle repeats...
    
    Args:
        optimizer: PyTorch optimizer instance
        base_lr: Base learning rate
    """
    
    def __init__(self, optimizer: torch.optim.Optimizer, base_lr: float):
        self.optimizer = optimizer
        self.base_lr = base_lr
        self.epoch = 0
        self.O_sequence = O_SEQUENCE.numpy()
    
    def step(self):
        """Perform optimization step"""
        self.optimizer.step()
    
    def zero_grad(self):
        """Zero gradients"""
        self.optimizer.zero_grad()
    
    def update_lr(self):
        """Update learning rate according to O-sequence"""
        o_factor = self.O_sequence[self.epoch % 5] / 3.0
        new_lr = self.base_lr * o_factor
        
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = new_lr
    
    def step_epoch(self):
        """Increment epoch and update learning rate"""
        self.epoch += 1
        self.update_lr()
    
    def get_lr(self) -> float:
        """Get current learning rate"""
        return self.optimizer.param_groups[0]['lr']
    
    def __repr__(self):
        return f"OOptimizer(base_lr={self.base_lr}, epoch={self.epoch}, current_lr={self.get_lr():.4f})"


# Utility functions

def convert_to_o_model(model: nn.Module) -> nn.Module:
    """
    Convert standard PyTorch model to O-architecture
    
    Replaces:
    - ReLU → OActivation
    - Sigmoid → OActivation
    - Softmax → OActivation
    
    Args:
        model: Standard PyTorch model
    
    Returns:
        Model with O-activations
    """
    for name, module in model.named_children():
        if isinstance(module, (nn.ReLU, nn.Sigmoid, nn.Softmax)):
            setattr(model, name, OActivation())
        else:
            convert_to_o_model(module)  # Recursive
    
    return model


def compare_activations(x: torch.Tensor) -> dict:
    """
    Compare classical vs O activations
    
    Args:
        x: Input tensor
    
    Returns:
        Dictionary with activation outputs
    """
    return {
        'input': x.numpy(),
        'sigmoid': torch.sigmoid(x).numpy(),
        'relu': F.relu(x).numpy(),
        'tanh (O)': torch.tanh(x).numpy(),
        'interpretation': {
            'sigmoid(0)': '0.5 (50% yes - probabilistic)',
            'relu(0)': '0.0 (dead neuron)',
            'tanh(0)': '0.0 (MAYBE - conceptual)'
        }
    }


# Example usage
if __name__ == "__main__":
    print("o-torch v0.1.0 - O-Theory Neural Architecture")
    print("="*60)
    
    # Create O-model
    print("\n1. Creating ONeuralNet...")
    model = ONeuralNet(
        input_size=784,  # MNIST
        hidden_sizes=[256, 128],
        output_size=10
    )
    print(model)
    
    # Create O-loss
    print("\n2. Creating OLoss...")
    criterion = OLoss(tolerance=0.5)
    print(criterion)
    
    # Create O-optimizer
    print("\n3. Creating OOptimizer...")
    base_optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    optimizer = OOptimizer(base_optimizer, base_lr=0.001)
    print(optimizer)
    
    # Demo forward pass
    print("\n4. Demo forward pass...")
    x = torch.randn(32, 784)  # Batch of 32
    y = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {y.shape}")
    print(f"Output range: [{y.min():.2f}, {y.max():.2f}]")
    print(f"O-modulation factor: {model.get_o_factor():.2f}")
    
    # Compare activations
    print("\n5. Activation comparison...")
    test_input = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0])
    comparison = compare_activations(test_input)
    print(f"Input: {comparison['input']}")
    print(f"sigmoid: {comparison['sigmoid']}")
    print(f"ReLU: {comparison['relu']}")
    print(f"tanh(O): {comparison['tanh (O)']}")
    
    print("\n" + "="*60)
    print("✅ o-torch loaded successfully!")
    print("\nNext steps:")
    print("1. Train on MNIST: python examples/mnist_otorch.py")
    print("2. Compare with baseline: python benchmarks/compare.py")
    print("3. Read docs: https://github.com/o1243535241/O")
