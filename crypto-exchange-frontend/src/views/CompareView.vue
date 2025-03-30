<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getComparison, ComparisonResult } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ExchangeList from '../components/exchanges/ExchangeList.vue'

const router = useRouter()
const route = useRoute()
const coinId = ref<string>(route.params.id as string)

const comparisonData = ref<ComparisonResult | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const selectedExchanges = ref<string[]>([])

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

const handleCompareExchanges = (exchangesToCompare: string[]) => {
  selectedExchanges.value = exchangesToCompare
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
          <p class="text-sm text-primary-700 mt-1">Compare prices and fees across different exchanges</p>
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
              <h3 class="text-lg font-bold text-gray-900 mb-3">Highest Volume</h3>
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
          
          <!-- Exchange List Component -->
          <ExchangeList 
            :exchanges="comparisonData.exchanges"
            :best-price-exchange="comparisonData.best_price?.exchange_name"
            :best-volume-exchange="comparisonData.best_for_large_orders?.exchange_name"
            @compare="handleCompareExchanges"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  @apply rounded-lg shadow-sm overflow-hidden transition-all duration-200;
}

.card:hover {
  @apply shadow-md;
}
</style> 