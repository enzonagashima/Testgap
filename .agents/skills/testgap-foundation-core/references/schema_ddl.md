# TestGap SQLite DDL Reference

This document provides the standard DDL schema for SQLite database tables in TestGap.

```sql
PRAGMA foreign_keys = ON;

-- 1. Schema Migrations Tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

-- 2. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

-- Default categories seed
INSERT OR IGNORE INTO categories (code, name, description, is_active, created_at) VALUES
('functional_coverage', 'Cobertura Funcional', 'Requisitos de negócio, fluxos principais e alternativos sem testes correspondentes.', 1, datetime('now')),
('boundary_values', 'Valores-Limite', 'Valores de borda, partições de equivalência, transições de faixa e casos extremos.', 1, datetime('now')),
('security_authorization', 'Segurança e Autorização', 'Autenticação, controle de acesso, injeção, permissões e vazamento de dados.', 1, datetime('now')),
('integration_state', 'Integração e Estado', 'Interação entre módulos, persistência, concorrência e transições de ciclo de vida.', 1, datetime('now')),
('test_quality', 'Qualidade da Suíte', 'Asserts fracos, dependências entre testes, testes duplicados ou comportamento frágil.', 1, datetime('now')),
('performance_reliability', 'Desempenho e Confiabilidade', 'Prazos de resposta, timeout, consumo de memória, recuperação de falhas e resiliência.', 1, datetime('now')),
('accessibility_usability', 'Acessibilidade e Usabilidade', 'Diretrizes WCAG, feedback de erro ao usuário e legibilidade da interface.', 1, datetime('now')),
('other', 'Outro', 'Casos atípicos ou lacunas específicas que não se enquadram nas categorias acima.', 1, datetime('now'));

-- 3. Examples Table
CREATE TABLE IF NOT EXISTS examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    public_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    project_name TEXT NOT NULL,
    description TEXT DEFAULT '',
    requirements_text TEXT NOT NULL,
    source_code TEXT DEFAULT '',
    source_language TEXT DEFAULT 'python',
    test_framework TEXT DEFAULT 'pytest',
    test_suite_text TEXT NOT NULL,
    test_format TEXT DEFAULT 'pytest',
    expected_behavior TEXT DEFAULT '',
    analysis_scope TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'pending',
    split_group TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'human_authored',
    source_reference TEXT DEFAULT '',
    dataset_version TEXT NOT NULL DEFAULT '1.0.0',
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (length(trim(title)) > 0),
    CHECK (length(trim(project_name)) > 0),
    CHECK (length(trim(requirements_text)) > 0),
    CHECK (length(trim(test_suite_text)) > 0),
    CHECK (review_status IN ('pending', 'approved', 'rejected', 'needs_revision')),
    CHECK (source_type IN ('human_authored', 'ai_generated', 'mutation_generated', 'public_dataset', 'imported', 'synthetic'))
);

CREATE INDEX IF NOT EXISTS idx_examples_public_id ON examples (public_id);
CREATE INDEX IF NOT EXISTS idx_examples_project_name ON examples (project_name);
CREATE INDEX IF NOT EXISTS idx_examples_review_status ON examples (review_status);
CREATE INDEX IF NOT EXISTS idx_examples_split_group ON examples (split_group);
CREATE INDEX IF NOT EXISTS idx_examples_content_hash ON examples (content_hash);

-- 4. Gaps Table
CREATE TABLE IF NOT EXISTS gaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    example_id INTEGER NOT NULL,
    gap_code TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    requirement_reference TEXT DEFAULT '',
    evidence TEXT DEFAULT '',
    severity TEXT NOT NULL DEFAULT 'medium',
    confidence REAL DEFAULT 1.0,
    suggested_test TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'confirmed',
    review_note TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (example_id) REFERENCES examples (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id),
    CHECK (length(trim(title)) > 0),
    CHECK (length(trim(description)) > 0),
    CHECK (severity IN ('critical', 'high', 'medium', 'low', 'informational')),
    CHECK (status IN ('proposed', 'confirmed', 'rejected', 'needs_revision')),
    CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX IF NOT EXISTS idx_gaps_example_id ON gaps (example_id);
CREATE INDEX IF NOT EXISTS idx_gaps_category_id ON gaps (category_id);
CREATE INDEX IF NOT EXISTS idx_gaps_severity ON gaps (severity);
CREATE INDEX IF NOT EXISTS idx_gaps_status ON gaps (status);

-- 5. Review History Table
CREATE TABLE IF NOT EXISTS review_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    example_id INTEGER NOT NULL,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    review_note TEXT DEFAULT '',
    changed_by TEXT NOT NULL DEFAULT 'local_ui',
    created_at TEXT NOT NULL,
    FOREIGN KEY (example_id) REFERENCES examples (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_review_history_example ON review_history (example_id);

-- 6. Audit Results Table
CREATE TABLE IF NOT EXISTS audit_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_date TEXT NOT NULL,
    audit_type TEXT NOT NULL,
    total_examined INTEGER NOT NULL,
    total_errors INTEGER NOT NULL,
    total_warnings INTEGER NOT NULL,
    report_json TEXT NOT NULL,
    rules_version TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_results_date ON audit_results (audit_date);
```
