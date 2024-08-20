import PySimpleGUI as sg
from PIL import Image, ExifTags
import io
import os

image_atual = None
image_path = None
image_metadata = {}

def resize_image(img):
    img = img.resize((800, 600), Image.Resampling.LANCZOS) 
    return img

def open_image(filename):
    global image_atual
    global image_path
    global image_metadata
    image_path = filename
    image_atual = Image.open(filename)    
    
    # Extracting important metadat
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
    
    resized_img = resize_image(image_atual)
    img_bytes = io.BytesIO()
    resized_img.save(img_bytes, format='PNG')
    window['-IMAGE-'].update(data=img_bytes.getvalue())

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

        # Displaying only relevant metadata
        model = image_metadata.get('Model', 'N/A')
        make = image_metadata.get('Make', 'N/A')
        date_time = image_metadata.get('DateTime', 'N/A')
        
        # GPS Information
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

layout = [
    [sg.Menu([
            ['Arquivo', ['Abrir', 'Salvar', 'Fechar']],
            ['Sobre a imagem', ['Informacoes']], 
            ['Sobre', ['Desenvolvedor']]
        ])],
    [sg.Image(key='-IMAGE-', size=(800, 600))],
]

window = sg.Window('Aplicativo de Imagem', layout, finalize=True)

while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, 'Fechar'):
        break
    elif event == 'Abrir':
        arquivo = sg.popup_get_file('Selecionar imagem', file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
        if arquivo:
            open_image(arquivo)
    elif event == 'Salvar':
        if image_atual:
            arquivo = sg.popup_get_file('Salvar imagem como', save_as=True, file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
            if arquivo:
                save_image(arquivo)
    elif event == 'Informacoes':
        info_image()
    elif event == 'Desenvolvedor':
        sg.popup('Desenvolvido por [Seu Nome] - BCC 6º Semestre')

window.close()

