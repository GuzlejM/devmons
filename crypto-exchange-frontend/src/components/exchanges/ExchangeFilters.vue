<script setup lang="ts">
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  search: {
    type: String,
    default: ''
  },
  priceRange: {
    type: Object,
    default: () => ({ min: null, max: null })
  },
  volumeRange: {
    type: Object,
    default: () => ({ min: null, max: null })
  },
  showOnlyWithFees: {
    type: Boolean,
    default: false
  },
  viewMode: {
    type: String,
    default: 'cards'
  },
  totalCount: {
    type: Number,
    default: 0
  },
  filteredCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits([
  'update:search', 
  'update:priceRange', 
  'update:volumeRange', 
  'update:showOnlyWithFees',
  'update:viewMode',
  'clear'
])

const hasActiveFilters = computed(() => {
  return props.search !== '' ||
    props.priceRange.min !== null ||
    props.priceRange.max !== null ||
    props.volumeRange.min !== null ||
    props.volumeRange.max !== null ||
    props.showOnlyWithFees
})

// Methods to update filters
const updateSearch = (value: string) => {
  emit('update:search', value)
}

const updatePriceMin = (value: string) => {
  const min = value === '' ? null : parseFloat(value)
  emit('update:priceRange', { ...props.priceRange, min })
}

const updatePriceMax = (value: string) => {
  const max = value === '' ? null : parseFloat(value)
  emit('update:priceRange', { ...props.priceRange, max })
}

const updateVolumeMin = (value: string) => {
  const min = value === '' ? null : parseFloat(value)
  emit('update:volumeRange', { ...props.volumeRange, min })
}

const updateVolumeMax = (value: string) => {
  const max = value === '' ? null : parseFloat(value)
  emit('update:volumeRange', { ...props.volumeRange, max })
}

const toggleShowOnlyWithFees = () => {
  emit('update:showOnlyWithFees', !props.showOnlyWithFees)
}

const clearFilters = () => {
  emit('clear')
}
</script>

<template>
  <div class="exchange-filters mb-6">
    <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-4 mb-4">
      <!-- Header with title and counts -->
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900">Filters</h3>
        <div class="text-sm text-gray-500">
          {{ filteredCount }} of {{ totalCount }} exchanges
        </div>
      </div>
      
      <!-- Search field -->
      <div class="mb-4">
        <label for="search" class="block text-sm font-medium text-gray-700 mb-1">Search</label>
        <div class="relative">
          <input
            id="search"
            type="text"
            :value="search"
            @input="e => updateSearch((e.target as HTMLInputElement).value)"
            class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            placeholder="Search exchanges..."
          />
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>
      
      <!-- Price range filter -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Price Range (USD)</label>
        <div class="flex space-x-2">
          <div class="w-1/2">
            <input
              type="number"
              :value="priceRange.min === null ? '' : priceRange.min"
              @input="e => updatePriceMin((e.target as HTMLInputElement).value)"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              placeholder="Min"
              min="0"
              step="0.01"
            />
          </div>
          <div class="w-1/2">
            <input
              type="number"
              :value="priceRange.max === null ? '' : priceRange.max"
              @input="e => updatePriceMax((e.target as HTMLInputElement).value)"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              placeholder="Max"
              min="0"
              step="0.01"
            />
          </div>
        </div>
      </div>
      
      <!-- Volume range filter -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Volume Range (USD)</label>
        <div class="flex space-x-2">
          <div class="w-1/2">
            <input
              type="number"
              :value="volumeRange.min === null ? '' : volumeRange.min"
              @input="e => updateVolumeMin((e.target as HTMLInputElement).value)"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              placeholder="Min"
              min="0"
              step="1000"
            />
          </div>
          <div class="w-1/2">
            <input
              type="number"
              :value="volumeRange.max === null ? '' : volumeRange.max"
              @input="e => updateVolumeMax((e.target as HTMLInputElement).value)"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              placeholder="Max"
              min="0"
              step="1000"
            />
          </div>
        </div>
      </div>
      
      <!-- Additional filters -->
      <div class="mb-4">
        <label class="flex items-center">
          <input 
            type="checkbox" 
            :checked="showOnlyWithFees"
            @change="toggleShowOnlyWithFees"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          >
          <span class="ml-2 text-sm text-gray-700">Show only with trading fees</span>
        </label>
      </div>
      
      <!-- Filter actions -->
      <div class="flex justify-end">
        <button 
          v-if="hasActiveFilters"
          @click="clearFilters"
          type="button"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg class="mr-2 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          Clear Filters
        </button>
      </div>
    </div>
  </div>
</template> 