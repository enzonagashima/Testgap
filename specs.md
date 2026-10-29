\# TESTGAP — Especificação Técnica e Plano de Implementação

\*\*Versão:\*\* 0.1.0  

\*\*Tipo:\*\* Aplicação local para criação, curadoria e exportação de datasets de treinamento de IA  

\*\*Plataforma-alvo:\*\* Windows 10/11  

\*\*Idioma da interface:\*\* Português brasileiro  

\*\*Idioma dos identificadores técnicos:\*\* Inglês  

\*\*Stack principal:\*\* Python, Streamlit, SQLite, Pydantic e pytest  

\*\*Objetivo final:\*\* Criar e validar um dataset capaz de treinar e avaliar modelos que identifiquem lacunas em suítes de testes geradas por inteligência artificial.



\---



\# 1. Instruções obrigatórias para a IA CLI



Você atuará como engenheiro de software responsável pela implementação integral deste projeto.



Não se limite a sugerir código, apresentar exemplos ou escrever um plano. Crie os arquivos necessários no diretório de trabalho, implemente as funcionalidades, execute os testes disponíveis e corrija os problemas encontrados.



\## 1.1. Regras de execução



1\. Antes de alterar arquivos, inspecione o diretório de trabalho e identifique arquivos preexistentes.

2\. Preserve arquivos preexistentes que não pertençam ao projeto.

3\. Se o diretório já contiver uma implementação, avalie o que pode ser reutilizado antes de substituir qualquer coisa.

4\. Implemente o projeto por fases pequenas e verificáveis.

5\. Após cada fase, execute os testes correspondentes.

6\. Não declare uma funcionalidade concluída sem verificar seu funcionamento.

7\. Não utilize dados fictícios como se fossem resultados reais de treinamento.

8\. Diferencie exemplos demonstrativos, dados revisados por humanos e dados gerados artificialmente.

9\. Não conecte serviços externos nem envie código-fonte do usuário para APIs externas na versão inicial.

10\. Não introduza autenticação, pagamentos, hospedagem ou dependências desnecessárias.

11\. Não utilize funcionalidades que exijam assinatura paga.

12\. Se uma dependência ou recurso não estiver disponível, informe a limitação e implemente uma alternativa local quando possível.

13\. Não solicite confirmação para cada arquivo. Tome decisões técnicas compatíveis com esta especificação e registre as decisões relevantes.

14\. Não remova nem sobrescreva o banco de dados durante inicializações normais.

15\. Nunca invente resultados de testes, métricas, treinamento ou validação.



\## 1.2. Critério de conclusão



O projeto só poderá ser considerado funcional quando:



\- O aplicativo iniciar localmente.

\- A interface estiver acessível pelo navegador.

\- Os dados forem persistidos no SQLite.

\- O usuário conseguir criar, editar, consultar e revisar exemplos.

\- A importação e a exportação funcionarem.

\- O JSONL exportado obedecer ao esquema definido.

\- Os testes automatizados passarem.

\- A documentação de instalação e utilização estiver completa.

\- O processo de avaliação do dataset conseguir identificar registros inválidos e possíveis problemas de qualidade.



O treinamento dos modelos será uma fase posterior e não deverá ser simulado ou apresentado como concluído nesta versão.



\---



\# 2. Visão geral do produto



O TestGap é uma ferramenta local de engenharia de dados para projetos de QA e inteligência artificial.



Seu propósito é permitir que uma pessoa construa manualmente um dataset de alta qualidade para ensinar e avaliar modelos que analisam:



1\. Requisitos de software.

2\. Código-fonte de uma aplicação.

3\. Suítes de testes criadas por IA ou por humanos.

4\. Lacunas reais de cobertura.

5\. Riscos não cobertos pelos testes existentes.

6\. Casos de teste adicionais que poderiam cobrir essas lacunas.



O sistema deve manter uma distinção rigorosa entre uma lacuna identificada, uma hipótese ainda não confirmada e um problema inexistente.



O TestGap não deverá presumir que todo requisito exige infinitos testes. O julgamento deve considerar os requisitos, as regras de negócio, os riscos e o escopo informado.



\## 2.1. Problema que o sistema pretende resolver



Suítes de testes geradas por IA podem conter:



\- Requisitos sem testes correspondentes.

\- Fluxos alternativos esquecidos.

\- Ausência de testes de valores-limite.

\- Casos de erro não contemplados.

\- Verificações de segurança insuficientes.

\- Asserts que não validam o comportamento esperado.

\- Testes duplicados ou redundantes.

\- Dependências entre testes.

\- Casos que passam mesmo quando o comportamento está incorreto.

\- Falta de cobertura de integrações e estados da aplicação.



O dataset deverá permitir treinar e avaliar modelos para detectar esses problemas, explicá-los e sugerir casos adicionais.



\## 2.2. O que não faz parte da versão 0.1



Não implementar nesta fase:



\- Treinamento de LLM dentro da interface.

\- Execução automática de código arbitrário fornecido pelo usuário.

\- Geração automática de rótulos aceitos sem revisão.

\- Integrações obrigatórias com OpenAI, Anthropic ou outros serviços pagos.

\- Sistema multiusuário ou autenticação.

\- Sincronização em nuvem.

\- Coleta automática de código de repositórios externos.

\- Afirmações de cobertura de código sem executar ferramentas de cobertura.

\- Avaliação automática considerada infalível.



A arquitetura deverá permitir adicionar esses recursos futuramente sem reescrever todo o núcleo.



\---



\# 3. Arquitetura técnica



\## 3.1. Tecnologias



\### Python



Linguagem principal para regras de negócio, persistência, validação, importação, exportação e ferramentas futuras de treinamento.



\### Streamlit



Responsável pela interface gráfica local, formulários, tabelas, filtros, páginas e visualizações.



\### SQLite



Banco de dados local, armazenado em arquivo no diretório de dados do projeto.



\### Pydantic



Responsável pela validação estrutural dos objetos de entrada e saída, incluindo importações e exportações.



\### pytest



Responsável pelos testes automatizados do projeto.



\### Pandas



Opcional, utilizado apenas quando facilitar a manipulação de tabelas ou relatórios. Não deve ser uma dependência obrigatória para operações que possam ser resolvidas com Python padrão.



\### JSONL



Formato principal de exportação do dataset. Cada linha deverá conter exatamente um registro JSON válido.



\### Git



Utilizado para controle de versão do código, migrações e documentação. Dados pessoais, código confidencial e grandes arquivos locais não devem ser publicados acidentalmente.



\## 3.2. Separação de responsabilidades



O projeto deverá manter quatro camadas:



\*\*Interface:\*\* recebe ações do usuário e apresenta resultados.



\*\*Serviços:\*\* implementam operações de negócio, validação e regras de curadoria.



\*\*Persistência:\*\* executa operações SQLite por meio de repositórios específicos.



\*\*Esquemas e dados:\*\* definem os modelos Pydantic, categorias, formatos de intercâmbio e versões do dataset.



A interface não deverá conter SQL espalhado pelas páginas. Toda operação persistente deverá passar pela camada de repositórios.



\## 3.3. Fluxo de dados



1\. O usuário cria um exemplo.

2\. O sistema valida os campos obrigatórios.

3\. O sistema salva o registro no SQLite.

4\. O usuário adiciona uma ou mais lacunas.

5\. O sistema verifica inconsistências estruturais.

6\. O usuário revisa e aprova ou rejeita o exemplo.

7\. O usuário executa a auditoria de qualidade.

8\. O sistema exporta os exemplos elegíveis para JSONL.

9\. Um pipeline posterior divide os dados por projeto e cria os conjuntos de treinamento, validação e teste.

10\. Os modelos são avaliados em dados reservados.



\---



\# 4. Estrutura obrigatória de diretórios



Crie uma estrutura semelhante à seguinte:



```text

testgap/

├── app.py

├── requirements.txt

├── requirements-dev.txt

├── pyproject.toml

├── .gitignore

├── .env.example

├── README.md

├── CHANGELOG.md

│

├── pages/

│   ├── 1\_Dataset.py

│   ├── 2\_Adicionar\_Exemplo.py

│   ├── 3\_Categorias.py

│   ├── 4\_Estatisticas.py

│   ├── 5\_Qualidade\_Dados.py

│   └── 6\_Configuracoes.py

│

├── testgap/

│   ├── \_\_init\_\_.py

│   ├── config.py

│   ├── database.py

│   ├── enums.py

│   ├── schemas.py

│   │

│   ├── repositories/

│   │   ├── \_\_init\_\_.py

│   │   ├── examples.py

│   │   ├── gaps.py

│   │   ├── categories.py

│   │   └── audit.py

│   │

│   ├── services/

│   │   ├── \_\_init\_\_.py

│   │   ├── example\_service.py

│   │   ├── gap\_service.py

│   │   ├── review\_service.py

│   │   ├── import\_service.py

│   │   ├── export\_service.py

│   │   ├── validation\_service.py

│   │   ├── quality\_service.py

│   │   └── statistics\_service.py

│   │

│   ├── ui/

│   │   ├── \_\_init\_\_.py

│   │   ├── components.py

│   │   └── styles.py

│   │

│   └── utils/

│       ├── \_\_init\_\_.py

│       ├── jsonl.py

│       ├── hashing.py

│       └── timestamps.py

│

├── schemas/

│   └── dataset-v1.schema.json

│

├── data/

│   ├── .gitkeep

│   ├── examples/

│   ├── exports/

│   └── backups/

│

├── scripts/

│   ├── init\_db.py

│   ├── seed\_demo\_data.py

│   ├── validate\_dataset.py

│   ├── export\_dataset.py

│   └── backup\_database.py

│

├── tests/

│   ├── conftest.py

│   ├── test\_database.py

│   ├── test\_examples.py

│   ├── test\_gaps.py

│   ├── test\_import.py

│   ├── test\_export.py

│   ├── test\_quality.py

│   └── test\_schemas.py

│

└── docs/

&#x20;   ├── ARCHITECTURE.md

&#x20;   ├── DATASET\_SCHEMA.md

&#x20;   ├── TAXONOMY.md

&#x20;   ├── DATA\_QUALITY.md

&#x20;   ├── MODEL\_EXPERIMENTS.md

&#x20;   └── ROADMAP.md

```



A estrutura pode ser ajustada se houver uma razão técnica real. Não crie arquivos vazios apenas para aparentar completude.



O diretório `data/` deve ser criado automaticamente caso não exista. O banco não deverá ficar dentro de diretórios temporários ou ser recriado a cada execução.



\---



\# 5. Banco de dados



Utilize SQLite com chaves estrangeiras habilitadas.



Crie uma tabela principal para exemplos, uma para lacunas, uma para categorias e tabelas auxiliares para auditoria e revisões.



Utilize transações para operações que alterem múltiplas tabelas.



\## 5.1. Tabela `examples`



Campos:



\- `id`: identificador interno inteiro.

\- `public\_id`: identificador legível e único, como `TG-000001`.

\- `title`: título curto do exemplo.

\- `project\_name`: nome do projeto ou aplicação.

\- `description`: contexto complementar.

\- `requirements\_text`: requisitos funcionais e não funcionais.

\- `source\_code`: código-fonte opcional.

\- `source\_language`: linguagem principal do código.

\- `test\_framework`: framework de testes, se conhecido.

\- `test\_suite\_text`: suíte original de testes.

\- `test\_format`: formato ou linguagem da suíte.

\- `expected\_behavior`: comportamento esperado.

\- `analysis\_scope`: escopo que deverá ser analisado.

\- `review\_status`: estado da revisão humana.

\- `split\_group`: identificador do grupo de projeto utilizado na divisão experimental.

\- `source\_type`: origem dos dados.

\- `source\_reference`: referência opcional à origem.

\- `dataset\_version`: versão do esquema.

\- `created\_at`: data de criação em UTC.

\- `updated\_at`: data da última atualização em UTC.

\- `content\_hash`: hash dos campos de conteúdo utilizados para detectar duplicatas exatas.



Restrições:



\- `public\_id` deve ser único.

\- Campos textuais obrigatórios não podem conter apenas espaços.

\- O texto integral do código não deve ser gravado nos logs.

\- `review\_status` deve aceitar somente valores previstos no enum.

\- `dataset\_version` deverá ser preenchida automaticamente.

\- `content\_hash` deverá ser recalculado quando os campos relevantes forem alterados.



\## 5.2. Tabela `gaps`



Cada exemplo poderá conter zero, uma ou várias lacunas.



Campos:



\- `id`: chave primária.

\- `example\_id`: referência ao exemplo.

\- `gap\_code`: identificador estável da lacuna.

\- `category\_id`: categoria da lacuna.

\- `title`: título curto.

\- `description`: descrição do comportamento não coberto.

\- `requirement\_reference`: requisito relacionado.

\- `evidence`: trecho ou explicação que sustenta a identificação.

\- `severity`: severidade.

\- `confidence`: confiança opcional, de 0 a 1.

\- `suggested\_test`: caso de teste proposto.

\- `expected\_result`: resultado esperado do teste.

\- `status`: estado da lacuna.

\- `review\_note`: observações do revisor.

\- `created\_at`: data de criação.

\- `updated\_at`: data de atualização.



Se não houver lacunas, não inventar uma lacuna fictícia. O resultado negativo será representado pela lista vazia, acompanhado da revisão do exemplo.



\## 5.3. Tabela `categories`



Criar categorias configuráveis, com identificador estável e descrição.



Categorias iniciais:



1\. `functional\_coverage`

2\. `boundary\_values`

3\. `security\_authorization`

4\. `integration\_state`

5\. `test\_quality`

6\. `performance\_reliability`

7\. `accessibility\_usability`

8\. `other`



Cada categoria deverá possuir:



\- ID.

\- Código único.

\- Nome em português.

\- Descrição.

\- Indicador de categoria ativa.

\- Data de criação.



Não permita que uma categoria seja removida se estiver sendo utilizada por registros. Permita desativá-la.



\## 5.4. Tabela `review\_history`



Armazene o histórico de revisões:



\- ID.

\- Exemplo relacionado.

\- Estado anterior.

\- Estado novo.

\- Observação da revisão.

\- Data da alteração.



A versão inicial não possui usuários autenticados. Portanto, não invente uma identidade de revisor. Utilize um campo opcional para identificar a origem da alteração, como `local\_ui` ou `import`.



\## 5.5. Tabela `audit\_results`



Registre resultados de auditorias de qualidade:



\- ID.

\- Data da auditoria.

\- Tipo de auditoria.

\- Quantidade de registros examinados.

\- Quantidade de erros.

\- Quantidade de avisos.

\- Relatório em JSON.

\- Versão das regras de auditoria.



As auditorias devem ser reproduzíveis e não alterar automaticamente os rótulos dos exemplos.



\## 5.6. Migrações



Implemente migrações versionadas do banco.



A inicialização normal deverá:



1\. Verificar a existência do banco.

2\. Criar o banco se não existir.

3\. Aplicar migrações pendentes.

4\. Criar índices e restrições.

5\. Preservar os registros existentes.



Não apague o banco para atualizar o esquema.



\---



\# 6. Modelo canônico do dataset



O SQLite é a fonte principal dos dados editáveis. O JSONL é o formato de intercâmbio e treinamento.



Utilize um esquema versionado, validado pelo Pydantic e documentado em `docs/DATASET\_SCHEMA.md`.



\## 6.1. Exemplo de registro canônico



```json

{

&#x20; "schema\_version": "1.0.0",

&#x20; "example\_id": "TG-000001",

&#x20; "project": {

&#x20;   "name": "Sistema de autenticação",

&#x20;   "language": "python",

&#x20;   "framework": "pytest"

&#x20; },

&#x20; "input": {

&#x20;   "requirements": "Após cinco tentativas de login inválidas, bloquear temporariamente a autenticação.",

&#x20;   "source\_code": "def authenticate(username, password): ...",

&#x20;   "test\_suite": "def test\_login\_invalid\_password(): ...",

&#x20;   "test\_format": "pytest",

&#x20;   "analysis\_scope": "autenticacao\_e\_bloqueio"

&#x20; },

&#x20; "expected\_output": {

&#x20;   "has\_gaps": true,

&#x20;   "gaps": \[

&#x20;     {

&#x20;       "category": "functional\_coverage",

&#x20;       "title": "Ausência de teste para limite de tentativas",

&#x20;       "description": "A suíte não verifica o bloqueio após cinco tentativas inválidas.",

&#x20;       "requirement\_reference": "REQ-AUTH-005",

&#x20;       "evidence": "O requisito exige bloqueio após cinco falhas, mas não existe caso correspondente na suíte.",

&#x20;       "severity": "high",

&#x20;       "suggested\_test": "Realizar cinco tentativas inválidas e verificar o bloqueio.",

&#x20;       "expected\_result": "O sistema bloqueia temporariamente novas tentativas conforme o requisito."

&#x20;     }

&#x20;   ]

&#x20; },

&#x20; "metadata": {

&#x20;   "source\_type": "human\_authored",

&#x20;   "review\_status": "approved",

&#x20;   "split\_group": "authentication\_project\_01",

&#x20;   "labels\_verified": true

&#x20; }

}

```



Esse é um exemplo didático. A implementação deverá usar exemplos coerentes e completos, sem apresentar o trecho abreviado de código como uma aplicação executável.



\## 6.2. Campos obrigatórios



Cada registro exportado deve conter:



\- Versão do esquema.

\- Identificador estável.

\- Contexto do projeto.

\- Requisitos.

\- Código-fonte, quando disponível.

\- Suíte de testes.

\- Formato da suíte.

\- Escopo da análise.

\- Rótulo `has\_gaps`.

\- Lista de lacunas.

\- Origem dos dados.

\- Estado de revisão.

\- Grupo de separação experimental.

\- Indicador de revisão dos rótulos.



O código-fonte poderá ser uma string vazia se estiver ausente. A ausência deverá ser explícita e não poderá ser interpretada como código analisado.



\## 6.3. Valores permitidos



\### `review\_status`



\- `pending`

\- `approved`

\- `rejected`

\- `needs\_revision`



\### `severity`



\- `critical`

\- `high`

\- `medium`

\- `low`

\- `informational`



\### `gap.status`



\- `proposed`

\- `confirmed`

\- `rejected`

\- `needs\_revision`



\### `source\_type`



\- `human\_authored`

\- `ai\_generated`

\- `mutation\_generated`

\- `public\_dataset`

\- `imported`

\- `synthetic`



A origem dos dados não deverá determinar se um exemplo é confiável. Um exemplo gerado por IA precisa ser revisado antes de ser tratado como referência validada.



\---



\# 7. Taxonomia de lacunas



A taxonomia deve ser documentada em `docs/TAXONOMY.md`.



\## 7.1. Cobertura funcional



Identifica regras de negócio e comportamentos obrigatórios que não possuem testes adequados.



Exemplos:



\- Fluxo principal não testado.

\- Fluxo alternativo ausente.

\- Regra de negócio ignorada.

\- Estado final não validado.

\- Requisito sem correspondência na suíte.



\## 7.2. Valores-limite



Identifica casos relacionados aos limites de entradas e condições.



Exemplos:



\- Zero.

\- Valores negativos.

\- Limite mínimo e máximo.

\- Valor imediatamente anterior e posterior ao limite.

\- Campos vazios.

\- Espaços em branco.

\- Entradas excessivamente longas.

\- Formatos inválidos.



\## 7.3. Segurança e autorização



Exemplos:



\- Acesso sem autenticação.

\- Usuário com permissão insuficiente.

\- Sessão expirada.

\- Token inválido.

\- Acesso a recursos de outro usuário.

\- Validação insuficiente de entradas.

\- Exposição indevida de dados.



A existência de uma lacuna deverá ser fundamentada no requisito, no código disponível e no escopo de segurança definido.



\## 7.4. Integração e estado



Exemplos:



\- Falha de banco de dados.

\- Timeout de serviço.

\- Resposta inesperada da API.

\- Requisição duplicada.

\- Estado inconsistente.

\- Operação parcialmente concluída.

\- Concorrência, quando relevante.



\## 7.5. Qualidade da suíte



Exemplos:



\- Assert ausente ou insuficiente.

\- Testes duplicados.

\- Dependência entre testes.

\- Dados compartilhados de forma insegura.

\- Teste que passa sem verificar o comportamento relevante.

\- Setup ou teardown incorreto.

\- Mock que esconde a falha que deveria ser detectada.



\## 7.6. Desempenho e confiabilidade



Exemplos:



\- Ausência de teste de timeout.

\- Falta de tratamento de indisponibilidade.

\- Ausência de teste de carga quando exigido.

\- Recursos não liberados.

\- Comportamento incorreto em condições de falha.



\## 7.7. Acessibilidade e usabilidade



Exemplos:



\- Mensagens de erro incompreensíveis.

\- Fluxos inacessíveis por teclado.

\- Rótulos de campos ausentes.

\- Estados de carregamento não validados.

\- Critérios de acessibilidade ignorados.



Não classifique um requisito como ausente se ele estiver fora do escopo estabelecido.



\## 7.8. Múltiplas categorias



Uma lacuna poderá receber mais de uma categoria somente quando isso representar aspectos distintos e justificáveis do problema.



Evite duplicar o mesmo problema para inflar a quantidade de rótulos.



\---



\# 8. Interface gráfica



O aplicativo deverá ter uma interface organizada, responsiva para desktop e com identidade visual consistente.



\## 8.1. Identidade visual



Nome exibido: `TestGap Dataset`.



Idioma: português brasileiro.



Estilo: painel de administração técnico, limpo e legível.



Elementos:



\- Navegação lateral.

\- Indicador de execução local.

\- Métricas principais.

\- Tabelas com paginação.

\- Formulários de cadastro.

\- Filtros.

\- Badges de status.

\- Mensagens de sucesso e erro.

\- Confirmação antes de ações destrutivas.

\- Feedback durante operações de importação e exportação.



A interface deverá ser utilizável sem conhecimento de SQL ou edição manual de JSON.



\## 8.2. Página inicial



Exibir:



\- Total de exemplos.

\- Exemplos aprovados.

\- Exemplos pendentes.

\- Exemplos rejeitados.

\- Exemplos com lacunas.

\- Exemplos sem lacunas.

\- Quantidade de lacunas por categoria.

\- Distribuição por severidade.

\- Alertas de qualidade.

\- Últimas alterações.



Todas as métricas devem ser calculadas a partir do banco real.



Se o banco estiver vazio, apresentar estado vazio com instruções para criar ou importar o primeiro exemplo. Não apresentar números fictícios.



\## 8.3. Página de dataset



Criar uma tabela pesquisável com:



\- ID.

\- Título.

\- Projeto.

\- Linguagem.

\- Framework.

\- Quantidade de lacunas.

\- Estado de revisão.

\- Origem.

\- Data de atualização.

\- Ações.



Filtros:



\- Texto livre.

\- Projeto.

\- Linguagem.

\- Framework.

\- Categoria.

\- Severidade.

\- Estado de revisão.

\- Origem dos dados.

\- Presença ou ausência de lacunas.



Permitir ordenar resultados e navegar por páginas.



A consulta deverá permanecer eficiente com milhares de registros.



Ações:



\- Abrir detalhes.

\- Editar.

\- Duplicar como novo rascunho.

\- Excluir mediante confirmação.

\- Marcar para revisão.



Não permitir que duplicar um exemplo preserve o mesmo ID público ou gere acidentalmente registros idênticos sem sinalização.



\## 8.4. Página de cadastro



Criar um formulário dividido em seções.



\### Seção A — Identificação



Campos:



\- Título.

\- Nome do projeto.

\- Descrição.

\- Linguagem principal.

\- Framework de testes.

\- Formato da suíte.



\### Seção B — Requisitos



Campo de texto multilinha para os requisitos.



Permitir que o usuário inclua identificadores como `REQ-001`, `REQ-002` e critérios de aceitação.



\### Seção C — Código-fonte



Campo de texto multilinha para o código.



Incluir um seletor de linguagem.



O código deverá ser armazenado como texto e não executado automaticamente.



\### Seção D — Suíte de testes



Campo de texto multilinha para a suíte original.



Permitir seleção do formato:



\- `pytest`

\- `unittest`

\- `playwright\_python`

\- `playwright\_typescript`

\- `jest`

\- `vitest`

\- `junit`

\- `testng`

\- `cypress`

\- `postman`

\- `newman`

\- `robot\_framework`

\- `gherkin`

\- `manual`

\- `other`



A lista poderá ser ampliada. Os identificadores devem permanecer estáveis.



\### Seção E — Escopo



Registrar quais partes do comportamento devem ser analisadas.



Exemplos:



\- Autenticação.

\- Autorização.

\- Cadastro.

\- Pagamentos.

\- Integrações.

\- Tratamento de erros.



\### Seção F — Rótulos esperados



Permitir marcar:



\- Existem lacunas.

\- Não existem lacunas relevantes no escopo analisado.

\- Análise inconclusiva.



O valor inconclusivo deverá ser representado por um estado de anotação, e não convertido automaticamente para `has\_gaps: false`.



\### Seção G — Metadados



Permitir informar origem dos dados, grupo do projeto e observações.



O sistema deverá validar os campos e exibir mensagens específicas para cada erro.



\## 8.5. Página de detalhes



Exibir o exemplo integralmente, com seções expansíveis:



\- Requisitos.

\- Código-fonte.

\- Suíte original.

\- Escopo.

\- Lacunas.

\- Casos de teste sugeridos.

\- Metadados.

\- Histórico de revisão.



Permitir editar lacunas individualmente.



Cada lacuna deverá ter:



\- Categoria.

\- Título.

\- Descrição.

\- Requisito relacionado.

\- Evidência.

\- Severidade.

\- Teste sugerido.

\- Resultado esperado.

\- Estado da revisão.



Uma lacuna rejeitada deverá continuar no histórico para auditoria, mas não poderá ser exportada como uma lacuna confirmada.



\## 8.6. Página de categorias



Exibir as categorias com:



\- Nome.

\- Código.

\- Descrição.

\- Quantidade de ocorrências.

\- Estado ativo ou inativo.



Permitir ativar e desativar categorias.



Não permitir códigos duplicados.



\## 8.7. Página de estatísticas



Criar gráficos com dados reais para:



\- Exemplos por categoria.

\- Lacunas por severidade.

\- Exemplos por framework.

\- Distribuição das origens.

\- Estado das revisões.

\- Exemplos com e sem lacunas.



Incluir totais numéricos para que as informações não dependam apenas de cores ou gráficos.



\## 8.8. Página de qualidade



Apresentar auditorias executáveis manualmente.



Exibir:



\- Quantidade de erros.

\- Quantidade de avisos.

\- Registros afetados.

\- Regra violada.

\- Explicação do problema.

\- Sugestão de correção.



O sistema não deverá alterar silenciosamente os registros para fazer a auditoria passar.



\## 8.9. Página de configurações



Permitir:



\- Consultar o caminho do banco.

\- Consultar a versão do esquema.

\- Ver a versão do aplicativo.

\- Exportar backup.

\- Definir preferências locais.

\- Consultar o diretório de exportação.



Não permitir que a alteração de um caminho apague o banco existente.



\---



\# 9. Validação e curadoria



Implemente validação em duas camadas.



\## 9.1. Validação estrutural



Verificar:



\- Campos obrigatórios.

\- Tipos corretos.

\- Valores de enums válidos.

\- Limites de confiança.

\- IDs únicos.

\- Referências válidas entre tabelas.

\- Datas válidas.

\- Strings não vazias nos campos obrigatórios.

\- Categorias existentes.

\- Versão do esquema compatível.



\## 9.2. Validação semântica



Verificar:



1\. Se uma lacuna contém descrição compreensível.

2\. Se existe relação com um requisito ou risco pertinente.

3\. Se a evidência sustenta a conclusão.

4\. Se o teste sugerido cobre a lacuna descrita.

5\. Se o resultado esperado é observável.

6\. Se o rótulo `has\_gaps` é coerente com as lacunas confirmadas.

7\. Se lacunas rejeitadas estão sendo excluídas da saída positiva.

8\. Se um exemplo sem lacunas passou por revisão adequada.

9\. Se o código-fonte está ausente e essa ausência limita a conclusão.

10\. Se existem duplicatas exatas ou possíveis duplicatas semânticas.



A validação semântica automatizada deverá produzir avisos para revisão humana, não substituir o julgamento de um especialista.



\## 9.3. Erros e avisos



Classifique os resultados em:



\- `error`: impede a exportação.

\- `warning`: requer atenção, mas pode permitir exportação dependendo da política.

\- `info`: observação não bloqueante.



Exemplos de erro:



\- JSON inválido.

\- Identificador duplicado.

\- Categoria inexistente.

\- Lacuna confirmada sem descrição.

\- Rótulo positivo sem nenhuma lacuna confirmada quando a política exige coerência estrita.



Exemplos de aviso:



\- Código-fonte ausente.

\- Exemplo com descrição muito curta.

\- Confiança não informada.

\- Possível duplicata semântica.

\- Pouca diversidade de categorias.

\- Exemplo aprovado sem revisão independente.



Não bloqueie um exemplo apenas porque sua descrição é curta sem avaliar se ela contém informação suficiente. Os critérios de comprimento devem ser configuráveis.



\---



\# 10. Revisão humana e confiabilidade dos rótulos



A qualidade dos rótulos é central para o sucesso do modelo.



Implemente o seguinte fluxo:



1\. Um exemplo é criado com estado `pending`.

2\. O usuário revisa os requisitos, o código e a suíte.

3\. O usuário adiciona lacunas e evidências.

4\. O usuário confirma ou rejeita cada lacuna.

5\. O usuário aprova ou rejeita o exemplo completo.

6\. O sistema registra a mudança de estado.

7\. O exemplo passa a ser elegível para exportação somente se cumprir a política de qualidade.



O aplicativo deverá distinguir a aprovação estrutural da aprovação semântica.



Um exemplo estruturalmente válido não é necessariamente verdadeiro.



Para exemplos importantes, permitir uma segunda revisão independente no futuro. A arquitetura deverá facilitar essa extensão.



Não considere a confiança subjetiva do anotador como probabilidade calibrada de acerto.



\---



\# 11. Importação de dados



Implemente importação de JSONL e CSV.



\## 11.1. JSONL



Para cada linha:



1\. Ler o conteúdo.

2\. Validar o JSON.

3\. Validar o esquema.

4\. Verificar a versão.

5\. Detectar campos desconhecidos conforme a política definida.

6\. Verificar duplicatas.

7\. Mostrar um resumo antes de confirmar.

8\. Permitir ao usuário cancelar.

9\. Executar a importação em transação.

10\. Registrar erros por número de linha.



Se uma linha for inválida, o sistema deverá informar o motivo sem encerrar silenciosamente todo o processamento.



A importação deverá permitir escolher entre:



\- Rejeitar o arquivo inteiro se houver erros.

\- Importar apenas registros válidos, exibindo explicitamente quais foram ignorados.



Nunca substituir silenciosamente um registro existente com o mesmo ID.



\## 11.2. CSV



O CSV deverá utilizar cabeçalhos documentados.



Como o formato CSV não representa naturalmente listas e objetos aninhados, defina uma estratégia de conversão explícita. Por exemplo, campos complexos poderão conter JSON válido dentro de uma célula.



O sistema deverá explicar o formato esperado e fornecer um arquivo de exemplo para download.



\---



\# 12. Exportação para treinamento



Implemente exportação para JSONL.



A exportação deverá ser reproduzível e apresentar um resumo antes da gravação.



\## 12.1. Modos de exportação



Criar dois modos.



\*\*Modo de curadoria:\*\* exporta os dados com metadados completos, incluindo estado da revisão, origem, histórico resumido e identificadores de projeto.



\*\*Modo de treinamento:\*\* exporta somente os campos definidos no contrato do dataset de treinamento, incluindo entradas e rótulos esperados.



Não misturar os formatos silenciosamente.



\## 12.2. Elegibilidade



Por padrão, somente exemplos aprovados e com rótulos revisados poderão entrar no conjunto de treinamento supervisionado.



Exemplos rejeitados, pendentes ou inconclusivos deverão ser excluídos, a menos que uma exportação diagnóstica os solicite explicitamente.



As lacunas rejeitadas não poderão aparecer como respostas positivas.



A ausência de lacunas deverá ser representada por uma lista vazia e `has\_gaps: false` apenas quando houver uma conclusão revisada de que não existem lacunas relevantes no escopo definido.



\## 12.3. Arquivos



Utilize nomes como:



\- `testgap\_curated\_20261026.jsonl`

\- `testgap\_training\_20261026.jsonl`

\- `testgap\_audit\_20261026.json`



A data deverá ser calculada na geração do arquivo.



Gravar os arquivos no diretório `data/exports/`.



Evitar sobrescrever arquivos sem aviso.



\## 12.4. Validação pós-exportação



Após gerar um JSONL:



\- Reabrir o arquivo.

\- Validar cada linha.

\- Conferir a quantidade de registros.

\- Conferir a quantidade de linhas.

\- Confirmar a ausência de JSON inválido.

\- Calcular um hash do arquivo.

\- Produzir um relatório de exportação.



Não informar que o arquivo foi validado se essa etapa não tiver sido executada.



\---



\# 13. Segurança e privacidade



Mesmo sendo um aplicativo local, os dados poderão conter código proprietário.



Requisitos:



\- Escutar somente em `127.0.0.1` por padrão.

\- Não expor a aplicação à rede local automaticamente.

\- Não executar código-fonte armazenado no dataset.

\- Não interpretar conteúdo de exemplos como comandos.

\- Não utilizar APIs externas na versão inicial.

\- Não registrar código completo em logs.

\- Não inserir segredos nos exemplos.

\- Não publicar o banco no Git.

\- Não publicar backups ou exports confidenciais.

\- Não utilizar `pickle` para importar dados não confiáveis.

\- Limitar tamanhos de arquivo e de campos para evitar consumo excessivo de memória.

\- Tratar erros sem exibir informações sensíveis do sistema.

\- Utilizar consultas SQL parametrizadas.

\- Não permitir que o usuário importe arquivos para caminhos arbitrários por meio de nomes de arquivo.



A importação de arquivos deverá usar seleção explícita do usuário e caminhos controlados pelo aplicativo.



\---



\# 14. Configuração local no Windows



O projeto deverá oferecer um processo de instalação simples.



\## 14.1. Arquivo `requirements.txt`



Declarar as dependências diretas necessárias à execução da interface e do núcleo.



Incluir, conforme necessário:



\- `streamlit`

\- `pydantic`



Outras bibliotecas deverão ser adicionadas somente se houver necessidade concreta.



\## 14.2. Arquivo `requirements-dev.txt`



Incluir as dependências de desenvolvimento:



\- `pytest`

\- `ruff`



Se houver bibliotecas adicionais para testes, justificá-las.



\## 14.3. Ambiente virtual



Documentar os comandos para PowerShell:



```powershell

py -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

pip install -r requirements-dev.txt

```



Se a política de execução do PowerShell impedir a ativação, documentar a alternativa de executar diretamente o Python do ambiente virtual, sem recomendar alterações globais desnecessárias nas políticas de segurança.



\## 14.4. Inicialização



Criar um comando documentado para inicializar o banco:



```powershell

python scripts/init\_db.py

```



Criar um comando para iniciar o aplicativo:



```powershell

python -m streamlit run app.py --server.address 127.0.0.1

```



O navegador deverá abrir ou exibir o endereço local de acesso.



\## 14.5. Scripts auxiliares



Criar scripts para:



\- Inicialização do banco.

\- Inserção opcional de exemplos demonstrativos.

\- Validação do dataset.

\- Exportação por linha de comando.

\- Backup do banco.



A inserção de dados demonstrativos deverá exigir uma ação explícita ou um comando específico. Não popular automaticamente o dataset de produção a cada inicialização.



\---



\# 15. Testes automatizados



Utilize pytest.



\## 15.1. Testes de banco



Verificar:



\- Criação do banco.

\- Aplicação das migrações.

\- Persistência após reconexão.

\- Integridade referencial.

\- IDs únicos.

\- Transações.

\- Recuperação após falhas.

\- Preservação dos dados em reinicializações.



\## 15.2. Testes de exemplos



Verificar:



\- Criação de exemplo válido.

\- Rejeição de campos obrigatórios vazios.

\- Edição.

\- Exclusão mediante serviço apropriado.

\- Duplicação com novo ID.

\- Atualização do hash.

\- Pesquisa e filtros.



\## 15.3. Testes de lacunas



Verificar:



\- Cadastro de lacunas.

\- Múltiplas lacunas por exemplo.

\- Categorias válidas.

\- Severidades válidas.

\- Estados de revisão.

\- Coerência entre rótulos e lacunas.

\- Exclusão de lacunas rejeitadas da exportação positiva.



\## 15.4. Testes de importação



Verificar:



\- JSONL válido.

\- JSON inválido.

\- Linha vazia.

\- Arquivo vazio.

\- Campos ausentes.

\- Tipos incorretos.

\- Versão incompatível.

\- Duplicatas.

\- Importação parcial.

\- Rollback em falhas transacionais.



\## 15.5. Testes de exportação



Verificar:



\- JSONL com múltiplas linhas.

\- Uma linha por registro.

\- JSON válido por linha.

\- Quantidade de registros correta.

\- Filtros de elegibilidade.

\- Exclusão de rótulos rejeitados.

\- Reprodutibilidade dos dados.

\- Hash do arquivo.

\- Validação após a gravação.



\## 15.6. Testes de qualidade



Criar exemplos deliberadamente inválidos e verificar se as regras de auditoria os identificam.



A auditoria deverá diferenciar erros bloqueantes de avisos.



\## 15.7. Testes de interface



Quando viável, utilizar `streamlit.testing.v1.AppTest` para verificar fluxos básicos.



Não afirmar que a interface foi testada manualmente no navegador se isso não aconteceu.



\---



\# 16. Documentação do projeto



Criar os seguintes documentos.



\## `README.md`



Deve conter:



\- Objetivo do projeto.

\- Funcionalidades.

\- Tecnologias.

\- Requisitos de instalação.

\- Instruções para Windows.

\- Como iniciar a aplicação.

\- Como executar testes.

\- Como cadastrar exemplos.

\- Como importar dados.

\- Como exportar JSONL.

\- Localização do banco.

\- Limitações conhecidas.

\- Estado atual da implementação.



\## `docs/ARCHITECTURE.md`



Explicar camadas, responsabilidades, fluxo de dados, dependências e decisões arquiteturais.



\## `docs/DATASET\_SCHEMA.md`



Documentar todos os campos do dataset, seus tipos, regras de validação, enums e exemplos.



\## `docs/TAXONOMY.md`



Explicar cada categoria de lacuna, seus limites e exemplos positivos e negativos.



\## `docs/DATA\_QUALITY.md`



Documentar regras de auditoria, severidades dos problemas e critérios de elegibilidade para exportação.



\## `docs/MODEL\_EXPERIMENTS.md`



Definir o protocolo futuro para comparar modelos.



\## `docs/ROADMAP.md`



Registrar as fases concluídas, pendentes, decisões e limitações.



\---



\# 17. Experimentos futuros de treinamento



A arquitetura deverá deixar o dataset preparado para uma fase posterior de ML.



O objetivo experimental será comparar:



\*\*Modelo A — treinamento do zero:\*\* pesos inicialmente aleatórios, tokenizer e vocabulário treinados de forma apropriada, seguido de treinamento com os dados disponíveis.



\*\*Modelo B — fine-tuning:\*\* modelo pré-treinado de licença compatível, especializado com exemplos supervisionados do TestGap.



Não confundir treinamento do zero com treinar um classificador simples. Se o experimento utilizar um Transformer com pesos aleatórios, deverá ser descrito como treinamento do modelo a partir de inicialização aleatória.



\## 17.1. Entradas comuns



Os dois modelos deverão receber a mesma representação lógica:



\- Requisitos.

\- Código-fonte, quando disponível.

\- Suíte de testes.

\- Escopo da análise.



A ausência de código deverá ser representada explicitamente.



\## 17.2. Saídas comuns



Os modelos deverão produzir uma estrutura validável contendo:



\- Existência ou ausência de lacunas relevantes.

\- Categoria de cada lacuna.

\- Descrição.

\- Requisito relacionado.

\- Evidência.

\- Severidade.

\- Teste sugerido.

\- Resultado esperado.



As saídas geradas deverão ser validadas antes de serem consideradas resultados.



\## 17.3. Separação experimental



A divisão deverá ocorrer por projeto, repositório ou grupo relacionado, evitando vazamento entre treino e teste.



Ajustes de hiperparâmetros deverão utilizar somente o conjunto de validação.



O conjunto de teste deverá permanecer reservado até a avaliação final.



Duplicatas e exemplos derivados do mesmo caso não poderão ser distribuídos indiscriminadamente entre os conjuntos.



\## 17.4. Métricas



Calcular:



\- Precisão.

\- Recall.

\- F1-score.

\- Falsos positivos.

\- Falsos negativos.

\- F1 por categoria.

\- Desempenho na identificação de ausência de lacunas.

\- Validade estrutural das respostas.

\- Qualidade dos casos de teste sugeridos, avaliada separadamente.



Não utilizar apenas acurácia, especialmente se as classes forem desbalanceadas.



A comparação deverá incluir uma linha de base simples e registrar as limitações de cada experimento.



\## 17.5. Recursos computacionais



O projeto deverá ser compatível com treinamento posterior em ambiente gratuito quando houver recursos disponíveis.



Não presumir que o computador local ou o Google Colab terá GPU disponível.



O treinamento integral de um modelo de linguagem com desempenho competitivo poderá exigir muito mais dados e computação do que o orçamento gratuito permite. O projeto deverá permitir experiências pequenas e registrar as limitações.



Nenhuma fase de treinamento deverá ser executada automaticamente durante a inicialização da aplicação.



\---



\# 18. Critérios de aceite da versão 0.1



A versão estará concluída quando os itens a seguir forem demonstrados.



\### Instalação e execução



\- \[ ] Instalação documentada no Windows.

\- \[ ] Aplicação inicializa localmente.

\- \[ ] Banco é criado automaticamente ou por comando documentado.

\- \[ ] Reiniciar a aplicação preserva os dados.

\- \[ ] A aplicação não exige API externa.



\### Gestão do dataset



\- \[ ] Criar exemplo.

\- \[ ] Editar exemplo.

\- \[ ] Consultar exemplo.

\- \[ ] Filtrar exemplos.

\- \[ ] Adicionar múltiplas lacunas.

\- \[ ] Revisar lacunas.

\- \[ ] Aprovar ou rejeitar exemplos.

\- \[ ] Registrar histórico de revisão.



\### Qualidade



\- \[ ] Validar estrutura dos registros.

\- \[ ] Detectar erros de enum.

\- \[ ] Detectar referências inválidas.

\- \[ ] Detectar inconsistências entre lacunas e rótulos.

\- \[ ] Apresentar erros e avisos.

\- \[ ] Preservar os dados durante a auditoria.



\### Importação e exportação



\- \[ ] Importar JSONL.

\- \[ ] Importar CSV.

\- \[ ] Exportar JSONL.

\- \[ ] Validar cada linha exportada.

\- \[ ] Exportar somente registros elegíveis no modo de treinamento.

\- \[ ] Gerar relatório de exportação.

\- \[ ] Evitar sobrescrita silenciosa.



\### Qualidade de software



\- \[ ] Testes automatizados implementados.

\- \[ ] Testes executados.

\- \[ ] Erros identificados corrigidos.

\- \[ ] README atualizado.

\- \[ ] Limitações registradas.

\- \[ ] Nenhum treinamento fictício apresentado como real.



\---



\# 19. Ordem de implementação



Implemente nesta ordem, sem tentar construir tudo simultaneamente.



\## Fase 1 — Fundação



1\. Inspecionar o ambiente.

2\. Criar a estrutura de diretórios.

3\. Criar os arquivos de dependências.

4\. Implementar configuração.

5\. Implementar banco SQLite.

6\. Implementar migrações.

7\. Implementar modelos Pydantic.

8\. Criar os testes iniciais.



Critério de saída: o banco inicializa e os modelos validam exemplos.



\## Fase 2 — Núcleo de dados



1\. Implementar repositório de exemplos.

2\. Implementar repositório de lacunas.

3\. Implementar categorias.

4\. Implementar serviços de criação e edição.

5\. Implementar estados de revisão.

6\. Implementar histórico.

7\. Criar testes de persistência e regras de negócio.



Critério de saída: o núcleo funciona independentemente da interface.



\## Fase 3 — Interface



1\. Criar a página inicial.

2\. Criar listagem do dataset.

3\. Criar cadastro.

4\. Criar edição e detalhes.

5\. Criar gestão de lacunas.

6\. Criar categorias.

7\. Criar estatísticas.

8\. Criar auditoria de qualidade.

9\. Criar configurações.



Critério de saída: todas as operações principais funcionam pelo navegador.



\## Fase 4 — Importação e exportação



1\. Implementar JSONL.

2\. Implementar CSV.

3\. Criar validação de importação.

4\. Criar pré-visualização.

5\. Implementar política de duplicatas.

6\. Implementar exportação de curadoria.

7\. Implementar exportação de treinamento.

8\. Validar os arquivos gerados.



Critério de saída: os dados podem sair e entrar no sistema sem perda silenciosa.



\## Fase 5 — Auditoria e estabilização



1\. Implementar todas as regras de qualidade.

2\. Executar os testes.

3\. Corrigir falhas.

4\. Verificar persistência.

5\. Testar arquivos inválidos.

6\. Verificar backups.

7\. Atualizar a documentação.

8\. Gerar um relatório final da implementação.



Critério de saída: todos os critérios de aceite estão verificados ou as pendências estão documentadas com clareza.



\## Fase 6 — Preparação para treinamento



Esta fase deverá ser preparada arquiteturalmente, mas não executada como treinamento na versão 0.1.



1\. Finalizar o contrato de exportação.

2\. Garantir identificadores de grupo para divisão dos dados.

3\. Registrar a origem e a revisão dos rótulos.

4\. Documentar o formato de entrada e saída do modelo.

5\. Definir como os resultados experimentais serão registrados.



\---



\# 20. Entrega final da IA CLI



Ao terminar a implementação, apresente um relatório com:



1\. Resumo do que foi implementado.

2\. Árvore de arquivos criada.

3\. Comandos para instalar e executar.

4\. Endereço local da aplicação.

5\. Localização real do banco SQLite.

6\. Comandos para executar os testes.

7\. Resultado real dos testes executados.

8\. Funcionalidades verificadas manualmente ou automaticamente, identificando qual método foi utilizado.

9\. Exemplo real de JSONL exportado.

10\. Limitações conhecidas.

11\. Problemas ainda pendentes.

12\. Próximo passo recomendado para iniciar o pipeline de treinamento.



Se algo não puder ser implementado, não esconda a limitação. Explique o motivo, o impacto e a alternativa proposta.



\*\*Prioridade máxima:\*\* construir uma base de dados confiável, revisável, auditável e reproduzível. O desempenho do modelo dependerá diretamente dessa qualidade.



Fim da especificação da versão 0.1.



