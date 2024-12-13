import psutil
from transformers import pipeline, BartTokenizer

def get_summary(text):
    with open(text, "r", encoding="utf-8") as f:
        input_text = f.read()

    # Initialize tokenizer and summarizer
    tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", tokenizer=tokenizer, device=-1)  # Use CPU

    # Split input text into chunks that fit within the model's maximum input length
    max_input_length = 40000  # Maximum number of tokens for BART
    tokens = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=max_input_length)["input_ids"]
    chunks = [tokens[:, i:i + max_input_length] for i in range(0, tokens.size(1), max_input_length)]

    # Monitor memory usage
    process = psutil.Process()
    print(f"Memory usage before summarization: {process.memory_info().rss / 1024 ** 2} MB")

    summaries = []
    for chunk in chunks:
        chunk_text = tokenizer.decode(chunk[0], skip_special_tokens=True)
        summary = summarizer(chunk_text, max_length=250, min_length=100, do_sample=False)[0]['summary_text']
        summaries.append(summary)

    print(f"Memory usage after summarization: {process.memory_info().rss / 1024 ** 2} MB")

    final_summary = " ".join(summaries)
    output_file = "text/finetuned-summary.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(final_summary)

    return final_summary