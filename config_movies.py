# Small character-level GPT for the movies dataset.
# Run: python train.py config_movies.py

# Dataset and checkpoint
dataset = 'movies'
out_dir = 'out_movies'

# Evaluation and logging
eval_interval = 250
eval_iters = 20
log_interval = 1
always_save_checkpoint = False
wandb_log = False
wandb_project = 'movies'

# Model and batches
gradient_accumulation_steps = 1
batch_size = 12
block_size = 64
n_layer = 4
n_head = 4
n_embd = 128
dropout = 0.0

# Optimizer and learning rate schedule
learning_rate = 0.001
max_iters = 2000
lr_decay_iters = 2000
min_lr = 0.0001
beta2 = 0.99
warmup_iters = 100

# Runtime
device = 'cpu'
compile = False
dtype = 'float32'
