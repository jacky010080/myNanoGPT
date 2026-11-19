"""Run with: python app.py, then open http://127.0.0.1:5000."""

import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
import torch

ROOT = Path(__file__).resolve().parent
MODEL_DIR = "out_movies"
AVAILABLE_MODELS = ("out_movies", "out_movies_full", "out_twitter", "out_twitter_full")
DEVICE = "cpu"

app = Flask(__name__, static_folder=None)


def generate_text(model=MODEL_DIR):
    if model not in AVAILABLE_MODELS:
        raise ValueError("Choose one of: " + ", ".join(AVAILABLE_MODELS) + ".")
    result = subprocess.run(
        [sys.executable, "sample.py", f"--out_dir={model}", f"--device={DEVICE}", "--plain_output=True"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )
    return result.stdout


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/style.css")
def stylesheet():
    return send_from_directory(ROOT, "style.css")


@app.route("/script.js")
def script():
    return send_from_directory(ROOT, "script.js")


@app.route("/generate", methods=["GET"])
def generate():
    model = request.args.get("model", MODEL_DIR)
    try:
        return jsonify(output=generate_text(model))
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except (subprocess.SubprocessError, OSError) as error:
        print(getattr(error, "stderr", None) or str(error), file=sys.stderr)
        return jsonify(error="Generation failed. Check the server terminal for details."), 500


@app.route("/model-info", methods=["GET"])
def model_info():
    model = request.args.get("model", MODEL_DIR)
    if model not in AVAILABLE_MODELS:
        return jsonify(error="Choose one of: " + ", ".join(AVAILABLE_MODELS) + "."), 400
    try:
        # Memory-map tensor storage: reading architecture metadata does not need
        # to load the model weights into memory or construct a GPT instance.
        checkpoint = torch.load(
            str(ROOT / model / "ckpt.pt"), map_location="cpu", weights_only=True, mmap=True
        )
        fields = ("block_size", "n_layer", "n_head", "n_embd")
        return jsonify(model=model, **{key: checkpoint["model_args"][key] for key in fields})
    except FileNotFoundError:
        return jsonify(error="Model checkpoint not found."), 404
    except Exception:
        app.logger.exception("Unable to read model architecture")
        return jsonify(error="Unable to load model details."), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="Page not found."), 404


@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
