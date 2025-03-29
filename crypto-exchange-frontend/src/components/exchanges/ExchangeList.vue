<script setup lang="ts">
import { ref, computed } from 'vue'
import ExchangeCard from './ExchangeCard.vue'
import ExchangeTable from './ExchangeTable.vue'
import Pagination from '../Pagination.vue'
import ExchangeFilters from './ExchangeFilters.vue'
import ExchangeGroupHeader from './ExchangeGroupHeader.vue'
import { useExchangeFilters } from '../../composables/useExchangeFilters'
import { useExchangeGrouping } from '../../composables/useExchangeGrouping'

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

interface PriceRange {
  min: number | null;
  max: number | null;
}

interface VolumeRange {
  min: number | null;
  max: number | null;
}

const props = defineProps({
  exchanges: {
    type: Array as () => Exchange[],
    required: true
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

const emit = defineEmits(['compare'])

// View state
const viewMode = ref('cards') // 'cards', 'table', 'top5', 'compare'
const currentPage = ref(1)
const itemsPerPage = ref(5)
const selectedExchanges = ref<string[]>([])
const expandedGroups = ref(['major', 'popular'])

// Use composables for filtering and grouping
const { 
  searchQuery, 
  priceRange, 
  volumeRange, 
  showOnlyWithFees,
  sortBy,
  sortDirection,
  filteredExchanges,
  sortedExchanges,
  clearFilters
} = useExchangeFilters(props.exchanges)

const { groupedExchanges } = useExchangeGrouping(sortedExchanges)

// Pagination
const paginatedExchanges = computed(() => {
  if (viewMode.value === 'top5') {
    return sortedExchanges.value.slice(0, 5)
  }
  
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return sortedExchanges.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(sortedExchanges.value.length / itemsPerPage.value)
})

// Methods
const handleViewModeChange = (mode: string) => {
  viewMode.value = mode
}

const handleSort = (field: string) => {
  if (sortBy.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortDirection.value = 'asc'
  }
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

const toggleGroupExpansion = (groupId: string) => {
  const index = expandedGroups.value.indexOf(groupId)
  if (index === -1) {
    expandedGroups.value.push(groupId)
  } else {
    expandedGroups.value.splice(index, 1)
  }
}

const toggleExchangeSelection = (exchangeName: string) => {
  const index = selectedExchanges.value.indexOf(exchangeName)
  if (index === -1) {
    if (selectedExchanges.value.length < 3) {
      selectedExchanges.value.push(exchangeName)
    }
  } else {
    selectedExchanges.value.splice(index, 1)
  }
}

const handleCompare = () => {
  if (selectedExchanges.value.length >= 2) {
    emit('compare', selectedExchanges.value)
  }
}

const updateSearch = (val: string) => {
  searchQuery.value = val
}

const updatePriceRange = (val: PriceRange) => {
  priceRange.value = val
}

const updateVolumeRange = (val: VolumeRange) => {
  volumeRange.value = val
}

const updateShowOnlyWithFees = (val: boolean) => {
  showOnlyWithFees.value = val
}

const updateViewMode = (val: string) => {
  viewMode.value = val
}
</script>

<template>
  <div class="exchange-list">
    <!-- Filters Section -->
    <ExchangeFilters 
      :search="searchQuery"
      :priceRange="priceRange"
      :volumeRange="volumeRange"
      :showOnlyWithFees="showOnlyWithFees"
      :viewMode="viewMode"
      :totalCount="props.exchanges.length"
      :filteredCount="filteredExchanges.length"
      @update:search="updateSearch"
      @update:priceRange="updatePriceRange"
      @update:volumeRange="updateVolumeRange"
      @update:showOnlyWithFees="updateShowOnlyWithFees"
      @update:viewMode="updateViewMode"
      @clear="clearFilters"
    />
    
    <!-- Results Count and View Mode Selector -->
    <div class="bg-gray-50 px-4 py-2 rounded-md mb-4 flex justify-between items-center">
      <p class="text-sm text-gray-600">
        Showing {{ filteredExchanges.length > 0 ? Math.min(filteredExchanges.length, itemsPerPage) : 0 }} 
        of {{ filteredExchanges.length }} exchanges
        <span v-if="searchQuery"> matching "{{ searchQuery }}"</span>
      </p>
      
      <div class="flex gap-2">
        <button 
          v-for="mode in ['cards', 'table', 'top5', 'compare']" 
          :key="mode"
          @click="handleViewModeChange(mode)"
          class="px-2 py-1 text-xs rounded"
          :class="viewMode === mode ? 'bg-primary-100 text-primary-800' : 'bg-gray-100 text-gray-500'"
        >
          {{ { cards: 'Cards', table: 'Table', top5: 'Top 5', compare: 'Compare' }[mode] }}
        </button>
      </div>
    </div>
    
    <!-- Compare Mode -->
    <div v-if="viewMode === 'compare'" class="mb-4">
      <div v-if="selectedExchanges.length < 2" class="bg-yellow-50 border border-yellow-200 p-4 rounded-md text-center">
        Select at least 2 exchanges to compare them side by side
      </div>
      <div v-else class="flex flex-col md:flex-row gap-4">
        <div 
          v-for="exchangeName in selectedExchanges" 
          :key="exchangeName"
          class="flex-1 card p-4"
        >
          <ExchangeCard 
            :exchange="props.exchanges.find(e => e.exchange_name === exchangeName) as Exchange"
            :isBestPrice="exchangeName === props.bestPriceExchange"
            :isBestVolume="exchangeName === props.bestVolumeExchange"
          />
          <button @click="toggleExchangeSelection(exchangeName)" class="btn-danger mt-2 w-full">
            Remove
          </button>
        </div>
      </div>
    </div>
    
    <!-- No Results Message -->
    <div v-else-if="filteredExchanges.length === 0" class="bg-gray-50 p-6 rounded-md text-center">
      No exchanges match your filters
    </div>
    
    <!-- Cards View -->
    <div v-else-if="viewMode === 'cards'" class="mb-4">
      <template v-for="(group, groupId) in groupedExchanges" :key="groupId">
        <ExchangeGroupHeader 
          :title="group.name" 
          :count="group.exchanges.length"
          :expanded="expandedGroups.includes(groupId)"
          @toggle="toggleGroupExpansion(groupId)"
        />
        
        <div v-if="expandedGroups.includes(groupId)" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          <div
            v-for="exchange in group.exchanges"
            :key="exchange.exchange_name"
            class="relative"
          >
            <ExchangeCard 
              :exchange="exchange"
              :isBestPrice="exchange.exchange_name === props.bestPriceExchange"
              :isBestVolume="exchange.exchange_name === props.bestVolumeExchange"
              :selectable="false"
              @click="toggleExchangeSelection(exchange.exchange_name)"
            />
          </div>
        </div>
      </template>
    </div>
    
    <!-- Table View -->
    <div v-else-if="viewMode === 'table'" class="mb-4">
      <ExchangeTable 
        :exchanges="paginatedExchanges"
        :sortBy="sortBy"
        :sortDirection="sortDirection"
        :bestPriceExchange="props.bestPriceExchange"
        :bestVolumeExchange="props.bestVolumeExchange"
        @sort="handleSort"
      />
    </div>
    
    <!-- Top 5 View -->
    <div v-else-if="viewMode === 'top5'" class="mb-4">
      <ExchangeTable 
        :exchanges="paginatedExchanges"
        :sortBy="sortBy"
        :sortDirection="sortDirection"
        :bestPriceExchange="props.bestPriceExchange"
        :bestVolumeExchange="props.bestVolumeExchange"
        @sort="handleSort"
      />
      
      <div v-if="sortedExchanges.length > 5" class="text-center mt-4">
        <button 
          @click="viewMode = 'table'"
          class="text-primary-600 hover:text-primary-800 text-sm font-medium"
        >
          View all {{ sortedExchanges.length }} exchanges
        </button>
      </div>
    </div>
    
    <!-- Pagination -->
    <Pagination 
      v-if="viewMode !== 'top5' && viewMode !== 'compare' && totalPages > 1"
      :current-page="currentPage"
      :total-pages="totalPages"
      @change-page="handlePageChange"
    />
  </div>
</template>

<style scoped>
.card {
  @apply bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden transition-all duration-200;
}

.btn-danger {
  @apply bg-red-600 hover:bg-red-700 text-white text-sm px-3 py-1 rounded;
}
</style> 