<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useCoinsStore } from '../stores/coins'
import { getCoinById } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Pagination from '../components/Pagination.vue'

const router = useRouter()
const toast = useToast()
const coinsStore = useCoinsStore()
const showDeleteModal = ref(false)
const coinToDelete = ref<{ id: number, name: string } | null>(null)
const directCoinId = ref('')

const handleCoinSelect = (coinId: string) => {
  router.push({ name: 'compare', params: { id: coinId } })
}

const handleAddCoin = () => {
  router.push({ name: 'add-coin' })
}

const confirmDelete = (e: Event, coin: { id: number, name: string }) => {
  e.stopPropagation() // Prevent card click event
  coinToDelete.value = coin
  showDeleteModal.value = true
}

const cancelDelete = () => {
  showDeleteModal.value = false
  coinToDelete.value = null
}

const deleteCoin = async () => {
  if (!coinToDelete.value) return
  
  try {
    await coinsStore.removeCoin(coinToDelete.value.id)
    showDeleteModal.value = false
    coinToDelete.value = null
  } catch (error) {
    // Error is handled in the store
  }
}

const searchById = async () => {
  if (!directCoinId.value) {
    toast.warning('Please enter a coin ID')
    return
  }

  const id = parseInt(directCoinId.value)
  if (isNaN(id)) {
    toast.error('Invalid ID format')
    return
  }

  try {
    // First check if the coin is already in our local store
    const localCoin = coinsStore.coins.find(c => c.id === id)
    if (localCoin) {
      toast.info(`Found coin: ${localCoin.name} (${localCoin.symbol})`)
      handleCoinSelect(localCoin.coingecko_id)
      return
    }

    // If not found locally, try to fetch it from the API
    const coin = await getCoinById(id)
    if (coin) {
      toast.success(`Retrieved coin: ${coin.name} (${coin.symbol})`)
      // Refresh coins to include this one
      await coinsStore.fetchCoins()
      handleCoinSelect(coin.coingecko_id)
    } else {
      toast.error(`No coin found with ID ${id}`)
    }
  } catch (error) {
    console.error('Error searching for coin by ID:', error)
    toast.error('Failed to find coin')
  }
}

onMounted(async () => {
  try {
    console.log('HomeView mounted - fetching coins...');
    await coinsStore.fetchCoins();
    console.log('Coins loaded successfully in HomeView');
  } catch (error) {
    console.error('Error loading coins in HomeView:', error);
    toast.error('There was a problem loading your coins. Please refresh the page.');
  }
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-4 md:mb-0">Crypto Exchange Comparison</h1>
      
      <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div class="relative w-full md:w-64">
          <input
            type="text"
            placeholder="Search cryptocurrencies..."
            v-model="coinsStore.searchQuery"
            @input="e => coinsStore.setSearchQuery((e.target as HTMLInputElement).value)"
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        
        <button @click="handleAddCoin" class="btn">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Coin
        </button>
      </div>
    </div>
    
    <div v-if="coinsStore.loading" class="flex justify-center items-center py-16">
      <LoadingSpinner />
    </div>
    
    <div v-else-if="coinsStore.error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-center">
      {{ coinsStore.error }}
    </div>
    
    <div v-else-if="coinsStore.paginatedCoins.length === 0" class="bg-gray-50 border border-gray-200 rounded-md p-8 text-center">
      <h3 class="text-xl font-medium text-gray-700">No cryptocurrencies found</h3>
      <p class="text-gray-500 mt-2">
        {{ coinsStore.searchQuery ? 'Try a different search term' : 'Add some cryptocurrencies to get started' }}
      </p>
      <button @click="handleAddCoin" class="btn mt-4">Add Coin</button>
    </div>
    
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <!-- Stats summary -->
      <div class="col-span-full mb-6">
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 shadow-sm">
          <div class="flex flex-wrap justify-between items-center">
            <div class="flex items-center">
              <div class="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div>
                <h4 class="text-sm font-medium text-gray-500">Total Cryptocurrencies</h4>
                <p class="text-xl font-bold text-gray-800">{{ coinsStore.coins.length }}</p>
              </div>
            </div>
            
            <div v-if="coinsStore.totalPages > 1" class="flex items-center text-sm text-gray-500">
              <span class="mr-2">Displaying {{ coinsStore.paginatedCoins.length }} coins per page</span>
            </div>
          </div>
        </div>
      </div>
      
      <div 
        v-for="coin in coinsStore.paginatedCoins" 
        :key="coin.id" 
        class="card hover:shadow-lg transition-shadow cursor-pointer"
        @click="handleCoinSelect(coin.coingecko_id)"
      >
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <div class="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center mr-4">
                <img 
                  v-if="coin.logo_url" 
                  :src="coin.logo_url" 
                  :alt="coin.name" 
                  class="h-8 w-8 rounded-full"
                />
                <span v-else class="text-primary-700 font-bold text-xl">{{ coin.symbol.charAt(0) }}</span>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">{{ coin.symbol }}</h3>
                <p class="text-sm text-gray-500">{{ coin.name }}</p>
              </div>
            </div>
            
            <button 
              class="text-gray-400 hover:text-red-500 p-1"
              @click.stop="confirmDelete($event, { id: coin.id, name: coin.name })"
              title="Delete coin"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
          
          <div class="border-t border-gray-100 pt-4 mt-2">
            <button class="w-full btn-secondary text-sm" @click.stop="handleCoinSelect(coin.coingecko_id)">
              View Comparison
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <Pagination 
      v-if="coinsStore.totalPages > 1" 
      :current-page="coinsStore.currentPage"
      :total-pages="coinsStore.totalPages"
      @change-page="coinsStore.setPage"
      class="mt-8" 
    />
    
    <!-- Delete confirmation modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6 animate-fade-in">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Confirm Deletion</h3>
        <p class="text-gray-700 mb-6">
          Are you sure you want to delete <strong>{{ coinToDelete?.name }}</strong>? This action cannot be undone.
        </p>
        <div class="flex justify-end gap-4">
          <button @click="cancelDelete" class="btn-secondary">
            Cancel
          </button>
          <button @click="deleteCoin" class="btn-danger">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.btn-danger {
  @apply bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg shadow-sm transition-colors;
}
</style> 