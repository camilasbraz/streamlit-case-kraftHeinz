def join(df1, df2):
    colunas_merge = ["id_nacional", "id_internacional"]
    df_join = df2.merge(df1, on=colunas_merge, how='left')

    return df_join