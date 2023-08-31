import pandas as pd
import numpy as np 

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