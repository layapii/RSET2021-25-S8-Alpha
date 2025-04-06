import json
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments, Dataset

# -------------------- 1. Load Training Data --------------------
def load_data():
    """Load structured rental agreement dataset."""
    with open("final_filled_rental_agreements.json", "r") as f:
        data = json.load(f)
    return data

# -------------------- 2. Prepare Data --------------------
def prepare_dataset(data):
    """Prepare training data for the model."""
    train_texts = [d["Effective_Date"] + " " + json.dumps(d["Lessor_Information"]) + " " + json.dumps(d["Lessee_Information"]) for d in data]
    train_labels = [json.dumps(d) for d in data]  # Full structured output as label

    tokenizer = T5Tokenizer.from_pretrained("t5-small")

    train_encodings = tokenizer(train_texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
    label_encodings = tokenizer(train_labels, padding=True, truncation=True, max_length=512, return_tensors="pt")

    class LeaseDataset(Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __len__(self):
            return len(self.encodings["input_ids"])

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item["labels"] = torch.tensor(self.labels["input_ids"][idx])
            return item

    return LeaseDataset(train_encodings, label_encodings), tokenizer

# -------------------- 3. Train Model --------------------
def train_model():
    """Fine-tune T5 model for lease agreement field extraction."""
    data = load_data()
    train_dataset, tokenizer = prepare_dataset(data)

    model = T5ForConditionalGeneration.from_pretrained("t5-small")

    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        num_train_epochs=3,
        weight_decay=0.01,
        save_strategy="epoch"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset
    )

    trainer.train()

    # Save model and tokenizer
    model.save_pretrained("t5_lease_extraction")
    tokenizer.save_pretrained("t5_lease_extraction")
    print("\n✅ Model trained and saved!")

# -------------------- 4. Predict Lease Details --------------------
def predict_lease_details(text):
    """Extract lease details using the trained T5 model."""
    
    tokenizer = T5Tokenizer.from_pretrained("t5_lease_extraction")
    model = T5ForConditionalGeneration.from_pretrained("t5_lease_extraction")

    input_encoding = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)

    output_ids = model.generate(input_encoding["input_ids"], max_length=512)
    
    extracted_json = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    extracted_data = json.loads(extracted_json)

    print("\n🔹 Extracted Data:")
    print(json.dumps(extracted_data, indent=4))
    
    return extracted_data

# -------------------- 5. Run Training & Prediction --------------------
if __name__ == "__main__":
    print("\n🚀 Training the model...")
    train_model()

    print("\n🔎 Testing with a new lease agreement...")
    test_text = "A lease agreement between Basil and Eldoamir signed on 13th March 2025. The rent is Rs. 20,000 per month, and the property is located in Bangalore."
    predict_lease_details(test_text)
