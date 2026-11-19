# Full character-level GPT for the twitter dataset.
# Run: python train.py config_twitter_full.py

# Dataset and checkpoint
dataset = 'twitter'
out_dir = 'out_twitter_full'

# Evaluation and logging
eval_interval = 250
eval_iters = 200
log_interval = 10
always_save_checkpoint = False
wandb_log = False
wandb_project = 'twitter'

# Model and batches
gradient_accumulation_steps = 1
batch_size = 64
block_size = 256
n_layer = 6
n_head = 6
n_embd = 384
dropout = 0.2

# Optimizer and learning rate schedule
learning_rate = 0.001
max_iters = 5000
lr_decay_iters = 5000
min_lr = 0.0001
beta2 = 0.99
warmup_iters = 100

# Runtime
device = 'cpu'
compile = False
dtype = 'float32'
