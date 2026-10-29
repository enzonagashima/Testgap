# TestGap Taxonomy of Test Gaps (Taxonomia de Lacunas)

This reference defines the taxonomy criteria for classifying test gaps in AI-generated and human-authored test suites.

---

## 1. Cobertura Funcional (`functional_coverage`)

- **Definição**: Requisitos explícitos de negócio, casos de uso principais ou fluxos alternativos descritos na especificação que não possuem nenhum caso de teste correspondente na suíte.
- **Critérios de Inclusão**:
  - Requisito funcional presente na documentação, mas ausente da suíte.
  - Regra de cálculo de impostos, juros ou descontos omitida.
  - Fluxo alternativo de cancelamento ou estorno não exercitado.
- **Critérios de Exclusão**:
  - Casos de erro que se enquadram em validação de limites ou segurança.

---

## 2. Valores-Limite (`boundary_values`)

- **Definição**: Ausência de testes para limites numéricos, extremos de intervalos, partições de equivalência, coleções vazias ou estouradas.
- **Critérios de Inclusão**:
  - Testes que validam valores intermediários (ex: 50), mas não testam os limites `0`, `1`, `99`, `100`, `101`.
  - Falta de testes para strings vazias, valores nulos (`None`/`null`), ou caracteres especiais.
  - Ausência de testes com listas com 0 itens, 1 item e limite máximo de itens.
- **Critérios de Exclusão**:
  - Falhas gerais de lógica de negócio que não dependem de valores de borda.

---

## 3. Segurança e Autorização (`security_authorization`)

- **Definição**: Falta de testes para autenticação, controle de permissões, vazamento de credenciais, injeção de código ou sanitização de entradas.
- **Critérios de Inclusão**:
  - Tentativa de acesso a rota protegida sem token ou com token expirado.
  - Acesso de usuário comum a recursos exclusivos de administrador (IDOR).
  - Ausência de testes de limite de tentativas de login (rate limiting / bloqueio por força bruta).
  - Verificação de que senhas ou chaves de API não aparecem em logs ou respostas.
- **Critérios de Exclusão**:
  - Problemas puramente funcionais sem impacto de segurança ou conformidade.

---

## 4. Integração e Estado (`integration_state`)

- **Definição**: Lacunas na verificação de efeitos colaterais em banco de dados, transições de máquina de estados, consistência transacional e concorrência.
- **Critérios de Inclusão**:
  - Teste valida retorno HTTP 200, mas não verifica se o registro foi realmente gravado no banco de dados.
  - Teste não valida rollback em caso de falha intermediária em transação.
  - Transições inválidas de status de pedido (ex: de 'cancelado' direto para 'entregue').
  - Problemas de concorrência ou condições de corrida (race conditions).
- **Critérios de Exclusão**:
  - Testes unitários puros isolados sem interação com estado persistente.

---

## 5. Qualidade da Suíte (`test_quality`)

- **Definição**: Testes presentes na suíte que sofrem de fragilidade técnica, asserts inexistentes ou fracos, dependência de ordem de execução ou mocks tautológicos.
- **Critérios de Inclusão**:
  - Teste que executa a função mas não contém asserções (`assert` ausente).
  - Asserção superficial (ex: apenas `assert response is not None`, sem validar o conteúdo).
  - Teste que passa mesmo quando o comportamento da aplicação é alterado (teste placebo).
  - Dependência entre testes (o Teste B só passa se o Teste A rodar antes).
  - Testes duplicados sem ganho de cobertura.
- **Critérios de Exclusão**:
  - Requisitos não testados (que devem ser `functional_coverage`).

---

## 6. Desempenho e Confiabilidade (`performance_reliability`)

- **Definição**: Ausência de validação de timeouts, tempo de resposta sob carga, tratamento de indisponibilidade de serviços externos e vazamento de memória.
- **Critérios de Inclusão**:
  - Falta de teste para timeout em chamadas de API externa.
  - Falta de teste para política de retry com backoff exponencial.
  - Ausência de validação de liberação de conexões de pool de banco ou descritores de arquivo.
- **Critérios de Exclusão**:
  - Benchmarks de carga pesada fora do escopo de testes automatizados da aplicação.

---

## 7. Acessibilidade e Usabilidade (`accessibility_usability`)

- **Definição**: Falta de testes para mensagens claras de erro ao usuário, requisitos de acessibilidade (ARIA, contraste, teclado) ou internacionalização.
- **Critérios de Inclusão**:
  - Validação de mensagens de erro humanizadas ao invés de mensagens genéricas ou rastros de pilha (`stack traces`).
  - Navegação por teclado em componentes interativos.
- **Critérios de Exclusão**:
  - Preferências estéticas puras de design sem especificação formal.

---

## 8. Outro (`other`)

- **Definição**: Lacunas reais identificadas que não se enquadram perfeitamente em nenhuma das 7 categorias anteriores. Deve ser acompanhada de justificativa na descrição da lacuna.
