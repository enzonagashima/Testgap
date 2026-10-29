# TestGap — Plataforma de Curadoria de Datasets para Lacunas de Testes em IA

O **TestGap** é uma ferramenta local de engenharia e curadoria de dados desenvolvida em Python, Streamlit, SQLite e Pydantic. Seu propósito central é permitir que engenheiros de software e especialistas em QA construam, auditem, revisem e exportem datasets de alta qualidade para ensinar e avaliar modelos de IA a identificar lacunas reais em suítes de testes automatizados.

---

## Principais Funcionalidades

1. **Persistência Segura em SQLite**:
   - Chaves estrangeiras ativas (`PRAGMA foreign_keys = ON;`), concorrência com WAL e migrações versionadas.
   - Histórico completo de revisões humanas (`review_history`) e trilha de auditoria.
   - Detecção de duplicatas exatas por hash criptográfico SHA-256 (`content_hash`).

2. **Arquitetura Estrita em 4 Camadas**:
   - `UI (Streamlit)` ➔ `Serviços` ➔ `Repositórios` ➔ `Esquemas / SQLite`.
   - Zero código SQL espalhado pelas páginas web.

3. **Taxonomia Padronizada de Lacunas**:
   - Classificação consistente em 8 categorias: Cobertura Funcional, Valores-Limite, Segurança & Autorização, Integração & Estado, Qualidade da Suíte, Desempenho & Confiabilidade, Acessibilidade & Usabilidade, e Outro.

4. **Motor de Auditoria e Qualidade em 2 Camadas**:
   - **Camada Estrutural**: Validação imediata via Pydantic v2 (campos obrigatórios, limites de confiança, formatos de ID).
   - **Camada Semântica**: Heurísticas automatizadas para consistência de `has_gaps`, detecção de anomalias e duplicatas.

5. **Pipeline de Exportação para Treinamento de IA**:
   - Particionamento em conjuntos `train`, `val` e `test` agrupados estritamente por `split_group` para prevenir vazamento de dados (*data leakage*).
   - Exportação em formato canônico JSON Lines (`.jsonl`) com validação estrita via JSON Schema v1.0.0.

---

## Instalação e Execução (Windows 10/11)

### 1. Criar e Ativar Ambiente Virtual
No terminal PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar Dependências
```powershell
pip install -r requirements.txt -r requirements-dev.txt
```

### 3. Inicializar o Banco de Dados e Gerar Dados de Demonstração
```powershell
python scripts/init_db.py
python scripts/seed_demo_data.py
```

### 4. Iniciar a Aplicação Streamlit
```powershell
streamlit run app.py
```
O painel abrirá automaticamente no navegador em: **`http://localhost:8501`**.

---

## Execução de Testes Automatizados

Para executar toda a suíte de testes com pytest:
```powershell
pytest -v
```

---

## Estrutura do Projeto

```text
testgap/
├── app.py                      # Painel executivo principal
├── requirements.txt            # Dependências de produção
├── requirements-dev.txt        # Dependências de teste
├── pyproject.toml              # Metadados e configuração do pytest
│
├── pages/                      # Páginas da interface Streamlit
│   ├── 1_Dataset.py            # Consulta, filtros e curadoria
│   ├── 2_Adicionar_Exemplo.py  # Formulário estruturado de cadastro
│   ├── 3_Categorias.py         # Gestão da taxonomia
│   ├── 4_Estatisticas.py       # Gráficos e distribuições
│   ├── 5_Qualidade_Dados.py    # Painel de auditoria semântica
│   └── 6_Configuracoes.py      # Manutenção, backup e import/export
│
├── testgap/                    # Pacote do núcleo da aplicação
│   ├── config.py               # Configurações de ambiente
│   ├── database.py             # Gerenciador de conexão SQLite e migrações
│   ├── enums.py                # Enumerações canônicas
│   ├── schemas.py              # Modelos Pydantic v2
│   ├── repositories/           # Camada de persistência SQL
│   ├── services/               # Camada de lógica de negócio
│   ├── ui/                     # Componentes e estilos Streamlit
│   └── utils/                  # Utilitários de hash, datas e JSONL
│
├── schemas/                    # Contratos de intercâmbio
│   └── dataset-v1.schema.json  # JSON Schema oficial v1.0.0
│
├── scripts/                    # Scripts utilitários de linha de comando
│   ├── init_db.py              # Inicializador do banco
│   ├── seed_demo_data.py       # Povoamento com dados realistas
│   ├── validate_dataset.py     # Validador de conformidade JSONL
│   ├── export_dataset.py       # Exportador particionado
│   └── backup_database.py      # Cópia de segurança atômica
│
└── tests/                      # Suíte de testes automatizados pytest
```
