-- =========================================
-- IT Job Market Analysis - Athena Queries
-- AWS Athena / Presto SQL
-- Salary values are treated as cleaned USD/year.
-- Salary analyses use WHERE salary BETWEEN 10000 AND 500000 to remove
-- mixed-period/currency outliers before visualization.
-- =========================================


-- =========================================
-- 1. Average salary by role
-- Shows average salary for each job title
-- Export result as: data/results/salary_by_role.csv
-- =========================================

SELECT
    job_title_clean,
    AVG(salary) AS avg_salary,
    COUNT(*) AS total_jobs
FROM it_job_market_db.processed_cleaned_data
WHERE salary BETWEEN 10000 AND 500000
GROUP BY job_title_clean
ORDER BY avg_salary DESC;


-- =========================================
-- 2. Top demanded technical skills
-- UNNEST transforms skill arrays into rows
-- Export result as: data/results/top_skills_analysis.csv
-- =========================================

SELECT
    skill,
    COUNT(*) AS demand
FROM it_job_market_db.processed_cleaned_data
CROSS JOIN UNNEST(skills) AS t(skill)
GROUP BY skill
ORDER BY demand DESC;


-- =========================================
-- 3. Average salary by skill
-- Calculates compensation by technology
-- Export result as: data/results/top_paying_skills.csv
-- =========================================

SELECT
    skill,
    AVG(salary) AS avg_salary,
    COUNT(*) AS total_jobs
FROM it_job_market_db.processed_cleaned_data
CROSS JOIN UNNEST(skills) AS t(skill)
WHERE salary BETWEEN 10000 AND 500000
GROUP BY skill
HAVING COUNT(*) > 1
ORDER BY avg_salary DESC;


-- =========================================
-- 4. Job count by role
-- Counts occurrences of cleaned job titles
-- =========================================

SELECT
    job_title_clean,
    COUNT(*) AS total_jobs
FROM it_job_market_db.processed_cleaned_data
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
FROM it_job_market_db.processed_cleaned_data
WHERE salary BETWEEN 10000 AND 500000
GROUP BY currency;


-- =========================================
-- 6. Table schema inspection
-- Displays Glue Catalog schema metadata
-- =========================================

DESCRIBE it_job_market_db.processed_cleaned_data;


-- =========================================
-- 7. Dataset preview
-- Shows sample records from the dataset
-- =========================================

SELECT *
FROM it_job_market_db.processed_cleaned_data
LIMIT 10;


-- =========================================
-- 8. Top paying technical skills
-- Shows technologies associated with highest salaries
-- =========================================

SELECT
    skill,
    AVG(salary) AS avg_salary,
    COUNT(*) AS total_jobs
FROM it_job_market_db.processed_cleaned_data
CROSS JOIN UNNEST(skills) AS t(skill)
WHERE salary BETWEEN 10000 AND 500000
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
        WHEN salary < 150000 THEN 'Medium Salary'
        ELSE 'High Salary'
    END AS salary_category,
    COUNT(*) AS total_jobs
FROM it_job_market_db.processed_cleaned_data
WHERE salary BETWEEN 10000 AND 500000
GROUP BY
    CASE
        WHEN salary < 50000 THEN 'Low Salary'
        WHEN salary < 150000 THEN 'Medium Salary'
        ELSE 'High Salary'
    END
ORDER BY total_jobs DESC;


-- =========================================
-- 10. Salary distribution by remote flag
-- Cross-sectional dimension: Remote vs Office average salary
-- Export result as: data/results/salary_by_work_mode.csv
-- =========================================

SELECT
    CASE
        WHEN remote = true THEN 'Remote'
        ELSE 'Office'
    END AS work_mode,
    COUNT(*) AS total_jobs,
    AVG(salary) AS avg_salary
FROM it_job_market_db.processed_cleaned_data
WHERE salary BETWEEN 10000 AND 500000
GROUP BY
    CASE
        WHEN remote = true THEN 'Remote'
        ELSE 'Office'
    END
ORDER BY avg_salary DESC;


-- =========================================
-- 11. Salary buckets
-- Cross-sectional dimension: Low / Medium / High salary categories
-- Export result as: data/results/salary_buckets.csv
-- =========================================

SELECT
    CASE
        WHEN salary < 50000 THEN 'Low'
        WHEN salary < 150000 THEN 'Medium'
        ELSE 'High'
    END AS salary_bucket,
    COUNT(*) AS total_jobs,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS share_percent
FROM it_job_market_db.processed_cleaned_data
WHERE salary BETWEEN 10000 AND 500000
GROUP BY
    CASE
        WHEN salary < 50000 THEN 'Low'
        WHEN salary < 150000 THEN 'Medium'
        ELSE 'High'
    END
ORDER BY total_jobs DESC;


-- =========================================
-- 12. Top countries by average salary
-- Cross-sectional dimension: country extracted from location
-- Export result as: data/results/top_countries_by_avg_salary.csv
-- =========================================

SELECT
    TRIM(SPLIT_PART(location, ',', CARDINALITY(SPLIT(location, ',')))) AS country,
    COUNT(*) AS total_jobs,
    AVG(salary) AS avg_salary
FROM it_job_market_db.processed_cleaned_data
WHERE salary BETWEEN 10000 AND 500000
GROUP BY TRIM(SPLIT_PART(location, ',', CARDINALITY(SPLIT(location, ','))))
HAVING COUNT(*) > 5
ORDER BY avg_salary DESC;
