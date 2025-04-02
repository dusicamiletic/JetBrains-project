import pandas as pd 
import re 
import nltk 

from nltk.corpus import stopwords
from nltk import PorterStemmer
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')  

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()


class DataProcessor:
    def __init__(self):
        self.data=None
        


    def preprocess_text(self, data):
        
        if data is None:
            return ""
    
        #print(data, "\n")
        #step 1 remove special characters, leave letters and numbers
        data = re.sub(r'[^a-zA-Z0-9]', ' ', data)
        #print(data, "\n")
        
        data = re.sub(r'(?<!\w)\d+(?!\w)', ' ', data)
        #remove numbers that aren't part of the word
    
        #step 2 lower characters
        data = data.lower()
        #print(data, "\n")
    
        #step 3  remove stop words
        data = [word for word in data.split(' ') if word not in stopwords.words('english')]
        #print(data, "\n")
    
        #step 4 stemming
        #data = [stemmer.stem(word) for word in data]
        #print(data, "\n")
    
        #step 4 lemmatizing 
        data = [lemmatizer.lemmatize(word) for word in data]
        #print(data, "\n")
    
        #step 5 remove empty strings
        data = [word for word in data if len(word) != 0]
        #print(data, "\n")
    
        #step 6 join into string
        data = " ".join(data)
        #print(data, "\n")
    
        return data      
    
    
    def preprocess_dataFrame(self,df):
        p_df = pd.DataFrame({
        'PMID': df['PMID'],
        'GEO ID': df['GEO ID'],
        'Title': df['Title'].apply(self.preprocess_text),
        'Experiment type': df['Experiment type'].apply(self.preprocess_text),
        'Summary': df['Summary'].apply(self.preprocess_text),
        'Organism': df['Organism'].apply(self.preprocess_text),
        'Overall design': df['Overall design'].apply(self.preprocess_text)  
        })
        
        return p_df
    

    def tf_idf_vectorizer(self, p_df):
        
        text_columns = ['Title', 'Experiment type', 'Summary', 'Organism', 'Overall design']
        corpus = p_df[text_columns].agg(' '.join, axis=1) 
        #combining all words from these columns into 1 long string
        
        #initialize vectorizer
        vectorizer = TfidfVectorizer(max_features=50)
        
        #fit and transform - creating TF-IDF matrix
        X_tfidf = vectorizer.fit_transform(corpus)
        
        #turn into dense format
        dense_tfidf = X_tfidf.toarray()
        
        #turn into dataFrame
        tfidf_df = pd.DataFrame(dense_tfidf, columns = vectorizer.get_feature_names_out())
        
        return X_tfidf, tfidf_df
