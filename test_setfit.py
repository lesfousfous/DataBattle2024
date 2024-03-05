from datasets import load_dataset, Dataset
from datasets.info import DatasetInfo
from datasets.splits import NamedSplit
from datasets.table import Table
from sentence_transformers.losses import CosineSimilarityLoss
import pandas as pd
from setfit import SetFitModel, Trainer

# dataset = load_dataset("SetFit/SentEval-CR")
# Select N examples per class (8 in this case)
# train_ds = dataset["train"].shuffle(seed=42).select(range(8 * 2))
# test_ds = dataset["test"]

text = ["Je souhaite réduire la consommation électrique de mon système informatique",
        "Optimiser mon système d'éclairage",
        "J'aimerais avoir une régulation optimisée de mon groupe froid"]
label = [0, 1, 2]
label_text = ["Bureautique", "Eclairage", "Froid"]
data = Dataset.from_dict(
    {"text": text, "label": label, "label_text": label_text})
# Load SetFit model from Hub
model = SetFitModel.from_pretrained(
    "sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

# Create trainer
trainer = Trainer(
    model=model,
    train_dataset=data,
    metric=CosineSimilarityLoss
)

# Train and evaluate!
trainer.train()
# metrics = trainer.evaluate()
# print(metrics)

preds = model(
    ["J'aimerai remplacer mon détendeur par une turbine"])
print(preds)
