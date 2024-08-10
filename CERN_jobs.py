import requests
from bs4 import BeautifulSoup
from typing import TypeAlias
import oracledb
import os

# grab Oracle data for container Oracle database 
username = os.getenv('ORACLE_DB_USERNAME')
password = os.getenv('ORACLE_DB_PASSWORD')
dsn = os.getenv('ORACLE_DB_DSN')

# Oracle database connection setup
connection = oracledb.connect(user=username, password=password, dsn=dsn, mode=oracledb.SYSDBA)
cursor = connection.cursor()

# URL of the early career CERN page
url = 'https://careers.smartrecruiters.com/CERN/entry-levels'

# Fetch the webpage content
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all job postings on the page
job_postings = soup.find_all('li', class_='opening-job')

# record current division and department I am aware to label
known_department = {"IR": "International Relations", "SCE": "Site and Civil Engineering Department", "TE": "Technology Department", "SY": "Accelerator Systems Department",
                    "EN": "Enginering Department", "DG": "Legal", "FAP": "Finance and Administrative Process", "EP": "Experimental Physics Department", "IT": "Information Technology"}
known_division = {"ABT": "Accelerator Beam Transfer", "AR": "Administration and Resources", "BI": "Beam Instrumentation", "EPC": "Electrical Power Converters", "RF": "Radio Frequency",
                  "STI": "Sources, Target and Interactions", "CRG" : "Cryogenics", "MSC": "Magnets, Superconductors, and Cryostats", "VSC": "Vacuum, Surfaces & Coatings",
                  "EL": "Electrical Engineering", "AA": "Access & Alarms", "ACE": "Accelerator Coordination and Engineering", "CV": "Cooling and Ventilation",
                  "HE": "Handling Engineering", "IM": "Information Management", "MME": "Mechanical and Materials Engineering", "PAS": "Planning Administration & Safety",
                  "SFT": "Software Development for Experiments", "CMX":"Compact Muon Solenoid", "ADT": "A Large Ion Collider Experiment", "ESE": "Electronics Systems for Experiments",
                  "CMG": "Compact Muon Solenoid", "DT": "Detector Technology", "PW":"Platforms & Workflows","DA":"Databases & Analytics"}

# given job title and "work tag" decipher job title, work tag, department, division
def extract_group(position_group: str) -> list[str,str,str,str]:
    words = position_group.split()
    position = " ".join(words[:-1])
    work_tag = words[-1][1:-1]
    department, division = work_tag.split("-")[:2]

    if department in known_department:
        department = known_department[department]
        if division in known_division:
            division = known_division[division]

    return [position, work_tag, department, division]

# Loop through each job posting and extract the details
for job in job_postings:
    # Extract the job link
    job_link = job.find('a', class_='link--block details')['href']
    
    # Extract the job position (title)
    position_group = job.find('h4', class_='job-title').text.strip()
    position, work_tag, department, division = extract_group(position_group)

    # Append the extracted information as a dictionary to the jobs list
    if department not in {"International Relations", "Site and Civil Engineering Department", "Legal", "Finance and Administrative Process","Information Technology"}:
        # Check if the work_tag already exists in the database
        cursor.execute("SELECT COUNT(*) FROM CERN_Listing WHERE worktag = :work_tag", [work_tag])
        result = cursor.fetchone()
        if result[0] == 0:  # If work_tag does not exist, insert the new record
            insert_query = '''
            INSERT INTO CERN_Listing (department, division, Position, worktag, job_link)
            VALUES (:department, :division, :position, :work_tag, :job_link)
            '''
            cursor.execute(insert_query, [department, division, position, work_tag, job_link])
            print(f"Inserted: {work_tag} - {position}")

# Commit the transaction
connection.commit()

# Close the database connection
cursor.close()
connection.close()
