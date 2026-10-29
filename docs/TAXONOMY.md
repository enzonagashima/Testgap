# Taxonomia de Lacunas de Testes

O TestGap organiza lacunas em 8 categorias essenciais:

1. **`functional_coverage` (Cobertura Funcional)**: Requisitos de negócio explícitos, fluxos principais ou alternativos sem testes correspondentes.
2. **`boundary_values` (Valores-Limite)**: Falta de testes para valores de fronteira (off-by-one, mínimos, máximos, coleções vazias).
3. **`security_authorization` (Segurança e Autorização)**: Autenticação, autorização, IDOR, injeção, força bruta ou vazamento de segredos.
4. **`integration_state` (Integração e Estado)**: Transições de máquinas de estado, efeito colateral em banco de dados, transações ACID e concorrência.
5. **`test_quality` (Qualidade da Suíte)**: Asserts fracos ou ausentes, testes frágeis, ordem de dependência entre testes ou testes placebo.
6. **`performance_reliability` (Desempenho e Confiabilidade)**: Falta de teste para timeouts, quedas de conexão de rede, retry logic e consumo de memória.
7. **`accessibility_usability` (Acessibilidade e Usabilidade)**: Mensagens de erro orientadas ao usuário, acessibilidade (WCAG) e internacionalização.
8. **`other` (Outro)**: Lacunas atípicas com justificativa específica documentada.
