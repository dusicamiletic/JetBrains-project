import requests
from data_handler import DataHandler

#pmid_file_path = "C:/Users/a-dmiletic/Downloads/PMIDs_list.txt" 
#pmid_list = load_pmids_from_file(pmid_file_path)

#url = "http://127.0.0.1:5000/visualize"
#data = pmid_list

#response = requests.post(url, json=data)

# Umesto print(response.json()), sačuvaj HTML i otvori ga
#html_file = "C:/Users/a-dmiletic/Downloads/cluster_visualization.html"
#with open(html_file, "w", encoding="utf-8") as f:
#    f.write(response.text)

#print(f"Visualization saved to {html_file}. Open it in a browser.")


class Client: 
    
    def __init__(self, api_url, pmid_file_path):
        self.api_url = api_url
        self.pmid_file_path = pmid_file_path
        
        
    def send_pmids(self):
        #load PMIDs and send to API visualize
        dataHandler = DataHandler()
        dataHandler.set_file_path(self.pmid_file_path)
        pmid_list = dataHandler.load_pmids_from_file()
        
        response = requests.post(self.api_url, json=pmid_list)
        
        if response.status_code == 200:
            print("PMIDs successfully processed!")
            print("You can view the visualization at: http://127.0.0.1:5000/")
        else:
            print(f"Error: API returned {response.status_code} - {response.text}")
            
   
API_URL = "http://127.0.0.1:5000/visualize"
PMID_FILE = "C:/Users/a-dmiletic/Downloads/PMIDs_list_sample.txt"
       
#run the client  
client = Client(API_URL, PMID_FILE) 


client.send_pmids()

   
            