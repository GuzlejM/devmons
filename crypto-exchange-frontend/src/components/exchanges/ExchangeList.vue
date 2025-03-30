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
const isFiltersOpen = ref(false)

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
    <!-- Persistent Search Bar -->
    <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-3 mb-4">
      <div class="relative">
        <input
          type="text"
          :value="searchQuery"
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

    <!-- Collapsible Filters Section -->
    <div class="mb-4">
      <div 
        class="bg-white border border-gray-200 rounded-lg shadow-sm p-3 cursor-pointer"
        @click="isFiltersOpen = !isFiltersOpen"
      >
        <div class="flex justify-between items-center">
          <div class="flex items-center">
            <svg 
              class="h-5 w-5 text-gray-500 mr-2" 
              :class="isFiltersOpen ? 'transform rotate-180' : ''"
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            <span class="font-medium">Advanced Filters</span>
          </div>
          <div class="text-sm text-gray-500">
            {{ filteredExchanges.length }} of {{ props.exchanges.length }} exchanges
          </div>
        </div>
      </div>
      <div v-show="isFiltersOpen" class="mt-2">
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
      </div>
    </div>
    
    <!-- Results Count and View Mode Selector -->
    <div class="bg-gray-50 px-4 py-2 rounded-md mb-4 flex flex-col md:flex-row justify-between items-center gap-2">
      <div class="flex items-center justify-between w-full md:w-auto">
        <p class="text-sm text-gray-600">
          Showing {{ filteredExchanges.length > 0 ? Math.min(filteredExchanges.length, itemsPerPage) : 0 }} 
          of {{ filteredExchanges.length }} exchanges
          <span v-if="searchQuery"> matching "{{ searchQuery }}"</span>
        </p>
        
        <!-- Sorting Options -->
        <div class="md:ml-4 flex items-center">
          <span class="text-sm text-gray-500 mr-2">Sort by:</span>
          <select 
            v-model="sortBy" 
            class="text-sm border-gray-300 rounded-md shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
            @change="sortDirection = 'asc'"
          >
            <option value="price_usd">Price</option>
            <option value="volume_24h">Volume</option>
            <option value="exchange_name">Name</option>
            <option value="spread">Spread</option>
          </select>
          <button 
            class="ml-2 p-1 rounded-md hover:bg-gray-200" 
            @click="sortDirection = sortDirection === 'asc' ? 'desc' : 'asc'"
            title="Toggle sort direction"
          >
            <svg class="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="sortDirection === 'asc'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>
      
      <div class="flex gap-2 mt-2 md:mt-0">
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
    
    <!-- Floating Compare Button when exchanges are selected -->
    <div 
      v-if="selectedExchanges.length >= 1 && viewMode !== 'compare'"
      class="fixed bottom-4 right-4 z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-3 border border-gray-200">
        <p class="text-sm font-medium mb-2">{{ selectedExchanges.length }} exchange{{ selectedExchanges.length !== 1 ? 's' : '' }} selected</p>
        <button 
          @click="viewMode = 'compare'" 
          class="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md flex items-center justify-center"
          :class="selectedExchanges.length >= 2 ? 'animate-pulse' : ''"
        >
          <span v-if="selectedExchanges.length < 2">Select one more to compare</span>
          <span v-else>Compare Now</span>
        </button>
      </div>
    </div>
    
    <!-- Compare Mode -->
    <div v-if="viewMode === 'compare'" class="mb-4">
      <div v-if="selectedExchanges.length < 2" class="bg-yellow-50 border border-yellow-200 p-4 rounded-md text-center">
        <p class="mb-2 font-medium">Select at least 2 exchanges to compare them side by side</p>
        <button 
          @click="viewMode = 'cards'" 
          class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          Go to Cards View to Select
        </button>
      </div>
      <div v-else>
        <div class="bg-blue-50 border border-blue-200 p-3 rounded-md mb-3">
          <div class="flex justify-between items-center">
            <p class="text-blue-800 text-sm">
              <span class="font-medium">Comparing {{ selectedExchanges.length }} exchanges.</span> 
              You can see their key metrics side by side.
            </p>
            <button 
              @click="selectedExchanges = []" 
              class="text-blue-700 hover:text-blue-900 text-sm underline"
            >
              Clear All
            </button>
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row gap-4">
          <div 
            v-for="exchangeName in selectedExchanges" 
            :key="exchangeName"
            class="flex-1"
          >
            <div 
              class="bg-white border rounded-lg shadow-sm overflow-hidden"
              :class="{
                'border-primary-500 ring-2 ring-primary-200': 
                  (exchangeName === props.bestPriceExchange || exchangeName === props.bestVolumeExchange)
              }"
            >
              <!-- Best Exchange Indicator -->
              <div 
                v-if="exchangeName === props.bestPriceExchange || exchangeName === props.bestVolumeExchange"
                class="bg-primary-100 text-primary-800 px-3 py-1 text-sm font-medium text-center border-b border-primary-200"
              >
                {{ exchangeName === props.bestPriceExchange ? 'Best Price' : 'Best Volume' }}
              </div>
              
              <ExchangeCard 
                :exchange="props.exchanges.find(e => e.exchange_name === exchangeName) as Exchange"
                :isBestPrice="exchangeName === props.bestPriceExchange"
                :isBestVolume="exchangeName === props.bestVolumeExchange"
              />
              <div class="border-t border-gray-100 p-3 bg-gray-50">
                <button 
                  @click="toggleExchangeSelection(exchangeName)" 
                  class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded text-sm font-medium flex items-center justify-center"
                >
                  <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V7" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16" />
                  </svg>
                  Unselect
                </button>
              </div>
            </div>
          </div>
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
              :selectable="true"
              :selected="selectedExchanges.includes(exchange.exchange_name)"
              @select="toggleExchangeSelection"
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
      v-if="viewMode === 'table' && totalPages > 1"
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