import boto3
import os 
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def upload_data_to_s3():
    """
    Função que autentica no S3
    Define o fluxo para o S3 por partição de data
    Faz upload dos dados no S3
    """

    # 1. Configurações
    s3_client = boto3.client(
        's3',
        aws_access_key_id       =   os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key    =   os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name             =   os.getenv('AWS_REGION')

    )

    # 2. Variáveis do Projeto
    BUCKET_NAME =   os.getenv('S3_RAW_BUCKET_NAME')
    CSV_PATH    =   os.getenv('CSV_PATH')
    PREFIXO_S3  =   'raw/'

    # 3. Captura a data atual e cria a partição de ingestão
    loading_date = datetime.now().strftime('%Y-%m-%d')

    for file in os.listdir(CSV_PATH):
        if file.endswith('.csv'):
            full_csv_path = os.path.join(CSV_PATH, file)
            entity_name = file.replace('.csv', '')

            s3_path = f"{PREFIXO_S3}{entity_name}/load_date={loading_date}/{file}"
            print(f"Upload: {file} - load_date={loading_date}")

            try:
                s3_client.upload_file(full_csv_path, BUCKET_NAME, s3_path)
                print(f"Sucess: {entity_name}")

            except Exception as e:
                print(f"Error {file}: {e}")

if __name__ == '__main__':
    upload_data_to_s3()