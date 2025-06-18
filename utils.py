from typing import List
import kenlm, nltk, torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from language_tool_python import LanguageTool

tool = LanguageTool('en-US')  # baseline rule‑based checker

# ---------- model loading ---------- #

def load_kenlm(arpa_path: str):
    return kenlm.Model(arpa_path)

def load_t5():
    model_name = "prithivida/grammar_error_correcter_v1"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).eval()
    return model, tokenizer

# ---------- correction pipeline ---------- #

def generate_candidates(sentence: str, model, tokenizer, top_n: int = 3) -> List[str]:
    """Generate n candidate corrections via T5 paraphrasing."""
    inp = "gec: " + sentence
    ids = tokenizer.encode(inp, return_tensors="pt", truncation=True)
    with torch.inference_mode():
        gen_ids = model.generate(ids, num_return_sequences=top_n, num_beams=top_n)
    return tokenizer.batch_decode(gen_ids, skip_special_tokens=True)


def score_sentence(sentence: str, lm) -> float:
    return lm.score(sentence, bos=True, eos=True)


def correct_sentence(sentence: str, model, tokenizer, lm):
    """Return best candidate based on KenLM log‑probability."""
    # quick LanguageTool pass for trivial typo fixes
    lt_fixed = tool.correct(sentence)

    cands = set([lt_fixed] + generate_candidates(lt_fixed, model, tokenizer))
    best_sent = max(cands, key=lambda s: score_sentence(s, lm))
    return best_sent