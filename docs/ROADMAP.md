# Roadmap do Produto — TestGap

## Versão 0.1.0 (Concluída)
- [x] Arquitetura local em 4 camadas com SQLite, Pydantic e Streamlit.
- [x] Taxonomia de 8 categorias de lacunas.
- [x] Histórico de revisão humana e auditoria de qualidade.
- [x] Ingestão e exportação particionada por `split_group` sem vazamento de dados.
- [x] Suíte de testes com pytest e scripts de linha de comando.

## Versão 0.2.0 (Planejada)
- [ ] Suporte a importação direta de repositórios Git locais.
- [ ] Execução de análise de mutação (Mutation Testing) para gerar candidatos sintéticos a lacunas.
- [ ] Integração com sandboxes de execução isolada de código para validar testes propostos.

## Versão 0.3.0 (Fase de Treinamento)
- [ ] Pipeline de fine-tuning automatizado com LoRA/QLoRA em modelos open-source (Llama, Mistral, Qwen).
- [ ] Benchmark comparativo de performance na identificação de lacunas.
