import requests
from bs4 import BeautifulSoup
from typing import TypeAlias
import oracledb
import os
from datetime import datetime
import re

# grab Oracle data for container Oracle database 
username = os.getenv('ORACLE_DB_USERNAME')
password = os.getenv('ORACLE_DB_PASSWORD')
dsn = os.getenv('ORACLE_DB_DSN')

# Oracle database connection setup
connection = oracledb.connect(user=username, password=password, dsn=dsn, mode=oracledb.SYSDBA)
cursor = connection.cursor()

cursor.execute("SELECT worktag, job_link FROM CERN_Listing")
jobs = cursor.fetchall()
cursor.execute("SELECT worktag FROM CERN_Skills")
processed = cursor.fetchall()

processed = {worktag for (worktag,) in processed}


# Function to parse the job page and find the deadline
def find_deadline(job_link: str) -> list[str]:
    response = requests.get(job_link)
    soup = BeautifulSoup(response.content, 'html.parser')
    section = soup.find('div', class_='wysiwyg', itemprop='responsibilities')
    skills_heading = section.find('p', string=lambda t: t and 'Skills and/or knowledge' in t)
    skills_ul = skills_heading.find_next('ul')
    skills = [li.text.strip() for li in skills_ul.find_all('li')]
    return skills


# Iterate through each job and find the deadline
for work_tag, job_link in jobs:
    if work_tag not in processed:
        print(f"{work_tag} skills being added")
        skills = find_deadline(job_link)
        for skill in skills:
            insert_query = '''
            INSERT INTO CERN_skills (worktag, skills)
            VALUES (:work_tag, :skill)
            '''
            cursor.execute(insert_query, [work_tag, skill])


# Commit the changes and close the connection
connection.commit()

# Close the database connection
cursor.close()
connection.close()