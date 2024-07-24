import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import plotly.express as px
from io import StringIO

st.set_page_config(layout="wide")


# Função para exibir os dados na interface Streamlit
def show_data(meses_df):

    sorter_month = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    meses_df["Mês"] = pd.Categorical(meses_df["Mês"], categories=sorter_month, ordered=True)
    

    st.title("Análise de Fechamento A&B")
    st.divider()

    produtos_unicos = meses_df["Descrição"].unique()
    meses = meses_df['Mês'].unique()

    meses_selecionados = st.sidebar.multiselect("Mes:", meses)
    produtos_selecionados = st.sidebar.multiselect("Produtos:", sorted(produtos_unicos))

    if len(produtos_selecionados) != 0:
        meses_df = meses_df.loc[meses_df['Descrição'].isin(produtos_selecionados)]

    if len(meses_selecionados) != 0:
        meses_df = meses_df.loc[meses_df['Mês'].isin(meses_selecionados)]


    # st.dataframe(produtos_df)

    if not meses_df.empty:
        # st.header("Dados Mensais [raw]")
        # st.dataframe(meses_df, hide_index=True, use_container_width=True)

        st.header("Estatísticas Gerais")
        sorter_month = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
        meses_df["Mês"] = pd.Categorical(meses_df["Mês"], categories=sorter_month, ordered=True)

        df_grouped_by_month = meses_df.groupby(["Mês"])["Diferença Valor"].sum().reset_index()
        meses_df["Mês"] = pd.Categorical(meses_df["Mês"], categories=sorter_month, ordered=True)

         #------------------------------ CURVA ABC 30 ITENS
        df_grouped_by_prod_consumo = meses_df.groupby(["Descrição"])["Diferença Valor"].sum().reset_index()

        fig_prod_2 = px.bar(df_grouped_by_prod_consumo.sort_values("Diferença Valor").head(30), 
                        x="Descrição", 
                        y="Diferença Valor", 
                        color="Descrição",
                        title="Curva ABC 30 itens",
                        orientation="v")
        
        st.plotly_chart(fig_prod_2)

        df_grouped_by_month_prod = meses_df.groupby(["Mês", "Descrição"])["Diferença Valor"].sum().reset_index()




        fig_prod_2 = px.bar(df_grouped_by_month.sort_values("Mês"), 
                        x="Mês", 
                        y="Diferença Valor", 

                        title="Total Diferenças Valor por mês",
                        orientation="v")
        col1, col2 = st.columns(2)

        col1.write("Diferenças Mes / Produto")
        col2.write("Total Diferenças por Mês")

        col2.dataframe(df_grouped_by_month, use_container_width=True, hide_index=True)
        col1.dataframe(df_grouped_by_month_prod.sort_values('Diferença Valor'), use_container_width=True, hide_index=True)
        st.plotly_chart(fig_prod_2, use_container_width=True)

        
        fig_prod_2 = px.bar(df_grouped_by_month_prod.sort_values("Mês"), 
                        x="Mês", 
                        y="Diferença Valor", 
                        color="Descrição",
                        title="Total Diferenças Valor detalhando Produtos",
                        orientation="v")
        
        st.plotly_chart(fig_prod_2, use_container_width=True,)


        df_grouped_by_month_consumo = meses_df.groupby(["Mês", "Descrição"])["Diferença"].sum().reset_index()

        fig_prod_3 = px.bar(df_grouped_by_month_consumo.sort_values("Mês"), 
                        x="Mês", 
                        y="Diferença", 
                        color="Descrição",
                        title="Total Consumos detalhando Produtos / unidade Medida",
                        orientation="v")
        
        st.plotly_chart(fig_prod_3, use_container_width=True,)

       

        #-----------------------------PREÇOS
        df_grouped_by_month_prod = meses_df.groupby(["Mês", "Descrição"])["Preço Médio"].mean().reset_index()
        fig_prod_4 = px.bar(df_grouped_by_month_prod.sort_values("Mês"), 
                        x="Mês", 
                        y="Preço Médio", 
                        color="Descrição",
                        title="Preço Médio / Unidade",
                        orientation="v")
        
        st.plotly_chart(fig_prod_4, use_container_width=True,)

        st.divider()
        st.header("Dados Mensais [raw]")
        st.dataframe(meses_df, hide_index=True, use_container_width=True)
        total_diferenca_valor = meses_df["Diferença Valor"].sum()
        st.write(f"Total Diferença em Valor: R$ {total_diferenca_valor}")


def load_data(files):

    data = []
    for file in files:

        string_data = file.read().decode("latin1")
        df = pd.read_csv(StringIO(string_data), sep=";")
        df.columns = ["Código", "Descrição", "Loc", "Saldo em Estoque", "Quantidade Contada", "Diferença", "Unidade", "Valor Estoque", "Valor Contada", "Diferença Valor"]
        df['Diferença Valor'] = df['Diferença Valor'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)
        df['Diferença'] = df['Diferença'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)

        df['Preço Médio'] = df['Diferença Valor'] / df['Diferença']
        df['Mês'] = str(file.name.lower()).replace('.csv', '')
        data.append(df)
    
    return pd.concat(data)

# Função principal para rodar a aplicação
def main():

    files = st.sidebar.file_uploader("Escolha os arquivos CSV", type="csv", accept_multiple_files=True)


    search = st.sidebar.button("Atualizar dos Arquivos")


    if search:
        if len(files) > 0:
            st.session_state['data'] = load_data(files)
        

    if 'data' in st.session_state:
        show_data(st.session_state['data'])
    else:
        pass


if __name__ == "__main__":
    main()
