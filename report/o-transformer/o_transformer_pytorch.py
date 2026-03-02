
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class OSparseAttention(nn.Module):
    """
    О-inspired Sparse Attention
    Between "many" and "nothing" - selective connections
    """
    
    def __init__(self, d_model, n_heads=8, sparsity=0.3, dropout=0.1):
        super().__init__()
        assert d_model % n_heads == 0
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.sparsity = sparsity  # О-principle: connect only 30%
        
        # Learned parameters
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x, mask=None):
        batch_size, seq_len, d_model = x.shape
        
        # Multi-head projections
        Q = self.W_q(x).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        
        # Attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        # О-PRINCIPLE: Sparse attention (між багато і ніяк)
        k = max(1, int(seq_len * self.sparsity))
        
        # Keep only top-k per query
        top_k_scores, top_k_indices = torch.topk(scores, k, dim=-1)
        
        # Create sparse mask
        sparse_mask = torch.full_like(scores, float('-inf'))
        sparse_mask.scatter_(-1, top_k_indices, top_k_scores)
        
        # Apply mask if provided
        if mask is not None:
            sparse_mask = sparse_mask.masked_fill(mask == 0, float('-inf'))
        
        # Softmax + dropout
        attn_weights = F.softmax(sparse_mask, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # Apply attention
        output = torch.matmul(attn_weights, V)
        
        # Reshape and project
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
        output = self.W_o(output)
        
        return output, attn_weights

class OHierarchicalFFN(nn.Module):
    """
    Feed-forward with hierarchical processing
    Information flows through multiple scales
    """
    
    def __init__(self, d_model, d_ff=None, dropout=0.1):
        super().__init__()
        if d_ff is None:
            d_ff = 4 * d_model
        
        # Hierarchical processing: 
        # Level 1: Expand
        self.linear1 = nn.Linear(d_model, d_ff)
        # Level 2: Transform (middle)
        self.linear_mid = nn.Linear(d_ff, d_ff)
        # Level 3: Compress
        self.linear2 = nn.Linear(d_ff, d_model)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        # Expand
        x = F.gelu(self.linear1(x))
        x = self.dropout(x)
        
        # Transform (hierarchical middle layer)
        x = F.gelu(self.linear_mid(x))
        x = self.dropout(x)
        
        # Compress
        x = self.linear2(x)
        x = self.dropout(x)
        
        return x

class OTransformerLayer(nn.Module):
    """
    Single О-Transformer layer
    Combines sparse attention + hierarchical FFN
    """
    
    def __init__(self, d_model, n_heads=8, d_ff=None, 
                 sparsity=0.3, dropout=0.1):
        super().__init__()
        
        # Sparse attention (О-principle)
        self.attention = OSparseAttention(d_model, n_heads, sparsity, dropout)
        
        # Hierarchical feed-forward
        self.ffn = OHierarchicalFFN(d_model, d_ff, dropout)
        
        # Layer normalization
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x, mask=None):
        # Self-attention with residual
        attn_out, attn_weights = self.attention(self.norm1(x), mask)
        x = x + self.dropout(attn_out)
        
        # Feed-forward with residual
        ffn_out = self.ffn(self.norm2(x))
        x = x + self.dropout(ffn_out)
        
        return x, attn_weights

class OTransformer(nn.Module):
    """
    Complete О-Transformer
    ✓ Learned parameters (embeddings, attention, FFN)
    ✓ Backpropagation capable
    ✓ О-principles (sparse, hierarchical, cyclic)
    ✓ Production ready
    """
    
    def __init__(self, vocab_size, d_model=512, n_layers=6, n_heads=8,
                 d_ff=2048, max_seq_len=512, sparsity=0.3, dropout=0.1):
        super().__init__()
        
        self.d_model = d_model
        self.n_layers = n_layers
        
        # Learned token embeddings
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        
        # Learned positional embeddings (vs fixed sin/cos)
        # О-principle: Let positions self-organize
        self.pos_embedding = nn.Embedding(max_seq_len, d_model)
        
        # Hierarchical layers (like 5 levels of О)
        self.layers = nn.ModuleList([
            OTransformerLayer(d_model, n_heads, d_ff, sparsity, dropout)
            for _ in range(n_layers)
        ])
        
        # Output projection
        self.output_projection = nn.Linear(d_model, vocab_size)
        
        self.dropout = nn.Dropout(dropout)
        
        # Initialize weights (Xavier/Glorot)
        self._init_weights()
        
    def _init_weights(self):
        """Initialize with small random values (О-principle: start simple)"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, x, mask=None):
        batch_size, seq_len = x.shape
        
        # Token embeddings
        token_emb = self.token_embedding(x)
        
        # Positional embeddings
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        pos_emb = self.pos_embedding(positions)
        
        # Combine (learned!)
        x = self.dropout(token_emb + pos_emb)
        
        # Process through hierarchical layers
        attention_maps = []
        for layer in self.layers:
            x, attn = layer(x, mask)
            attention_maps.append(attn)
        
        # Output projection
        logits = self.output_projection(x)
        
        return logits, attention_maps
    
    def generate(self, prompt_ids, max_length=50, temperature=1.0):
        """
        Auto-regressive generation
        О-principle: Let text self-organize naturally
        """
        self.eval()
        
        generated = prompt_ids.clone()
        
        with torch.no_grad():
            for _ in range(max_length):
                # Forward pass
                logits, _ = self.forward(generated)
                
                # Get next token logits
                next_token_logits = logits[:, -1, :] / temperature
                
                # Sample (stochastic, not greedy - more О-like)
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Append
                generated = torch.cat([generated, next_token], dim=1)
                
                # Stop if max length reached
                if generated.shape[1] >= max_length:
                    break
        
        return generated

class OCyclicTrainer:
    """
    О-inspired training with cyclic /2 refinement
    Like water finding optimal form through iterations
    """
    
    def __init__(self, model, initial_lr=1e-3, cycles=5):
        self.model = model
        self.initial_lr = initial_lr
        self.cycles = cycles
        self.history = []
        
    def train_cycle(self, train_loader, val_loader, cycle_num):
        """Train for one cycle"""
        # Learning rate decreases by /2 each cycle (О-principle)
        lr = self.initial_lr / (2 ** cycle_num)
        
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()
        
        self.model.train()
        
        epoch_loss = 0
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            optimizer.zero_grad()
            
            # Forward
            logits, _ = self.model(inputs)
            
            # Compute loss
            loss = criterion(logits.view(-1, logits.size(-1)), targets.view(-1))
            
            # Backward
            loss.backward()
            
            # Update
            optimizer.step()
            
            epoch_loss += loss.item()
        
        avg_loss = epoch_loss / len(train_loader)
        
        # Validation
        val_loss = self.validate(val_loader, criterion)
        
        return avg_loss, val_loss, lr
    
    def validate(self, val_loader, criterion):
        """Validation pass"""
        self.model.eval()
        
        val_loss = 0
        with torch.no_grad():
            for inputs, targets in val_loader:
                logits, _ = self.model(inputs)
                loss = criterion(logits.view(-1, logits.size(-1)), targets.view(-1))
                val_loss += loss.item()
        
        return val_loss / len(val_loader)
    
    def train(self, train_loader, val_loader):
        """
        Full cyclic training
        О-principle: Refine through /2 cycles like water
        """
        print("\n🔄 О-Cyclic Training:")
        
        for cycle in range(self.cycles):
            train_loss, val_loss, lr = self.train_cycle(train_loader, val_loader, cycle)
            
            self.history.append({
                'cycle': cycle + 1,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'lr': lr
            })
            
            print(f"  Cycle {cycle+1}/{self.cycles}:")
            print(f"    LR: {lr:.6f}")
            print(f"    Train Loss: {train_loss:.4f}")
            print(f"    Val Loss: {val_loss:.4f}")
            
            # Check convergence (О-principle: stop when water settles)
            if cycle > 0:
                prev_val_loss = self.history[-2]['val_loss']
                improvement = prev_val_loss - val_loss
                
                if improvement < 1e-4:
                    print(f"  ✅ Converged at cycle {cycle+1}")
                    break
        
        return self.history

# Usage example
def create_o_transformer(vocab_size=10000):
    """
    Create production-ready О-Transformer
    """
    model = OTransformer(
        vocab_size=vocab_size,
        d_model=512,        # Standard size
        n_layers=6,         # 6 layers (hierarchical)
        n_heads=8,          # 8 attention heads
        d_ff=2048,          # Feed-forward dimension
        max_seq_len=512,    # Max sequence length
        sparsity=0.3,       # О: Connect 30% (між багато і ніяк)
        dropout=0.1
    )
    
    return model

# Training example
def train_o_transformer(model, train_data, val_data):
    """
    Train with О-cyclic method
    """
    trainer = OCyclicTrainer(
        model=model,
        initial_lr=1e-3,
        cycles=5  # 5 cycles with /2 refinement
    )
    
    history = trainer.train(train_data, val_data)
    
    return model, history

if __name__ == "__main__":
    # Create model
    print("Creating О-Transformer...")
    model = create_o_transformer(vocab_size=10000)
    
    # Count parameters
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {n_params:,}")
    
    # Example forward pass
    print("\nTesting forward pass...")
    batch_size = 2
    seq_len = 10
    dummy_input = torch.randint(0, 10000, (batch_size, seq_len))
    
    logits, attention_maps = model(dummy_input)
    
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {logits.shape}")
    print(f"Attention maps: {len(attention_maps)} layers")
    
    # Show sparsity
    first_attn = attention_maps[0]
    sparsity_actual = (first_attn > 0).float().mean().item()
    print(f"Actual attention sparsity: {sparsity_actual:.1%}")
    
    print("\n✅ О-Transformer ready for training!")
