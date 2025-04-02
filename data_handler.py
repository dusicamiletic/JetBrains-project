import requests
import xml.etree.ElementTree as ET 
import pandas as pd 
import re 
import nltk 



class DataHandler:
    def __init__(self):
        self.file_path = None
        
    def set_file_path(self, file_path):
        self.file_path = file_path
        
    def get_file_path(self):
        return self.file_path

#%%function to load PMIDs from PMIDs_list.txt
    def load_pmids_from_file(self):
        
        if not self.file_path:
            raise ValueError("File path is not set. Use set_file_path() first.")
        
        
        with open(self.file_path, "r") as file:
            pmids=[line.strip() for line in file.readlines()]
            
            
        return pmids 

#%%function to get GEO IDs from PMIDs list 
    def get_geo_ids_from_pmids(self, pmids):
        #need to provide API endpoint to automatically search data
        #we want to connect data between databases 
        #automatically retrieve results in XML format 
        #API endpoint
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
        geo_ids={}
        
        for pmid in pmids:
            params={
                "dbfrom":"pubmed",
                "db":"gds",
                "linkname":"pubmed_gds",
                "id":pmid,
                "retmode":"xml"
            }
            #use of request library to send HTTP GET request to API
            #request library connects base_url and params into one single url 
            #https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=gds&linkname=pubmed_gds&id=25404168&retmode=xml
    
            response=requests.get(base_url, params=params)
            #results saved in response - GET HTTP request 
            
            if response.status_code==200:
                #turn into object root that can be analyzed
                root=ET.fromstring(response.content)
                gse_ids=[id_elem.text for id_elem in root.findall(".//Link/Id")]
                #search for GEO Id tags inside of <Link>
                geo_ids[pmid]=gse_ids if gse_ids else ["No GEO IDs connected"]
            else:
                geo_ids[pmid]=["Request error"]
                
                         
        return geo_ids    

#%%save results 
    def save_results_to_file(self, results, output_file):
        with open(output_file, "w") as file:
            for pmid, gse_ids in results.items():
                file.write(f"PMID:{pmid} -> GEO IDs: {', '.join(gse_ids)}\n")
                
                
#%% Overall design from Bioproject DataBase 

    def get_overall_design(self, bioproject_id):
        
        if bioproject_id != "N/A":
            
            params1 = {
                "db" : "bioproject",
                "id": bioproject_id,
                "retmode" : "xml"
                }
            
            bioproject_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            
            response1 = requests.get(bioproject_url, params=params1)
        

        
            if response1.status_code == 200:
                
                response_text = response1.text
            
                start_tag = "<Description>" 
                end_tag = "</Description>"
            
                description_start = response_text.find(start_tag)
                description_end = response_text.find(end_tag)
                
                if description_start != -1 and description_end != -1:
            
                    description = response_text[description_start + len(start_tag): description_end].strip()
                    
                    # Ispis celokupnog opisa da biste proverili šta se nalazi
                    #print(f"Full Description: {description}")
                    
                    match = re.search(r"Overall design:(.*)", description)
                
                    # Ako je pronađena sekvenca "Overall design:"
                    if match:
                        overall_design = match.group(1).strip()
                    else:
                        overall_design = "N/A" #Nema 'Overall design:' u opisu.
                else:
                        overall_design = "N/A" #Nema 'Description' u odgovoru.
            else:
                    overall_design = "N/A" #Greška u API odgovoru za Bioproject.

        else:
            
           
            overall_design = "N/A" #Nema bioproject ID-a.
        
        return overall_design 
    
              
                
#%% GET GEO ID DATA 
#preuzimanje podataka za jedan GEO ID
#funkcija za izdvajanje podataka o JEDNOM GEO DATASET-u

    def get_geo_data(self, geo_id):
        #API URL za preuzimanje podataka, base URL
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        
        #parametri API poziva
        params = {
            "db":"gds",
            "id": geo_id, 
            "retmode":"json"
            }
        
        #slanje zahteva
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return {"error": f"Request failed with status code {response.status_code}"}
        
        try:
            data=response.json() #parsiranje JSON odgovora
            
            #da li postoji key result:
            if "result" not in data:
                return {"error" : "No result found with provided GEO ID."}
        
            #podaci za jedan dataset
            dataset = data["result"][geo_id]
            title = dataset.get("title", "N/A")
            exp_type = dataset.get("gdstype", "N/A")
            summary = dataset.get("summary", "N/A")
            organism = dataset.get("taxon", "N/A")  # Organism
            
            
            bioproject_id = dataset.get("bioproject", "N/A")  
            overall_design = self.get_overall_design(bioproject_id)
            
        
            return title, exp_type, summary, organism, overall_design
        except Exception as e:
            return {"error" : f"Error processing data: {str(e)}"}
           
#%% all GEO Datasets info load 


#funkcija za obradu fajla PMID_to_GEO_results.txt 
#iz liste PMIDs i povezanih GEO IDs - input file
#kreira se output file - podaci o GEO datasetovima

    def process_pmid_geo_file(self, input_file, output_file):
        
        print(f"Processing data from {input_file}")
        
        with open(input_file, 'r') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            for line in infile:
                #parsiranje linije
                parts=line.strip().split(" -> ")
                pmid = parts[0].replace("PMID:","").strip() #izvlacim samo PMID ID
                geo_ids = parts[1].replace("GEO IDs:","").strip().split(", ") #povezani GEO IDovi, odvajam ih na osnovu zareza
                
                
                #pisanje naslovne linije sa PMID
                outfile.write(f"PMID: {pmid}\n")
                
                #prolaz kroz svaki GEO ID
                for geo_id in geo_ids:
                    title, exp_type, summary, organism, overall_design = self.get_geo_data(geo_id)
                    #ispis svih podataka u fajl 
                    outfile.write(f"\tGEO ID: {geo_id}\n")
                    outfile.write(f"\t\tTitle: {title}\n")
                    outfile.write(f"\t\tExperiment type: {exp_type}\n")
                    outfile.write(f"\t\tSummary: {summary}\n")
                    outfile.write(f"\t\tOrganism: {organism}\n")
                    outfile.write(f"\t\tOverall design: {overall_design}\n")
                outfile.write("\n")  # Dodavanje praznog reda između različitih PMID
                
                
        print(f"Processed data and stored in {output_file}") 
    

#%%
#input file = "PMID_GEO_data.txt"
#ucitavanje u dataFrame svih podataka vezanih za GEO datasetove, iz .txt fajla 

    def turn_data_into_dataFrame(self, input_file):
        
        with open(input_file, "r", encoding = 'utf-8') as f:
            lines = f.readlines()
            
        data = "".join(lines) #pretvaram u string    
            
        pmid_pattern = r"PMID:\s*(\d+)"
        geo_id_pattern = r"GEO ID:\s*(\d+)"
        title_pattern = r"Title:\s*(.+)"
        experiment_type_pattern = r"Experiment type:\s*(.+)"
        summary_pattern = r"Summary:\s*(.+?)\s+Organism"
        organism_pattern = r"Organism:\s*(.+?)\s+Overall design"
        overall_design_pattern = r"Overall design:\s*(.+?)(?:\n|$)" #till new row or end of string 
    
    
        #podela svih zapisa tako da je svaki element tekst izmedju dva PMID-a
        entries = re.split(r"PMID:\s*\d+", data)[1:]
        pmids = re.findall(pmid_pattern, data) #izlistam sve PMIDs
    
        records = []
        for pmid, entry in zip(pmids, entries):
            geo_ids = re.findall(geo_id_pattern, entry) 
            titles = re.findall(title_pattern, entry)
            experiment_types = re.findall(experiment_type_pattern, entry)
            summaries = re.findall(summary_pattern, entry)
            organisms = re.findall(organism_pattern, entry)
            overall_designs = re.findall(overall_design_pattern, entry)
    
            #sad iterirati kroz svaki GEO ID, sacuvati podatke zajedno 
            for i in range(len(geo_ids)):
                record = {
                    "PMID" : pmid, 
                    "GEO ID" : geo_ids[i] if i < len(geo_ids) else None,
                    "Title" : titles[i] if i < len(titles) else None, 
                    "Experiment type" : experiment_types[i] if i < len(experiment_types) else None, 
                    "Summary" : summaries[i] if i < len(summaries) else None, 
                    "Organism" : organisms[i] if i < len(organisms) else None, 
                    "Overall design" : overall_designs[i] if i < len(overall_designs) else None
                }
                records.append(record)  #lista recnika (hash-mapa)
    
        df = pd.DataFrame(records)
        print("Data succesfully packed in DataFrame!")
        
        return df           

#%%
