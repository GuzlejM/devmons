import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { Coin, getCoins, getComparison, createCoin, deleteCoin } from '../services/api'
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
  const itemsPerPage = ref(24)
  
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
    // Only update loading state during initial load
    if (coins.value.length === 0) {
      loading.value = true
    }
    error.value = null
    
    try {
      console.log('Fetching coins from API...')
      const fetchedCoins = await getCoins()
      console.log('Coins fetched successfully:', fetchedCoins.length, 'coins')
      
      if (Array.isArray(fetchedCoins)) {
        coins.value = fetchedCoins
      } else {
        console.error('Invalid coins data format:', fetchedCoins)
        throw new Error('Invalid response format')
      }
    } catch (err) {
      console.error('Error fetching coins:', err)
      error.value = 'Failed to load coins'
      toast.error('Failed to load coins. Please try refreshing the page.')
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
  
  const addNewCoin = async (coin: { coingecko_id: string, symbol: string, name: string, logo_url: string }) => {
    // Don't change global loading state at all
    error.value = null
    
    try {
      // Make the API call without touching the loading state
      const response = await createCoin(coin)
      console.log('Coin added successfully:', response)
      
      if (response && response.id) {
        // Prepend to array to show newly added coin at the top
        coins.value.unshift(response)
        toast.success(`${coin.name} added successfully`)
        return response
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      console.error('Error adding coin:', err)
      error.value = 'Failed to add coin'
      toast.error('Failed to add coin. Please try again.')
      throw err
    }
  }
  
  const removeCoin = async (coinId: number) => {
    loading.value = true
    error.value = null
    
    try {
      // Find the coin before deletion for the success message
      const coinToDelete = coins.value.find(c => c.id === coinId)
      
      // Call API to delete the coin
      await deleteCoin(coinId)
      
      // Remove from local state
      coins.value = coins.value.filter(c => c.id !== coinId)
      
      // Show success message
      if (coinToDelete) {
        toast.success(`Removed ${coinToDelete.name} successfully!`)
      } else {
        toast.success('Coin removed successfully')
      }
    } catch (err: any) {
      console.error('Error removing coin:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to remove coin'
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
    addNewCoin,
    removeCoin
  }
}) 