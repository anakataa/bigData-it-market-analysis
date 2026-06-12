import sys
from pyspark import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, lower, explode

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

input_path = "s3://it-job-market-analysis-project-kstaroshchuk/raw/"
output_path = "s3://it-job-market-analysis-project-kstaroshchuk/processed/cleaned_data/"

df = spark.read.option("multiline", "true").json(input_path)

cleaned_df = df.dropna(subset=["salary"]) \
               .withColumn("job_title_clean", lower(col("job_title")))


cleaned_df.write.mode("overwrite").parquet(output_path)

print(f"Готово! Обработано строк: {cleaned_df.count()}")
job.commit()