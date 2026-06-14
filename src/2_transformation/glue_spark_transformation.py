import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, lower, when

# Glue job arguments. JOB_NAME is passed automatically by AWS Glue.
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

# Raw NDJSON zone and processed Parquet silver zone.
input_path = "s3://it-job-market-analysis-project-kstaroshchuk/raw/jobs/"
output_path = "s3://it-job-market-analysis-project-kstaroshchuk/processed/cleaned_data/"

print(f"[ETL] Reading raw NDJSON from: {input_path}")
raw_df = spark.read.json(input_path)

# Salary midpoint logic:
# - if both salary_min and salary_max exist: average them
# - if only one boundary exists: use that boundary
# - if both are null: salary remains null and is filtered out
cleaned_df = (
    raw_df
    .withColumn(
        "salary",
        when(col("salary_min").isNotNull() & col("salary_max").isNotNull(),
             (col("salary_min") + col("salary_max")) / 2)
        .when(col("salary_min").isNotNull(), col("salary_min"))
        .when(col("salary_max").isNotNull(), col("salary_max"))
    )
    .filter(col("salary").isNotNull())
    .filter((col("salary") >= 10000) & (col("salary") <= 500000))
    .withColumn("job_title_clean", lower(col("job_title")))
)

record_count = cleaned_df.count()
print(f"[ETL] Cleaned records: {record_count}")
print(f"[ETL] Writing Parquet to: {output_path}")

cleaned_df.write.mode("overwrite").parquet(output_path)

print("[ETL] Parquet write completed successfully")
job.commit()
