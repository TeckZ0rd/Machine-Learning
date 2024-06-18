from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import spacy
import nltk
from transformers import pipeline
import json
nltk.download('punkt')
nltk.download('stopwords')


stopwords = set(stopwords.words('english'))
nlp_model = spacy.load('en_core_web_lg')
# data = open("../webscraped data/traveltriangle.txt", "r").read()
data = open("../webscraped data/vietnam_traveltriangle.txt", "r", encoding='utf-8').read()
data_processed = nlp_model(data)

sentences = [sent.text.strip() for sent in data_processed.sents]


# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
pipeline_model = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")
sentences_processed = []
current_index = 0
attractions = {}
for sentence in sentences:
    s = sentence.split("\n")
    for i in s:
        s_ = i.split(".")
        sentences_processed.extend(s_)

for index in range(len(sentences_processed)):
    sentence = sentences_processed[index].strip()
    if sentence.isdigit():
        val = int(sentences_processed[index])
        if val == current_index + 1:
            current_index += 1
            attractions[current_index] = ""
    
    else:
        if current_index != 0:
            attractions[current_index] += (sentence + " ")


# result = {}

# write_file = open("../after_scraping/Initial/traveltriangle_after-vietnam.txt", "w")
write_file = open("../after_scraping/Initial/traveltriangle_after-vietnam.txt", "w", encoding='utf-8')

json_data = {}
context_id = 0
for id, attraction_data in attractions.items():
    words = word_tokenize(attraction_data)
    words = [w for w in words if w != ":" and w != "-" and w.lower() != "image" and w.lower() != "credit" and w.lower() != "source"]
    val = {"Location": "", "Timings": "", "Entry Fee": "", "Description": "", "Built By": "", "Built In": "", "Price For Two": ""}
    current = "Description"
    count = 0
    while (count < len(words)):
        word = words[count].lower()
        if word == "location":
            current = "Location"

        elif word == "timings":
            current = "Timings"
            
        elif (word == "entry" and words[count + 1].lower() == "fee"):
            current = "Entry Fee"
            count += 2; continue
        elif (word == "fee"):
            current = "Entry Fee"
        elif (word == "price" and words[count + 1].lower() == "for" and words[count + 2].lower() == "two"):
            current = "Price For Two"
            count+=3;continue
        elif word == "built" and words[count + 1].lower() == "by":
            current = "Built By"
            count+=2;continue

        elif word == "built-in":
            current = "Built In"

        elif word == "how" and words[count + 1].lower() == "to" and words[count + 2].lower() == "reach":
            current = "Location"
            count +=3; continue
        
        else:
            val[current] += (word + " ")
        
        count += 1

    question1 = "What is the name of the attraction?"
    name = pipeline_model(question=question1, context=str(val["Description"]))
    if val["Location"]:
        question2 = "What is the location of the attraction?"
        location = pipeline_model(question=question2, context=val["Location"])
    else:
        location =  {"answer": "Not Found"}

    if val["Timings"]:
        question3 = "What are the timings of the attraction?"
        timings = pipeline_model(question=question3, context=val["Timings"])
    else:
        timings = {"answer": "Not Found"}
    if val["Entry Fee"]:
        question4 = "What is the entry fee of the attraction?"
        entry_fee = pipeline_model(question=question4, context=val["Entry Fee"])
        if "no" in entry_fee["answer"].lower():
            entry_fee = {"answer": "No"}
    else:
        entry_fee =  {"answer": "Not Found"}

    if val["Built In"]:
        question5 = "When was the attraction built?"
        built_in = pipeline_model(question=question5, context=val["Built In"])
    else:
        built_in =  {"answer": "Not Found"}

    if val["Built By"]:
        question6 = "Who built the attraction?"
        built_by = pipeline_model(question=question6, context=val["Built By"])

    else:
        built_by =  {"answer": "Not Found"}

    if val["Price For Two"]:
        question7 = "What is the price for two at the attraction in inr?"
        price_for_two = pipeline_model(question=question7, context=val["Price For Two"])
    else:
        price_for_two =  {"answer": "Not Found"}

    write_file.write(
f"""
Name: {name['answer']}
Location: {location['answer']}
Timings: {timings['answer']}
Entry Fee: {entry_fee['answer']}
Built In: {built_in['answer']}
Built By: {built_by['answer']}
Price For Two: {price_for_two['answer']}
Description: {val['Description']}
""")
    
    json_data[str(context_id)] = attraction_data
    context_id += 1



with open("../after_scraping/Context-Data/fine-tuning-traveltriangle-vietnam.json", "w") as f:
    json.dump(json_data, f, indent=4)

write_file.close()