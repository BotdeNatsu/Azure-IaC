//Global Parameters
param locationRG string
param tenantId string

//Key Vault Parameters
param kvName string

resource kv 'Microsoft.KeyVault/vaults@2021-11-01-preview' = {
  name: kvName
  location: locationRG
  properties: {
    enabledForDeployment: true
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
    tenantId: tenantId
    enableSoftDelete: true
    enablePurgeProtection: true
    softDeleteRetentionInDays: 90
    enableRbacAuthorization:true
    accessPolicies:[]
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

