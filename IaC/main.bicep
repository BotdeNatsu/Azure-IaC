// =========== main.bicep ===========
targetScope = 'resourceGroup'

param locationRG string
param resourceGroupName string
param environment string


//kv-clasimag-dev-eastus2

resource kv 'Microsoft.KeyVault/vaults@2021-11-01-preview' = {
  name: 'keyVaultName-testinterno'
  location: locationRG
}

