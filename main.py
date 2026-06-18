import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import pygame
from mutagen.mp3 import MP3
import os
import json
import sys

def resource_path(arquivo):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, arquivo)
    return arquivo



#CONFIG
pygame.mixer.init()
ctk.set_appearance_mode("dark")
playlist_file = "playlist.json"


#JANELA
janela = ctk.CTk()
janela.iconbitmap(resource_path("icone.ico"))
janela.title("OrangeMusic")
janela.geometry("900x700")
janela.configure(fg_color="#000000")



#CARREGANDO AS IMAGENS
image_pause = ctk.CTkImage(Image.open(resource_path("pause.png")) , size=(65, 65))
image_anterior = ctk.CTkImage(Image.open(resource_path("anterior.png")) , size=(45, 45))
image_proximo = ctk.CTkImage(Image.open(resource_path("proximo.png")) , size=(45, 45))
image_play = ctk.CTkImage(Image.open(resource_path("play.png")) , size=(65, 65))

#GIF FUNDO
gif_label=ctk.CTkFrame(janela, corner_radius=0 , border_width=0 , fg_color="transparent" )
gif_label.place(x=0,y=0,relwidth=1,relheight=1)
gif = Image.open(resource_path("fundo.gif"))

frames_originais = []
for frame in ImageSequence.Iterator(gif):
    frames_originais.append(frame.copy())
img_label = tk.Label(gif_label, bd=0, bg="black" , highlightthickness=0 , borderwidth=0)
img_label.place(x=0, y=0, relwidth=1, relheight=1)

gif_label.lift()

frame_index = 0
foto_atual = None



def animar_gif():
    global frame_index , foto_atual

    largura = janela.winfo_width()
    altura = janela.winfo_height()

    if largura > 1 and altura > 1:
        frame_redim = frames_originais[frame_index].resize((largura, altura))
        foto_atual = ImageTk.PhotoImage(frame_redim)
        img_label.configure(image=foto_atual)
        img_label.image = foto_atual

    frame_index = (frame_index + 1) % len(frames_originais)

    janela.after(45, animar_gif)

animar_gif()



#VARIAVEIS
musica_atual = ""
movendo_barra = False
pausado = False
tempo_inicio = 0
playlist = []
indice_atual =-1
playlist_visivel = False



#PERSISTÊNCIA
def salvar_playlist():
    with open(playlist_file, "w" , encoding="utf-8") as f:
        json.dump(playlist, f , ensure_ascii=False, indent=2)

def carregar_playlist_salva():
    global playlist
    if os.path.exists(playlist_file):
        with open(playlist_file, "r" , encoding="utf-8") as f:
            dados = json.load(f)
        playlist = [m for m in dados if os.path.exists(m["caminho"])]
        salvar_playlist()

#FUNÇÔES DE REPRODUÇÂO
def tocar_por_indice(idx):
    global musica_atual , indice_atual , tempo_inicio , pausado
    if idx <0 or idx >= len(playlist):
        return
    indice_atual = idx
    musica_atual = playlist[idx]["caminho"]
    tempo_inicio = 0
    pausado = False

    label_musica.configure(text=playlist[idx]["nome"])
    btn_pause.configure(text="")
    audio = MP3(musica_atual)
    duracao = int(audio.info.length)
    barra.configure(to=duracao)
    barra.set(0)

    pygame.mixer.music.load(musica_atual)
    pygame.mixer.music.play()
    atualizar_lista_ui()


#FUNÇÕES
def carregar_musica():
    arquivos = filedialog.askopenfilenames(filetypes=[("Arquivos MP3", "*.mp3")])
    for caminho in arquivos:
        nome = caminho.split("/")[-1].replace(".mp3" , "")
        if not any(m["caminho"] == caminho for m in playlist):
            playlist.append({"caminho": caminho, "nome": nome})
    salvar_playlist()
    atualizar_lista_ui()
    if musica_atual == "" and len(playlist) > 0:
        tocar_por_indice(0)



def remover_musica(idx):
    global indice_atual , musica_atual
    if idx <0 or idx >= len(playlist):
        return
    era_atual = (idx == indice_atual)
    playlist.pop(idx)
    salvar_playlist()

    if era_atual:
        pygame.mixer.music.stop()
        musica_atual = ""
        indice_atual = -1
        label_musica.configure(text="Nenhuma mídia de reprodução carregada")
        barra.set(0)
        tempo_label.configure(text="00:00")
        btn_pause.configure(text="")
        if len(playlist) > 0:
            novo_idx = min(idx, len(playlist) - 1)
            tocar_por_indice(novo_idx)
    elif idx < indice_atual:
        indice_atual -= 1
    atualizar_lista_ui()

def atualizar_lista_ui():
    for widget in frame_lista_interna.winfo_children():
        widget.destroy()
    for i, musica in enumerate(playlist):
        cor_fundo = "#2a1200" if i == indice_atual else "#1a1a1a"
        cor_texto = "#ff8352" if i == indice_atual else "#dddddd"

        item_frame = ctk.CTkFrame(frame_lista_interna , fg_color=cor_fundo , corner_radius=8)
        item_frame.pack(fill="x" , padx=6 , pady= 2)

        nome_curto = musica["nome"][:40] + "..." if len(musica["nome"]) > 40 else musica["nome"]

        btn_nome = ctk.CTkButton(item_frame, text=f"{nome_curto}" , anchor="w" ,
            fg_color="transparent" , hover_color="#3a2000" , text_color=cor_texto , font=("Product Sans", 13 , "bold"),
            cursor="hand2" , command=lambda idx=i: tocar_por_indice(idx))
        btn_nome.pack(side="left", fill="x", expand=True)

        btn_remover = ctk.CTkButton(item_frame,
            text="✕" , width=30 , height=28 , fg_color="transparent" , hover_color="#3a2000",
            font=("Product Sans", 13 , "bold"), cursor="hand2" , command=lambda idx=i: remover_musica(idx))
        btn_remover.pack(side="right", padx=4)



def toggle_playlist():
    global playlist_visivel
    if playlist_visivel:
        frame_playlist.pack_forget()
        playlist_visivel = False
        btn_playlist.configure(text="☰  Playlist")

    else:
        frame_playlist.pack(in_=gif_label, pady=5 , padx=20 , fill="x", after=frame_controles)
        playlist_visivel = True
        btn_playlist.configure(text="✕  Fechar")
        atualizar_lista_ui()

def tocar():
    global tempo_inicio
    if musica_atual == "":
        return
    pygame.mixer.music.load(musica_atual)
    pygame.mixer.music.play(start=tempo_inicio)


def pause():
    global pausado

    if musica_atual == "":
        return
    if not pygame.mixer.music.get_busy() and not pausado:
        tocar()
        btn_pause.configure(image=image_pause)
        return
    if not pausado:
        pygame.mixer.music.pause()
        pausado = True
        btn_pause.configure(image=image_play)

    else:
        pygame.mixer.music.unpause()
        pausado = False
        btn_pause.configure(image=image_pause)

def parar_musica():
    global tempo_inicio
    pygame.mixer.music.stop()
    tempo_inicio = 0
    barra.set(0)
    tempo_label.configure(text="00:00")

def mudar_volume(valor):
    volume = float(valor) / 100
    pygame.mixer.music.set_volume(volume)


def atualizar_tempo():
    global movendo_barra
    global tempo_inicio

    if pygame.mixer.music.get_busy():
        tempo_atual = (pygame.mixer.music.get_pos() // 1000 ) + tempo_inicio

        minutos = tempo_atual // 60
        segundos = tempo_atual % 60

        tempo_label.configure(text=f"{minutos:02d}:{segundos:02d}")

        if not movendo_barra:
            barra.set(tempo_atual)

    janela.after(1000, atualizar_tempo)

def ativar_barra(event):
    global movendo_barra
    movendo_barra = True

def soltar_barra(event):
    global movendo_barra
    global tempo_inicio

    movendo_barra = False
    tempo_inicio = int(barra.get())
    pygame.mixer.music.load(musica_atual)
    pygame.mixer.music.play(start=tempo_inicio)

def mudar_tempo(valor):
    segundos = int(float(valor))
    minutos = segundos // 60
    segundos_restantes = segundos % 60

    tempo_label.configure(text=f"{minutos:02d}:{segundos_restantes:02d}")

def proxima_musica():
    if len(playlist) == 0:
        return
    novo_idx = (indice_atual + 1) % len(playlist)
    tocar_por_indice(novo_idx)

def musica_anterior():
    if len(playlist) == 0:
        return
    novo_idx = (indice_atual - 1) % len(playlist)
    tocar_por_indice(novo_idx)



#TITULO
titulo=ctk.CTkLabel(gif_label, text="OrangeMusic" , font=("Product Sans", 93, "bold") , text_color="#ff7226" , fg_color="transparent")
titulo.pack(pady=20)



#FRAME MUSICA
frame_musica = ctk.CTkFrame(gif_label, fg_color="#141414" , border_width=0)
frame_musica.pack(pady=0, side="bottom")



#NOME DA MUSICA
label_musica = ctk.CTkLabel(frame_musica, text="Nenhuma mídia de reprodução carregada", font=("Product Sans", 18 , "bold") , fg_color="transparent" )
label_musica.pack(pady=10)



#FRAME TEMPO+NOME
frame_tempo = ctk.CTkFrame(frame_musica, fg_color="transparent" , border_width=0)
frame_tempo.pack()



#FRAME CONTROLES
frame_controles = ctk.CTkFrame(gif_label, fg_color="transparent" , border_width=0)
frame_controles.pack(pady=20 , expand=False)



#FRAME BOTÕES
frame_botoes = ctk.CTkFrame(frame_controles, fg_color="transparent" , corner_radius=20 , border_width=0)
frame_botoes.pack(side="left", padx=25)



#FRAMES NAV
frame_nav = ctk.CTkFrame(frame_musica, fg_color="transparent")
frame_nav.pack(pady=(0, 4))



#FRAME PLAYLIST
frame_playlist = ctk.CTkFrame(gif_label, fg_color="#0f0f0f" , corner_radius=12 , border_width=1 , border_color="#3a1a00")
frame_playlist_header = ctk.CTkFrame(frame_playlist, fg_color="transparent")
frame_playlist_header.pack(fill="x", padx=10, pady=(8, 4))
ctk.CTkLabel(frame_playlist_header, text="Playlist" , font=("Product Sans" , 16 , "bold") , text_color="#ff7842").pack(side="left")

ctk.CTkLabel(
    frame_playlist_header,
    text="(Salva automaticamente)",
    font=("Product Sans" , 11),
    text_color="#666666").pack(side="left" , padx=8)

frame_lista_scroll = ctk.CTkScrollableFrame(frame_playlist, fg_color="transparent" , height=160 , scrollbar_button_color="#ff8352", scrollbar_button_hover_color="#ff7842")
frame_lista_scroll.pack(fill="both", expand=True, padx=6 , pady=(0, 8 ))

frame_lista_interna=ctk.CTkFrame(frame_lista_scroll, fg_color="transparent" )
frame_lista_interna.pack(fill="both", expand=True)



#ESTILO BOTÕES
estilo_botao = {
    "fg_color": "#ff7842",
    "hover_color": "#e06736",
    "text_color": "#1a1a1a",
    "font": ("Product Sans", 17 , "bold"),
    "cursor": "hand2",
    "width": 470,
    "height": 90,
    "corner_radius": 12,
    "border_width": 0,

}

estilo_botao_pequeno = {
    "fg_color": "#ff7842",
    "hover_color": "#e06736",
    "text_color": "#1a1a1a",
    "font": ("Product Sans", 15, "bold"),
    "cursor": "hand2",
    "corner_radius": 12,
    "border_width": 0,
}



#BOTÕES
btn_carregar = ctk.CTkButton(frame_botoes, text="Carregar Mídia .MP3", command=carregar_musica , **estilo_botao)
btn_carregar.pack(pady=4)

btn_anterior = ctk.CTkButton(frame_nav , image=image_anterior , text="" , command=musica_anterior , width=10 , height=25, corner_radius=85,
font=("Arial", 24), fg_color="transparent" ,hover_color="#3a2000" , cursor="hand2")
btn_anterior.pack(side="left")

btn_pause = ctk.CTkButton(frame_nav, image=image_pause , text="", command=pause , width=10, height=30, corner_radius=85, font=("Arial", 24) , fg_color="transparent" ,
hover_color="#3a2000")
btn_pause.pack(side="left")

btn_parar = ctk.CTkButton(frame_botoes, text="Interromper", command=parar_musica , **estilo_botao)
btn_parar.pack()

btn_playlist = ctk.CTkButton(frame_botoes , text="☰  Playlist" , command=toggle_playlist , width=470, height=40, **{k: v for k, v in estilo_botao_pequeno.items()})
btn_playlist.pack(pady=(6, 0))

btn_proximo = ctk.CTkButton(frame_nav , image=image_proximo , text="" , command=proxima_musica , width=10 , height=25, corner_radius=85,
font=("Arial", 24), fg_color="transparent" ,hover_color="#3a2000" , cursor="hand2")
btn_proximo.pack(side="left")



#TEMPO
tempo_label = ctk.CTkLabel(
    frame_tempo,
    text="00:00",
    font=("Product Sans", 27, "bold"),
    fg_color="transparent",
)
tempo_label.pack(side="left" , padx=15)




#VOLUME
volume_barra = ctk.CTkSlider(
    frame_controles,
    from_=0,
    to=100,
    height=218,
    orientation="vertical",
    command=mudar_volume,
    progress_color="#ff956b",
    button_color="#fc6c32",
    button_hover_color="#fc5714",
    border_width=0
)
volume_barra.set(50)
volume_barra.pack(pady=10)



#MUDAR TEMPO
barra = ctk.CTkSlider(
    frame_tempo,
    from_=0,
    to=0,
    orientation="horizontal",
    width=1900,
    command=mudar_tempo,
    progress_color="#ff956b",
    button_color="#fc6c32",
    button_hover_color="#fc5714",
    border_width=0

)

barra.pack(pady=3)
barra.bind("<ButtonPress-1>",ativar_barra)
barra.bind("<ButtonRelease-1>",soltar_barra)

carregar_playlist_salva()
if len(playlist) > 0:
    atualizar_lista_ui()
    label_musica.configure(text=f"{len(playlist)} música(s) na playlist - clique ▶ para tocar ")


#LOOP
atualizar_tempo()
janela.mainloop()