from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'almacenamientofaena' # Must be replaced by your <storage_account_name>
    account_key = 'M9kP3rnKDBkjTpcKfzp0PRfQOH2wiDddgXvGx4k+GFqo0sMB40ISfyVl18e4hB7tGVJEDhZCxkTCPmP3p2nP1g==' # Must be replaced by your <storage_account_key>
    azure_container = 'media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = 'almacenamientofaena' # Must be replaced by your storage_account_name
    account_key = 'M9kP3rnKDBkjTpcKfzp0PRfQOH2wiDddgXvGx4k+GFqo0sMB40ISfyVl18e4hB7tGVJEDhZCxkTCPmP3p2nP1g==' # Must be replaced by your <storage_account_key>
    azure_container = 'static'
    expiration_secs = None