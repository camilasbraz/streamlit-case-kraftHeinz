import pandas as pd
import numpy as np
import streamlit as st 

def limpeza_dados(df, nome):
    # Converter as colunas de int64 para string
    colunas_data = ['Original Hire Date', 'Date of Birth', 'Data da Admissão ', 'Data de Desligamento ', 'Data de Nascimento ']  

    # Converter colunas para texto
    colunas_para_texto = [coluna for coluna in df.columns if coluna not in colunas_data]
    df[colunas_para_texto] = df[colunas_para_texto].astype(str)

    # Converter colunas de datas para datetime
    colunas_para_data = [coluna for coluna in df.columns if coluna in colunas_data]
    for coluna in colunas_para_data:
        df[coluna] = pd.to_datetime(df[coluna], format='%m/%d/%Y', errors='coerce')


    # Remover espaços em branco extras das células e dos nomes das colunas
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.rename(columns=lambda x: x.strip(), inplace=True)

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
    # Reordenando as colunas em df_workday

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

    # Reordenando as colunas em df
    df = df[nova_ordem]

    return df

def join(df1, df2):
    colunas_merge = ["id_nacional", "id_internacional"]
    df_join = df2.merge(df1, on=colunas_merge, how='left')

    return df_join

def col_check(df):

    # Mapeamento para a coluna 'raca_etnia_adp' para 'raca_etnia_workday'
    mapping_raca_etnia = {
        'Branco': 'White (Branco) (Brazil)',
        'Pardo': 'Brown (Pardo) (Brazil)',
        'Preto': 'Black (Preto) (Brazil)',
        'Não Informado': 'Prefer not to answer (Não desejo responder) (Brazil)',
        'Amarelo': 'Asian (Amarelo) (Brazil)',
        'Mulato': 'Not Listed (Outros) (Brazil)',
        'Indígena': 'Indigenous (Indígena) (Brazil)',
        '-': 'nan'
    }
    # melhor errar por excesso que faltar --> garantir erro, conversar com o time
    # mapear mulato para mulato
    # ver a questão do nan --> se todo - for nan, pode dexar, mas apontar isso

    df['raca_etnia_adp'] = df['raca_etnia_adp'].map(mapping_raca_etnia)

    # Mapeamento para a coluna 'estado_civil_adp' para 'estado_civil_workday'
    mapping_estado_civil = {
        'Solteiro': 'Single (Brazil)',
        'Casado': 'Married (Brazil)',
        'Divorciado': 'Divorced (Brazil)',
        'União Estável': 'Prefer not to answer (Brazil)',
        'Separado': 'Separated (Brazil)',
        'Outros': 'Other (Brazil)',
        'Viúvo': 'Widowed (Brazil)'
    }
    # Separar uniao estavel
    df['estado_civil_adp'] = df['estado_civil_adp'].map(mapping_estado_civil)

    # Mapeamento para a coluna 'genero_adp' para 'genero_workday'
    mapping_genero = {
        'Masculino': 'Male',
        'Feminino': 'Female',
        '28000': 'nan'
    }
    # 28000 e nan fazer mesma coisa de raça
    df['genero_adp'] = df['genero_adp'].map(mapping_genero)

    # Verificar se as colunas mapeadas são iguais às colunas originais e criar colunas de verificação
    df['genero_check'] = df['genero_adp'] == df['genero_workday']
    df['raca_etnia_check'] = df['raca_etnia_adp'] == df['raca_etnia_workday']
    df['estado_civil_check'] = df['estado_civil_adp'] == df['estado_civil_workday']
    df['data_nascimento_check'] = df['data_nascimento_adp'] == df['data_nascimento_workday']
    df['data_admissao_check'] = df['data_admissao_adp'] == df['data_admissao_workday']
    

    return df

def create_monitoring_card(title, irregularities, total_records):
        st.write(f"#### {title}")
        st.write("Quantidade de Irregularidades:", irregularities)
        st.write("Quantidade de Dados Corretos:", total_records - irregularities)
        st.write("Porcentagem de Irregularidades:", round((irregularities / total_records) * 100, 2), "%")
        st.progress(1 - irregularities / total_records)
        if irregularities == 0:
                st.success('Irregularidade corrigida!!')
        else:
                st.warning('Irregularidade presente.')