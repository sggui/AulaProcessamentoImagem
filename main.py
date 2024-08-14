import PySimpleGUI as sg
from PIL import Image, ImageTk

# Layout do menu
menu_layout = [
    ['Arquivo', ['Abrir Imagem', 'Salvar Como', 'Sair']],
    ['Ajuda', ['Sobre']]
]

# Layout principal
layout = [
    [sg.Menu(menu_layout)],
    [sg.Image(key='-IMAGE-')],
    [sg.Text('', size=(40, 1), key='-FILENAME-')],
]

# Criar a janela com finalize=True
window = sg.Window("Visualizador de Imagens", layout,
                   size=(800, 600), finalize=True)

# Função para abrir a imagem sem salvar temporariamente


def open_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")  # Garantir a compatibilidade
        img = ImageTk.PhotoImage(img)
        return img
    except Exception as e:
        sg.popup(f"Erro ao abrir a imagem: {e}")
        return None


# Loop de eventos
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Sair':
        break
    elif event == 'Abrir Imagem':
        image_path = sg.popup_get_file('Abrir', file_types=(
            ("Arquivos de Imagem", "*.png;*.jpg;*.jpeg"),))
        if image_path:
            img = open_image(image_path)
            if img:
                window['-IMAGE-'].update(data=img)
                window['-FILENAME-'].update(image_path)
    elif event == 'Salvar Como':
        if image_path:
            save_path = sg.popup_get_file('Salvar Como', save_as=True, no_window=True, file_types=(
                ("Arquivos PNG", "*.png"), ("Arquivos JPEG", "*.jpg;*.jpeg")))
            if save_path:
                image = Image.open(image_path)
                image.save(save_path)
                sg.popup('Arquivo salvo com sucesso!')
        else:

            sg.popup('Nenhuma imagem carregada para salvar.')
    elif event == 'Sobre':
        sg.popup('Guilherme Santos Guimarães\nGustavo Piroupo Neumann')


window.close()
