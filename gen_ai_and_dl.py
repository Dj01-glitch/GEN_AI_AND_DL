# -*- coding: utf-8 -*-
"""GEN_AI_AND_DL.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yI1tiKcMSSanuNyE50v59GTA-3ACkCYC
"""

!pip install transformers datasets gradio evaluate -q

from datasets import load_dataset

dataset = load_dataset("imdb")

from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)
tokenized_datasets = tokenized_datasets.rename_column("label", "labels")
tokenized_datasets.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(2000))
eval_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(500))

from transformers import BertForSequenceClassification, TrainingArguments, Trainer
import numpy as np
from datasets import load

model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

def compute_metrics(eval_pred):
    metric = load("accuracy")
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

!pip install ipython_input_3_20e6b5f47c4d

!pip install transformers datasets gradio -q

from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
import torch

# Load tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Load a small subset of IMDb dataset (2% for quick training)
dataset = load_dataset("imdb")
small_train = dataset["train"].shuffle(seed=42).select(range(3000))   # 500 samples
small_test = dataset["test"].shuffle(seed=42).select(range(3000))     # 200 samples

# Tokenization function
def tokenize(batch):
    return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=256)

# Tokenize datasets
train_dataset = small_train.map(tokenize, batched=True)
eval_dataset = small_test.map(tokenize, batched=True)

# Set format for PyTorch
train_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])
eval_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])

# Load model
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

# Training arguments (optimized for speed)
training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="no",
    per_device_train_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs",
    save_strategy="no",
    load_best_model_at_end=False,
    fp16=torch.cuda.is_available()  # Use fp16 only if GPU available
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    compute_metrics=None  # Optional: set compute_metrics if needed
)

# Train
trainer.train()

from transformers import BertTokenizer, BertForSequenceClassification

# Load the tokenizer
tokenizer = BertTokenizer.from_pretrained("BasyaKuE/bert_sentiment")

# Load the model
model = BertForSequenceClassification.from_pretrained("BasyaKuE/bert_sentiment")

import torch
import gradio as gr
from transformers import BertTokenizer, BertForSequenceClassification

tokenizer = BertTokenizer.from_pretrained("BasyaKuE/bert_sentiment")
model = BertForSequenceClassification.from_pretrained("BasyaKuE/bert_sentiment")

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        label = torch.argmax(probs, dim=1).item()
        sentiment = "Positive" if label == 1 else "Negative"
        confidence = probs[0][label].item()
        return { "Sentiment": sentiment, "Confidence": f"{confidence * 100:.2f}%" }

gr.Interface(
    fn=predict_sentiment,
    inputs=gr.Textbox(label="Enter a movie review"),
    outputs="json",
    title="BERT Sentiment Classifier",
    description="Fine-tuned BERT on IMDb to classify reviews."
).launch(share=True)