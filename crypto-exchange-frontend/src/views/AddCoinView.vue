<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCoinsStore } from '../stores/coins'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import { searchAvailableCoins, CoinGeckoListItem } from '../services/api'

const router = useRouter()
const coinsStore = useCoinsStore()

const form = ref({
  coingecko_id: '',
  symbol: '',
  name: '',
  logo_url: ''
})

const searchQuery = ref('')
const validationErrors = ref<Record<string, string>>({})
const isSubmitting = ref(false)
const searchResults = ref<CoinGeckoListItem[]>([])
const isSearching = ref(false)
const showSearchResults = ref(false)
const searchTimeout = ref<number | null>(null)

// Create a flag to track when we're updating the search query programmatically
const isInternalUpdate = ref(false)

// Custom debounce function
const debounceSearch = (fn: Function, delay: number) => {
  return (...args: any[]) => {
    if (searchTimeout.value) {
      clearTimeout(searchTimeout.value)
    }
    searchTimeout.value = setTimeout(() => {
      fn(...args)
      searchTimeout.value = null
    }, delay) as unknown as number
  }
}

// Search logic
const performSearch = async (query: string) => {
  // Don't search when the query is being updated internally
  if (isInternalUpdate.value) return
  
  if (!query || query.length < 2) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }
  
  isSearching.value = true
  try {
    searchResults.value = await searchAvailableCoins(query)
    showSearchResults.value = searchResults.value.length > 0
  } catch (error) {
    console.error('Error searching coins:', error)
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

const searchCoins = debounceSearch(performSearch, 300)

watch(() => searchQuery.value, (newQuery) => {
  // Only trigger search if not being updated internally
  if (!isInternalUpdate.value) {
    searchCoins(newQuery)
  }
})

const selectCoin = (coin: CoinGeckoListItem) => {
  form.value.coingecko_id = coin.id
  form.value.symbol = coin.symbol.toUpperCase()
  form.value.name = coin.name
  
  // Set flag before updating search query
  isInternalUpdate.value = true
  searchQuery.value = coin.name
  
  // Reset flag after a short delay
  setTimeout(() => {
    isInternalUpdate.value = false
  }, 100)
  
  // If coin has an image from CoinGecko, use it as logo
  if (coin.image) {
    form.value.logo_url = coin.image
  }
  
  showSearchResults.value = false
}

const handleInputFocus = () => {
  // Only show results if we're not in the middle of a selection
  // and there are actual results to show
  if (!isInternalUpdate.value && searchResults.value.length > 0) {
    showSearchResults.value = true
  }
}

const handleInputBlur = () => {
  // Delayed hide to allow clicking on results
  setTimeout(() => {
    showSearchResults.value = false
  }, 200)
}

const validateForm = () => {
  const errors: Record<string, string> = {}
  
  if (!form.value.coingecko_id.trim()) {
    errors.coingecko_id = 'CoinGecko ID is required'
  }
  
  if (!form.value.symbol.trim()) {
    errors.symbol = 'Symbol is required'
  }
  
  if (!form.value.name.trim()) {
    errors.name = 'Name is required'
  }
  
  if (form.value.logo_url && !form.value.logo_url.match(/^https?:\/\/.+/)) {
    errors.logo_url = 'Logo URL must be a valid URL starting with http:// or https://'
  }
  
  validationErrors.value = errors
  return Object.keys(errors).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isSubmitting.value = true
  
  try {
    await coinsStore.addNewCoin({
      coingecko_id: form.value.coingecko_id.trim(),
      symbol: form.value.symbol.trim().toUpperCase(),
      name: form.value.name.trim(),
      logo_url: form.value.logo_url.trim() || undefined
    })
    
    router.push('/')
  } catch (error) {
    // Error handling is done in the store
  } finally {
    isSubmitting.value = false
  }
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-3xl mx-auto">
      <div class="flex items-center mb-8">
        <button @click="goBack" class="mr-4 text-gray-600 hover:text-gray-900">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <h1 class="text-3xl font-bold text-gray-900">Add New Cryptocurrency</h1>
      </div>
      
      <div class="card p-6">
        <form @submit.prevent="handleSubmit">
          <!-- Coin Search Field -->
          <div class="mb-6 relative">
            <label for="coin_search" class="block text-sm font-medium text-gray-700 mb-1">Add new Cryptocurrency</label>
            <input
              id="coin_search"
              v-model="searchQuery"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Search by name, symbol, or ID..."
              @focus="handleInputFocus"
              @blur="handleInputBlur"
            />
            
            <!-- Search Results Dropdown -->
            <div v-if="showSearchResults" class="absolute z-10 w-full mt-1 bg-white rounded-md shadow-lg max-h-80 overflow-auto">
              <div v-if="isSearching" class="p-2 text-center text-gray-500">
                <LoadingSpinner class="w-4 h-4 mx-auto" />
                <span class="text-sm">Searching...</span>
              </div>
              <ul v-else class="py-1">
                <li 
                  v-for="coin in searchResults" 
                  :key="coin.id" 
                  @mousedown="selectCoin(coin)"
                  class="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-b-0"
                  :class="{'bg-green-50': coin.has_market_data}"
                >
                  <div class="flex items-center gap-2">
                    <img v-if="coin.image" :src="coin.image" alt="coin logo" class="w-6 h-6 rounded-full" />
                    <div class="flex-1">
                      <div class="flex items-center justify-between">
                        <span class="text-gray-800 font-medium">{{ coin.name }}</span>
                        <span v-if="coin.current_price" class="text-gray-700 text-sm font-medium">
                          ${{ coin.current_price.toLocaleString() }}
                        </span>
                      </div>
                      <div class="flex justify-between items-center">
                        <div class="text-xs text-gray-500 flex items-center gap-1">
                          <span class="uppercase font-medium">{{ coin.symbol }}</span>
                          <span class="text-xs text-gray-400">({{ coin.id }})</span>
                        </div>
                        <div v-if="coin.price_change_24h" class="text-xs" :class="coin.price_change_24h >= 0 ? 'text-green-600' : 'text-red-600'">
                          {{ coin.price_change_24h >= 0 ? '+' : '' }}{{ coin.price_change_24h.toFixed(2) }}%
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-if="!coin.has_market_data" class="text-xs text-amber-600 mt-1 font-medium">
                    Note: This coin doesn't have price data on CoinGecko
                  </div>
                </li>
              </ul>
              <div v-if="searchResults.length === 0 && !isSearching && searchQuery.length >= 2" class="p-2 text-center text-gray-500">
                No coins found matching your search
              </div>
            </div>
            
            <p class="mt-1 text-sm text-gray-500">
              Search and select a cryptocurrency that's not already in your app
            </p>
          </div>
          
          <div class="mb-6">
            <label for="coingecko_id" class="block text-sm font-medium text-gray-700 mb-1">CoinGecko ID</label>
            <input
              id="coingecko_id"
              v-model="form.coingecko_id"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-gray-50"
              placeholder="e.g. bitcoin"
              :class="{'border-red-500': validationErrors.coingecko_id}"
              readonly
            />
            <p v-if="validationErrors.coingecko_id" class="mt-1 text-sm text-red-600">
              {{ validationErrors.coingecko_id }}
            </p>
            <p class="mt-1 text-sm text-gray-500">
              The ID used by CoinGecko API. This will be verified against CoinGecko.
            </p>
          </div>
          
          <div class="mb-6">
            <label for="symbol" class="block text-sm font-medium text-gray-700 mb-1">Symbol</label>
            <input
              id="symbol"
              v-model="form.symbol"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="e.g. BTC"
              :class="{'border-red-500': validationErrors.symbol}"
            />
            <p v-if="validationErrors.symbol" class="mt-1 text-sm text-red-600">
              {{ validationErrors.symbol }}
            </p>
          </div>
          
          <div class="mb-6">
            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="e.g. Bitcoin"
              :class="{'border-red-500': validationErrors.name}"
            />
            <p v-if="validationErrors.name" class="mt-1 text-sm text-red-600">
              {{ validationErrors.name }}
            </p>
          </div>
          
          <div class="mb-8">
            <label for="logo_url" class="block text-sm font-medium text-gray-700 mb-1">Logo URL (optional)</label>
            <input
              id="logo_url"
              v-model="form.logo_url"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="e.g. https://example.com/bitcoin.png"
              :class="{'border-red-500': validationErrors.logo_url}"
            />
            <p v-if="validationErrors.logo_url" class="mt-1 text-sm text-red-600">
              {{ validationErrors.logo_url }}
            </p>
          </div>
          
          <div class="flex justify-end gap-4">
            <button 
              type="button" 
              @click="goBack" 
              class="btn-secondary"
              :disabled="isSubmitting"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn"
              :disabled="isSubmitting"
            >
              <LoadingSpinner v-if="isSubmitting" class="w-4 h-4 mr-2" />
              {{ isSubmitting ? 'Adding...' : 'Add Cryptocurrency' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Add any additional styles here if needed */
</style> 