// =========== main.bicep ===========
targetScope = 'resourceGroup'

//Global Parameters
param locationRG string
param resourceGroupName string
param environment string
param tenantId string

//Key Vault Parameters
param kvName string


module kv 'modules/keyvault.bicep' = {
  name: 'KeyVaultDeploy'
  params:{
    kvName:kvName
    locationRG:locationRG
    tenantId:tenantId
  }
}
