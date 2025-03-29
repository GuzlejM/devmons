<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

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
  exchanges: {
    type: Array as () => Exchange[],
    required: true
  },
  sortBy: {
    type: String,
    default: 'price_usd'
  },
  sortDirection: {
    type: String,
    default: 'asc'
  },
  bestPriceExchange: {
    type: String,
    default: null
  },
  bestVolumeExchange: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['sort'])

const handleSort = (field: string) => {
  emit('sort', field)
}

const formatPrice = (price?: number): string => {
  if (price === undefined || price === null) return 'N/A'
  return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const formatPercent = (value?: number): string => {
  if (value === undefined || value === null) return 'N/A'
  return `${value.toFixed(2)}%`
}

const getRowClass = (exchangeName: string): string => {
  if (exchangeName === props.bestPriceExchange) return 'bg-green-50'
  if (exchangeName === props.bestVolumeExchange) return 'bg-blue-50'
  return ''
}
</script>

<template>
  <div class="exchange-table">
    <div v-if="exchanges.length === 0" class="bg-gray-50 p-6 rounded-md text-center">
      No exchanges match your filters
    </div>
    
    <div v-else class="overflow-x-auto">
      <div class="table-container">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50 sticky top-0 z-10">
            <tr>
              <th 
                scope="col" 
                class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                @click="handleSort('exchange_name')"
              >
                <div class="flex items-center">
                  Exchange
                  <svg v-if="sortBy === 'exchange_name'" class="ml-1 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path v-if="sortDirection === 'asc'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </th>
              <th 
                scope="col" 
                class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                @click="handleSort('price_usd')"
              >
                <div class="flex items-center">
                  Price (USD)
                  <svg v-if="sortBy === 'price_usd'" class="ml-1 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path v-if="sortDirection === 'asc'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </th>
              <th 
                scope="col" 
                class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                @click="handleSort('volume_24h')"
              >
                <div class="flex items-center">
                  24h Volume
                  <svg v-if="sortBy === 'volume_24h'" class="ml-1 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path v-if="sortDirection === 'asc'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </th>
              <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Bid/Ask
              </th>
              <th 
                scope="col" 
                class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                @click="handleSort('spread')"
              >
                <div class="flex items-center">
                  Spread
                  <svg v-if="sortBy === 'spread'" class="ml-1 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path v-if="sortDirection === 'asc'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </th>
              <th 
                scope="col" 
                class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                @click="handleSort('trading_fee')"
              >
                <div class="flex items-center">
                  Fee
                  <svg v-if="sortBy === 'trading_fee'" class="ml-1 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path v-if="sortDirection === 'asc'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="exchange in exchanges" 
              :key="exchange.exchange_name"
              class="hover:bg-gray-50 transition-colors"
              :class="getRowClass(exchange.exchange_name)"
            >
              <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                <div class="flex items-center">
                  {{ exchange.exchange_name }}
                  <span 
                    v-if="exchange.exchange_name === bestPriceExchange" 
                    class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                  >
                    Best
                  </span>
                  <span 
                    v-else-if="exchange.exchange_name === bestVolumeExchange" 
                    class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    Volume
                  </span>
                </div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm font-semibold text-gray-900">
                {{ formatPrice(exchange.price_usd) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ formatPrice(exchange.volume_24h) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                <div class="space-y-1">
                  <div>Bid: {{ formatPrice(exchange.bid_price) }}</div>
                  <div>Ask: {{ formatPrice(exchange.ask_price) }}</div>
                </div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ formatPercent(exchange.spread) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ formatPercent(exchange.trading_fee) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

thead {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

th, td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

th {
  position: sticky;
  top: 0;
  background-color: #f9fafb;
  z-index: 10;
}

tbody tr:last-child td {
  border-bottom: none;
}

/* Custom scrollbar for Webkit browsers */
.table-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style> 