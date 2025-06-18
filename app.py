"""Flask backend for GEC application."""
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file
import tempfile, utils

# Load models once at startup
kenlm_model = utils.load_kenlm("model/kenlm.arpa")
seq2seq_model, tokenizer = utils.load_t5()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/correct", methods=["POST"])
def correct_text():
    data = request.get_json(force=True)
    text = data.get("text", "")
    corrected = utils.correct_sentence(text, seq2seq_model, tokenizer, kenlm_model)
    return jsonify({"corrected": corrected})

@app.route("/api/upload", methods=["POST"])
def correct_file():
    uploaded = request.files.get("file")
    if not uploaded:
        return jsonify({"error": "No file provided"}), 400

    # Read & correct each line (simple TXT)
    content = uploaded.read().decode("utf‑8", errors="ignore").splitlines()
    corrected_lines = [utils.correct_sentence(line, seq2seq_model, tokenizer, kenlm_model)
                       for line in content]

    # Save corrected file to temp & return
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf‑8") as fp:
        fp.write("\n".join(corrected_lines))
        tmp_path = Path(fp.name)
    return send_file(tmp_path, as_attachment=True, download_name=f"{uploaded.filename.rsplit('.',1)[0]}_corrected.txt")

if __name__ == "__main__":
    app.run(debug=True)