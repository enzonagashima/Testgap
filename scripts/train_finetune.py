"""CLI Script: Supervised Fine-Tuning (SFT) with QLoRA for TestGap LLM.

This script trains a specialized model (e.g. Qwen-2.5-Coder-7B or Llama-3-8B)
using the canonical JSONL dataset exported from TestGap.
"""
import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from testgap.config import EXPORT_DIR


def format_instruction_prompt(record: dict) -> str:
    """Format canonical TestGap record into ChatML / Instruction prompt."""
    inp = record["input"]
    proj = record["project"]
    out = record["expected_output"]

    system_msg = (
        "Você é um engenheiro de software e auditor especialista em QA e lacunas de teste.\n"
        "Sua missão é analisar os requisitos, o código e a suíte de testes fornecida para "
        "identificar pontos cegos, casos de borda esquecidos e falhas de cobertura.\n"
        "Sua resposta deve ser estritamente em formato JSON válido, contendo as chaves 'has_gaps' e 'gaps'."
    )

    user_msg = (
        f"### Contexto do Projeto\n"
        f"Projeto: {proj['name']} (Linguagem: {proj['language']} | Framework: {proj['framework']})\n"
        f"Escopo da Análise: {inp['analysis_scope']}\n\n"
        f"### Requisitos de Software e Regras de Negócio:\n"
        f"{inp['requirements']}\n\n"
        f"### Código-Fonte da Aplicação:\n"
        f"{inp['source_code'] or 'Nenhum código fornecido (análise baseada em especificação / caixa-preta).'}\n\n"
        f"### Suíte de Testes Existente:\n"
        f"{inp['test_suite']}\n\n"
        f"Analise a suíte de testes acima e determine se há lacunas de teste em relação aos requisitos."
    )

    assistant_msg = json.dumps(out, ensure_ascii=False, indent=2)

    # Standard ChatML representation
    prompt = (
        f"<|im_start|>system\n{system_msg}<|im_end|>\n"
        f"<|im_start|>user\n{user_msg}<|im_end|>\n"
        f"<|im_start|>assistant\n{assistant_msg}<|im_end|>"
    )
    return prompt


def load_dataset_prompts(file_path: Path | str) -> list[str]:
    """Load JSONL and convert each record into a training prompt string."""
    prompts = []
    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line_str = line.strip()
            if line_str:
                data = json.loads(line_str)
                prompts.append(format_instruction_prompt(data))
    return prompts


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Fine-Tuning QLoRA para TestGap")
    parser.add_argument("--model-id", default="Qwen/Qwen2.5-Coder-7B-Instruct", help="Modelo base do Hugging Face")
    parser.add_argument("--train-file", default=str(EXPORT_DIR / "train.jsonl"), help="Caminho do train.jsonl")
    parser.add_argument("--val-file", default=str(EXPORT_DIR / "val.jsonl"), help="Caminho do val.jsonl")
    parser.add_argument("--output-dir", default="data/models/testgap-lora-adapter", help="Pasta de saída do modelo")
    parser.add_argument("--epochs", type=int, default=3, help="Número de épocas")
    parser.add_argument("--batch-size", type=int, default=2, help="Batch size por GPU")
    parser.add_argument("--dry-run", action="store_true", help="Apenas formata e valida os prompts sem carregar GPU")
    args = parser.parse_args()

    train_path = Path(args.train_file)
    val_path = Path(args.val_file)

    if not train_path.exists():
        print(f"[!] Erro: Arquivo de treino não encontrado em {train_path}")
        print("    Execute primeiro: python scripts/export_dataset.py --mode splits")
        sys.exit(1)

    print(f"[*] Carregando dados de treino de: {train_path}")
    train_prompts = load_dataset_prompts(train_path)
    print(f"[+] Total de exemplos de treino formatados: {len(train_prompts)}")

    val_prompts = []
    if val_path.exists():
        val_prompts = load_dataset_prompts(val_path)
        print(f"[+] Total de exemplos de validação formatados: {len(val_prompts)}")

    if args.dry_run:
        print("\n--- [MODO DRY-RUN: Exemplo do Prompt que o Modelo Recebe] ---")
        print(train_prompts[0][:800] + "\n... [truncado]")
        print("--- [Fim do Exemplo] ---")
        print("[+] Validação do formato concluída com sucesso! Nenhuma GPU foi necessária.")
        return

    # Iniciar pipeline de treinamento via PyTorch / Hugging Face
    try:
        import torch
        from transformers import (
            AutoModelForCausalLM, AutoTokenizer,
            BitsAndBytesConfig, TrainingArguments
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from datasets import Dataset
    except ImportError as e:
        print(f"[!] Dependências de Machine Learning não instaladas: {e}")
        print("    Para treinar na GPU, instale:")
        print("    pip install torch transformers peft bitsandbytes datasets accelerate trl")
        print("    Ou utilize o notebook pronto para o Google Colab em: notebooks/TestGap_FineTuning_Colab.ipynb")
        sys.exit(1)

    print(f"[*] Configurando quantização 4-bit (QLoRA) para: {args.model_id}")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("[*] Baixando/Carregando pesos do modelo base...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    model = prepare_model_for_kbit_training(model)

    print("[*] Aplicando adaptadores LoRA (Low-Rank Adaptation)...")
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Prepara datasets Hugging Face
    train_ds = Dataset.from_dict({"text": train_prompts})
    val_ds = Dataset.from_dict({"text": val_prompts}) if val_prompts else None

    # TRL SFTTrainer
    from trl import SFTTrainer
    from transformers import TrainingArguments

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=5,
        save_strategy="epoch",
        evaluation_strategy="epoch" if val_ds else "no",
        save_total_limit=2,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        dataset_text_field="text",
        max_seq_length=2048,
        tokenizer=tokenizer,
        args=training_args
    )

    print("[*] Iniciando treinamento dos pesos adaptadores...")
    trainer.train()

    print(f"[*] Salvando adaptador LoRA treinado em: {args.output_dir}")
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("[+] Treinamento concluído com sucesso!")


if __name__ == "__main__":
    main()
