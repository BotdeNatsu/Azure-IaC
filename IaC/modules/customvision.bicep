//Custom Vision Parameters
@description('Display name of Custom Vision Service')
param customVisionName string

@description('SKU for Computer Vision API')
@allowed([
  'F0'
  'S0'
])
param customVisionSKU string

@description('Location for all resources.')
param location string = resourceGroup().location

//Set Variables
var customVisionNameTraining = customVisionName
var customVisionNamePrediction = '${customVisionName}-Prediction'

resource customVisionTraining 'Microsoft.CognitiveServices/accounts@2022-03-01' = {
  name: customVisionNameTraining
  location: location
  kind: 'CustomVision.Training'
  sku: {
    name: customVisionSKU
  }
  properties: {
    customSubDomainName: customVisionNameTraining
  }
}

resource customVisionPrediction 'Microsoft.CognitiveServices/accounts@2022-03-01' = {
  name: customVisionNamePrediction
  location: location
  kind: 'CustomVision.Prediction'
  sku: {
    name: customVisionSKU
  }
  properties: {
    customSubDomainName: customVisionNamePrediction
  }
}
