-- =========================================
-- IT Job Market Analysis - Athena Queries
-- AWS Athena / Presto SQL
-- =========================================


-- =========================================
-- 1. Average salary by role
-- Shows average salary for each job title
-- =========================================

SELECT
    job_title,
    AVG(salary) AS avg_salary
FROM cleaned_data
GROUP BY job_title
ORDER BY avg_salary DESC;


-- =========================================
-- 2. Top demanded technical skills
-- UNNEST transforms skill arrays into rows
-- =========================================

SELECT
    skill,
    COUNT(*) AS demand
FROM cleaned_data
CROSS JOIN UNNEST(skills) AS t(skill)
GROUP BY skill
ORDER BY demand DESC;


-- =========================================
-- 3. Average salary by skill
-- Calculates compensation by technology
-- =========================================

SELECT
    skill,
    AVG(salary) AS avg_salary,
    COUNT(*) AS total_jobs
FROM cleaned_data
CROSS JOIN UNNEST(skills) AS t(skill)
GROUP BY skill
ORDER BY avg_salary DESC;


-- =========================================
-- 4. Job count by role
-- Counts occurrences of cleaned job titles
-- =========================================

SELECT
    job_title_clean,
    COUNT(*) AS total_jobs
FROM cleaned_data
GROUP BY job_title_clean
ORDER BY total_jobs DESC;


-- =========================================
-- 5. Salary statistics by currency
-- Useful for international comparison
-- =========================================

SELECT
    currency,
    COUNT(*) AS total_jobs,
    AVG(salary) AS avg_salary
FROM cleaned_data
GROUP BY currency;


-- =========================================
-- 6. Table schema inspection
-- Displays Glue Catalog schema metadata
-- =========================================

DESCRIBE cleaned_data;


-- =========================================
-- 7. Dataset preview
-- Shows sample records from the dataset
-- =========================================

SELECT *
FROM cleaned_data
LIMIT 10;

-- =========================================
-- 8. Top paying technical skills
-- Shows technologies associated with highest salaries
-- =========================================

SELECT
    skill,
    AVG(salary) AS avg_salary,
    COUNT(*) AS total_jobs
FROM cleaned_data
CROSS JOIN UNNEST(skills) AS t(skill)
GROUP BY skill
HAVING COUNT(*) > 1
ORDER BY avg_salary DESC
LIMIT 10;

-- =========================================
-- 9. Salary distribution categories
-- Groups salaries into ranges
-- =========================================

SELECT
    CASE
        WHEN salary < 50000 THEN 'Low Salary'
        WHEN salary < 100000 THEN 'Medium Salary'
        ELSE 'High Salary'
    END AS salary_category,
    COUNT(*) AS total_jobs
FROM cleaned_data
GROUP BY
    CASE
        WHEN salary < 50000 THEN 'Low Salary'
        WHEN salary < 100000 THEN 'Medium Salary'
        ELSE 'High Salary'
    END
ORDER BY total_jobs DESC;
