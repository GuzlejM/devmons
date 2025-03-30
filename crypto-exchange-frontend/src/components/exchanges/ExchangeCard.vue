<script setup lang="ts">
import { defineProps, defineEmits, computed } from 'vue'

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
  },
  selected: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select'])

const handleClick = () => {
  if (props.selectable) {
    emit('select', props.exchange.exchange_name)
  }
}

const formatPrice = (price?: number): string => {
  if (price === undefined || price === null) return 'N/A'
  return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const formatPercent = (value?: number): string => {
  if (value === undefined || value === null) return 'N/A'
  return `${value.toFixed(2)}%`
}

const isValueMissing = (value?: any): boolean => {
  return value === undefined || value === null
}

const getHighlightClass = (): string => {
  if (props.selected) return 'border-primary-500 ring-2 ring-primary-500 bg-primary-50'
  if (props.isBestPrice) return 'border-green-300 bg-green-50'
  if (props.isBestVolume) return 'border-blue-300 bg-blue-50'
  return 'border-gray-200'
}

const missingFieldCount = computed(() => {
  let count = 0;
  if (isValueMissing(props.exchange.volume_24h)) count++;
  if (isValueMissing(props.exchange.spread)) count++;
  if (isValueMissing(props.exchange.bid_price)) count++;
  if (isValueMissing(props.exchange.ask_price)) count++;
  if (isValueMissing(props.exchange.trading_fee)) count++;
  return count;
})
</script>

<template>
  <div 
    class="exchange-card p-4 rounded-lg border shadow-sm hover:shadow-md transition-all duration-200 relative"
    :class="[
      getHighlightClass(),
      selectable ? 'cursor-pointer hover:border-primary-400' : ''
    ]"
    @click="handleClick"
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
      <div v-if="!isValueMissing(exchange.volume_24h)" class="stat-item">
        <div class="text-gray-500">Volume (24h)</div>
        <div class="font-medium">
          {{ formatPrice(exchange.volume_24h) }}
        </div>
      </div>
      
      <!-- Spread -->
      <div v-if="!isValueMissing(exchange.spread)" class="stat-item">
        <div class="text-gray-500">Spread</div>
        <div class="font-medium">
          {{ formatPercent(exchange.spread) }}
        </div>
      </div>
      
      <!-- Bid -->
      <div v-if="!isValueMissing(exchange.bid_price)" class="stat-item">
        <div class="text-gray-500">Bid</div>
        <div class="font-medium">
          {{ formatPrice(exchange.bid_price) }}
        </div>
      </div>
      
      <!-- Ask -->
      <div v-if="!isValueMissing(exchange.ask_price)" class="stat-item">
        <div class="text-gray-500">Ask</div>
        <div class="font-medium">
          {{ formatPrice(exchange.ask_price) }}
        </div>
      </div>
      
      <!-- Trading Fee -->
      <div v-if="!isValueMissing(exchange.trading_fee)" class="stat-item">
        <div class="text-gray-500">Trading Fee</div>
        <div class="font-medium">
          {{ formatPercent(exchange.trading_fee) }}
        </div>
      </div>
      
      <!-- Last Updated - always show this -->
      <div class="stat-item">
        <div class="text-gray-500">Updated</div>
        <div class="font-medium">
          {{ new Date(exchange.last_updated).toLocaleTimeString() }}
        </div>
      </div>
    </div>
    
    <!-- If most fields are missing, show a message to fill space -->
    <div 
      v-if="missingFieldCount > 3" 
      class="text-center text-sm text-gray-500 mt-4 mb-8"
    >
      Limited data available from this exchange
    </div>
    
    <!-- Select button or Selected label -->
    <div 
      v-if="selectable" 
      class="absolute bottom-2 right-2 z-10"
    >
      <button 
        v-if="!selected"
        class="bg-primary-500 hover:bg-primary-600 text-white text-xs font-medium px-4 py-1.5 rounded-full shadow-sm"
        @click.stop="handleClick"
      >
        Select
      </button>
      <div 
        v-else 
        class="bg-primary-100 text-primary-700 px-4 py-1.5 rounded-full text-xs font-medium"
      >
        Selected ✓
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