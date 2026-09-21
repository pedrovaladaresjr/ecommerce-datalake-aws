import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job 
import pyspark.sql.functions as F 
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType 

# Captura de Parâmetros do AWS Glue (Substitui o dotenv)
# O JOB_NAME é padrão. O S3_BUCKET_NAME você configurará na tela do Glue.
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_BUCKET_NAME'])

BUCKET_NAME = args['S3_BUCKET_NAME']
BRONZE_PATH = f"s3://{BUCKET_NAME}/raw/olist_orders_dataset/"   
SILVER_PATH = f"s3://{BUCKET_NAME}/trusted/orders"

#1. Inicialização
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# 2. Definição do Schema
schema = StringType([
    StructField('order_id', StringType(), True),
    StructField('customer_id', StringType(), True),
    StructField('order_status', StringType(), True),
    StructField('order_purchase_timestamp', TimestampType(), True),
    StructField('order_approved_at', TimestampType(), True),
    StructField('order_delivered_carrier_date', TimestampType(), True),
    StructField('order_delivered_customer_date', TimestampType(), True),
    StructField('order_estimated_delivery_date', TimestampType(), True),
])

# 3. Leitura do arquivo raw do s3
df_orders = spark.read\
                .format('csv')\
                .option('header', 'true')\
                .schema(schema)\
                .load(BRONZE_PATH)


# 4. Remoção de valores ausentes
df_transformed = df_transformed.dropna(subset = ["order_id"])

# 5. Garantindo que a data da entrega não seja menor que a data da compra
df_transformed = df_transformed.withColumn(
                        "order_delivered_customer_date",
                        F.when(
                            F.col("order_delivered_customer_date") < F.col("order_purchase_timestamp"), 
                            F.lit(None).cast("timestamp")
                        ).otherwise(F.col("order_delivered_customer_date")))\
                        .withColumn("order_status", F.trim(F.lower(F.col("order_status"))))


# 6. Extrai ano e mês da data da compra para criar as partições da silver
df_transformed = df_transformed\
                    .withColumn('order_year', F.year(F.col('order_purchase_timestamp')))\
                    .withColumn('order_month', F.month(F.col('order_purchase_timestamp')))

# 7. Escrita no Trusted S3
print('Carregando dados na camada Trusted (Silver) em parquet')

try:

    df_transformed.write\
        .mode('overwrite')\
        .partitionBy('order_year', 'order_month')\
        .parquet(SILVER_PATH)   

    print("Job finalizado com sucesso!")
 
except Exception as e:

    print(f'Erro na gravação: {e}')
    raise e 

# Finaliza a execução do Job no AWS Glue
job.commit()

