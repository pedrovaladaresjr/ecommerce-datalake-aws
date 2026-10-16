import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job 
import pyspark.sql.functions as F 

# Configuração
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_BUCKET_NAME'])
BUCKET_NAME = args['S3_BUCKET_NAME']

SILVER_BASE_PATH= f"s3://{BUCKET_NAME}/trusted/"
GOLD_BASE_PATH    = f"s3://{BUCKET_NAME}/refined/"

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

try:
    df_orders       = spark.read.parquet(f"{SILVER_BASE_PATH}tb_orders/")
    df_items        = spark.read.parquet(f"{SILVER_BASE_PATH}tb_order_items/")
    df_customers    = spark.read.parquet(f"{SILVER_BASE_PATH}tb_customers/")
    df_reviews      = spark.read.parquet(f"{SILVER_BASE_PATH}tb_order_reviews/")

    # Um pedido pode ter mais de uma avaliação. Se usarmos JOIN direto, a linha vai 
    # duplicar e inflar o valor da receita (price). Vamos pegar apenas a avaliação mais recente.
    df_review_dedup = df_reviews.dropDuplicates(["order_id"])

    # JOIN dos dados
    # Trazemos apenas os clientes que fizeram pedidos JOIN
    # Como nem todo cliente faz review, aplico o LEFT JOIN 
    df_gold = df_orders.join(df_customers, on = "customer_id", how = "inner")\
                       .join(df_items, on = "order_id", how = "inner") \
                       .join(df_reviews, on = "order_id", how = "left")

    # Aplica a regra para o tempo de entrega, atrasos e valor total
    df_gold = df_gold\
                .withColumn("tempo_entrega_dias", 
                            F.date_diff(F.col("order_delivered_customer_date"), F.col("order_purchase_timestamp")))\
                .withColumn("atraso_entrega",
                            F.when(F.col("order_delivered_customer_date") > F.col("order_estimated_delivery_date"), True)
                            .otherwise(False))\
                .withColumn("valor_total_pedido", F.round(F.col("price") + F.col("freight_value"), 2))

    # Tabela Fato - Seleção Final e Organização das colunas 
    df_final = df_gold.select(
        # Chaves de granularidade e Relacionamento
        "order_id",
        "order_item_id",
        "customer_id",
        "review_id",

        # Dimensões Desnormalizadas
        "customer_city",
        "customer_state",
        "order_status",

        # Métricas Financeiras
        "price",
        "freight_value",
        "valor_total_pedido",

        # Métricas Logísticas e Qualidade
        "tempo_entrega_dias",
        "atraso_entrega",
        "review_score",

        # Particionamento Temporal
        "order_year",
        "order_month"
    )

    # Escrita na Camada Gold
    target_path = f"{GOLD_BASE_PATH}gold_fato_vendas_logistica/"

    df_final.write\
            .mode("overwrite")\
            .partitionBy("order_year", "order_month")\
            .parquet(target_path)

    print("Tabela Fato na criada em Refined no S3...")
    print("Tabela: gold_fato_vendas_logistica")

except Exception as e:
    print(f"Erro ao processar a camada Gold: {e}") 
    raise e 

print("Job Gold Finalizado")
job.commit()
