<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getComparison, ComparisonResult } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const route = useRoute()
const coinId = ref<string>(route.params.id as string)

const comparisonData = ref<ComparisonResult | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const fetchComparisonData = async (id: string) => {
  if (!id) return
  
  loading.value = true
  error.value = null
  
  try {
    const data = await getComparison(id)
    comparisonData.value = data
  } catch (err) {
    console.error('Error fetching comparison data:', err)
    error.value = 'Failed to load comparison data'
    comparisonData.value = null
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    coinId.value = newId as string
    fetchComparisonData(coinId.value)
  }
}, { immediate: true })

onMounted(() => {
  if (coinId.value) {
    fetchComparisonData(coinId.value)
  }
})

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center mb-8">
      <button @click="goBack" class="mr-4 text-gray-600 hover:text-gray-900">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
      </button>
      <h1 class="text-3xl font-bold text-gray-900">Exchange Comparison</h1>
    </div>
    
    <div v-if="loading" class="flex justify-center items-center py-16">
      <LoadingSpinner />
    </div>
    
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-center">
      {{ error }}
    </div>
    
    <div v-else-if="!comparisonData" class="bg-gray-50 border border-gray-200 rounded-md p-8 text-center">
      <h3 class="text-xl font-medium text-gray-700">No comparison data available</h3>
      <p class="text-gray-500 mt-2">
        Please select a different cryptocurrency or try again later.
      </p>
      <button @click="goBack" class="btn mt-4">Back to Coins</button>
    </div>
    
    <div v-else>
      <div class="bg-white rounded-lg shadow-md overflow-hidden mb-8">
        <div class="px-6 py-4 bg-primary-50 border-b border-primary-100">
          <h2 class="text-2xl font-bold text-primary-900">{{ comparisonData.coin }} Prices</h2>
        </div>
        
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div v-if="comparisonData.best_price" class="card p-6 bg-green-50 border border-green-100">
              <h3 class="text-lg font-bold text-gray-900 mb-3">Best Price</h3>
              <div class="flex items-center mb-3">
                <div class="bg-green-100 text-green-800 font-semibold rounded-full px-3 py-1 text-sm mr-2">
                  {{ comparisonData.best_price.exchange_name }}
                </div>
              </div>
              <div class="text-3xl font-bold text-green-700 mb-2">
                ${{ comparisonData.best_price.price_usd.toLocaleString() }}
              </div>
              <div class="text-sm text-gray-600">
                24h Volume: ${{ comparisonData.best_price.volume_24h?.toLocaleString() || 'N/A' }}
              </div>
            </div>
            
            <div v-if="comparisonData.best_for_large_orders" class="card p-6 bg-blue-50 border border-blue-100">
              <h3 class="text-lg font-bold text-gray-900 mb-3">Best for Large Orders</h3>
              <div class="flex items-center mb-3">
                <div class="bg-blue-100 text-blue-800 font-semibold rounded-full px-3 py-1 text-sm mr-2">
                  {{ comparisonData.best_for_large_orders.exchange_name }}
                </div>
              </div>
              <div class="text-3xl font-bold text-blue-700 mb-2">
                ${{ comparisonData.best_for_large_orders.price_usd.toLocaleString() }}
              </div>
              <div class="text-sm text-gray-600">
                24h Volume: ${{ comparisonData.best_for_large_orders.volume_24h?.toLocaleString() || 'N/A' }}
              </div>
            </div>
          </div>
          
          <h3 class="text-xl font-bold text-gray-900 mb-4">All Exchanges</h3>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Exchange
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price (USD)
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    24h Volume
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Bid
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ask
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Spread
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trading Fee
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr 
                  v-for="exchange in comparisonData.exchanges" 
                  :key="exchange.exchange_name"
                  :class="{'bg-green-50': exchange.exchange_name === comparisonData.best_price?.exchange_name}"
                >
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {{ exchange.exchange_name }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                    ${{ exchange.price_usd?.toLocaleString() || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${{ exchange.volume_24h?.toLocaleString() || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${{ exchange.bid_price?.toLocaleString() || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${{ exchange.ask_price?.toLocaleString() || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ exchange.spread ? exchange.spread.toFixed(2) + '%' : 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ exchange.trading_fee ? exchange.trading_fee.toFixed(2) + '%' : 'N/A' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template> 