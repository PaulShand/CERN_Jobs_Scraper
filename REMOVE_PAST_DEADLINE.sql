DELETE FROM CERN_Listing
WHERE DEADLINE < SYSDATE;

DELETE FROM CERN_skills cs
WHERE NOT EXISTS (
    SELECT 1 
    FROM CERN_listing cl
    WHERE cs.worktag = cl.worktag
);

COMMIT;
EXIT;