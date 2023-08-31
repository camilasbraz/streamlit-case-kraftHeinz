import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
from io import BytesIO
from functions import *

# URLs para ícone da página e imagem
favicon_url = "assets/favicon.ico"
imagem_url = 'assets/logo.png'

# Configuração da página
st.set_page_config(page_icon=favicon_url)

# Título e imagem
col1, col2 = st.columns([1, 3])  # Distribuição de largura das colunas
# Coluna 1 (imagem)
with col1:
    st.image(imagem_url)
# Coluna 2 (título)
with col2:
    st.title("Comparação de dados das bases ADP e Workday")


# Carregar bases de dados através da barra lateral
st.sidebar.header("Carregar Bases de Dados")
file1 = st.sidebar.file_uploader("Selecione a primeira base de dados Workday (Excel)", type=["xlsx"])
file2 = st.sidebar.file_uploader("Selecione a segunda base de dados ADP (Excel)", type=["xlsx"])

# Verificar se as bases de dados foram carregadas
if file1 and file2:
    if file1.name == "Workday.xlsx" and file2.name == "ADP.xlsx":
        # Leitura, limpeza e join
        df1 = pd.read_excel(file1, engine='openpyxl')
        df2 = pd.read_excel(file2, engine='openpyxl')
        df1_cleaned = limpeza_dados(df1, "workday")
        df2_cleaned = limpeza_dados(df2, "adp")
        merged_df = join(df1_cleaned, df2_cleaned)
        check_df = col_check(merged_df)
        check_columns = [col for col in check_df.columns if col.endswith('_check')]



        # Exibir panorama geral da base integrada
        st.write("### Pânorama geral da base de dados integrada")
        st.write("##### Aqui é possível visualizar a base de dado que junta as informações dos dois sistemas, filtrar pelos campos de interesse e baixar os dados filtrados.")
        # Verificar irregularidades nas colunas e criar coluna 'Irregularidade presente'
        check_df['Irregularidade presente'] = check_df.apply(lambda row: any(row[col] == False for col in check_columns), axis=1)
        filtrar_apenas_com_falso = st.checkbox("Mostrar apenas colaboradores com irregularidades?", key="1")
        if filtrar_apenas_com_falso:
            filtro_false = check_df[check_df['Irregularidade presente']]
        else:
            filtro_false = check_df
        # Selecionar colunas de interesse
        opcoes = ["Gênero", "Raça/Etnia", "Estado Civil", "Data de Nascimento", "Data de Admissão"]
        selecionados = st.multiselect("Selecione as opções:", opcoes, default=opcoes)
        column_mapping2 = {
            'Gênero': 'genero',
            'Raça/Etnia': 'raca_etnia',
            'Estado Civil': 'estado_civil',
            'Data de Nascimento': 'data_nascimento',
            'Data de Admissão': 'data_admissao'
        }
        # Filtrar colunas selecionadas
        colunas_selecionadas = ['id_nacional', 'id_internacional', 'Irregularidade presente']
        for opcao in selecionados:
            coluna_adp = f"{column_mapping2[opcao]}_adp"
            coluna_workday = f"{column_mapping2[opcao]}_workday"
            colunas_selecionadas.extend([coluna_adp, coluna_workday])
        df_select = filtro_false[colunas_selecionadas]
        # Remover colunas irrelevantes
        colunas_skip = ['id_nacional', 'id_internacional', 'Irregularidade presente','Tipo de Admissão', 'Data de Desligamento', 'Modo Ponto', 'work_country', 'genero_check', 'raca_etnia_check', 'estado_civil_check', 'data_nascimento_check', 'data_admissao_check']
        ordenar = ['id_nacional','id_internacional', 'Irregularidade presente'] + [col for col in filtro_false.columns if col not in colunas_skip]
        df_select = df_select[ordenar]
        # Filtrar por ID Nacional e Internacional
        filter_id_nacional = st.text_input("Filtrar por ID Nacional")
        filter_id_internacional = st.text_input("Filtrar por ID Internacional")
        if filter_id_nacional:
            df_select = df_select[df_select['id_nacional'].astype(str).str.contains(filter_id_nacional, case=False)]
        if filter_id_internacional:
            df_select = df_select[df_select['id_internacional'].astype(str).str.contains(filter_id_internacional, case=False)]
        # Exibir DataFrame filtrado
        st.dataframe(df_select)

        # Botão de download para Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_select.to_excel(writer, sheet_name='Sheet1', index=False)
        excel_buffer.seek(0)
        st.download_button(
            label="Download Arquivo Excel",
            data=excel_buffer,
            file_name="base_ADP_Workday.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


        # Exibir panorama geral das irregularidades
        st.write("## Panorama geral das irregularidades:")
        st.write("##### Aqui estão os detalhes sobre as irregularidades e dados corretos")
       
        # Mapeamento de colunas para nomes legíveis
        column_mapping = {
            'check_genero': 'Gênero',
            'check_raca': 'Raça/Etnia',
            'check_estado_civil': 'Estado Civil',
            'check_data_nascimento': 'Data de Nascimento',
            'check_data_admissao': 'Data de Admissão'
        }
        
        # Contagem de registros e contagem de irregularidades por coluna
        total_records = check_df.shape[0]
        check_df_cols = check_df[check_columns]

        false_counts = check_df_cols.apply(lambda col: col.value_counts().get(False, 0))

        # Preparar dados para os cards de monitoramento
        card_data = [
            [ "Sem ID internacional (ADP)", 8],
            [ "Sem ID nacional (ADP)", 0],
            [ "Sem ID internacional (WDAY)", 5],
            [ "Sem ID nacional (WDAY)", 0],
            # IDS NACIONAL E INTERNACIONAL JUNTOS PARA COMPARAR DUPLCIADAS
            [ "Linhas duplicadas (ADP)", 6],
            [ "Linhas duplicadas (WDAY)", 6],
        ]
        # Adicionar contagem de irregularidades por coluna aos dados do card
        for i, (column, count) in enumerate(false_counts.items(), start=1):
            column_name = list(column_mapping.values())[i - 1]
            card_data.append((column_name, count))
        # Ordenar dados do card por contagem de irregularidades
        card_data.sort(key=lambda x: x[1], reverse=True)
        # Criar e exibir cards de monitoramento
        col1, col2 = st.columns(2)
        for i, (title, irregularities) in enumerate(card_data, start=1):
            with col1 if i <= len(card_data) // 2 else col2:
                create_monitoring_card(title, irregularities, total_records)
        # Verificar discrepância entre bases quanto à localização (Brasil)
        work_from_brazil = df1_cleaned['work_country'].value_counts()['Brazil']
        if work_from_brazil > total_records:
            with col1:
                st.info(f'#### A base Workday possui {work_from_brazil} colaboradores com "Brazil" na coluna "work country" e a base ADP possui {total_records} colaboradores. Diferença de {work_from_brazil - total_records}')
                st.warning('Irregularidade presente.')
        elif total_records > work_from_brazil:
            with col1:
                st.info(f'#### A base ADP possui {total_records} colaboradores com "Brazil" na coluna "work country" e a base Workday possui {work_from_brazil} colaboradores. Diferença de {total_records - work_from_brazil}')
                st.warning('Irregularidade presente.')
        else:
            with col1:
                st.info(f'#### Sem diferença no número de colaboradores na base Workday que possui {work_from_brazil} colaboradores com "Brazil" na coluna "work country" a base ADP, com {total_records} colabordores')
                st.success('Irregularidade corrigida!!')
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

