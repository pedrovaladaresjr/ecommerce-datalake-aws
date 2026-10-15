import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job 
import pyspark.sql.functions as F 
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType, IntegerType

# 1. Configurações Iniciais e Parâmetros
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_BUCKET_NAME'])
BUCKET_NAME = args['S3_BUCKET_NAME']

BRONZE_BASE_PATH = f"s3://{BUCKET_NAME}/raw/"   
SILVER_BASE_PATH = f"s3://{BUCKET_NAME}/trusted/"

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# 2. Dicionário de Metadados
table_configs = {
    "olist_orders_dataset": {
        "target_name": "tb_orders",
        "primary_key": ["order_id"],
        "partition_cols": ["order_year", "order_month"],
        "schema": StructType([
            StructField('order_id', StringType(), True),
            StructField('customer_id', StringType(), True),
            StructField('order_status', StringType(), True),
            StructField('order_purchase_timestamp', TimestampType(), True),
            StructField('order_approved_at', TimestampType(), True),
            StructField('order_delivered_carrier_date', TimestampType(), True),
            StructField('order_delivered_customer_date', TimestampType(), True),
            StructField('order_estimated_delivery_date', TimestampType(), True)
        ])
    },
    "olist_order_items_dataset": {
        "target_name": "tb_order_items",
        "primary_key": ["order_id", "order_item_id"],
        "partition_cols": [],
        "schema": StructType([
            StructField('order_id', StringType(), True),
            StructField('order_item_id', IntegerType(), True),
            StructField('product_id', StringType(), True),
            StructField('seller_id', StringType(), True),
            StructField('shipping_limit_date', TimestampType(), True),
            StructField('price', DoubleType(), True),
            StructField('freight_value', DoubleType(), True)
        ])
    },
    "olist_order_reviews_dataset": {
        "target_name": "tb_order_reviews",
        "primary_key": ["review_id"],
        "partition_cols": [],
        "schema": StructType([
            StructField('review_id', StringType(), True),
            StructField('order_id', StringType(), True),
            StructField('review_score', IntegerType(), True),
            StructField('review_comment_title', StringType(), True),
            StructField('review_comment_message', StringType(), True),
            StructField('review_creation_date', TimestampType(), True),
            StructField('review_answer_timestamp', TimestampType(), True)
        ])
    },
     "olist_customers_dataset": {
        "target_name": "tb_customers",
        "primary_key": ["customer_id"],
        "partition_cols": [],
        "schema": StructType([
            StructField('customer_id', StringType(), True),
            StructField('customer_unique_id', StringType(), True),
            StructField('customer_zip_code_prefix', StringType(), True),
            StructField('customer_city', StringType(), True),
            StructField('customer_state', StringType(), True)
        ])
    }
}

# 3. Loop Genérico
for source_folder, config in table_configs.items():
    print(f"--- Processando tabela: {source_folder} ---")
    
    source_path = f"{BRONZE_BASE_PATH}{source_folder}/"
    target_path = f"{SILVER_BASE_PATH}{config['target_name']}/"
    
    try:
        df = spark.read\
            .format('csv')\
            .option('header', 'true')\
            .schema(config['schema'])\
            .load(source_path)
            
        df = df.dropna(subset=config['primary_key'])
        df = df.dropDuplicates(subset=config['primary_key'])
        
        if source_folder == "olist_orders_dataset":
             df = df\
                .withColumn('order_year', F.year(F.col('order_purchase_timestamp')))\
                .withColumn('order_month', F.month(F.col('order_purchase_timestamp')))
             
             df = df.withColumn(
                "order_delivered_customer_date",
                F.when(
                    F.col("order_delivered_customer_date") < F.col("order_purchase_timestamp"), 
                    F.lit(None).cast("timestamp")
                ).otherwise(F.col("order_delivered_customer_date"))
             )
        
        print(f"Escrevendo {config['target_name']} no S3...")
        writer = df.write.mode('overwrite')
        
        if config['partition_cols']:
            writer = writer.partitionBy(*config['partition_cols'])
            
        writer.parquet(target_path)
        print(f"Sucesso: {config['target_name']}")
        
    except Exception as e:
        print(f"Erro ao processar {source_folder}: {e}")

print("--- Job Finalizado ---")
job.commit()