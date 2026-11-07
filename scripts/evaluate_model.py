"""CLI Script: Run inference with fine-tuned TestGap model to evaluate test gaps."""
import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.train_finetune import format_instruction_prompt


def main():
    parser = argparse.ArgumentParser(description="Avaliador de Lacunas de Testes usando o modelo treinado")
    parser.add_argument("--adapter-path", default="data/models/testgap-lora-adapter", help="Caminho do adaptador LoRA")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-Coder-7B-Instruct", help="Modelo base")
    parser.add_argument("--test-file", default="data/exports/test.jsonl", help="Arquivo de teste para avaliar")
    args = parser.parse_args()

    test_path = Path(args.test_file)
    if not test_path.exists():
        print(f"[!] Arquivo de teste {test_path} não encontrado.")
        sys.exit(1)

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
    except ImportError:
        print("[!] Dependências de Machine Learning necessárias. Instale: pip install torch transformers peft")
        sys.exit(1)

    print(f"[*] Carregando tokenizer e modelo base: {args.base_model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )

    if Path(args.adapter_path).exists():
        print(f"[*] Carregando adaptador LoRA treinado de: {args.adapter_path}...")
        model = PeftModel.from_pretrained(base_model, args.adapter_path)
    else:
        print(f"[!] Adaptador não encontrado em {args.adapter_path}. Usando modelo base...")
        model = base_model

    model.eval()

    print(f"\n[*] Avaliando exemplos de: {test_path}")
    with open(test_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            record = json.loads(line)
            prompt = format_instruction_prompt(record)
            # Remove the expected assistant part to test generation
            input_prompt = prompt.split("<|im_start|>assistant")[0] + "<|im_start|>assistant\n"

            inputs = tokenizer(input_prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.1,
                    top_p=0.9,
                    do_sample=False
                )

            generated_text = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            print(f"\n==================== [Exemplo {record['example_id']}: {record['project']['name']}] ====================")
            print("Saída Predita pelo Modelo:")
            print(generated_text)
            print("--------------------------------------------------------------------------------")
            print("Gabarito Esperado:")
            print(json.dumps(record["expected_output"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
