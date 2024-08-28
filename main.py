import PySimpleGUI as sg
from PIL import Image, ExifTags
import io
import os

image_atual = None
image_path = None
image_metadata = {}
previous_state = None


def resize_image(img, new_width=None, new_height=None, keep_aspect_ratio=True):
    largura, altura = img.size
    if keep_aspect_ratio:
        aspect_ratio = largura / altura
        if new_width:
            new_height = int(new_width / aspect_ratio)
        elif new_height:
            new_width = int(new_height * aspect_ratio)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return img

def open_image(filename):
    global image_atual
    global image_path
    global image_metadata
    global previous_state
    image_path = filename
    image_atual = Image.open(filename)
    previous_state = image_atual.copy()

    if image_atual._getexif():
        for k, v in image_atual._getexif().items():
            tag_name = ExifTags.TAGS.get(k)
            if tag_name in ['DateTime', 'Model', 'Make', 'GPSInfo']:
                if tag_name == 'GPSInfo':
                    gps_info = {}
                    for t in v:
                        sub_tag_name = ExifTags.GPSTAGS.get(t)
                        gps_info[sub_tag_name] = v[t]
                    image_metadata['GPSInfo'] = gps_info
                else:
                    image_metadata[tag_name] = v

    img_bytes = io.BytesIO()
    image_atual.save(img_bytes, format='PNG')
    window['-IMAGE-'].update(data=img_bytes.getvalue())
    window['-WIDTH-'].update(value=str(image_atual.size[0]), visible=True)
    window['-HEIGHT-'].update(value=str(image_atual.size[1]), visible=True)
    window['-ASPECT_RATIO-'].update(visible=True)
    window['Redimensionar'].update(visible=True)

def save_image(filename):
    global image_atual
    if image_atual:
        with open(filename, 'wb') as file:
            image_atual.save(file)

def get_gps_decimal(gps_info, ref):
    d, m, s = gps_info
    decimal = d + (m / 60.0) + (s / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def info_image():
    global image_atual
    global image_path
    global image_metadata
    if image_atual:
        largura, altura = image_atual.size
        formato = image_atual.format
        tamanho_bytes = os.path.getsize(image_path)
        tamanho_mb = tamanho_bytes / (1024 * 1024)

        model = image_metadata.get('Model', 'N/A')
        make = image_metadata.get('Make', 'N/A')
        date_time = image_metadata.get('DateTime', 'N/A')

        gps_info = image_metadata.get('GPSInfo', {})
        if gps_info:
            lat = get_gps_decimal(gps_info.get('GPSLatitude', (0, 0, 0)), gps_info.get('GPSLatitudeRef', 'N'))
            lon = get_gps_decimal(gps_info.get('GPSLongitude', (0, 0, 0)), gps_info.get('GPSLongitudeRef', 'E'))
        else:
            lat = 'N/A'
            lon = 'N/A'

        sg.popup(f"Tamanho: {largura} x {altura}\nFormato: {formato}\nTamanho em MB: {tamanho_mb:.2f}\n\n"
                 f"Modelo da Câmera: {model}\nFabricante: {make}\nData/Hora: {date_time}\n"
                 f"Latitude: {lat}\nLongitude: {lon}")

def apply_gray_filter():
    global image_atual
    global previous_state
    if image_atual:
        largura, altura = image_atual.size
        pixels = image_atual.load()
        previous_state = image_atual.copy()

        for w in range(largura):
            for h in range(altura):
                r, g, b = image_atual.getpixel((w, h))
                gray = int(0.1 * r + 0.1 * g + 0.8 * b)
                pixels[w, h] = (gray, gray, gray)

        img_bytes = io.BytesIO()
        image_atual.save(img_bytes, format='PNG')
        window['-IMAGE-'].update(data=img_bytes.getvalue())

def apply_brown_filter():
    global image_atual
    global previous_state
    if image_atual:
        largura, altura = image_atual.size
        pixels = image_atual.load()
        previous_state = image_atual.copy()

        for w in range(largura):
            for h in range(altura):
                r, g, b = image_atual.getpixel((w, h))
                gray = int(0.3 * r + 0.59 * g + 0.11 * b)
                new_r = min(gray + 110, 255)
                new_g = min(gray + 70, 255)
                new_b = gray
                pixels[w, h] = (new_r, new_g, new_b)

        img_bytes = io.BytesIO()
        image_atual.save(img_bytes, format='PNG')
        window['-IMAGE-'].update(data=img_bytes.getvalue())

def invert_colors():
    global image_atual
    global previous_state
    if image_atual:
        largura, altura = image_atual.size
        pixels = image_atual.load()
        previous_state = image_atual.copy()

        for w in range(largura):
            for h in range(altura):
                r, g, b = image_atual.getpixel((w, h))
                inverted_color = (255 - r, 255 - g, 255 - b)
                pixels[w, h] = inverted_color

        img_bytes = io.BytesIO()
        image_atual.save(img_bytes, format='PNG')
        window['-IMAGE-'].update(data=img_bytes.getvalue())

def resize_image_and_show(new_width=None, new_height=None, keep_aspect_ratio=True):
    global image_atual
    if image_atual:
        resized_img = resize_image(image_atual, new_width=new_width, new_height=new_height, keep_aspect_ratio=keep_aspect_ratio)
        img_bytes = io.BytesIO()
        resized_img.save(img_bytes, format='PNG')
        window['-IMAGE-'].update(data=img_bytes.getvalue())
        window['-WIDTH-'].update(value=str(resized_img.size[0]))
        window['-HEIGHT-'].update(value=str(resized_img.size[1]))
    else:
        sg.popup("Nenhuma imagem aberta")

def validate_and_clean_input(value):
    cleaned_value = ''.join(filter(str.isdigit, value))
    return cleaned_value

layout = [
    [sg.Menu([
        ['Arquivo', ['Abrir', 'Salvar', 'Fechar']],
        ['Sobre a imagem', ['Informacoes', 'Aplicar Filtro de Cinza', 'Aplicar Filtro Inverter Cores', 'Aplicar Filtro Marrom']],
        ['Sobre', ['Desenvolvedor']]
    ])],
    [sg.Image(key='-IMAGE-', size=(800, 600))],
    [sg.Text('Largura:'), sg.InputText(key='-WIDTH-', size=(10, 1), enable_events=True, visible=False),
     sg.Text('Altura:'), sg.InputText(key='-HEIGHT-', size=(10, 1), enable_events=True, visible=False)],
    [sg.Checkbox('Manter Proporção', default=True, key='-ASPECT_RATIO-', visible=False)],
    [sg.Button('Redimensionar', visible=False), sg.Button('Sair')]
]

window = sg.Window('Aplicativo de Imagem', layout, finalize=True)

while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, 'Sair'):
        break
    elif event == 'Abrir':
        arquivo = sg.popup_get_file('Selecionar imagem', file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
        if arquivo:
            open_image(arquivo)
    elif event == 'Salvar':
        if image_atual:
            arquivo = sg.popup_get_file('Salvar imagem como', save_as=True,
                                        file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
            if arquivo:
                save_image(arquivo)
    elif event == 'Informacoes':
        info_image()
    elif event == 'Aplicar Filtro de Cinza':
        apply_gray_filter()
    elif event == 'Aplicar Filtro Inverter Cores':
        invert_colors()
    elif event == 'Aplicar Filtro Marrom':
        apply_brown_filter()
    elif event == 'Redimensionar':
        new_width = int(values['-WIDTH-']) if values['-WIDTH-'] else None
        new_height = int(values['-HEIGHT-']) if values['-HEIGHT-'] else None
        keep_aspect_ratio = values['-ASPECT_RATIO-']
        resize_image_and_show(new_width=new_width, new_height=new_height, keep_aspect_ratio=keep_aspect_ratio)
    elif event == '-WIDTH-':
        cleaned_value = validate_and_clean_input(values['-WIDTH-'])
        window['-WIDTH-'].update(value=cleaned_value)
        if cleaned_value and values['-ASPECT_RATIO-']:
            largura_atual = int(cleaned_value)
            altura_atual = int(image_atual.size[1] * largura_atual / image_atual.size[0])
            window['-HEIGHT-'].update(value=str(altura_atual))
    elif event == '-HEIGHT-':
        cleaned_value = validate_and_clean_input(values['-HEIGHT-'])
        window['-HEIGHT-'].update(value=cleaned_value)
        if cleaned_value and values['-ASPECT_RATIO-']:
            altura_atual = int(cleaned_value)
            largura_atual = int(image_atual.size[0] * altura_atual / image_atual.size[1])
            window['-WIDTH-'].update(value=str(largura_atual))
    elif event == 'Desenvolvedor':
        sg.popup('Desenvolvido por Guilherme - BCC 6º Semestre')

window.close()