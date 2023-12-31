import pandas as pd
import numpy as np
import streamlit as st 
import plotly.express as px

def limpeza_dados(df, nome):
   # Converter as colunas 
    colunas_data = ['Original Hire Date', 'Date of Birth', 'Data da Admissão ', 'Data de Desligamento ', 'Data de Nascimento ']  
    colunas_para_converter = [coluna for coluna in df.columns if coluna not in colunas_data]
    df[colunas_para_converter] = df[colunas_para_converter].astype(str)
    colunas_para_data = [coluna for coluna in df.columns if coluna in colunas_data]
    for coluna in colunas_para_data:
        df[coluna] = pd.to_datetime(df[coluna], format='%m/%d/%Y', errors='coerce')

    # Remover espaços em branco extras das células e dos nomes das colunas
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.rename(columns=lambda x: x.strip(), inplace=True)

    # Renomear e reordenar as colunas
    col_mapping = {
        'External Payroll ID': 'id_nacional',
        'Employee ID': 'id_internacional',
        'Original Hire Date': 'data_admissao_workday',
        'Date of Birth': 'data_nascimento_workday',
        'Race/Ethnicity': 'raca_etnia_workday',
        'Marital Status': 'estado_civil_workday',
        'Gender': 'genero_workday',
        'Work Country': 'work_country',
        'Matrícula': 'id_nacional',
        'Id Global': 'id_internacional',
        'Data da Admissão': 'data_admissao_adp',
        'Data de Nascimento': 'data_nascimento_adp',
        'Cútis': 'raca_etnia_adp',
        'Estado Civil - Nome': 'estado_civil_adp',
        'Sexo': 'genero_adp'
    }

    df.rename(columns=col_mapping, inplace=True)
    if nome == "adp":
        nova_ordem = [
        'id_nacional', 'id_internacional', 'data_admissao_adp', 'data_nascimento_adp',
        'raca_etnia_adp', 'estado_civil_adp', 'genero_adp', 'Tipo de Admissão', 'Data de Desligamento', 'Modo Ponto'
        ]
    else:
        nova_ordem = [
            'id_nacional', 'id_internacional', 'data_admissao_workday', 'data_nascimento_workday',
            'raca_etnia_workday', 'estado_civil_workday', 'genero_workday', 'work_country'
        ]
    df = df[nova_ordem]

    return df

def join(df1, df2):
    colunas_merge = ["id_nacional", "id_internacional"]
    df_join = df2.merge(df1, on=colunas_merge, how='left')

    return df_join

def col_check(df):
    mapping_raca_etnia_workday = {
    'Nao Informado (Brazil) (inactive)' : 'Prefer not to answer (Não desejo responder) (Brazil)'
    }

    # Mapeamento para a coluna 'raca_etnia_adp' para 'raca_etnia_workday'
    mapping_raca_etnia = {
        'Branco': 'White (Branco) (Brazil)',
        'Pardo': 'Brown (Pardo) (Brazil)',
        'Preto': 'Black (Preto) (Brazil)',
        'Não Informado': 'Prefer not to answer (Não desejo responder) (Brazil)',
        'Amarelo': 'Asian (Amarelo) (Brazil)',
        'Mulato': 'Not Listed (Outros) (Brazil)',
        'Indígena': 'Indigenous (Indígena) (Brazil)',
        '-':'-' ,
        '0':'0'
    }

    df['raca_etnia_adp'] = df['raca_etnia_adp'].map(mapping_raca_etnia)

    # Mapeamento para a coluna 'estado_civil_adp' para 'estado_civil_workday'
    mapping_estado_civil = {
        'Solteiro': 'Single (Brazil)',
        'Casado': 'Married (Brazil)',
        'Divorciado': 'Divorced (Brazil)',
        'Separado': 'Separated (Brazil)',
        'Outros': 'Other (Brazil)',
        'Viúvo': 'Widowed (Brazil)',
        'União Estável': 'União Estável'
    }
    # Separar uniao estavel
    df['estado_civil_adp'] = df['estado_civil_adp'].map(mapping_estado_civil)

    # Mapeamento para a coluna 'genero_adp' para 'genero_workday'
    mapping_genero = {
        'Masculino': 'Male',
        'Feminino': 'Female',
        '28.000,00': '28.000,00'
    }
    df['genero_adp'] = df['genero_adp'].map(mapping_genero)

    # Verificar se as colunas mapeadas são iguais às colunas originais e criar colunas de verificação
    df['genero_check'] = df['genero_adp'] == df['genero_workday']
    df['raca_etnia_check'] = df['raca_etnia_adp'] == df['raca_etnia_workday']
    df['estado_civil_check'] = df['estado_civil_adp'] == df['estado_civil_workday']
    df['data_nascimento_check'] = df['data_nascimento_adp'] == df['data_nascimento_workday']
    df['data_admissao_check'] = df['data_admissao_adp'] == df['data_admissao_workday']

    return df

def create_monitoring_card(title, irregularities, total_records):
        if title  == 'Número de colaboradores':
            st.write(f"#### {title}")
            percentage_text = (
                f"Quantidade de irregularidades: "
                f"<span style='border: 1px solid #4d4d4d; border-radius: 5px; padding: 4px; background-color: #4d4d4d;'>{irregularities}</span>"
            )
            st.markdown(percentage_text, unsafe_allow_html=True)
            irregularities_text = f"Colaboradores na base ADP: <span style='border: 1px solid #4d4d4d; border-radius: 5px; padding: 4px; background-color: #4d4d4d;'>{total_records}</span>"
            st.markdown(irregularities_text, unsafe_allow_html=True)
            correct_data_text = f"Colaboradores na base WDAY: <span style='border: 1px solid #4d4d4d; border-radius: 5px; padding: 4px; background-color: #4d4d4d;'>{total_records+irregularities}</span>"
            st.markdown(correct_data_text, unsafe_allow_html=True)
            st.progress(1- irregularities / total_records)
            st.warning('Irregularidade presente.')
            if irregularities == total_records:
                st.success('Irregularidade corrigida!!')
        else:
            st.write(f"#### {title}")
            irregularities_text = f"Quantidade de Irregularidades: <span style='border: 1px solid #4d4d4d; border-radius: 5px; padding: 4px; background-color: #4d4d4d;'>{irregularities}</span>"
            st.markdown(irregularities_text, unsafe_allow_html=True)
            correct_data_text = f"Quantidade de Dados Corretos: <span style='border: 1px solid #4d4d4d; border-radius: 5px; padding: 4px; background-color: #4d4d4d;'>{total_records - irregularities}</span>"
            st.markdown(correct_data_text, unsafe_allow_html=True)
            percentage = round((irregularities / total_records) * 100, 1)
            percentage_text = (
                f"Porcentagem de Irregularidades: "
                f"<span style='border: 1px solid #4d4d4d; border-radius: 5px; padding: 4px; background-color: #4d4d4d;'>{percentage}%</span>"
            )
            st.markdown(percentage_text, unsafe_allow_html=True)
            st.progress(1- irregularities / total_records)
            if irregularities == 0:
                st.success('Irregularidade corrigida!!')
            else:
                st.warning('Irregularidade presente.')


def grafico(data, total_records):
    df_graf = pd.DataFrame(data)
    df_graf = df_graf.rename(columns={0: "Categoria", 1: "Quantidade de Irregularidades"})
    # Filtrar apenas as linhas com "Quantidade de Irregularidades" > 0 e criar label
    df_graf_filtrado = df_graf[df_graf["Quantidade de Irregularidades"] > 0]
    df_graf_filtrado["perc"] = round(100 * df_graf_filtrado["Quantidade de Irregularidades"] / total_records, 1)
    df_graf_filtrado["perc_txt"] = df_graf_filtrado["perc"].astype(str) + "%"
    df_graf_filtrado = df_graf_filtrado.sort_values(by="Quantidade de Irregularidades")
    # Gráfico de barras horizontais interativo com Plotly Express
    fig = px.bar(
        df_graf_filtrado,
        y="Categoria",
        x="Quantidade de Irregularidades",
        orientation='h',
        title="",
        color_discrete_sequence=["#1D3C6D"],
    )
    largura_da_barra = df_graf_filtrado['Quantidade de Irregularidades']
    text_position = ['inside' if largura >= 800 else 'outside' for largura in largura_da_barra]
    df_graf_filtrado['custom_text'] = df_graf_filtrado.apply(
    lambda row: f"A categoria {row['Categoria']} apresenta {row['Quantidade de Irregularidades']} irregularidades",
    axis=1
    )
    fig.update_traces(
        text=df_graf_filtrado["perc_txt"],
        textposition=text_position,
        textfont=dict(size=14),
        hovertemplate=df_graf_filtrado["custom_text"]
    )
    fig.update_xaxes(title_text="", showticklabels=False)
    fig.update_yaxes(title_text="", tickfont=dict(size=14, family="Roboto"))
    fig.update_layout(
        margin=dict(l=0, r=0),
        bargap=0.3,
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        showlegend=False,
        height=500
    )
    # Exibir o gráfico
    st.plotly_chart(fig, config={"displayModeBar": False, 'displaylogo': False,})