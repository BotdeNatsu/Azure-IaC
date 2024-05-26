// =========== main.bicep ===========
targetScope = 'resourceGroup'

param locationRG string
param resourceGroupName string
param environment string
param tenantId string


//kv-clasimag-dev-eastus2

resource kv 'Microsoft.KeyVault/vaults@2021-11-01-preview' = {
  name: 'keyVaultName-testinterno'
  location: locationRG
  properties: {
    enabledForDeployment: true
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
    tenantId: tenantId
    enableSoftDelete: true
    enablePurgeProtection: true
    softDeleteRetentionInDays: 90
    sku: {
      name: 'standard'
      family: 'A'
    }
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

