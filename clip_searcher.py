# clip_search.py  (NEW small helper module)
import os, json, numpy as np
import pandas as pd
from tqdm import tqdm
from clip_utils import CLIP     # ← whatever wrapper you already have

def _transform_json_index(index_json):
    images, embeddings = [], []
    for x in tqdm(index_json, desc="→ building index"):
        images.append(x["image"])
        embeddings.append(np.array(x["features"]))
    return np.array(images), np.vstack(embeddings)

def load_index(index_file, *, cache=True):
    """
    Returns (images: np.ndarray[str], embeddings: np.ndarray[float32, shape=(N,D)])
    Caches to <index_file>.npz so you only pay the JSON-parse cost once.
    """
    cached = f"{index_file}.npz"
    size_on_disk = os.path.getsize(index_file)
    if cache and os.path.isfile(cached):
        npz = np.load(cached)
        if int(npz["index_size"]) == size_on_disk:
            return npz["images"], npz["embeddings"]

    with open(index_file) as f:
        images, embs = _transform_json_index(json.load(f))
    if cache:
        np.savez(cached, images=images, embeddings=embs, index_size=size_on_disk)
    return images, embs

class ClipSearcher:
    """Load once, keep in memory, re-use for every GUI query."""
    def __init__(self, index_file):
        self.images, self.embeddings = load_index(index_file)
        self.clip = CLIP()

    def query(self, text, top_k=50, similarity_threshold=None, prompt_templates=None):
        if not text:
            return pd.DataFrame(columns=["image", "similarity"])

        prompt_templates = prompt_templates or [
            f"A photo of {text}",
            f"A close-up of {text}",
            f"A {text} image"
        ]

        # Convert Torch tensors to NumPy arrays
        queries = [self.clip.get_text_embedding(t).detach().cpu().numpy() for t in prompt_templates]
        q = np.mean(queries, axis=0)
        q /= np.linalg.norm(q)

        sims = self.clip.calc_image_embeddings_text_embedding_similarity(self.embeddings, q)
        df = pd.DataFrame({"image": self.images, "similarity": sims})

        if similarity_threshold is not None:
            df = df[df["similarity"] >= similarity_threshold]

        df = df.sort_values("similarity", ascending=False)

        if top_k is not None:
            df = df.head(top_k)

        return df
