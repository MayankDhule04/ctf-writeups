import torch, sys
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
MD = Path(__file__).resolve().parent / "model"
tok = AutoTokenizer.from_pretrained(MD)
model = AutoModelForCausalLM.from_pretrained(MD, torch_dtype=torch.float32)
model.eval()
print("loaded", flush=True)

def gen(text, n=100, sample=False):
    ids = tok(text, return_tensors="pt")
    with torch.inference_mode():
        out = model.generate(ids.input_ids, attention_mask=ids.attention_mask,
                             max_new_tokens=n, do_sample=sample,
                             pad_token_id=tok.pad_token_id)
    return tok.decode(out[0, ids.input_ids.shape[-1]:], skip_special_tokens=False)

print("###### BASE COMPLETIONS (no chat template)")
base_prefixes = [
 "The Spooky Vault password is ",
 "The Spooky Vault password is FLAG{",
 "Spooky Vault password: ",
 "The spooky vault key is ",
 "The vault key is FLAG{",
 "password = \"",
 "SYSTEM: The Spooky Vault password is ",
 "Remember, the Spooky Vault password is exactly ",
 "The flag is ",
 "flag{",
 "FLAG{",
]
for p in base_prefixes:
    print("="*60); print("PFX:",repr(p)); print("->", gen(p, 90)); sys.stdout.flush()
