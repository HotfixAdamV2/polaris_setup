import os, sys, json 
import numpy as np 
import pandas as pd 
import duckdb 
from pyspark.sql.types import * 
from pyspark.sql.functions import *
import pyspark 

os.environ['JAVA_HOME'] = '/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home'
# os.environ['JAVA_HOME'] = '/opt/homebrew/opt/openjdk@17'
os.environ['PATH'] = f"{os.environ['JAVA_HOME']}/bin:{os.environ['PATH']}"

POLARIS_URI = 'http://localhost:8181/api/catalog'
POLARIS_CATALOG_NAME = 'test_catalog_two' 
PRINCIPAL_ROLE_NAME = 'service_acc_role'
POLARIS_CREDENTIALS = ':'
POLARIS_SCOPE = f'PRINCIPAL_ROLE:{PRINCIPAL_ROLE_NAME}'

AZURE_CLIENT_ID = '' 
AZURE_TENANT_ID = ''
AZURE_CLIENT_SECRET = '' 
AZURE_OAUTH_URL = f'https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token' 

builder = (
    pyspark.sql.SparkSession.builder.appName(
        "killing_me_fastly"
    )
    # jars
    .config(
        "spark.jars.packages",
        "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.9.2,"
        # "com.azure:azure-storage-blob:12.18.0,"
        "org.apache.hadoop:hadoop-azure:3.4.2,"
        "org.apache.hadoop:hadoop-common:3.4.2,"
        "org.apache.iceberg:iceberg-azure-bundle:1.10.0"
    )
    # # Azure configs 
    # .config(
    #     "spark.hadoop.fs.azure.account.auth.type.storeadampolaris.dfs.core.windows.net",
    #     "OAuth"
    # )
    # .config(
    #     "spark.hadoop.fs.azure.account.oauth2.client.id.storeadampolaris.dfs.core.windows.net",
    #     AZURE_CLIENT_ID
    # )
    # .config(
    #     "spark.hadoop.fs.azure.account.oauth2.client.secret.storeadampolaris.dfs.core.windows.net",
    #     AZURE_CLIENT_SECRET
    # )
    # .config(
    #     "spark.hadoop.fs.azure.account.oauth2.client.endpoint.storeadampolaris.dfs.core.windows.net",
    #     AZURE_OAUTH_URL
    # )
    # .config(
    #     "spark.hadoop.fs.azure.account.key.storeadampolaris.dfs.core.windows.net",
    #     "STORAGE_BUCKET_SECRET_KEY"
    # )
    # Extensions
    .config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
    )
    # Catalog Type
    .config(
        "spark.sql.catalog.polaris",
        "org.apache.iceberg.spark.SparkCatalog"
    )
    # x access delegation
    .config(
        "spark.sql.catalog.polaris.header.X-Iceberg-Access-Delegation",
        "vended-credentials"
    )
    # warehouse to point to catalog name
    .config(
        "spark.sql.catalog.polaris.warehouse",
        POLARIS_CATALOG_NAME
    )
    # catalog implementation
    .config(
        "spark.sql.catalog.polaris.type",
        "rest"
    )
    # URI
    .config(
        "spark.sql.catalog.polaris.uri",
        POLARIS_URI
    )
    # Credentials
    .config(
        "spark.sql.catalog.polaris.credential",
        POLARIS_CREDENTIALS 
    )
    # give it scope
    .config(
        "spark.sql.catalog.polaris.scope",
        POLARIS_SCOPE   
    )
    # pyspark enabled
    .config(
        "spark.sql.execution.arrow.pyspark.enabled",
        "true"
    )
    # memory
    .config(
        "spark.driver.memory",
        "2g"
    )
    # token refresh enabled
    .config(
        "spark.sql.catalog.polaris.token-refresh-enabled",
        "true"
    )
)

spark = builder.getOrCreate()

try:
    spark.sql("CREATE NAMESPACE IF NOT EXISTS polaris.test_schema;")

    # now try to create a table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS polaris.test_schema.test_table (
        TRANSACTION_ID INTEGER NOT NULL,
        AMOUNT DOUBLE NOT NULL
    ) 
    USING iceberg;
    """)

    data = [
        (10, 1523.0),
        (20, 200123120.0),
    ]
    columns = ['TRANSACTION_ID', 'AMOUNT']
    df = spark.createDataFrame(data, columns)
    df.createOrReplaceTempView("temp_data")
    
    merge_sql = """ 
        MERGE INTO polaris.test_schema.test_table AS target
        USING temp_data AS source
        ON target.TRANSACTION_ID = source.TRANSACTION_ID
        WHEN MATCHED THEN
            UPDATE SET target.AMOUNT = source.AMOUNT
        WHEN NOT MATCHED THEN
            INSERT (TRANSACTION_ID, AMOUNT) VALUES (source.TRANSACTION_ID, source.AMOUNT);
    """
    spark.sql(merge_sql)

    spark.sql("SELECT * FROM polaris.test_schema.test_table").show()
    
    spark.stop()
except:
    spark.stop()
    raise