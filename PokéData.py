import pandas as pd 
import plotly.express as px
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# Configuração do Streamlit
st.set_page_config(page_title="PokéData", page_icon=":bar_chart:", layout="wide")

# Carregar os dados
df = pd.read_csv('pokemon_data.csv')

# Criação de containers para melhor organização visual
st.title("📊 PokéData")
st.markdown("Um dashboard interativo para fãs de Pokémon que querem mergulhar fundo nos dados. Acompanhe categorias, atributos e curiosidades em gráficos bonitos e informativos.")

st.markdown("---")
st.subheader("🎮 Filtro de Geração")
filtroGeracao = st.selectbox("Selecione a geração:", options=["Todas"] + sorted(df['gen'].unique()))

if filtroGeracao == "Todas":
    df_filtrado = df.copy()
else:
    df_filtrado = df[df['gen'] == filtroGeracao]

st.markdown("---")

## Base Stats
def baseStats(df):
    df_basestats = df_filtrado.sort_values('Base_Stats', ascending=False)
    df_maiores_basestats = df_basestats.head(10)
    # Criar DataFrame com os 10 Pokémons com maiores Base Stats
    df_maiores_basestats = df_maiores_basestats[['Name', 'Base_Stats']]
    df_maiores_basestats = df_maiores_basestats.set_index('Name')   
    PokemonsComMaioresBaseStats = df_maiores_basestats
    return PokemonsComMaioresBaseStats

# Média de atributos
def mediaAtributos(df):
    atributos = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
    # Lista pra guardar os resultados
    dados = []
    # Loop para calcular média, máximo e mínimo
    for atributo in atributos:
        media = df_filtrado[atributo].mean()
        dados.append({
                'Atributo': atributo,
                'Média': round(media, 2),
            })
    # Criar DataFrame com os resultados
    dfResumo = pd.DataFrame(dados)
    dfResumo = dfResumo.set_index('Atributo')
    return dfResumo

# Gráfico de correlação
def atributos(df):
    # Selecionar só os atributos de batalha
    atributos_batalha = df[['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']]
    # Calcular a correlação
    matriz_corr = atributos_batalha.corr()
    # Plotar o heatmap com Plotly
    figCorr = px.imshow(
        matriz_corr,
        text_auto=True,  # mostra os valores em cada quadradinho
        color_continuous_scale='RdBu_r',  # esquema de cor parecido com o coolwarm
        aspect="auto",  # deixa o quadrado bem formado
        title='Correlação entre Atributos de Batalha dos Pokémon'
    )
    figCorr.update_layout(
        width=700,
        height=600,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return figCorr

# Gráfico de categorias dos Pokémons
def categoria(df):
    df_copia = df.copy()
    # Cria a coluna de categorias especiais
    df_copia['Categoria'] = df_copia.apply(
        lambda row: 'Lendário' if row['Is_Legendary'] == 1 else
                    'Mítico' if row['Is_Mythical'] == 1 else
                    'Ultra Beast' if row['Is_Ultra_Beast'] == 1 else
                    'Outros',
        axis=1
    )
    # Conta quantos em cada categoria
    df_categoria = df_copia['Categoria'].value_counts().reset_index()
    df_categoria.columns = ['Categoria', 'Quantidade']
    figCategoria = px.bar(
        df_categoria,
        x='Categoria',
        y='Quantidade',
        color='Quantidade',
        title='Distribuição de Pokémon por Categoria'
        
        
    )
    return figCategoria

# Gráfico de comparação de atributos
def plot_comparacao_atributos(df):
    # Filtrar dados
    df_lendarios = df[df['Is_Legendary'] == 1]
    df_normais = df[df['Is_Legendary'] == 0]
    df_Mythical = df[df['Is_Mythical'] == 1]
    df_UltraBeast = df[df['Is_Ultra_Beast'] == 1]
    
    atributos = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
    data = []

    for atributo in atributos:
        data.append({
            'Atributo': atributo,
            'Lendários': df_lendarios[atributo].mean(),
            'Normais': df_normais[atributo].mean(),
            'Míticos': df_Mythical[atributo].mean(),
            'Ultra Beasts': df_UltraBeast[atributo].mean(),
            'Média Geral': df[atributo].mean()  # Aqui também!
        })

    df_comparacao = pd.DataFrame(data)
    df_comparacao = pd.DataFrame(data).fillna(0)

    # Criar gráfico
    figMedia = go.Figure()

    # Adicionar barras (usando a paleta de cores sugerida)
    categorias = ['Lendários', 'Normais', 'Míticos', 'Ultra Beasts']
    cores = ['#4A9CEE', '#5A5A5A', '#E6E69C', '#29739C']
    
    for cat, cor in zip(categorias, cores):
        figMedia.add_trace(go.Bar(
            x=df_comparacao['Atributo'],
            y=df_comparacao[cat],
            name=cat,
            marker_color=cor,
            hovertemplate=f"{cat}: %{{y:.1f}}<extra></extra>"
        ))

    # Linha de média geral
    figMedia.add_hline(
        y=df[atributos].mean().mean(),
        line_dash="dash",
        line_color="#FF6B6B",
        annotation_text="Média Geral",
        annotation_position="bottom right",
        annotation_font_size=12
    )

    # Ajustes de layout
    figMedia.update_layout(
        title="Comparação de Atributos Médios por Categoria",
        xaxis_title="Atributos",
        yaxis_title="Valor Médio",
        barmode="group",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return figMedia

# Pokémons mais imunes
def imunes(df):
    df_mais_imunes = df.sort_values('number_immune', ascending=False).head(15)
    df_mais_imunes = df_mais_imunes[['Name', 'number_immune']]
    df_mais_imunes.reset_index(drop=True, inplace=True)
    df_mais_imunes = df_mais_imunes.set_index('Name')
    df_mais_imunes = df_mais_imunes.rename(columns={'number_immune': 'Número de Imunidade'})
    return df_mais_imunes

# Quantidade de Pokémons por Geração
def quantidadePorGeracao(df):
    geracao = df.value_counts('gen').reset_index(name='Quantidade')
    geracao.sort_values('gen', ascending=True, inplace=True)
    geracao.set_index('gen', inplace=True)
    return geracao

# Gráfico de aumento de base stats ao longo das gerações
def aumentoBaseStats(df):
    dfGeracao = df.groupby('gen')['Base_Stats'].mean().reset_index()
    dfGeracao.columns = ['Geração', 'Média Base Stats']
    dfGeracao['Média Base Stats'] = dfGeracao['Média Base Stats'].round(0)

    figMediaBaseStats = px.line(dfGeracao, x='Geração', y='Média Base Stats', title='Média de Base Stats por Geração')
    figMediaBaseStats.update_traces(mode='markers+lines', marker=dict(size=10, color='#5A5A5A'))
    figMediaBaseStats.update_layout(title_x=0.5, xaxis_title='Geração', yaxis_title='Média Base Stats')
    return figMediaBaseStats

# Top 5 Pokémons mais rápidos
def maisRapidos(df):
    df_mais_rapidos = df.sort_values('Speed', ascending=False).head(5)
    df_mais_rapidos = df_mais_rapidos[['Name', 'Speed']]
    df_mais_rapidos.reset_index(drop=True, inplace=True)
    df_mais_rapidos = df_mais_rapidos.set_index('Name')
    return df_mais_rapidos

# Pokemóns normais com mais ataques
def maisAtaquesNormais(df):
    dfPokemonNormais = df[(df['Is_Legendary'] == 0) & (df['Is_Mythical'] == 0) & (df['Is_Ultra_Beast'] == 0)]
    dfPokemonNormais = dfPokemonNormais.sort_values('Attack', ascending=False).head(5)
    dfPokemonNormais = dfPokemonNormais[['Name', 'Attack']]
    dfPokemonNormais.set_index('Name', inplace=True)
    return dfPokemonNormais

# Relação entre speed e base stats
def relacao (df):
    df['Speed'] = df['Speed'].astype(float)
    df['Base_Stats'] = df['Base_Stats'].astype(float)
    figRelacaoSpeedBaseStats = px.scatter(df, x='Speed', y='Base_Stats', title='Relação entre Speed e Base Stats')
    figRelacaoSpeedBaseStats.update_traces(marker=dict(size=7, color='#29739C'))
    figRelacaoSpeedBaseStats.update_layout(title_x=0.5, xaxis_title='Speed', yaxis_title='Base Stats')
    return figRelacaoSpeedBaseStats

# Distribuição de tipos
def distribuicaoTipos(df):
    # Contar os tipos combinando Type 1 e Type 2
    tipo1 = df['Type 1'].value_counts()
    tipo2 = df['Type 2'].value_counts()

    # Somar os dois
    tipo_total = tipo1.add(tipo2, fill_value=0).sort_values(ascending=False)

    # Criar DataFrame
    df_tipos = tipo_total.reset_index()
    df_tipos.columns = ['Tipo', 'Quantidade']

    # Plotar gráfico de barras
    figTipo = px.bar(df_tipos, x='Tipo', y='Quantidade', text='Quantidade',
                title='Distribuição dos Tipos de Pokémon (Tipo 1 + Tipo 2)',
                color='Tipo',
                color_discrete_sequence=px.colors.qualitative.Dark24)
    figTipo.update_traces(textposition='outside')
    figTipo.update_layout(showlegend=False, template='plotly_white')
    return figTipo


# Layout em 3 colunas (ajustado com proporção)
col1, col2, col3 = st.columns([1.2, 2, 2])

# COLUNA 1 - Dados em tabela
with col1:
    st.subheader("🏆 Top Pokémons")
    with st.container():
        st.markdown("**🔝 Maiores Base Stats:**")
        df_basestats = baseStats(df_filtrado)
        st.dataframe(df_basestats, use_container_width=True)

        st.markdown("**📊 Média dos Atributos:**")
        df_media = mediaAtributos(df_filtrado)
        st.dataframe(df_media, use_container_width=True)

        st.markdown("**🛡️ Mais Imunes:**")
        df_imunes = imunes(df_filtrado)
        st.dataframe(df_imunes, use_container_width=True)

        st.markdown("**📅 Quantidade por Geração:**")
        df_geracao = quantidadePorGeracao(df)
        st.dataframe(df_geracao, use_container_width=True)

# COLUNA 2 - Gráficos de análise
with col2:
    st.subheader("📈 Análises Visuais")
    with st.container():
        figCorr2 = atributos(df_filtrado)
        st.plotly_chart(figCorr2, use_container_width=True)

        figCategoria2 = categoria(df_filtrado)
        st.plotly_chart(figCategoria2, use_container_width=True)

        figTipo2 = distribuicaoTipos(df_filtrado)
        st.plotly_chart(figTipo2, use_container_width=True)

        st.markdown("**⚡ Top 5 Mais Rápidos:**")
        df_mais_rapidos = maisRapidos(df_filtrado)
        st.dataframe(df_mais_rapidos, use_container_width=True)

# COLUNA 3 - Comparações e tendências
with col3:
    st.subheader("📊 Comparações e Tendências")
    with st.container():
        figMedia2 = plot_comparacao_atributos(df_filtrado)
        st.plotly_chart(figMedia2, use_container_width=True)

        figMediaBaseStats2 = aumentoBaseStats(df)
        st.plotly_chart(figMediaBaseStats2, use_container_width=True)

        figRelacao = relacao(df)
        st.plotly_chart(figRelacao, use_container_width=True)

        st.markdown("**💥 Normais com mais Ataque:**")
        df_mais_ataques = maisAtaquesNormais(df_filtrado)
        st.dataframe(df_mais_ataques, use_container_width=True)
