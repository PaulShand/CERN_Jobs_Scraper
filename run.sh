#!/bin/bash

# Source the environment variables from variables.sh
source variables.sh
SQL_FILE="REMOVE_PAST_DEADLINE.sql"


# Run the Python scripts
echo "Updating CERN database with new jobs..."
python3.10 CERN_jobs.py
python3.10 CERN_jobs_deadline.py

# Execute the SQL file using sqlplus to remove expired jobs
echo checking possible removal
sqlplus -S "${ORACLE_DB_USERNAME}/${ORACLE_DB_PASSWORD}@${ORACLE_DB_DSN} AS SYSDBA" @"${SQL_FILE}"

if [ $? -eq 0 ]; then
    echo "SQL script executed successfully."
else
    echo "SQL script execution failed."
fi

python3.10 CERN_collect_skills.py

echo "Done updating CERN list"

