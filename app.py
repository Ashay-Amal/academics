from flask import Flask, render_template, request
import pandas as pd
from M_summarizer import get_summary
from datetime import datetime
from webscrape import arxivscrape, downloadpdf 
from M_pdfscrape import pdfscrape
from M_ImageCapScrape import extract_images_and_captions
from M_LexRankSummarizer import lexrank
from M_PreProcess import preprocess_sum

import os

app = Flask(__name__)
UPLOAD_FOLDER = 'OnlyPDFs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
titles = []
keytakeaways = []

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")


@app.route("/summary", methods=['GET', 'POST'])
def summary():
    global titles
    global keytakeaways
    if request.method == "POST":
        topic = request.form["input"]
        arxivscrape.scrape(topic)
        df = pd.read_csv("Scrape.csv")
        titles = []
        for i in range(min(3, len(df))):  # Ensure index is within range
            titles.append(df.iloc[i, 0])
        csv_file = "OnlyURL.csv"
        base_filename = "NewPdf"
        target_folder = "OnlyPDFs"
        downloadpdf.download_all_pdfs(csv_file, base_filename, target_folder)
        keytakeaways = []

        # Ensure the text directory exists
        os.makedirs('text', exist_ok=True)

        for i in range(min(3, len(df))):  # Ensure index is within range
            pdfscrape(f'{base_filename}{i}')
            
            keytakeaways.append(lexrank(f'text/{base_filename}{i}.txt'))

        current_dateTime = datetime.now()
        inputs = []
        for i in range(min(3, len(df))):  # Ensure index is within range
            print(current_dateTime)
            preprocess_sum(f'text/{base_filename}{i}.txt')
            newInput = get_summary(f'KeyTakeaway/clean_sum.txt')
            inputs.append(newInput)
            current_dateTime = datetime.now()
            print(current_dateTime)
    return render_template("summary.html", titles=titles, inputs=inputs)

@app.route("/keytakeaway")
def keytakeaway():
    global titles
    global keytakeaways
    return render_template("keytakeaway.html", titles=titles, keytakeaways=keytakeaways)

@app.route("/images")
def images():
    global titles
    base_filename = "NewPdf"
    target_folder = "OnlyPDFs/"
    pdf_location = target_folder + base_filename
    
    images_caption = []
    if len(titles) == 1:
        images_caption.append(extract_images_and_captions(f'{target_folder + titles[0]}.pdf'))
    else:
        for i in range(len(titles)):
            images_caption.append(extract_images_and_captions(f'{pdf_location}{i}.pdf'))

    return render_template("images.html", images_caption = images_caption, data_length = len(images_caption), titles= titles)

@app.route("/upload", methods=("GET","POST"))
def upload():
    if request.method == "POST":
        try:
            pdf = request.files.get("pdf")
            if not pdf:
                raise ValueError("No file uploaded")
            print("File uploaded successfully")
            base_filename = pdf.filename[:-4]
            pdf.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename))
            print(f"File saved to {os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename)}")
            
            # Ensure the text directory exists
            os.makedirs('text', exist_ok=True)
            
            pdfscrape(base_filename)
            print(f"PDF scraped: {base_filename}")
            textFile = 'text/' + base_filename + '.txt'
            keytakeaways.clear()
            keytakeaways.append(lexrank(textFile))
            print(f"Key takeaways extracted from {textFile}")
          
            current_dateTime = datetime.now()
            print(current_dateTime)
            preprocess_sum(textFile)
            print(f"Preprocessed summary for {textFile}")
            inp = get_summary(f'KeyTakeaway/clean_sum.txt')
            print(f"Summary generated for {textFile}")
            titles.clear()
            titles.append(base_filename)
            inputs = []
            inputs.append(inp)
            current_dateTime = datetime.now()
            print(current_dateTime)
        except Exception as e:
            print(f"Error processing upload: {e}")
            return "Internal Server Error", 500

    return render_template("summary.html", titles=titles, inputs=inputs)


if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
