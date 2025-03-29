import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { Coin, getCoins, getComparison, createCoin } from '../services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

export const useCoinsStore = defineStore('coins', () => {
  // State
  const coins = ref<Coin[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedCoin = ref<string | null>(null)
  const searchQuery = ref('')
  const currentPage = ref(1)
  const itemsPerPage = ref(12)
  
  // Getters
  const filteredCoins = computed(() => {
    return coins.value.filter(coin => 
      coin.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  })
  
  const paginatedCoins = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredCoins.value.slice(start, end)
  })
  
  const totalPages = computed(() => {
    return Math.ceil(filteredCoins.value.length / itemsPerPage.value)
  })
  
  // Actions
  const fetchCoins = async () => {
    loading.value = true
    error.value = null
    
    try {
      coins.value = await getCoins()
    } catch (err) {
      console.error('Error fetching coins:', err)
      error.value = 'Failed to load coins'
      toast.error('Failed to load coins')
    } finally {
      loading.value = false
    }
  }
  
  const setSelectedCoin = (coinId: string | null) => {
    selectedCoin.value = coinId
  }
  
  const setSearchQuery = (query: string) => {
    searchQuery.value = query
    currentPage.value = 1 // Reset to first page when searching
  }
  
  const setPage = (page: number) => {
    currentPage.value = page
  }
  
  const addNewCoin = async (coin: { coingecko_id: string, symbol: string, name: string, logo_url?: string }) => {
    loading.value = true
    error.value = null
    
    try {
      const newCoin = await createCoin(coin)
      coins.value.push(newCoin)
      toast.success(`Added ${newCoin.name} successfully!`)
      return newCoin
    } catch (err: any) {
      console.error('Error adding coin:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to add coin'
      error.value = errorMessage
      toast.error(errorMessage)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    // State
    coins,
    loading,
    error,
    selectedCoin,
    searchQuery,
    currentPage,
    itemsPerPage,
    
    // Getters
    filteredCoins,
    paginatedCoins,
    totalPages,
    
    // Actions
    fetchCoins,
    setSelectedCoin,
    setSearchQuery,
    setPage,
    addNewCoin
  }
}) 