<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  currentPage: number
  totalPages: number
}>()

const emit = defineEmits(['change-page'])

const goToPage = (page: number) => {
  if (page < 1 || page > props.totalPages) return
  emit('change-page', page)
}

const pages = computed(() => {
  // Always show first and last page, and a window around current page
  const window = 1
  const allPages = []
  
  for (let i = 1; i <= props.totalPages; i++) {
    if (
      i === 1 || 
      i === props.totalPages || 
      (i >= props.currentPage - window && i <= props.currentPage + window)
    ) {
      allPages.push(i)
    } else if (
      (i === props.currentPage - window - 1) || 
      (i === props.currentPage + window + 1)
    ) {
      allPages.push('...')
    }
  }
  
  // Remove duplicates (for small total pages)
  return allPages.filter((page, index, self) => 
    page === '...' ? page !== self[index - 1] : true
  )
})
</script>

<template>
  <nav class="flex justify-center">
    <ul class="inline-flex items-center -space-x-px">
      <li>
        <button 
          @click="goToPage(currentPage - 1)" 
          :disabled="currentPage === 1"
          class="block px-3 py-2 ml-0 leading-tight text-gray-500 bg-white border border-gray-300 rounded-l-lg hover:bg-gray-100 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span class="sr-only">Previous</span>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </li>
      
      <li v-for="(page, index) in pages" :key="index">
        <button 
          v-if="page !== '...'"
          @click="goToPage(Number(page))" 
          :class="[
            'px-3 py-2 leading-tight border border-gray-300',
            currentPage === page 
              ? 'text-white bg-primary-600 border-primary-600' 
              : 'text-gray-500 bg-white hover:bg-gray-100 hover:text-gray-700'
          ]"
        >
          {{ page }}
        </button>
        <span 
          v-else
          class="px-3 py-2 leading-tight text-gray-500 bg-white border border-gray-300"
        >
          {{ page }}
        </span>
      </li>
      
      <li>
        <button 
          @click="goToPage(currentPage + 1)" 
          :disabled="currentPage === totalPages"
          class="block px-3 py-2 leading-tight text-gray-500 bg-white border border-gray-300 rounded-r-lg hover:bg-gray-100 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span class="sr-only">Next</span>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </li>
    </ul>
  </nav>
</template> 