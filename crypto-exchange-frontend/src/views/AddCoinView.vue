<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCoinsStore } from '../stores/coins'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const coinsStore = useCoinsStore()

const form = ref({
  coingecko_id: '',
  symbol: '',
  name: '',
  logo_url: ''
})

const validationErrors = ref<Record<string, string>>({})
const isSubmitting = ref(false)

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
          <div class="mb-6">
            <label for="coingecko_id" class="block text-sm font-medium text-gray-700 mb-1">CoinGecko ID</label>
            <input
              id="coingecko_id"
              v-model="form.coingecko_id"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="e.g. bitcoin"
              :class="{'border-red-500': validationErrors.coingecko_id}"
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