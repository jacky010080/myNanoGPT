# myNanoGPT

A character-level text generation project built with Python, PyTorch, and Flask, based on [nanoGPT](https://github.com/karpathy/nanoGPT) by Andrej Karpathy.

This project focuses on training lightweight GPT models using movie and Twitter text datasets, generating new text, and exploring how different model architectures and training configurations affect generation quality.

## Features

- Prepare character-level training data from a text file.
- Train GPT models with configurable architectures and training settings.
- Generate text from the command line or a browser.
- Switch between Small and Full models in the web interface.
- Keep page structure, styling, browser interactions, and backend logic in separate files.

## Requirements

- Python 3.11, matching the project's `.python-version` file.
- [uv](https://docs.astral.sh/uv/) for environment and dependency management.
- A CPU is sufficient for the examples below; training time depends on the model size and hardware.

Run the following commands from the project root. The activation command shown below is for macOS and Linux.

## 1. Set Up the Environment

Install the dependencies declared in `pyproject.toml` using the versions in `uv.lock`, then activate the environment:

```bash
uv sync --locked --python 3.11
source .venv/bin/activate
```

This is a script-based project: `uv` manages its dependencies without installing it as a Python package. Run the scripts directly from the project root.

Model checkpoints and generated dataset files are not tracked in Git. If you already have the checkpoints and their matching `meta.pkl`, you can skip the data preparation and training steps and proceed to text generation or the web interface.

## 2. Prepare the Datasets

The source text files are `data/movies/input.txt` and `data/twitter/input.txt`. Prepare the datasets you plan to train on:

```bash
python data/movies/prepare.py
python data/twitter/prepare.py
```

Each script writes the following files into its dataset directory:

| File | Purpose |
| --- | --- |
| `train.bin` | Encoded training data |
| `val.bin` | Encoded validation data |
| `meta.pkl` | Character vocabulary and encoding/decoding mappings |

Keep the vocabulary used during training together with its checkpoints. Regenerating `meta.pkl` from different text can change the character mappings and make it incompatible with an existing model.

## 3. Train the Models

Each model has an independent configuration file containing its dataset, architecture, training settings, and output directory:

| Dataset | Size | Configuration File | Checkpoint Directory |
| --- | --- | --- | --- |
| Movies | Small | `config_movies.py` | `out_movies` |
| Movies | Full | `config_movies_full.py` | `out_movies_full` |
| Twitter | Small | `config_twitter.py` | `out_twitter` |
| Twitter | Full | `config_twitter_full.py` | `out_twitter_full` |

### Movie Models

```bash
# Small
python train.py config_movies.py

# Full
python train.py config_movies_full.py
```

### Twitter Models

```bash
# Small
python train.py config_twitter.py

# Full
python train.py config_twitter_full.py
```

All four configurations explicitly use CPU training, `compile=False`, and `dtype='float32'`. Small models use 4 layers, 4 attention heads, 128 embedding dimensions, and a 2,000-iteration training budget. Full models use 6 layers, 6 attention heads, 384 embedding dimensions, and a 5,000-iteration budget. Each configuration saves to its own output directory.

The existing Full models (`out_movies_full` and `out_twitter_full`) were manually stopped at iteration 500 because completing all 5,000 iterations would take several hours on CPU. Their configuration files retain the original 5,000-iteration budget; the existing checkpoints and reported results reflect the runs stopped at iteration 500.

`train.py` provides defaults for settings not specified in the configuration file. Command-line arguments placed after the configuration file can still override individual values for an experiment:

```bash
python train.py config_movies.py --max_iters=1000 --lr_decay_iters=1000
```

Training reports training and validation loss. Checkpoints are saved as `ckpt.pt` in the selected output directory when the configured checkpoint conditions are met. Editing a configuration file changes future training runs; existing checkpoints retain their saved weights and metadata.

## 4. Generate Text from the Command Line

After training, sample from any of the four checkpoints:

```bash
# Movie models
python sample.py --out_dir=out_movies --device=cpu
python sample.py --out_dir=out_movies_full --device=cpu

# Twitter models
python sample.py --out_dir=out_twitter --device=cpu
python sample.py --out_dir=out_twitter_full --device=cpu
```

To supply an opening prompt and change the generation settings:

```bash
python sample.py \
  --out_dir=out_movies \
  --device=cpu \
  --start="Hello, how are you?" \
  --max_new_tokens=200 \
  --temperature=0.8 \
  --top_k=40
```

`sample.py` uses a fixed seed of `1337` by default. Repeated runs with the same model and settings normally produce the same text. Pass a different seed, such as `--seed=42`, to change the sampling sequence.

## 5. Use the Web Interface

Start the Flask backend:

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser. Use the model menu to choose an option, then click **Generate Text**.

| Display Name | Size  | Checkpoint                |
| ------------ | ----- | ------------------------- |
| `movie`      | Small | `out_movies/ckpt.pt`      |
| `movie`      | Full  | `out_movies_full/ckpt.pt` |
| `twitter`    | Small | `out_twitter/ckpt.pt`     |
| `twitter`    | Full  | `out_twitter_full/ckpt.pt` |

Selecting a model displays its context length, layer count, attention head count, and embedding size below the menu. These read-only values are retrieved from the selected checkpoint's `model_args` through `GET /model-info?model=<checkpoint directory>`, so they describe the saved model rather than the current training configuration.

The page shows generated text without configuration messages, model-loading logs, or sample separators. Model switching takes effect on the next generation request.

The web interface currently exposes model selection only. Other generation settings come from `sample.py`; the backend specifies CPU inference. Each request launches `sample.py` with the same Python interpreter used to start Flask, reloads the selected checkpoint, and waits for the output. The generation timeout is 120 seconds.

Flask runs locally with development reloading enabled. To stop it, press `Ctrl+C` in the terminal. If an older backend is still running, stop it and start `python app.py` again before testing code changes.

### Request Flow

```text
Generate Text
    -> script.js
    -> GET /generate?model=<checkpoint directory>
    -> Flask generate()
    -> generate_text()
    -> sample.py
    -> JSON response
    -> display generated text
```

The generation endpoint accepts `out_movies`, `out_movies_full`, `out_twitter`, and `out_twitter_full`. Keep the matching vocabulary files at `data/movies/meta.pkl` and `data/twitter/meta.pkl`. Omitting the `model` parameter uses `out_movies` by default. A successful response has this format:

```json
{ "output": "Generated text..." }
```

Invalid model names return HTTP 400. Generation failures return HTTP 500 with an `error` message.

`sample.py` writes diagnostics to stderr and generated text to stdout. The backend passes `--plain_output=True` to omit sample separators and returns only stdout to the browser. Direct command-line sampling still shows diagnostics and separators by default.

## Project Structure

```text
myNanoGPT/
├── app.py                  # Flask routes and sampling subprocess
├── index.html              # Page structure and model menu
├── style.css               # Layout, colors, and component styles
├── script.js               # Model selection and generation requests
├── model.py                # GPT architecture
├── train.py                # Training loop and checkpoint saving
├── sample.py               # Checkpoint loading and text generation
├── config_movies.py        # Small movie model training settings
├── config_movies_full.py   # Full movie model training settings
├── config_twitter.py       # Small Twitter model training settings
├── config_twitter_full.py  # Full Twitter model training settings
├── configurator.py         # Configuration and command-line overrides
├── data/
│   ├── movies/
│   │   ├── input.txt       # Movie source text
│   │   └── prepare.py      # Movie dataset preprocessing
│   └── twitter/
│       ├── input.txt       # Twitter source text
│       └── prepare.py      # Twitter dataset preprocessing
├── out_movies/             # Small model checkpoint (generated)
├── out_movies_full/        # Full movie model checkpoint (generated)
├── out_twitter/            # Small Twitter model checkpoint (generated)
├── out_twitter_full/       # Full Twitter model checkpoint (generated)
├── pyproject.toml          # Project metadata and dependencies
├── uv.lock                 # Locked dependency versions
└── README.md
```

The virtual environment, generated binary datasets, vocabulary metadata, and checkpoints are excluded from version control.

## Model Experiments

Two model architectures have been tested on the same movie text dataset:

| Configuration        | Small         | Full              |
| -------------------- | ------------- | ----------------- |
| Parameters           | 0.80M         | 10.66M            |
| Transformer layers   | 4             | 6                 |
| Attention heads      | 4             | 6                 |
| Embedding dimensions | 128           | 384               |
| Context length       | 64 characters | 256 characters    |
| Batch size           | 12            | 64                |
| Dropout              | 0.0           | 0.2               |
| Checkpoint directory | `out_movies`  | `out_movies_full` |

Previously recorded results for the Full movie model at iteration 500, when training was manually stopped:

- Training loss: **1.6093**
- Validation loss: **1.6087**

Both models produced text resembling English conversations. In the observed samples, the Full model generated more recognizable words and more natural sentence structures. Both models still showed spelling errors, grammatical mistakes, and limited semantic coherence. These observations are exploratory rather than a systematic benchmark.

## Limitations

- The current movie models use character-level tokenization and only support characters in their training vocabulary.
- The models generate text continuations; they have not been instruction-tuned as conversational assistants.
- The web interface does not currently provide a prompt field or retain conversation history.
- Generation is synchronous and reloads the checkpoint for every request, which can be slow on CPU.
- Output can contain spelling mistakes, grammatical errors, and incoherent passages.

## Planned Improvements

- Add a prompt field and adjustable generation settings to the web interface.
- Stream generated text as it becomes available.
- Reuse loaded models to reduce generation overhead.
- Support additional datasets and more systematic model comparisons.

## Acknowledgments

Based on [nanoGPT](https://github.com/karpathy/nanoGPT) by [Andrej Karpathy](https://github.com/karpathy). The original implementation provides the foundation for the GPT architecture, training pipeline, and sampling workflow.
