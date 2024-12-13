import fitz  # PyMuPDF
import os

def pdfscrape(name):
    doc = fitz.open(f'OnlyPDFs/{name}.pdf')
    text = "" 
    for page in doc: 
        text += page.get_text() 

    output_dir = 'text'
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
    output_file = os.path.join(output_dir, f'{name}.txt')
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)
