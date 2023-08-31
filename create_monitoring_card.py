import streamlit as st
def create_monitoring_card(title, irregularities, total_records):
        st.write(f"#### {title}")
        st.write("Quantidade de Irregularidades:", irregularities)
        st.write("Quantidade de Dados Corretos:", total_records - irregularities)
        st.write("Porcentagem de Irregularidades:", round((irregularities / total_records) * 100, 2), "%")
        st.progress(1 - irregularities / total_records)
