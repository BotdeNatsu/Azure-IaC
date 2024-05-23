// =========== main.bicep ===========
targetScope = 'subscription'

param locationRG string
param resourceGroupName string
param environment string


resource rg 'Microsoft.Resources/resourceGroups@2021-01-01' = {
  name: resourceGroupName
  location: locationRG
}
