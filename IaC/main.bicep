// =========== main.bicep ===========
targetScope = 'resourceGroup'

//Global Parameters
@description('The location of the Resource Group')
param locationRG string
@description('The name of the Resource Group')
param resourceGroupName string
@description('The name of the environment')
param environment string
@description('The valuo of the Tenant ID')
param tenantId string

//Key Vault Parameters
@description('The name of the Key Vault')
param kvName string

//Storage Account Parameters
@description('The name of the Storage Account')
param storageAccountName string

//Cosmos Parameters
@description('Azure Cosmos DB account name, max length 44 characters')
param cosmosAccountName string
@description('The primary region for the Azure Cosmos DB account.')
param cosmosPrimaryRegion string
@description('The secondary region for the Azure Cosmos DB account.')
param cosmosSecondaryRegion string
@description('The name for the database')
param cosmosDatabaseName string
@description('The name for the container')
param cosmosContainerName string
@minValue(400)
@maxValue(1000000)
@description('The throughput for the container')
param cosmosThroughput int

//Computer Vision Parameters
@description('Display name of Computer Vision API account')
param computerVisionName string
@description('SKU for Computer Vision API')
@allowed([
  'F0'
  'S1'
])
param computerVisionSKU string

//Custom Vision Parameters
@description('Display name of Custom Vision Service')
param customVisionName string

@description('SKU for Computer Vision API')
@allowed([
  'S0'
])
param customVisionSKU string

//Documentt Intelligence Parameters
@description('Display name of Documentt Intelligence')
param documentIntelligenceName string

@description('SKU for Documentt Intelligence')
@allowed([
  'F0'
  'S0'
])
param documentIntelligenceSKU string

//Function App Parameters
@description('The name of the function app that you wish to create.')
param appName string

@description('The version of python the function app that you wish to create.')
param PYTHON_VERSION string

@description('The pricing tier for the hosting plan.')
@allowed([
  'D1'
  'F1'
  'B1'
  'B2'
  'B3'
  'S1'
  'S2'
  'S3'
  'P1'
  'P2'
  'P3'
  'P1V2'
  'P2V2'
  'P3V2'
  'EP1'
  'EP2'
  'EP3'
  'I1'
  'I2'
  'I3'
  'Y1'
])
param appSKU string

//API Management Parameters
@description('The name of the API Management service instance')
param apiManagementServiceName string

@description('The email address of the owner of the service')
@minLength(1)
param publisherEmailAPIManagement string

@description('The name of the owner of the service')
@minLength(1)
param publisherNameAPIManagement string

@description('The pricing tier of this API Management service')
@allowed([
  'Developer'
  'Basic'
  'Standard'
  'Premium'
])
param APIManagementSKU string

//Modules

module kv 'modules/keyvault.bicep' = {
  name: 'KeyVaultDeploy'
  params:{
    kvName:kvName
    tenantId:tenantId
  }
}

module sa 'modules/storage.bicep' = {
  name: 'StorageAccountDeploy'
  params:{
    storageAccountName: storageAccountName
  }
}

module cdb 'modules/cosmos.bicep' = {
  name: 'CosmosAccountDeploy'
  params:{
    accountName: cosmosAccountName
    containerName: cosmosContainerName
    databaseName: cosmosDatabaseName
    primaryRegion: cosmosPrimaryRegion
    secondaryRegion: cosmosSecondaryRegion
    throughput: cosmosThroughput
  }
}

module computerv 'modules/computervision.bicep' = {
  name: 'ComputerVisionDeploy'
  params: {
    computerVisionName: computerVisionName
    computerVisionSKU: computerVisionSKU
  }
}

module customv 'modules/customvision.bicep' ={
  name: 'CustomVisionDeploy'
  params: {
    customVisionName: customVisionName
    customVisionSKU: customVisionSKU
  }
}

module documenti 'modules/documentintelligence.bicep' = {
  name: 'DocumentIntelligenceDeploy'
  params:{
    documentIntelligenceName: documentIntelligenceName
    documentIntelligenceSKU: documentIntelligenceSKU
  }
}

module af 'modules/functionapp.bicep' = {
  name: 'FunctionAppDeploy'
  dependsOn:[
    sa
  ]
  params: {
    appName: appName
    PYTHON_VERSION: PYTHON_VERSION
    appSKU: appSKU
    storageAccountId: sa.outputs.storageAccountId
    storageAccountName: storageAccountName
  }
}

module apim 'modules/apimanagement.bicep' = {
  name: 'APIManagementDeploy'
  params:{
    apiManagementSKU: APIManagementSKU
    apiManagementServiceName: apiManagementServiceName
    publisherEmailAPIManagement: publisherEmailAPIManagement
    publisherNameAPIManagement: publisherNameAPIManagement
  }
}
