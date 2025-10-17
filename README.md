### Le Java
 * Need java 21 for polaris...
    ```shell
    # Install
    brew install openjdk@21

    # find the java home...
    # This may or may not be the correct one...
    export JAVA_HOME=/opt/homebrew/opt/openjdk@21
    export PATH=/opt/homebrew/opt/openjdk@21/bin:$PATH

    # It may also be this one...
    # /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home

    # Do the gradlew build
    cd /pathto/polaris
    ./gradlew \
    :polaris-server:assemble \
    :polaris-server:quarkusAppPartsBuild --rerun \
    :polaris-admin:assemble \
    :polaris-admin:quarkusAppPartsBuild --rerun \
    -Dquarkus.container-image.build=true

    # Environment variables...
    export ASSETS_PATH=$(pwd)/getting-started/assets/
    export QUARKUS_DATASOURCE_JDBC_URL=jdbc:postgresql://postgres:5432/POLARIS
    export QUARKUS_DATASOURCE_USERNAME=postgres
    export QUARKUS_DATASOURCE_PASSWORD=postgres
    export CLIENT_ID=root
    export CLIENT_SECRET=s3cr3t
    export AZURE_TENANT_ID=your_tenant_id
    # is service principal client id and secret
    export AZURE_CLIENT_ID=your_client_id
    export AZURE_CLIENT_SECRET=your_client_secret

    # running docker image...
    # Must add three environment variables to the docker-compose.yml (in order to get this working)
    # Those being (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET) where the client id and secret are your service principal
    docker compose -p polaris -f getting-started/assets/postgres/docker-compose-postgres.yml \
    -f getting-started/jdbc/docker-compose-bootstrap-db.yml \
    -f getting-started/jdbc/docker-compose.yml up
    ```
 * Need Java 17 for pyspark
    ```shell
    brew install openjdk@17
    # Path
    export PATH=/opt/homebrew/opt/openjdk@17/bin:$PATH

    #For compilers to find openjdk@17 you may need to set:
    #export CPPFLAGS="-I/opt/homebrew/opt/openjdk@17/include"
    ```
 
Catalog Creation
```shell
# Catalog creation
./polaris catalogs create \
    --type INTERNAL \
    --storage-type AZURE \
    --tenant-id {AZURE_TENANT_ID} \
    --multi-tenant-app-name Polaris-API \
    --consent-url "https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/authorize?client_id={SERVICE_PRINCIPAL_CLIENT_ID}&response_type=code" \
    --default-base-location abfss://{CONTAINER_NAME}@{STORAGE_BUCKET_NAME}.dfs.core.windows.net/catalog_data/ \
    --allowed-location abfss://{CONTAINER_NAME}@{STORAGE_BUCKET_NAME}.dfs.core.windows.net/catalog_data/ \
    test_catalog

# principal creation
./polaris principals create service_acc

# Create principal role
./polaris principal-roles create service_acc_role

# Assign principal role to principal
./polaris principal-roles grant --principal service_acc service_acc_role

# create catalog role
./polaris catalog-roles create --catalog test_catalog service_acc_full_access

# grant catalog role to the principal role 
./polaris catalog-roles grant --catalog test_catalog --principal-role service_acc_role service_acc_full_access

# Grant permissions to catalog role
./polaris privileges catalog grant --catalog test_catalog --catalog-role service_acc_full_access CATALOG_MANAGE_CONTENT

## Creating a second catalog (this time no multi tenant app name and consent urlllll)
./polaris catalogs create \
    --type INTERNAL \
    --storage-type AZURE \
    --tenant-id {AZURE_TENANT_ID} \
    --default-base-location abfss://{CONTAINER_NAME}@{STORAGE_BUCKET_NAME}.dfs.core.windows.net/catalog_data_two/ \
    --allowed-location abfss://{CONTAINER_NAME}@{STORAGE_BUCKET_NAME}.dfs.core.windows.net/catalog_data_two/ \
    test_catalog_two

# Create a catalog role for the second catalog
./polaris catalog-roles create --catalog test_catalog_two service_acc_full_access

# grant catalog role to the principal role 
./polaris catalog-roles grant --catalog test_catalog_two --principal-role service_acc_role service_acc_full_access

# Grant permissions to catalog role
./polaris privileges catalog grant --catalog test_catalog_two --catalog-role service_acc_full_access CATALOG_MANAGE_CONTENT
```