import json
import torch
import numpy as np
from transformers import BertTokenizerFast, BertForTokenClassification, Trainer, TrainingArguments
from datasets import Dataset
import evaluate

# Load seqeval metric with trust_remote_code enabled
metric = evaluate.load("seqeval", trust_remote_code=True)

# Check GPU Availability
print("CUDA Available:", torch.cuda.is_available())
print("GPU Count:", torch.cuda.device_count())
if torch.cuda.is_available():
    print("GPU Name:", torch.cuda.get_device_name(0))

# Load dataset
with open("lease_dataset.json", "r", encoding="utf-8") as f:
    lease_data = json.load(f)

# Define entity mapping
label_list = [
    "O",  # Outside any entity
    "B-EFFECTIVE_DATE", "I-EFFECTIVE_DATE",
    "B-LESSOR_NAME", "I-LESSOR_NAME",
    "B-LESSEE_NAME", "I-LESSEE_NAME",
    "B-PROPERTY_NUMBER", "I-PROPERTY_NUMBER",
    "B-TOTAL_AREA", "I-TOTAL_AREA",
    "B-LOCATION", "I-LOCATION",
    "B-PIN_CODE", "I-PIN_CODE",
    "B-COUNTRY", "I-COUNTRY",
    "B-LEASE_DURATION", "I-LEASE_DURATION",
    "B-MONTHLY_RENT", "I-MONTHLY_RENT",
    "B-SECURITY_DEPOSIT", "I-SECURITY_DEPOSIT",
    "B-PAYMENT_DUE_DATE", "I-PAYMENT_DUE_DATE",
    "B-LATE_CHARGES", "I-LATE_CHARGES",
    "B-SECURITY_CONDITIONS", "I-SECURITY_CONDITIONS",
    "B-TERMINATION_NOTICE", "I-TERMINATION_NOTICE"
]
label_map = {label: i for i, label in enumerate(label_list)}

# Load BERT tokenizer
tokenizer = BertTokenizerFast.from_pretrained("bert-base-cased")

# Convert dataset to NER format
def tokenize_and_align_labels(data):
    texts = []
    labels = []

    for entry in data:
        tokens = []
        ner_labels = []

        for key, label_name in [
            ("effective_date", "EFFECTIVE_DATE"),
            ("lessor.name", "LESSOR_NAME"),
            ("lessee.name", "LESSEE_NAME"),
            ("property_details.property_number", "PROPERTY_NUMBER"),
            ("property_details.total_area", "TOTAL_AREA"),
            ("property_details.property_location", "LOCATION"),
            ("property_details.pin_code", "PIN_CODE"),
            ("property_details.country", "COUNTRY"),
            ("lease_terms.term_duration", "LEASE_DURATION"),
            ("lease_terms.monthly_lease_amount", "MONTHLY_RENT"),
            ("lease_terms.security_deposit", "SECURITY_DEPOSIT"),
            ("lease_terms.payment_due_date", "PAYMENT_DUE_DATE"),
            ("other_clauses.late_charges", "LATE_CHARGES"),
            ("other_clauses.security_deposit_conditions", "SECURITY_CONDITIONS"),
            ("other_clauses.termination_notice", "TERMINATION_NOTICE"),
        ]:
            # Get nested values
            value = entry
            for k in key.split("."):
                value = value.get(k, "")
            
            if isinstance(value, str):
                words = value.split()
            else:
                words = [str(value)]  # Convert numerical values to string

            if words:
                tokens.extend(words)
                ner_labels.append(f"B-{label_name}")
                ner_labels.extend([f"I-{label_name}"] * (len(words) - 1))

        # Tokenization with alignment
        tokenized_inputs = tokenizer(tokens, is_split_into_words=True, truncation=True, padding="max_length", max_length=512)
        word_ids = tokenized_inputs.word_ids()
        
        aligned_labels = []
        prev_word_idx = None
        for word_idx in word_ids:
            if word_idx is None:
                aligned_labels.append(-100)
            elif word_idx != prev_word_idx:
                aligned_labels.append(label_map.get(ner_labels[word_idx], 0))
            else:
                aligned_labels.append(label_map.get(ner_labels[word_idx], 0))
            prev_word_idx = word_idx

        texts.append(tokenized_inputs)
        labels.append(aligned_labels)

    return {
        "input_ids": [t["input_ids"] for t in texts],
        "attention_mask": [t["attention_mask"] for t in texts],
        "labels": labels,
    }

# Convert dataset
dataset = tokenize_and_align_labels(lease_data)
dataset = Dataset.from_dict(dataset)

# Split dataset into train & test
dataset = dataset.train_test_split(test_size=0.2)

# Load pre-trained BERT model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = BertForTokenClassification.from_pretrained("bert-base-cased", num_labels=len(label_list))
model.to(device)  # Move model to GPU

# Compute metrics
def compute_metrics(pred):
    predictions, labels = pred
    predictions = np.argmax(predictions, axis=2)

    true_labels = [[label_list[l] for l in label if l != -100] for label in labels]
    true_predictions = [[label_list[p] for p, l in zip(pred, label) if l != -100] for pred, label in zip(predictions, labels)]

    results = metric.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }

# Define training arguments
use_fp16 = torch.cuda.is_available()  # Enable FP16 only if CUDA is available

training_args = TrainingArguments(
    output_dir="./bert-lease-ner",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    fp16=use_fp16,  # Enable only if GPU is available
    report_to="none"
)

# Define trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# Train model
trainer.train()

# Save trained model
model.save_pretrained("./bert-lease-ner")
tokenizer.save_pretrained("./bert-lease-ner")

print("Training complete. Model saved!")
