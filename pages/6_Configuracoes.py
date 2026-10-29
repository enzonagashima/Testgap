"""System configuration, database maintenance, import, and export."""
import streamlit as st
import shutil
from pathlib import Path
from datetime import datetime, timezone

from testgap.config import DB_PATH, BACKUP_DIR, EXPORT_DIR
from testgap.database import default_db
from testgap.services.export_service import ExportService
from testgap.services.import_service import ImportService
from testgap.ui.styles import apply_custom_styles
from testgap.ui.components import render_header

st.set_page_config(page_title="TestGap — Configurações", page_icon="⚙️", layout="wide")
apply_custom_styles()

export_service = ExportService()
import_service = ImportService()

render_header("Configurações e Manutenção", "Gerenciamento de banco de dados, backups, importação e exportação de dados")

tab_db, tab_exp, tab_imp = st.tabs(["🗄️ Banco de Dados & Backups", "📤 Exportação para IA", "📥 Ingestão de Dados"])

with tab_db:
    st.subheader("Informações de Armazenamento SQLite")
    db_file = Path(DB_PATH)
    file_size_kb = db_file.stat().st_size / 1024 if db_file.exists() else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Caminho do Banco", db_file.name)
    c2.metric("Tamanho em Disco", f"{file_size_kb:.1f} KB")
    c3.metric("Modo de Concorrência", "WAL")

    st.caption(f"Caminho absoluto: `{db_file.resolve()}`")

    st.divider()

    st.subheader("Cópias de Segurança (Backup)")
    if st.button("💾 Criar Cópia de Segurança Agora", type="primary"):
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dest_file = BACKUP_DIR / f"testgap_backup_{ts}.db"
        shutil.copy2(db_file, dest_file)
        st.success(f"Cópia de segurança criada com sucesso em:\n`{dest_file.resolve()}`")

    # List existing backups
    backups = list(BACKUP_DIR.glob("*.db"))
    if backups:
        st.write(f"**Backups existentes ({len(backups)}):**")
        for b in sorted(backups, reverse=True)[:5]:
            st.code(f"{b.name} ({b.stat().st_size / 1024:.1f} KB)")

with tab_exp:
    st.subheader("Exportar Dataset para Treinamento de IA")
    st.markdown(
        "Os datasets exportados seguem o esquema canônico `schemas/dataset-v1.schema.json` "
        "e são particionados por `split_group` para prevenir contaminação (data leakage)."
    )

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        only_approved = st.checkbox("Exportar apenas registros com status 'approved'", value=True)
    with col_e2:
        split_partition = st.checkbox("Particionar em treino / validação / teste", value=True)

    if st.button("🚀 Iniciar Exportação", type="primary"):
        with st.spinner("Exportando e validando conformidade com JSON Schema..."):
            if split_partition:
                results = export_service.export_for_training(only_approved=only_approved)
                st.success("Exportação particionada concluída!")
                for split_name, info in results.items():
                    st.write(f"• **{split_name}.jsonl**: {info['count']} registros gravados em `{info['file']}`")
            else:
                out_file = EXPORT_DIR / "dataset_full.jsonl"
                count, path = export_service.export_dataset(out_file, only_approved=only_approved)
                st.success(f"Exportados {count} registros para `{path}`!")

with tab_imp:
    st.subheader("Importação de Dados (JSONL ou CSV)")
    uploaded_file = st.file_uploader("Selecione um arquivo .jsonl ou .csv", type=["jsonl", "csv"])

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        content = uploaded_file.getvalue().decode("utf-8")

        # Save to temp location for streaming inspection
        temp_import_path = EXPORT_DIR / f"temp_{uploaded_file.name}"
        temp_import_path.write_text(content, encoding="utf-8")

        if file_ext == "jsonl":
            preview = import_service.preview_jsonl(temp_import_path)
            st.write(f"**Total de linhas:** {preview['total_lines']} | **Válidas:** {preview['valid_count']} | **Erros:** {preview['error_count']} | **Duplicatas:** {preview['duplicate_count']}")

            if preview["error_count"] > 0:
                st.warning("Foram encontrados erros de sintaxe ou conformidade:")
                st.json(preview["errors"])

            dup_policy = st.selectbox("Política para Registros com Hash Duplicado:", options=["skip", "error"])
            if st.button("Confirmar Importação de Registros Válidos", type="primary"):
                res = import_service.import_jsonl(temp_import_path, duplicate_policy=dup_policy)
                st.success(f"Importados: {res['imported_count']} | Ignorados: {res['skipped_count']}")
                temp_import_path.unlink(missing_ok=True)
                st.rerun()

        elif file_ext == "csv":
            if st.button("Confirmar Importação CSV", type="primary"):
                res = import_service.import_csv(temp_import_path)
                st.success(f"Importados: {res['imported_count']} | Ignorados: {res['skipped_count']}")
                temp_import_path.unlink(missing_ok=True)
                st.rerun()
