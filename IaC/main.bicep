// =========== main.bicep ===========
targetScope = 'resourceGroup'

param locationRG string
param resourceGroupName string
param environment string


//kv-clasimag-dev-eastus2

resource kv 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: 'Kv-calssif-test-dev'
}
