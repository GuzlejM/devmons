<script setup lang="ts">
import { defineProps } from 'vue'

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

const props = defineProps({
  exchange: {
    type: Object as () => Exchange,
    required: true
  },
  isBestPrice: {
    type: Boolean,
    default: false
  },
  isBestVolume: {
    type: Boolean,
    default: false
  },
  selectable: {
    type: Boolean,
    default: false
  }
})

const formatPrice = (price?: number): string => {
  if (price === undefined || price === null) return 'N/A'
  return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const formatPercent = (value?: number): string => {
  if (value === undefined || value === null) return 'N/A'
  return `${value.toFixed(2)}%`
}

const getHighlightClass = (): string => {
  if (props.isBestPrice) return 'border-green-300 bg-green-50'
  if (props.isBestVolume) return 'border-blue-300 bg-blue-50'
  return 'border-gray-200'
}
</script>

<template>
  <div 
    class="exchange-card p-4 rounded-lg border shadow-sm hover:shadow-md transition-all duration-200"
    :class="getHighlightClass()"
  >
    <!-- Header section -->
    <div class="flex justify-between items-start mb-3">
      <div class="font-semibold text-lg text-gray-900">{{ exchange.exchange_name }}</div>
      <div class="flex space-x-2">
        <span v-if="isBestPrice" class="badge bg-green-100 text-green-800">Best Price</span>
        <span v-if="isBestVolume" class="badge bg-blue-100 text-blue-800">High Volume</span>
      </div>
    </div>
    
    <!-- Main price -->
    <div class="mb-4">
      <div class="text-2xl font-bold text-gray-900">{{ formatPrice(exchange.price_usd) }}</div>
      <div class="text-sm text-gray-500">Price</div>
    </div>
    
    <!-- Stats grid -->
    <div class="grid grid-cols-2 gap-3 text-sm">
      <!-- Volume -->
      <div class="stat-item">
        <div class="text-gray-500">Volume (24h)</div>
        <div class="font-medium">{{ formatPrice(exchange.volume_24h) }}</div>
      </div>
      
      <!-- Spread -->
      <div class="stat-item">
        <div class="text-gray-500">Spread</div>
        <div class="font-medium">{{ formatPercent(exchange.spread) }}</div>
      </div>
      
      <!-- Bid -->
      <div class="stat-item">
        <div class="text-gray-500">Bid</div>
        <div class="font-medium">{{ formatPrice(exchange.bid_price) }}</div>
      </div>
      
      <!-- Ask -->
      <div class="stat-item">
        <div class="text-gray-500">Ask</div>
        <div class="font-medium">{{ formatPrice(exchange.ask_price) }}</div>
      </div>
      
      <!-- Trading Fee -->
      <div class="stat-item">
        <div class="text-gray-500">Trading Fee</div>
        <div class="font-medium">{{ formatPercent(exchange.trading_fee) }}</div>
      </div>
      
      <!-- Last Updated -->
      <div class="stat-item">
        <div class="text-gray-500">Updated</div>
        <div class="font-medium">{{ new Date(exchange.last_updated).toLocaleTimeString() }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.badge {
  @apply px-2 py-0.5 text-xs font-medium rounded-full whitespace-nowrap;
}

.stat-item {
  @apply flex flex-col;
}
</style> 