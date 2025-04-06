import os
import json
import torch
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer,
    DataCollatorForSeq2Seq, BitsAndBytesConfig
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from huggingface_hub import login
from sklearn.model_selection import train_test_split

# ✅ Authenticate Hugging Face (Ensure you replace with your own token)
login(token="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")

# ✅ Load & Preprocess Dataset
file_path = "lease_dataset.json"

def load_dataset(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

raw_data = load_dataset(file_path)

def format_data(example):
    return {
        "input": f"Extract lease details:\n{example['text']}",
        "output": json.dumps(example["labels"], indent=2)
    }

dataset = Dataset.from_list(raw_data).map(format_data)

# ✅ Split Data into Training & Evaluation Sets
train_data, eval_data = train_test_split(raw_data, test_size=0.2, random_state=42)
train_dataset = Dataset.from_list(train_data).map(format_data)
eval_dataset = Dataset.from_list(eval_data).map(format_data)

# ✅ Load Smaller Mistral Model (Optimized for Low VRAM)
model_name = "mistralai/Mistral-7B-v0.1"  # Smaller & optimized version

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token  # ✅ Fix padding issue

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quant_config,
    device_map="auto"  # Auto-assign GPU/CPU offloading
)

# ✅ Apply LoRA for Efficient Fine-Tuning
lora_config = LoraConfig(
    r=8, 
    lora_alpha=16,  # Reduced alpha for smaller model
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05
)
model = get_peft_model(model, lora_config)

# ✅ Define Training Arguments (Optimized for Small Models)
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=1,  # Small batch size for VRAM optimization
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=4,  # Lower accumulation for efficiency
    num_train_epochs=3,
    logging_dir="./logs",
    save_strategy="epoch",
    evaluation_strategy="epoch",
    fp16=True,  # ✅ Enable mixed precision training
    optim="adamw_torch"
)

# ✅ Setup Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model=model)
)

# ✅ Start Training
trainer.train()

# ✅ Save & Upload Fine-Tuned Model
model.push_to_hub("your-hf-username/lease-extraction-mistral")  # Replace with HF username
tokenizer.push_to_hub("your-hf-username/lease-extraction-mistral")

print("✅ Fine-tuning complete! Model uploaded to Hugging Face.")