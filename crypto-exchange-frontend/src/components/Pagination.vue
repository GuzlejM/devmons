<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  maxPageButtons: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits(['change-page'])

// Calculate which page buttons to show
const pageButtons = computed(() => {
  // If we have fewer pages than max buttons, show all pages
  if (props.totalPages <= props.maxPageButtons) {
    return Array.from({ length: props.totalPages }, (_, i) => i + 1)
  }
  
  // Calculate start and end of page buttons with current page in the middle if possible
  let start = Math.max(props.currentPage - Math.floor(props.maxPageButtons / 2), 1)
  let end = start + props.maxPageButtons - 1
  
  // Adjust if end is beyond total pages
  if (end > props.totalPages) {
    end = props.totalPages
    start = Math.max(end - props.maxPageButtons + 1, 1)
  }
  
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

const goToPage = (page: number) => {
  if (page === props.currentPage) return
  if (page < 1 || page > props.totalPages) return
  
  emit('change-page', page)
}
</script>

<template>
  <div class="pagination flex justify-center mt-4">
    <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
      <!-- Previous Page Button -->
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-10 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span class="sr-only">Previous</span>
        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clip-rule="evenodd" />
        </svg>
      </button>
      
      <!-- Page Buttons -->
      <button
        v-for="page in pageButtons"
        :key="page"
        @click="goToPage(page)"
        :class="[
          'relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-10',
          currentPage === page 
            ? 'bg-primary-600 text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600' 
            : 'text-gray-900 hover:bg-gray-50'
        ]"
      >
        {{ page }}
      </button>
      
      <!-- Next Page Button -->
      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-10 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span class="sr-only">Next</span>
        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
        </svg>
      </button>
    </nav>
  </div>
</template> 