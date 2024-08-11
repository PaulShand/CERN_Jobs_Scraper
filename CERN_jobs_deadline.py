import requests
from bs4 import BeautifulSoup
from typing import TypeAlias
import oracledb
import os
from datetime import datetime
import re

def convert_to_sql_date(date_str):
    date_str = re.sub(r'\s*at.*$', '', date_str)
    # Define patterns to match different date formats
    date_patterns = [
        r"(\d{2})\.(\d{2})\.(\d{4})",  # DD.MM.YYYY
        r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})",  # DD Month YYYY
        r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})",  # Month DD, YYYY
        r"(\d{1,2})\s+([A-Za-z]+)",  # DD Month
        r"([A-Za-z]+)\s+(\d{1,2})",  # Month DD
    ]

    # Months mapping
    months = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12",
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            groups = match.groups()
            if len(groups) == 3:  # Full date with year
                day, month, year = groups
                if month.isalpha():
                    month = months[month]
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            elif len(groups) == 2:  # Date without year
                day, month = groups
                if day.isalpha():
                    day, month = month, day
                if month.isalpha():
                    month = months[month]
                return f"{datetime.now().year}-{month.zfill(2)}-{day.zfill(2)}"
    
    # If no pattern matches, raise an error or return None
    raise ValueError(f"Date format not recognized: {date_str}")



# grab Oracle data for container Oracle database 
username = os.getenv('ORACLE_DB_USERNAME')
password = os.getenv('ORACLE_DB_PASSWORD')
dsn = os.getenv('ORACLE_DB_DSN')

# Oracle database connection setup
connection = oracledb.connect(user=username, password=password, dsn=dsn, mode=oracledb.SYSDBA)
cursor = connection.cursor()

cursor.execute("SELECT worktag, job_link, deadline FROM CERN_Listing")
jobs = cursor.fetchall()


# Function to parse the job page and find the deadline
def find_deadline(job_link):
    response = requests.get(job_link)

    soup = BeautifulSoup(response.content, 'html.parser')
    # Example search patterns for a deadline (modify as needed based on actual HTML structure)
    # This example assumes the deadline might be in a <div> or <p> with a specific class or text
    deadline = soup.find('div', class_='wysiwyg', itemprop='incentives').find('p').find('strong').text.strip()
    deadline = convert_to_sql_date(deadline)
    # for tag in soup.find_all(['p', 'div']):
    #     if 'deadline' in tag.text.lower():
    #         deadline = tag.text.strip()
    #         break
    return deadline + " 14:59:00" if deadline else "Deadline not found"



# Iterate through each job and find the deadline
for work_tag, job_link, deadline in jobs:
        if not deadline:
            deadline = find_deadline(job_link)
            # print(f"Work Tag: {work_tag}")
            # print(f"Job Link: {job_link}")
            print(f"Deadline: {deadline}")
            print(work_tag)
            cursor.execute('''UPDATE CERN_Listing SET DEADLINE = TO_DATE(:deadline, 'YYYY-MM-DD HH24:MI:SS') WHERE WORKTAG = :work_tag''', [deadline, work_tag])

# Commit the changes and close the connection
connection.commit()

# Close the database connection
cursor.close()
connection.close()