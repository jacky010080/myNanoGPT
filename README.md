# myNanoGPT

A character-level text generation project built with Python and PyTorch, based on [nanoGPT](https://github.com/karpathy/nanoGPT) by Andrej Karpathy.

This project focuses on training lightweight GPT models using custom text datasets, generating new text, and exploring how different model architectures and training configurations affect generation quality.

The current implementation uses a movie text dataset, with plans to expand into an interactive AI-powered text generation application.

## Features

- **Text Preprocessing:** Convert raw text into encoded training and validation datasets.
- **GPT Model Training:** Train Transformer-based language models from scratch using PyTorch.
- **Configurable Models:** Customize model architecture and training hyperparameters.
- **Text Generation:** Generate new text using trained model checkpoints.
- **Model Comparison:** Experiment with different model sizes and evaluate their performance.

## Project Structure

```text
myNanoGPT/
├── data/
│   └── movies/
│       ├── input.txt
│       └── prepare.py
├── configurator.py
├── model.py
├── train.py
├── sample.py
├── config.py
├── README.md
└── .gitignore
```

The movie text dataset is included in the repository. Generated binary files, model checkpoints, and the local virtual environment are excluded from version control.

## Getting Started

### 1. Set Up the Environment

Create and activate a Python 3.11 virtual environment using `uv`:

```bash
uv venv --python 3.11
source .venv/bin/activate
```

Install the required dependencies:

```bash
uv pip install torch numpy tiktoken
```

### 2. Prepare the Dataset

The project includes a cleaned movie text dataset in `data/movies/input.txt`.

Run the preprocessing script:

```bash
cd data/movies
python prepare.py
cd ../..
```

This generates:

- `train.bin`: Encoded training data.
- `val.bin`: Encoded validation data.
- `meta.pkl`: Character vocabulary and encoding metadata.

### 3. Train the Model

Model architecture and training parameters can be configured in `config.py` or overridden through command-line arguments.

To train a model using the current configuration:

```bash
python train.py config.py --device=cpu --compile=False --dtype=float32
```

To train the smaller GPT architecture:

```bash
python train.py config.py \
  --device=cpu \
  --compile=False \
  --dtype=float32 \
  --eval_iters=20 \
  --log_interval=1 \
  --block_size=64 \
  --batch_size=12 \
  --n_layer=4 \
  --n_head=4 \
  --n_embd=128 \
  --max_iters=2000 \
  --lr_decay_iters=2000 \
  --dropout=0.0 \
  --out_dir=out_movies
```

Training progress is monitored using training and validation loss. Model checkpoints are saved according to the configured checkpoint conditions.

### 4. Generate Text

After training, generate text using a saved model checkpoint.

**Small Model:**

```bash
python sample.py --out_dir=out_movies --device=cpu
```

**Large Model:**

```bash
python sample.py --out_dir=out_movies_full --device=cpu
```

The `--out_dir` argument specifies the directory containing the trained model checkpoint (`ckpt.pt`).

Generated text is displayed in the terminal.

## Model Experiments

Two GPT architectures were tested using the same movie text dataset.

| Configuration | Small Model | Large Model |
|---|---|---|
| Parameters | 0.80M | 10.66M |
| Transformer Layers | 4 | 6 |
| Attention Heads | 4 | 6 |
| Embedding Dimensions | 128 | 384 |
| Context Length | 64 | 256 |
| Batch Size | 12 | 64 |
| Dropout | 0.0 | 0.2 |
| Checkpoint Directory | `out_movies` | `out_movies_full` |

### Training Results

The large model reached the following results after 500 training iterations:

- Training Loss: 1.6093
- Validation Loss: 1.6087

Both models successfully generated text resembling English conversations. The larger model produced more recognizable words and relatively natural sentence structures in the observed samples, while both models still showed spelling errors, grammatical inconsistencies, and limited semantic coherence.

These observations are based on initial experiments rather than a comprehensive benchmark.

## Limitations

- The model uses character-level tokenization rather than subword tokenization.
- Generated text may contain spelling mistakes, grammatical errors, and incoherent sentences.
- Training larger models can be computationally expensive, particularly on CPU-only devices.
- The current implementation supports command-line interaction only.

## Future Development

Planned improvements include:

- Developing a web-based interface for interactive text generation.
- Supporting customizable text generation parameters.
- Improving training efficiency and generation quality.
- Supporting additional text datasets.
- Implementing model selection and comparison features.

## Acknowledgments

This project is based on [nanoGPT](https://github.com/karpathy/nanoGPT) by [Andrej Karpathy](https://github.com/karpathy).

The original nanoGPT implementation provides the foundation for the GPT architecture, training pipeline, and text generation functionality used in this project.