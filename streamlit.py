import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
from io import BytesIO
from limpeza_de_dados import limpeza_dados
from join_bases import join
from comparacao_de_colunas import col_check
from create_monitoring_card import create_monitoring_card

favicon_url = "assets/favicon.ico"
imagem_url = 'assets/logo.png'

st.set_page_config( page_icon=favicon_url)
st.title('Comparação de dados das bases ADP e Workday')

# Carregar bases de dados
st.sidebar.header("Carregar Bases de Dados")
file1 = st.sidebar.file_uploader("Selecione a primeira base de dados Workday (Excel)", type=["xlsx"])
file2 = st.sidebar.file_uploader("Selecione a segunda base de dados ADP (Excel)",  type=[ "xlsx"])
# Verificar se as bases de dados foram carregadas

if file1 and file2:
    if file1.name == "Workday.xlsx" and file2.name == "ADP.xlsx":

        # Leitura, limpeza e join
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        df1_cleaned = limpeza_dados(df1, "workday")
        df2_cleaned = limpeza_dados(df2, "adp")

        merged_df = join(df1_cleaned, df2_cleaned)
        check_df = col_check(merged_df)

        check_columns = [col for col in check_df.columns if col.endswith('_check')]
        check_df_cols = check_df[check_columns]
        # st.header("Base de dados integrada")
        # Panorama geral base integrada
        st.write("### Pânorama geral da base de dados integrada")
        st.write("##### Aqui é possível visualizar a base de dado que junta as informações dos dois sistemas, filtrar pelos campos de interesse e baixar os dados filtrados.")
        check_df['Irregularidade presente'] = check_df.apply(lambda row: any(row[col] == False for col in check_columns), axis=1)
        filtrar_apenas_com_falso = st.checkbox("Mostrar apenas colaboradores com irregularidades?", key = "1")
        if filtrar_apenas_com_falso:
            filtro_false = check_df[check_df['Irregularidade presente']]
        else:
            filtro_false = check_df

        opcoes = ["Gênero", "Raça/Etnia", "Estado Civil", "Data de Nascimento", "Data de Admissão"]
        selecionados = st.multiselect("Selecione as opções:", opcoes, default=opcoes)
        column_mapping2 = {
        'Gênero': 'genero',
        'Raça/Etnia': 'raca_etnia',
        'Estado Civil': 'estado_civil',
        'Data de Nascimento': 'data_nascimento',
        'Data de Admissão': 'data_admissao'
        }
        # Filtrar a base para mostrar as colunas selecionadas
        colunas_selecionadas = ['id_nacional', 'id_internacional', 'Irregularidade presente']

        for opcao in selecionados:
            coluna_adp = f"{column_mapping2[opcao]}_adp"
            coluna_workday = f"{column_mapping2[opcao]}_workday"
            colunas_selecionadas.extend([coluna_adp, coluna_workday])

        df_select= filtro_false[colunas_selecionadas]
        colunas_skip = ['id_nacional', 'id_internacional', 'Irregularidade presente','Tipo de Admissão', 'Data de Desligamento', 'Modo Ponto', 'work_country', 'genero_check', 'raca_etnia_check', 'estado_civil_check', 'data_nascimento_check', 'data_admissao_check']

        ordenar = ['id_nacional','id_internacional', 'Irregularidade presente'] + [col for col in filtro_false.columns if col not in colunas_skip]
        df_select = df_select[ordenar]
        filter_id_nacional = st.text_input("Filtrar por ID Nacional")
        filter_id_internacional = st.text_input("Filtrar por ID Internacional")
        filtered_df = df_select
        if filter_id_nacional:
            filtered_df = filtered_df[filtered_df['id_nacional'].astype(str).str.contains(filter_id_nacional, case=False)]
        if filter_id_internacional:
            filtered_df = filtered_df[filtered_df['id_internacional'].astype(str).str.contains(filter_id_internacional, case=False)]

        st.dataframe(filtered_df)
        # Botão de download
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, sheet_name='Sheet1', index=False)
        excel_buffer.seek(0)
        st.download_button(
        label="Download Arquivo Excel",
        data=excel_buffer,
        file_name="base_ADP_Workday.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )



        st.write("## Panorama geral das irregularidades:")
        st.write("##### Aqui estão os detalhes sobre as irregularidades e dados corretos")
       
        # Apresentar irregularidades por coluna
        column_mapping = {
            'check_genero': 'Gênero',
            'check_raca': 'Raça/Etnia',
            'check_estado_civil': 'Estado Civil',
            'check_data_nascimento': 'Data de Nascimento',
            'check_data_admissao': 'Data de Admissão'
        }
        

        total_records =  check_df.shape[0]

        false_counts = check_df_cols.apply(lambda col: col.value_counts().get(False, 0))
        
        
        card_data = [
            [ "Sem ID internacional (ADP)", 5],
            [ "Sem ID nacional (ADP)", 6],
            [ "Sem ID internacional (WDAY)", 5],
            [ "Sem ID nacional (WDAY)", 6],
            # IDS NACIONAL E INTERNACIONAL JUNTOS PARA COMPARAR DUPLCIADAS
            [ "Linhas duplicadas (ADP)", 6],
            [ "Linhas duplicadas (WDAY)", 6],
        ]

        


        for i, (column, count) in enumerate(false_counts.items(), start=1):
            column_name = list(column_mapping.values())[i - 1]
            card_data.append((column_name, count))
            # card_data.append((f"Irregularidade {column_name}", count))

        
        card_data.sort(key=lambda x: x[1], reverse=True)

        col1, col2 = st.columns(2)
        for i, (title, irregularities) in enumerate(card_data, start=1):
            with col1 if i <= len(card_data) // 2 else col2:
                create_monitoring_card(title, irregularities, total_records)
        
        work_from_brazil = df1_cleaned['work_country'].value_counts()['Brazil']
        if work_from_brazil > total_records:
            with col1:
                st.info(f'#### A base Workday possui {work_from_brazil} colaboradores com "Brazil" na coluna "work country" e a base ADP possui {total_records} colaboradores. Diferença de {work_from_brazil - total_records}')
        elif total_records > work_from_brazil:
            with col2:
                st.info(f'#### A base ADP possui {total_records} colaboradores com "Brazil" na coluna "work country" e a base Workday possui {work_from_brazil} colaboradores. Diferença de {total_records - work_from_brazil}')
    

        # Apresentar irregularidades de valores nulos
        valores_especiais = ["nan", "null", np.nan, "",  pd.NaT]
        contagem_especiais_por_coluna = merged_df.apply(lambda col: col.isin(valores_especiais).sum())
       
        # Criação da tabela com contagem de valores nulos
        table = pd.DataFrame(contagem_especiais_por_coluna, columns=['Contagem'])


        # Filtrar apenas as linhas com contagem diferente de zero
        table_filtrada = table[table['Contagem'] != 0]


        st.write("##### Valores nulos:")

        # Mostrar tabela filtrada
        st.table(table_filtrada)

       


        

    else:
        st.warning("Por favor, carregue os arquivos com os nomes corretos.")

else:
    st.warning("Por favor, carregue as bases de dados.")

