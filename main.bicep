// =========== main.bicep ===========
targetScope = 'subscription'

//param locationRG string
//param resourceGroupName string
param LOCATIONRG string
param RESOURCEGROUPNAME string

resource rg 'Microsoft.Resources/resourceGroups@2021-01-01' = {
  name: RESOURCEGROUPNAME
  location: LOCATIONRG
}
