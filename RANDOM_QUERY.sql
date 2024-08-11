SELECT * FROM CERN_LISTING;

UPDATE CERN_Listing 
SET DEADLINE = TO_DATE('2024-08-29 14:59:00', 'YYYY-MM-DD HH24:MI:SS') 
WHERE WORKTAG = 'TE-CRG-GLO-2024-138-GRAE';

ALTER TABLE CERN_listing ADD deadline DATE;

DELETE FROM CERN_LISTING WHERE WORKTAG = 'TE-CRG-GLO-2024-138-GRAE';

COMMIT;

DELETE CERN_skills;

SELECT
    skills --,
    -- COUNT(*) AS skill_count
FROM
    CERN_skills
GROUP BY
    skills;
-- ORDER BY
--     skill_count DESC;

CREATE OR REPLACE VIEW most_common_skills AS
SELECT
    DBMS_LOB.SUBSTR(skills, 4000, 1) AS skill_text,
    COUNT(*) AS skill_count
FROM
    CERN_skills
GROUP BY
    DBMS_LOB.SUBSTR(skills, 4000, 1)
ORDER BY
    skill_count DESC;

CREATE OR REPLACE VIEW position_to_skills AS
SELECT
    cj.position,
    DBMS_LOB.SUBSTR(cs.skills, 4000, 1) AS skill_text,
    cj.deadline
FROM
    CERN_skills cs
JOIN
    CERN_listing cj
ON
    cs.worktag = cj.worktag
ORDER BY
    cj.deadline ASC, cj.position ASC;