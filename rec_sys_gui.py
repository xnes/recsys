from faulthandler import disable
import PySimpleGUI as sg
import rec_sys_colab as rs
#criado em 05/10/2022 por Rodrigo Sze 
# usando https://csveda.com/creating-tabbed-interface-using-pysimplegui/
# e https://www.geeksforgeeks.org/themes-in-pysimplegui/

sg.theme('DarkBlue3')   # Add a touch of color


tab_FreqMovies = [[sg.Text('Popular Movies                                                                                        ')],
    [sg.Table(values = [], headings=['movieId', 'Votos','       Título          ', '    Gênero   '], num_rows=10, key='-TABLE_FREQ-')],
    [sg.Text("0 filmes", key='-RODAPE1-')]]

tab_UserBased = [[sg.Text('Memory Based usando'),sg.InputText('5', size = 3, key='-N_SIMILAR_USERS-'),sg.Text('usuários mais similares')],
    [sg.Table(values = [], headings=['userId', 'Votos','Soma dos Ratings', 'Média dos Ratings'], 
        num_rows=10, key='-TABLE_USERS-', enable_events = True)],
    [sg.Text("0 usuários", key='-RODAPE2-'),
    sg.Button('Similaridade por Cosine', key='-BTN_USER_COSINE-', disabled=True)]]

tab_ItemBased = [[sg.Text('Memory Based')],
    [sg.Table(values = [], headings=['Score', '              Título                '], 
        num_rows=10, key='-TABLE_ITEMS-')],]

tab_SVD = [[sg.Text('Fatoração de Matriz')],
    [sg.Listbox(values = sg.theme_list(),
        size =(20, 12),
        key ='-LIST3-',
        enable_events = True)],
    [sg.Button('Exit')]]

## MOVIELENS #############################
# LOAD # FreqMovies # Pivot # USERS # TEST #
##########################################
btns_layout = [sg.Button('LOAD'),
    sg.Button('FreqMovies', key='-BTN_FMovies-', disabled=True),
    sg.Button('Pivot', key='-BTN_PIVOTAR-', disabled=True),
    sg.Button('USERS', key='-BTN_USERS-', disabled=True),
    sg.Button('ITEMS', key='-BTN_ITEMS-', disabled=True),
    sg.Button('TEST')]
    
frame_layout = [sg.Frame('MOVIELENS:',[
    btns_layout,
    [sg.Text('Arquivo de Ratings'), sg.InputText('ratings_small.csv', key='-RATING_FILENAME-')],
    [sg.Text('Arquivo de Movies'), sg.InputText('movies_small.csv', key='-MOVIE_FILENAME-')],
    [sg.Text('Suporte'), sg.InputText('10000', key='-VALOR_SUPORTE-'), sg.Button('FILTER', key='-BTN_SUPORTE-', disabled=True),],
    ],)]

layout_tab = [sg.TabGroup([    #Define Layout with Tabs         
        [sg.Tab('Freq. Movies', tab_FreqMovies, title_color='Yellow', key='-TAB0-'),
        sg.Tab('User-Based', tab_UserBased, title_color='Red', key='-TAB1-'),
        sg.Tab('Item-Based', tab_ItemBased,title_color='Blue',key='-TAB2-'),
        sg.Tab('SVD', tab_SVD,title_color='Black', key='-TAB3-')]],
        key='-TABGROUP-'
        )]        

rodape = [sg.Text('Dados estatísticos', key='-RODAPE-')]

layout_master = [ frame_layout, layout_tab, rodape]
        
def janela_freq_movies(lista=[]):
    #data = [[356, 81491, 'Forrest Gump (1994)', 'Comedy|Drama|Romance|War'], [318, 81482, 'Shawshank Redemption, The (1994)', 'Crime|Drama'], [296, 79672, 'Pulp Fiction (1994)', 'Comedy|Crime|Drama|Thriller'], [593, 74127, 'Silence of the Lambs, The (1991)', 'Crime|Horror|Thriller'], [2571, 72674, 'Matrix, The (1999)', 'Action|Sci-Fi|Thriller'], [260, 68717, 'Star Wars: Episode IV - A New Hope (1977)', 'Action|Adventure|Sci-Fi'], [480, 64144, 'Jurassic Park (1993)', 'Action|Adventure|Sci-Fi|Thriller'], [527, 60411, "Schindler's List (1993)", 'Drama|War'], [110, 59184, 'Braveheart (1995)', 'Action|Drama|War'], [2959, 58773, 'Fight Club (1999)', 'Action|Crime|Drama|Thriller']]
    tabela = [sg.Table(values=lista,
                  headings = ['movieId', 'Votos','Título', 'Gênero'],
                  auto_size_columns=True,
                  num_rows = min(25, 2000))]
    rodape = str(len(lista))+ " filmes"                
    window = sg.Window("Frequência dos filmes", [tabela,[sg.Text(rodape)]], modal=True)
    janela['-TABLE_FREQ-'].update(values=lista)
    janela['-RODAPE1-'].update(rodape)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    window.close()

def atualizar_rodape(texto):
    janela['-RODAPE-'].update(texto)

def janela_matriz_pivot(data):
    lista = data.values.tolist()[:2000]
    matriz = [sg.Table(values=lista,
                  headings = list(data.columns)[:10], #nomes dos filmes
                  auto_size_columns=True,
                  num_rows = min(25, 2000))]
    rodape = str(len(lista))+ " usuários"  
    window = sg.Window("Matriz usuário X filme", [matriz,[sg.Text(rodape)]], modal=True)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    window.close()

def janela_usuario(linha):
    usuario = lista_usuarios.iloc[linha]
    userId = usuario.name
    texto = [sg.Text('Dados do usuário {}'.format(userId))]
    lista = [sg.Table(values = rs.get_movies_from_user(userId),
        size =(80, 12), headings=['Título', 'Nota'])],
    window = sg.Window("Usuário {}".format(str(userId)),[texto,lista], modal=True)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    window.close()

def janela_rec_user(linha, n_similares):
    usuario = lista_usuarios.iloc[linha]
    userId = usuario.name    
    lista = [sg.Table(values = rs.rec_user_based(userId, n_similares).reset_index().values.tolist(),
        size =(80, 12), headings=['Título', 'Rating', 'Votos'])],
    window = sg.Window("Recomendações para usuário {}".format(str(userId)),[lista], modal=True)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    window.close()

janela = sg.Window(title="Recommendation System - Atividade 1 - Collaborative Filtering", layout=layout_master) #, margins=(600, 400))


# This is an Event Loop
while True:  
    event, values = janela.read()    
    print(event)
    print(values)
    global lista_frequencias
    global lista_usuarios
    
    if event in (None, 'Exit'):
        break
    else:
        match event:
            case 'LOAD':
                #Carregar arquivos, mostrar dados estatísticos, HABILITAR DEMAIS BOTOES
                atualizar_rodape(rs.load_files(values['-RATING_FILENAME-'], values['-MOVIE_FILENAME-']))
                janela['-BTN_FMovies-'].update(disabled=False)
                janela['-BTN_PIVOTAR-'].update(disabled=False)
            case '-BTN_FMovies-':
                lista_frequencias = rs.gerar_freq_movies().values.tolist()   
                rodape = str(len(lista_frequencias))+ " filmes"                
                janela['-TABLE_FREQ-'].update(values=lista_frequencias)
                janela['-RODAPE1-'].update(rodape) 
                janela['-BTN_SUPORTE-'].update(disabled=False)  
                janela['-BTN_USERS-'].update(disabled=False)
                janela['-BTN_ITEMS-'].update(disabled=False)
                janela['-TABGROUP-'].Widget.select(0) #Exibit aba 0
            case '-BTN_PIVOTAR-':
                janela_matriz_pivot(rs.pivotar_ratings_users())
                janela['-BTN_USERS-'].update(disabled=False)
            case '-BTN_USERS-':
                rs.pivotar_ratings_users()
                lista_usuarios = rs.descrever_users()
                janela['-TABLE_USERS-'].update(values=lista_usuarios.reset_index().values.tolist())
                janela['-RODAPE2-'].update(str(len(lista_usuarios))+ " usuários.")
                janela['-TABGROUP-'].Widget.select(1)
            case '-BTN_ITEMS-':
                if (values['-TABLE_FREQ-'] == []):
                    sg.Popup('Selecione um filme na 1ª aba!')
                    janela['-TABGROUP-'].Widget.select(0)
                else:
                    titulo_filme = lista_frequencias[values['-TABLE_FREQ-'][0]][2]
                    janela['-TABGROUP-'].Widget.select(2) #Aba de items
                    janela['-TABLE_ITEMS-'].update(rs.rec_item_based(titulo_filme).values.tolist())
            case 'TEST':
                print('Teste :)')  
            case '-BTN_SUPORTE-':
                suporte = int(values['-VALOR_SUPORTE-'])
                lista_frequencias = rs.gerar_freq_movies(suporte).values.tolist()   
                janela_freq_movies(lista_frequencias)  
                print(len(lista_frequencias)," filmes agora.")        
            case 'Close':
                print (len(rs.ratings))
            case '-TABLE_USERS-':
                janela_usuario(values['-TABLE_USERS-'][0])
                janela['-BTN_USER_COSINE-'].update(disabled=False)
            case '-BTN_USER_COSINE-':
                janela_rec_user(values['-TABLE_USERS-'][0],values['-N_SIMILAR_USERS-'])
            case '-LIST1-':
                sg.theme(values['-LIST1-'][0])
                sg.popup_get_text('This is {}'.format(values['-LIST1-'][0]))
            case 'Exit':
                break
          
janela.close()