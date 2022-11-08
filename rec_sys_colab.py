import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import operator
#Item-Based
import sklearn
from sklearn.decomposition import TruncatedSVD

def load_files(rating_file, movie_file):
    global ratings
    global movies
    ratings = pd.read_csv(rating_file)
    movies = pd.read_csv(movie_file)

    n_ratings = len(ratings)
    l_movies = ratings['movieId'].unique()
    n_movies = len(l_movies)
    l_users = ratings['userId'].unique()
    n_users = len(l_users)

    estatisticas = (f"Total de ratings: {'{:,.0f}'.format(n_ratings)}\n"
        f"Total de filmes: {'{:,.0f}'.format(n_movies)}\n"
        f"Total de usuários: {'{:,.0f}'.format(n_users)}\n"
        f"Média de ratings/user: {round(n_ratings/n_users, 2)}\n"
        f"Média de ratings/movie: {round(n_ratings/n_movies, 2)}")
    return(estatisticas)

def gerar_freq_movies(suporte = 0):
    print("suporte: ", suporte)
    global freq_movies
    freq_movies = ratings.groupby('movieId').agg(votos=('rating', np.count_nonzero))
    freq_movies = freq_movies.merge(movies, on='movieId', how='left')
    freq_movies.sort_values(by=['votos'], inplace=True, ascending=False)
    freq_movies = freq_movies[freq_movies.votos > suporte]
    return freq_movies

def gerar_ratings_suporte():
    global ratings_suporte
    ratings_suporte = pd.merge(ratings, freq_movies, on="movieId", how='right')
    print(len(ratings_suporte), " ratings a serem avaliados ainda.")
    return ratings_suporte

def pivotar_ratings_users():
    global ratings_users

    gerar_ratings_suporte()
    if (len(ratings_suporte)==0):
        pass
        #implementar
    else:
        ratings_users = ratings_suporte.pivot_table(index="userId", columns="title", values="rating", aggfunc='mean', fill_value=0)
    ratings_users = ratings_users.dropna(how='all')# .fillna(0) #eliminar usuarios que todas as colunas estão sem notas
    return ratings_users                                     # e converter notas vazias para 0

def descrever_users():
    global users 
    users = pd.DataFrame()
    users['Votos'] = ratings_users.astype(bool).sum(axis=1) #Quantidade de Votos dados (soma as colunas )
    users['Sum_Ratings'] = ratings_users.sum(axis='columns') #Soma todos os valores nas colunas
    users['Avg_Ratings'] = (users['Sum_Ratings']/users['Votos']).round(1)
    # média dos ratings dados = data.mean(axis='columns') #Neste caso considera as colunas com zero também
    #
    #AVISO: ao converter este dataframe para lista, TENDO UMA COLUNA FLOAT TODAS VIRAM FLOAT!!!
    return users

def get_movies_from_user(id):
    ratings_do_usuario = ratings.loc[ratings['userId'] == id]
    return ratings_do_usuario.merge(movies, on='movieId')[['title','rating']].values.tolist()

def similaridade_user(userId):
    matriz_filmes_usuario = ratings_users[ratings_users.index == userId]
    matriz_demais_usuarios = ratings_users[ratings_users.index != userId]
    similaridades = cosine_similarity(matriz_filmes_usuario, matriz_demais_usuarios)

    indice_similaridade = dict(zip(matriz_demais_usuarios.index.to_list(),similaridades.tolist()[0]))
    indice_similaridade_sorted = sorted(indice_similaridade.items(), key=operator.itemgetter(1))
    indice_similaridade_sorted.reverse()
    return indice_similaridade_sorted


def rec_user_based(userId, n_similares):
    #Obter lista dos [n_similares] usuários mais similares 
    lista_similares = similaridade_user(userId)
    try:
        n_similares = int(n_similares)
    except:
        n_similares = 5
    lista_similares = [a[0] for a in lista_similares][:n_similares]
    #Obter a lista de filmes que estes usuários viram
    matriz_selecao = ratings_suporte[ratings_suporte['userId'].isin(lista_similares)]
    matriz_selecao = matriz_selecao.groupby('title')[['rating','votos']].mean().sort_values(['rating','votos'],ascending=False)    
    #Obter lista de filmes que o usuario viu
    assistidos = [a[0] for a in get_movies_from_user(userId)]
    #sugerir para eles aqueles que ele ainda não viu
    matriz_selecao = matriz_selecao[~matriz_selecao.index.isin(assistidos)]
    #eliminar sugestões com notas médias < 3 e com menos de 3 votos
    matriz_selecao = matriz_selecao.drop(matriz_selecao[(matriz_selecao.rating<3)|(matriz_selecao.votos<3)].index)
    return matriz_selecao

def set_movies_similarity():
    global movies_similarity
    if 'movies_similarity' not in vars():
        movies_similarity = ratings_users.corr()
    
def rec_item_based(movieTitle):
    set_movies_similarity()
    corr_specific = movies_similarity[movieTitle]
    recomendacao = pd.DataFrame({'corr_specific':corr_specific, 'Movies': ratings_users.columns})
    return recomendacao.sort_values('corr_specific', ascending=False).head(10)


