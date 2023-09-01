import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
from io import BytesIO
from functions import *



# URLs para ícone da página e imagem
favicon_url = "assets/favicon.ico"
imagem_url = 'assets/kraft-heinz-logo.png'

# Configuração da página
st.set_page_config(page_icon=favicon_url, page_title="KaftHeinz | case Camila Braz")

# Título e imagem


st.title("Comparação de dados das bases ADP e Workday")

css='''
<style>
[data-testid="stFileUploadDropzone"] div div::before {content:"Adicione o arquivo aqui"}
[data-testid="stFileUploadDropzone"] div div span{display:none;}
[data-testid="stFileUploadDropzone"] div div::after {font-size: .8em; content:"Limite de 200MB por arquivo | XLSX"}
[data-testid="stFileUploadDropzone"] div div small{display:none;}
</style>
'''

st.markdown(css, unsafe_allow_html=True)


# Carregar bases de dados através da barra lateral
st.sidebar.image(imagem_url, width = 250)
st.sidebar.header("Carregar Bases de Dados")
file1 = st.sidebar.file_uploader("Selecione a primeira base de dados Workday (Excel)", type=["xlsx"])
file2 = st.sidebar.file_uploader("Selecione a segunda base de dados ADP (Excel)", type=["xlsx"])

# Verificar se as bases de dados foram carregadas
if file1 and file2:
    if file1.name == "Workday.xlsx" and file2.name == "ADP.xlsx":


        # Leitura, limpeza e join
        df1 = pd.read_excel(file1, engine='openpyxl')
        df2 = pd.read_excel(file2, engine='openpyxl')

        colunas_desejadas_workday = ['Employee ID', 'External Payroll ID', 'Gender', 'Marital Status',
       'Race/Ethnicity', 'Date of Birth', 'Original Hire Date',
       'Work Country']
        colunas_presentes_workday = list(df1.columns)
        colunas_faltando_workday = [coluna for coluna in colunas_desejadas_workday if coluna not in colunas_presentes_workday]

         # Verifica se as colunas desejadas estão presentes
        colunas_desejadas_adp = ['Matrícula ', 'Id Global            ', 'Data da Admissão ',
       'Data de Desligamento ', 'Data de Nascimento ', 'Cútis           ',
       'Estado Civil - Nome            ', 'Modo Ponto                ',
       'Sexo      ', 'Tipo de Admissão               ']
        colunas_presentes_adp = list(df2.columns)
        colunas_faltando_adp = [coluna for coluna in colunas_desejadas_adp if coluna not in colunas_presentes_adp]

        if not colunas_faltando_workday and not colunas_faltando_adp:
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
                if filtrar_apenas_com_falso:
                    coluna_check = f"{column_mapping2[opcao]}_check"
                    colunas_selecionadas.extend([coluna_check])
        
            df_select = filtro_false[colunas_selecionadas]

            # Se o filtro de "False" for necessário, você pode aplicá-lo assim:
            if filtrar_apenas_com_falso:
                # Encontre as colunas "_check"
                colunas_check = [coluna for coluna in df_select.columns if coluna.endswith('_check')]
                # Mantenha apenas as linhas onde todas as colunas "_check" são True
                df_select = df_select[~df_select[colunas_check].any(axis=1)]
                # Remova as colunas "_check" do DataFrame
                df_select = df_select.drop(columns=colunas_check)      

            # Remover colunas irrelevantes
            colunas_skip = ['id_nacional', 'id_internacional', 'Irregularidade presente','Tipo de Admissão', 'Data de Desligamento', 'Modo Ponto', 'work_country', 'genero_check', 'raca_etnia_check', 'estado_civil_check', 'data_nascimento_check', 'data_admissao_check']
            ordenar = ['id_nacional','id_internacional', 'Irregularidade presente'] + [col for col in df_select.columns if col not in colunas_skip]
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
            st.write("**Ponto de atenção:** uma parte do número de irregularidades ocorre pela ausência de valores nas colunas de identificares em ambas as bases, e outra parte por incoerência nos valores de cada base.")

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

            
            # Preparar dados para os cards/graficos de monitoramento
            valores_especiais = ["nan", "null", np.nan, "",  pd.NaT]
            work_from_brazil = df1_cleaned['work_country'].value_counts()['Brazil']
            sem_id_nac_adp  = df1_cleaned['id_nacional'].isin(valores_especiais).sum()
            sem_id_inter_adp = df1_cleaned['id_internacional'].isin(valores_especiais).sum()
            sem_id_nac_workday  = df2_cleaned['id_nacional'].isin(valores_especiais).sum()
            sem_id_inter_workday  = df2_cleaned['id_internacional'].isin(valores_especiais).sum()
            duplicadas_adp = df1_cleaned.duplicated(['id_nacional', 'id_internacional']).sum()
            duplicadas_workday = df2_cleaned.duplicated(['id_nacional', 'id_internacional']).sum()

            if work_from_brazil > total_records:
                num_col = work_from_brazil - total_records
            elif work_from_brazil < total_records:
                num_col = total_records - work_from_brazil 
            
            card_data = [
                [ "Sem ID internacional (ADP)", sem_id_nac_adp],
                [ "Sem ID nacional (ADP)", sem_id_inter_adp],
                [ "Sem ID internacional (WDAY)", sem_id_nac_workday],
                [ "Sem ID nacional (WDAY)", sem_id_inter_workday],
                # IDS NACIONAL E INTERNACIONAL JUNTOS PARA COMPARAR DUPLCIADAS
                [ "Linhas duplicadas (ADP)", duplicadas_adp],
                [ "Linhas duplicadas (WDAY)", duplicadas_workday],
                ["Número de colaboradores", num_col]
            ]

            # Adicionar contagem de irregularidades por coluna aos dados do card
            for i, (column, count) in enumerate(false_counts.items(), start=1):
                column_name = list(column_mapping.values())[i - 1]
                card_data.append((column_name, count))
            # Ordenar dados do card por contagem de irregularidades
            card_data.sort(key=lambda x: x[1], reverse=True)

            
            grafico(card_data, total_records)
        

            # Criar e exibir cards de monitoramento
            col1, col2 = st.columns(2)
            for i, (title, irregularities) in enumerate(card_data, start=1):
                if i % 2 == 1:  # Números ímpares vão para a coluna esquerda
                    with col1:
                        create_monitoring_card(title, irregularities, total_records)
                else:  # Números pares vão para a coluna direita
                    with col2:
                        create_monitoring_card(title, irregularities, total_records)
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
        elif colunas_faltando_workday:
            st.warning(f"Colunas faltando no arquivo Workday: {', '.join(colunas_faltando_workday)}")
        elif colunas_faltando_adp:
            st.warning(f"Colunas faltando no arquivo ADP: {', '.join(colunas_faltando_adp)}")
    else:
        st.warning("Por favor, carregue os arquivos com os nomes corretos.")
else:
    st.warning("Por favor, carregue as bases de dados.")

