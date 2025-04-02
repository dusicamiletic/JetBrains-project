from flask import Flask, request, jsonify, redirect, url_for, session
import requests
import json
import pandas as pd 
import numpy as np
import os 

#from get_GEO_IDs_from_PMIDs import get_geo_ids_from_pmids
#from save_GEO_IDs_from_PMIDs import save_results_to_file
#from process_pmid_geo_file import process_pmid_geo_file
#from turn_data_into_dataframe import turn_data_into_dataFrame
#from preprocess_dataFrame import preprocess_dataFrame
#from tf_idf_vectorizer import tf_idf_vectorizer


from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px


from data_handler import DataHandler 
from data_processor import DataProcessor
from visualization import Visualizer 



#kreiranje aplikacije
app = Flask(__name__)
#objekat app predstavlja nasu web aplikaciju

#kreiranje rute/putanje 
#mesto na internetu na kojem ce aplikacija da ceka zahteve od korisnika

#kada neko posalje POST zahtev na adresu /visualize, pozovi funkciju visualize
#POST - korisnik salje podatke serveru
#najcesce u formi JSON objekta 
#Flask poziva funkciju visualize

print("Starting Flask app...")

# Globalna promenljiva za HTML grafiku
latest_graph = None


from flask import render_template_string
import matplotlib.pyplot as plt 

@app.route('/', methods=['GET'])
def home():
    
    global latest_graph
    graph_html = latest_graph if latest_graph else "<p>Još uvek nije generisan graf.</p>"
    
    #graph_html = session.get("latest_graph", "<p>Još uvek nije generisan graf.</p>")

    
    return render_template_string(f"""                                
     <html>
     <head>
         <title>GEO Datasets Clusters Visualization</title>    
    </head>
    <body>
        <h1>GEO Datasets Clusters Visualization</h1>
       {graph_html}
    </body> 
    </html>                        
    """), 200
                                   

@app.route('/visualize', methods=['POST'])
def visualize():
    
    print("POST zahtev primljen!")
    
    #azuriranje globalne varijable 
    global latest_graph
    
    #ovde FLASK API prima zahtev sa app_post, uzima poslate podatke
    data = request.get_json() 
    
    if not isinstance(data, list):
        return jsonify({"error" : "Input must be list of PMIDs"}), 400

    dataHandler = DataHandler()
    geo_ids = dataHandler.get_geo_ids_from_pmids(data)
    
    #geo_ids = get_geo_ids_from_pmids(data) 
    pmid_to_geo="C:/Users/a-dmiletic/Downloads/project_directory/PMID_to_GEO_results_proba.txt"  # Gde će se sačuvati rezultati

    dataHandler.save_results_to_file(geo_ids, pmid_to_geo)
    
    geo_data = "C:/Users/a-dmiletic/Downloads/project_directory/PMID_to_GEO_data_proba.txt"
    dataHandler.process_pmid_geo_file(pmid_to_geo, geo_data)
    
    df = dataHandler.turn_data_into_dataFrame(geo_data)
    
    
    csv_file_path = "C:/Users/a-dmiletic/Downloads/project_directory/geo_data.csv"
    df.to_csv(csv_file_path, index=False)  
    print(f"DataFrame saved to {csv_file_path}")
    
    
    dataProcessor = DataProcessor()
    
    p_df = dataProcessor.preprocess_dataFrame(df)
    
    p_csv_file_path = "C:/Users/a-dmiletic/Downloads/project_directory/p_geo_data.csv"
    p_df.to_csv(p_csv_file_path, index=False)  
    print(f"Preprocessed DataFrame saved to {p_csv_file_path}")
    
    #dataFrame
    X_tfidf ,tfidf_df = dataProcessor.tf_idf_vectorizer(p_df)
    tfidf_df.to_csv('tfidf_matrix_proba.csv', index=False)
    print("TF-IDF DataFrame saved.")
    
    pca = PCA(n_components=3)  # Može i 3 za 3D prikaz
    X_pca = pca.fit_transform(X_tfidf.toarray())
    df_pca = pd.DataFrame(X_pca, columns=["PC1", "PC2", "PC3"])

    
    kmeans = KMeans(n_clusters=3, random_state=42) 
    kmeans.fit(X_tfidf)
    p_df['Cluster'] = kmeans.labels_
    df_pca["Cluster"] = p_df["Cluster"]
    
    df_pca["Cluster_Label"] = "Cluster " + df_pca["Cluster"].astype(str)
    
    df_pca["GEO ID"] = p_df["GEO ID"]
    df_pca["PMID"] = p_df["PMID"]


    
    # Generiši interaktivni graf
    fig = px.scatter_3d(df_pca, x="PC1", y="PC2", z="PC3", color="Cluster_Label",
                        hover_data={"PC1": False, "PC2": False, "PC3":False, "GEO ID": True, "PMID": True},
                        title="3D Interactive Cluster Visualization",
                        labels={"PC1": "Principal Component 1", "PC2": "Principal Component 2", "PC3":"Principal Component 3"})
    
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(legend_title_text="Cluster")
    
    
    # Generiši HTML kod za grafiku
    latest_graph = fig.to_html(full_html=False)
    

    # Vratiti HTML šablon sa grafikom
    return redirect(url_for("home"))



#POKRETANJE FLASK APLIKACIJE 
if __name__ == '__main__':
    app.run(debug=True)

#aplikacija se pokrece i postavlja se FLASK server
#Flask server pocinje da slusa zahteve na adresi  http://127.0.0.1:5000 (ova adresa je lokalna, samo za vaš računar).
    

#POKRETANJE APLIKACIJE U CONDA PROMPTU 
#conda activate myenv
#cd C:/Users/a-dmiletic/Downloads
#python app.py

#FLASK POKRECE SERVER -  * Running on http://127.0.0.1:5000

 



