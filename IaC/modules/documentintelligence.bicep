//Documentt Intelligence Parameters
@description('Display name of Documentt Intelligence')
param documentIntelligenceName string

@description('SKU for Documentt Intelligence')
@allowed([
  'F0'
  'S0'
])
param documentIntelligenceSKU string

@description('Location for all resources.')
param location string = resourceGroup().location

resource account 'Microsoft.CognitiveServices/accounts@2022-03-01' = {
  name: documentIntelligenceName
  location: location
  kind: 'FormRecognizer'
  sku: {
    name: documentIntelligenceSKU
  }
  properties: {
  }
}
