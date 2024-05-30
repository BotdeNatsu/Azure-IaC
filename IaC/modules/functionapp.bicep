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

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Location for Application Insights')
param appInsightsLocation string = resourceGroup().location

//Storage Account Parameters
@description('The name of the created Storage Account.')
param storageAccountName string

@description('The ID of the created Storage Account.')
param storageAccountId string

//Set Variables
var functionAppName = 'func-${appName}'
var hostingPlanName = 'plan-${appName}'
var applicationInsightsName = 'api-${appName}'

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: appInsightsLocation
  tags: {
    'hidden-link:${resourceId('Microsoft.Web/sites', applicationInsightsName)}': 'Resource'
  }
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'IbizaWebAppExtensionCreate'
    
  }
}

resource hostingPlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: hostingPlanName
  location: location
  sku: {
    name: appSKU

  }
  kind: 'elastic'
  properties: {
    elasticScaleEnabled: true
    isSpot: false
    reserved: true
    maximumElasticWorkerCount: 20
  }
}

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity:{
    type:'SystemAssigned'
  }
  properties: {
    reserved: true
    serverFarmId: hostingPlan.id
    clientAffinityEnabled: false
    siteConfig: {
      alwaysOn: false
      linuxFxVersion: 'PYTHON|${PYTHON_VERSION}'
    }
    httpsOnly: true
  }
}

resource appsettings 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: functionApp
  name: 'appsettings'
  properties: {
    AzureWebJobsStorage: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${listKeys(storageAccountId, '2021-09-01').keys[0].value}'
    APPINSIGHTS_INSTRUMENTATIONKEY: reference(applicationInsights.id, '2020-02-02').InstrumentationKey
    FUNCTIONS_EXTENSION_VERSION: '~4'
    FUNCTIONS_WORKER_RUNTIME: 'python'
    ftpsState: 'Disabled'
    minTlsVersion: '1.2'
  }
}
