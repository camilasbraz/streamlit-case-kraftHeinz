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