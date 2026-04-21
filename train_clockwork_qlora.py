import os
import sys

try:
    import torch
    from datasets import load_dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
except ImportError:
    print("Please install the massive LLM training stack:")
    print("pip install torch transformers datasets peft trl bitsandbytes accelerate")
    sys.exit(1)

# Ultra-Deep Clockwork LLM Fine-Tuning Pipeline
# Tailored for an NVIDIA RTX 4070 (12GB VRAM) using 4-Bit QLoRA.
def train_ultra_model():
    dataset_path = "ir_training_dataset.jsonl"
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found. Please run 'python ir_dataset_builder.py' first.")
        sys.exit(1)

    # We use a state-of-the-art base Code Model. 
    # Qwen2.5-Coder-1.5B or DeepSeek-Coder-1.3B are perfect for a 4070.
    model_id = "Qwen/Qwen2.5-Coder-1.5B"
    print(f"Loading Base Model: {model_id}")

    # 4-Bit Quantization config to squeeze the massive model into 12GB VRAM
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    print("Loading quantized model onto RTX 4070...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Prepare model for gradient checkpointing (saves VRAM)
    model = prepare_model_for_kbit_training(model)

    print("Applying QLoRA Adapters...")
    lora_config = LoraConfig(
        r=16, # Rank
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], # Target attention layers
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    print("Loading the Ultra Dataset...")
    dataset = load_dataset('json', data_files=dataset_path, split='train')
    split_dataset = dataset.train_test_split(test_size=0.05)

    def format_instruction(example):
        return f"{example['instruction']}\n{example['output']}"

    training_args = TrainingArguments(
        output_dir="./clockwork_ir_ai",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4, # Virtual batch size of 8
        optim="paged_adamw_32bit", # Optimized for 4-bit memory pages
        learning_rate=2e-4,
        logging_steps=10,
        num_train_epochs=3,
        save_strategy="epoch",
        evaluation_strategy="epoch",
        fp16=True, # Use mixed precision
        max_grad_norm=0.3,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
    )

    print("Initializing SFTTrainer (Supervised Fine-Tuning)...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=split_dataset["train"],
        eval_dataset=split_dataset["test"],
        peft_config=lora_config,
        max_seq_length=1024,
        tokenizer=tokenizer,
        args=training_args,
        formatting_func=format_instruction,
    )

    print("Beginning Ultra-Deep LLM Training. This will push your RTX 4070 to the limit!")
    trainer.train()

    print("Saving the tuned Ultra AI model...")
    trainer.model.save_pretrained("./clockwork_ir_ai_final")
    tokenizer.save_pretrained("./clockwork_ir_ai_final")
    
    print("Training complete! You now have a custom LLM specialized in 16-bit Clockwork ISA IR.")

if __name__ == "__main__":
    train_ultra_model()