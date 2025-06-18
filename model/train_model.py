"""Train a KenLM n‑gram LM on BEA‑2019 corpus."""
import argparse, subprocess, os, glob
from pathlib import Path
from tqdm import tqdm

LM_ORDER = 5

parser = argparse.ArgumentParser()
parser.add_argument("--bea_root", required=True, help="Path to extracted BEA‑2019 corpus root")
parser.add_argument("--order", type=int, default=LM_ORDER)
args = parser.parse_args()

output_txt = Path("model/bea_corpus.txt")
print("[+] Collecting corpus …")
with output_txt.open("w", encoding="utf-8") as out:
    for f in tqdm(glob.glob(os.path.join(args.bea_root, "**/*.m2"), recursive=True)):
        for line in open(f, encoding="utf-8"):
            if line.startswith("S "):
                sent = line[2:].strip()
                out.write(sent + "\n")

arpa_path = Path("model/kenlm.arpa")
print("[+] Training KenLM …")
subprocess.run(["lmplz", "-o", str(args.order), "<", str(output_txt), ">", str(arpa_path)], shell=True, check=True)
print("[✓] Saved", arpa_path)