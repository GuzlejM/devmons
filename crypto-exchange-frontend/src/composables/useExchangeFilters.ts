import { ref, computed, Ref } from 'vue'

interface Exchange {
  exchange_name: string;
  price_usd: number;
  volume_24h?: number;
  bid_price?: number;
  ask_price?: number;
  trading_fee?: number;
  withdrawal_fee?: number;
  spread?: number;
  last_updated: string;
}

export function useExchangeFilters(exchanges: Ref<Exchange[]> | Exchange[]) {
  const searchQuery = ref('')
  const priceRange = ref({ min: null as number | null, max: null as number | null })
  const volumeRange = ref({ min: null as number | null, max: null as number | null })
  const showOnlyWithFees = ref(false)
  const sortBy = ref('price_usd')
  const sortDirection = ref('asc')

  const exchangesValue = computed(() => {
    return 'value' in exchanges ? exchanges.value : exchanges
  })

  const filteredExchanges = computed(() => {
    if (!exchangesValue.value || !exchangesValue.value.length) return []
    
    return exchangesValue.value.filter(exchange => {
      // Filter by search query
      if (searchQuery.value && 
          !exchange.exchange_name.toLowerCase().includes(searchQuery.value.toLowerCase())) {
        return false
      }
      
      // Filter by price range
      if (priceRange.value.min !== null && exchange.price_usd < priceRange.value.min) {
        return false
      }
      if (priceRange.value.max !== null && exchange.price_usd > priceRange.value.max) {
        return false
      }
      
      // Filter by volume range
      if (volumeRange.value.min !== null && 
          (exchange.volume_24h === undefined || exchange.volume_24h < volumeRange.value.min)) {
        return false
      }
      if (volumeRange.value.max !== null && 
          (exchange.volume_24h === undefined || exchange.volume_24h > volumeRange.value.max)) {
        return false
      }
      
      // Filter by fees
      if (showOnlyWithFees.value && !exchange.trading_fee) {
        return false
      }
      
      return true
    })
  })

  const sortedExchanges = computed(() => {
    return [...filteredExchanges.value].sort((a, b) => {
      const aValue = a[sortBy.value as keyof Exchange] ?? 0
      const bValue = b[sortBy.value as keyof Exchange] ?? 0
      
      return sortDirection.value === 'asc' 
        ? (aValue < bValue ? -1 : aValue > bValue ? 1 : 0)
        : (bValue < aValue ? -1 : bValue > aValue ? 1 : 0)
    })
  })

  const clearFilters = () => {
    searchQuery.value = ''
    priceRange.value = { min: null, max: null }
    volumeRange.value = { min: null, max: null }
    showOnlyWithFees.value = false
    sortBy.value = 'price_usd'
    sortDirection.value = 'asc'
  }

  return {
    searchQuery,
    priceRange,
    volumeRange,
    showOnlyWithFees,
    sortBy,
    sortDirection,
    filteredExchanges,
    sortedExchanges,
    clearFilters
  }
} 