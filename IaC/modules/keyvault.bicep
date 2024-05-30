//Global Parameters
@description('The location of the Resource Group')
param locationRG string = resourceGroup().location
@description('The valuo of the Tenant ID')
param tenantId string

//Key Vault Parameters
@description('The name of the Key Vault')
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

