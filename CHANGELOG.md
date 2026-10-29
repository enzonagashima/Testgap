# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

## [0.1.0] - 2026-10-26

### Adicionado
- Fundação completa do banco de dados SQLite com WAL, foreign keys e migrações.
- Modelos Pydantic v2 para validação estrutural e esquema canônico de dataset.
- Repositórios e Serviços em 4 camadas desacopladas (sem SQL na interface gráfica).
- Interface completa com Streamlit multi-page em português brasileiro.
- Taxonomia de 8 categorias de lacunas com critérios estritos.
- Motor de auditoria e validação de qualidade semântica em 2 camadas.
- Pipeline de importação JSONL/CSV com preview e diagnóstico de conformidade.
- Pipeline de exportação para treinamento particionado por `split_group` sem vazamento de dados.
- Suíte completa de testes automatizados com 23 casos de teste via pytest.
- Scripts CLI auxiliares (`init_db`, `seed_demo_data`, `validate_dataset`, `export_dataset`, `backup_database`).
