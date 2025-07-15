# Para rodar o app:
# streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import os
from sqlalchemy.orm import Session
from utils.parser import parse_postman_json
from db.models import Benchmark, BenchmarkResult, BenchmarkTime, init_db
from db.database import get_db
from db.enums import Semaphore
from utils.report_wkhtmltopdf import generate_pdf

TIME_OK = 5
TIME_WARNING = (5, 10)

db: Session = next(get_db())
benchmarks = db.query(Benchmark).all()

# Função de modal para exclusão de teste
@st.dialog("Painel de confirmação de exclusão")
def confirmDeleteDialog(object, description = "Tem certeza que deseja excluir este item?"):
    st.write(description)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sim", type="primary"):
            db.delete(object)
            db.commit()
            st.success(f"Teste '{object.test_name}' deletado com sucesso!")
            st.rerun()
    with col2:
        if st.button("Não"):
            st.rerun()

# Função de modal para exclusão de teste
@st.dialog("Painel de edição")
def editDialog(object, description = "Edição de nome de teste"):
    st.write(description)

    test_name_edited = st.text_input("Nome do teste:", value=object.test_name)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar", type="primary"):
            object.test_name = test_name_edited
            db.commit()
            st.success(f"Teste '{object.test_name}' deletado com sucesso!")
            st.rerun()
    with col2:
        if st.button("Cancelar"):
            st.rerun()

def build_metrics_dataframe(benchmark, include_semaphore=True):
    rows = []
    for result in benchmark.results:
        for t in result.times:
            rows.append({
                "Requisição": result.request_name,
                "Tempo (segundos)": round(t.time / 1000, 2)
            })

    if not rows:
        return None

    df = pd.DataFrame(rows)
    metrics = df.groupby(["Requisição"])["Tempo (segundos)"].agg(["mean", "min", "max", "count"]).reset_index()
    metrics = metrics.rename(columns={
        "mean": "Tempo médio",
        "min": "Tempo mínimo",
        "max": "Tempo máximo",
        "count": "Qtd. Requisições"
    })

    # Arredondamento para 2 casas
    for col in ["Tempo médio", "Tempo mínimo", "Tempo máximo"]:
        metrics[col] = metrics[col].round(2)

    # Adiciona coluna de semáforo
    conditions = [
        metrics["Tempo médio"] <= TIME_OK,
        (metrics["Tempo médio"] > TIME_WARNING[0]) & (metrics["Tempo médio"] <= TIME_WARNING[1]),
        metrics["Tempo médio"] > TIME_WARNING[1]
    ]

    if include_semaphore:
        values = [
            Semaphore.OK.value,
            Semaphore.WARNING.value,
            Semaphore.CRITICAL.value
        ]
    else:
        values = ["OK", "ATENÇÃO", "CRÍTICO"]
    
    metrics["Semáforo"] = np.select(conditions, values, default=Semaphore.CRITICAL)

    return metrics

# Função para retornar dados de benchmark
def get_benchmark_data():
    benchmark_data = []
    for b in benchmarks:
        metrics = build_metrics_dataframe(b, include_semaphore=False)
        if metrics is not None:
            benchmark_data.append({
                "nome": b.test_name,
                "df": metrics
            })
    return benchmark_data

st.set_page_config(page_title="Benchmark da API", layout="wide")

init_db()

st.title("🧪 Benchmark de Performance da API")

# Importar JSON
st.header("1️⃣ Enviar JSON de Teste")
test_name = st.text_input("Nome do teste (ex: Teste em dev)")
uploaded_file = st.file_uploader("Selecione o arquivo JSON exportado do Postman", type=["json"])

submit = st.button("📤 Importar JSON")

if submit and uploaded_file and test_name:
    db: Session = next(get_db())

    # Verifica se o nome do teste já existe
    existing_test = db.query(Benchmark).filter_by(test_name=test_name).first()
    if existing_test:
        st.warning("❌ Já existe um teste com esse nome. Escolha outro nome único.")
    else:
        try:
            parsed_results = parse_postman_json(uploaded_file)

            benchmark = Benchmark(test_name=test_name)
            db.add(benchmark)
            db.flush()

            for request_name, times in parsed_results:
                result = BenchmarkResult(request_name=request_name, benchmark_id=benchmark.id)
                db.add(result)
                db.flush()

                for t in times:
                    bt = BenchmarkTime(time=t, benchmark_result_id=result.id)
                    db.add(bt)

            db.commit()
            st.success("✅ Teste armazenado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao processar JSON: {e}")

# Métricas por requisição
st.divider()
st.header("📊 Métricas por Requisição")

if benchmarks:
    for b in benchmarks:
        metrics = build_metrics_dataframe(b)

        if metrics is not None:
            with st.expander(f"🧪 {b.test_name}"):
                st.dataframe(metrics, use_container_width=True)

                if st.button("❌ Deletar teste", key=f"delete_{b.id}"):
                    confirmDeleteDialog(b)
                
                if st.button("🖋️ Editar teste", key=f"edit_{b.id}"):
                    editDialog(b)
else:
    st.info("Nenhum dado armazenado ainda.")

# Comparativo entre testes
st.divider()
st.header("📊 Comparativo entre testes (Tempo Médio por Requisição)")

comparative_rows = []
for b in benchmarks:
    for result in b.results:
        tempos = [t.time for t in result.times]
        if tempos:
            avg_time = sum(tempos) / len(tempos)
            comparative_rows.append({
                "Requisição": result.request_name,
                "Teste": b.test_name,
                "Tempo médio (segundos)": round(avg_time / 1000, 2)
            })

if comparative_rows:
    df_comparativo = pd.DataFrame(comparative_rows)
    df_pivot = df_comparativo.pivot_table(index="Requisição", columns="Teste", values="Tempo médio (segundos)")

    mean_by_test = df_pivot.mean().sort_values()
    df_pivot = df_pivot[mean_by_test.index]

    st.dataframe(df_pivot, use_container_width=True)
else:
    st.info("Ainda não há dados suficientes para comparação.")

# Relatório em PDF
if st.button("📄 Gerar relatório em PDF"):
    benchmark_data = get_benchmark_data()
    pdf_path = generate_pdf(benchmark_data, df_pivot)

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 Baixar relatório PDF",
            data=f,
            file_name="relatorio.pdf",
            mime="application/pdf"
        )
    
    # Remove o arquivo temporário
    os.remove(pdf_path)