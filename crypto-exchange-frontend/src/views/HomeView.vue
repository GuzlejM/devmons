<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useCoinsStore } from '../stores/coins'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Pagination from '../components/Pagination.vue'

const router = useRouter()
const toast = useToast()
const coinsStore = useCoinsStore()

const handleCoinSelect = (coinId: string) => {
  router.push({ name: 'compare', params: { id: coinId } })
}

const handleAddCoin = () => {
  router.push({ name: 'add-coin' })
}

onMounted(async () => {
  await coinsStore.fetchCoins()
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
      <div 
        v-for="coin in coinsStore.paginatedCoins" 
        :key="coin.id" 
        class="card hover:shadow-lg transition-shadow cursor-pointer"
        @click="handleCoinSelect(coin.coingecko_id)"
      >
        <div class="p-6">
          <div class="flex items-center mb-4">
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
  </div>
</template> 