-- Average salary by role
SELECT
    job_title,
    AVG(salary) AS avg_salary
FROM cleaned_data
GROUP BY job_title
ORDER BY avg_salary DESC;

-- Top demanded skills
SELECT
    skill,
    COUNT(*) AS demand
FROM cleaned_data
CROSS JOIN UNNEST(skills) AS t(skill)
GROUP BY skill
ORDER BY demand DESC;

-- Salary by skill
SELECT
    skill,
    AVG(salary) AS avg_salary,
    COUNT(*) AS total_jobs
FROM cleaned_data
CROSS JOIN UNNEST(skills) AS t(skill)
GROUP BY skill
ORDER BY avg_salary DESC;

-- Job count by role
SELECT
    job_title_clean,
    COUNT(*) AS total_jobs
FROM cleaned_data
GROUP BY job_title_clean
ORDER BY total_jobs DESC;
