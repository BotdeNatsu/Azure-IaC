//Computer Vision Parameters
@description('Display name of Computer Vision API account')
param computerVisionName string

@description('SKU for Computer Vision API')
@allowed([
  'F0'
  'S1'
])
param computerVisionSKU string

@description('Location for all resources.')
param location string = resourceGroup().location

resource account 'Microsoft.CognitiveServices/accounts@2022-03-01' = {
  name: computerVisionName
  location: location
  kind: 'ComputerVision'
  sku: {
    name: computerVisionSKU
  }
  properties: {
  }
}
