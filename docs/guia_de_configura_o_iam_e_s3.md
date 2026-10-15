# Passo a Passo: Criação de Usuário e Bucket na AWS

## 1. Acessando o IAM e Criando o Usuário

1. Faça login na sua conta AWS.

2. Acesse diretamente a página de Usuários do IAM através deste link: [https://console.aws.amazon.com/iamv2/home#/users](https://console.aws.amazon.com/iamv2/home?utm_source=gemini#/users)

3. No canto superior direito, clique no botão laranja **"Criar usuário"** (Create user).

4. **Detalhes do usuário:** Diga o nome do usuário (ex: `engenheiro-dados-local`). Não marque a opção de dar acesso ao Console de Gerenciamento da AWS (Management Console), pois esse usuário será usado apenas por scripts/código. Clique em **Próximo**.

## 2. Dando Permissões (O que esse usuário pode fazer?)

1. Na tela de permissões, escolha a terceira opção: **"Anexar políticas diretamente"** (Attach policies directly).

2. Na barra de pesquisa logo abaixo, digite `AmazonS3FullAccess`.

3. Marque a caixa de seleção ao lado de **AmazonS3FullAccess** na lista que aparecer. *(Nota: Em um ambiente corporativo super restrito, criaríamos uma política que dá acesso apenas ao seu bucket específico, mas para nosso projeto de portfólio, essa política gerenciada da AWS é o padrão inicial).*

4. Clique em **Próximo** e depois em **Criar usuário** (Create user).

## 3. Gerando as Chaves de Acesso (Access Key e Secret Key)

1. Você voltará para a lista de usuários. Clique no nome do usuário que você acabou de criar (`engenheiro-dados-local`).

2. Vá na aba **"Credenciais de segurança"** (Security credentials).

3. Role a página para baixo até encontrar a seção "Chaves de acesso" (Access keys) e clique em **"Criar chave de acesso"** (Create access key).

4. Selecione a opção **"Interface da linha de comando (CLI)"** (Command Line Interface). Marque a caixa de confirmação lá embaixo e clique em **Próximo**.

5. Opcional: Coloque uma tag descritiva, como "Projeto Data Lake". Clique em **Criar chave de acesso**.

6. **⚠️ ATENÇÃO MÁXIMA:** Esta é a ÚNICA vez que a AWS mostrará a sua `Secret Access Key`.

   * Copie a **Access Key** e cole no seu arquivo `.env`.

   * Copie a **Secret Access Key** e cole no seu arquivo `.env`.

   * (Opcional) Faça o download do arquivo .csv com as chaves e guarde em um local seguro na sua máquina (fora da pasta do GitHub).

7. Clique em **Concluído**.

## 4. Criando o Bucket S3 (O "Balde" de Dados)

O script Python que escrevemos tenta enviar arquivos para um bucket existente. Precisamos criá-lo:

1. Acesse o console do S3: [https://console.aws.amazon.com/s3/](https://console.aws.amazon.com/s3/?utm_source=gemini)

2. Clique em **"Criar bucket"** (Create bucket).

3. **Nome do bucket:** Lembre-se, precisa ser globalmente único! Tente algo como `datalake-ecommerce-seunome-2026`. (Copie esse nome exato para a variável `S3_BUCKET_NAME` no seu `.env`).

4. **Região da AWS:** Escolha `us-east-1` (Norte da Virgínia) pois costuma ser a mais barata e onde lançam as novidades primeiro. (Coloque essa mesma região no `.env`).

5. Role até o final da página e clique em **Criar bucket**. Não precisa alterar nenhuma outra configuração de segurança padrão por enquanto.