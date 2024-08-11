# CERN Job Skills Management

## Overview

This project is designed to manage and analyze entry-level job listings at CERN, with a specific focus on departments and the required skills. The project includes collecting CERN job listing data, linking job positions with relevant skills, sorting positions by deadlines, and ensuring data integrity across related tables.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Usage](#usage)
- [TODO](#todo)

## Project Structure

- **`CERN_jobs.py`**: Collects all URLs to job openings, labels them based on their department and division, and populates the `CERN_LISTING` table.
- **`CERN_jobs_deadline.py`**: Gathers the application deadlines from the previously collected list of URLs.
- **`CERN_collect_skills.py`**: Collects the skills needed for each "worktag" associated with every position and populates the `CERN_SKILLS` table.
- **`INIT_TABLE.sql`**: SQL script to initialize the required tables.
- **`REMOVE_PAST_DEADLINE.sql`**: SQL script to remove job positions that have expired based on their deadlines.
- **`run.sh`**: Executes the above scripts in the correct order.
- **`Generated_Table_11-8-2024`**: Example of the collected tables generated on a specific date.

## Database Schema

The project involves the following tables:

- **CERN_skills**
  - **`ID`**: Unique identifier for each combination of `worktag` and associated skill.
  - **`worktag`**: `VARCHAR2(100)` - Identifier for the job position.
  - **`skills`**: `CLOB` - A required skill for the specified position.

- **CERN_listing**
  - **`Department`**: `VARCHAR2(100)` - The specific department of the job, if known.
  - **`Division`**: `VARCHAR2(100)` - The specific division of the job, if known.
  - **`Position`**: `VARCHAR2(100)` - The title of the job position.
  - **`worktag`**: `VARCHAR2(100)` - Identifier for the job position.
  - **`job_link`**: `CLOB` - The URL to the job listing.
  - **`deadline`**: `DATE` - Application deadline for the job.

- **Views**
  - **`most_common_skills`**: Lists skills and their frequency across all job listings.
  - **`position_skills_sorted`**: Shows skills attached to job titles, sorted by the closest deadline.

## Usage

1. **Set Up the Database:**
   - I followed this [tutorial](https://www.youtube.com/watch?v=uxvoMhkKUPE), which allowed me to run a Docker container of my database on my machine with an M1 chip.

2. **Manage Data:**
   - Populate the required tables using `INIT_TABLE.sql`, then set up a `variables.sh` file with the necessary environment variables:
     - `ORACLE_DB_USERNAME`
     - `ORACLE_DB_PASSWORD`
     - `ORACLE_DB_DSN`

3. **Query Data:**
   - Finally, execute `./run.sh` to populate the required tables.

## TODO

- **Filter and Normalize Skills**: Implement a method to filter and normalize the collected skills data. This could involve grouping similar skills under broader categories (e.g., "Python" and "Bash" under "Scripting Languages") to allow for more understandable analysis of the most required skills.
- **Enhanced Skill Analysis**: Develop more advanced queries and views to provide better insights into the most sought-after skills across departments and divisions.
- **Automated Data Refresh**: Set up a scheduled task or cron job to automatically refresh the job listings and associated skills data at regular intervals.
