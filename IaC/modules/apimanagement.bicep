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
param apiManagementSKU string

@description('The instance size of this API Management service.')
@allowed([
  1
  2
])
param skuCount int = 1

@description('Location for all resources.')
param location string = resourceGroup().location

resource apiManagementService 'Microsoft.ApiManagement/service@2021-08-01' = {
  name: apiManagementServiceName
  location: location
  sku: {
    name: apiManagementSKU
    capacity: skuCount
  }
  properties: {
    publisherEmail: publisherEmailAPIManagement
    publisherName: publisherNameAPIManagement
  }
}
