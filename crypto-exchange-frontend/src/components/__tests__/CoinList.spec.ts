import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import CoinList from '../CoinList.vue'
import * as api from '../../services/api'

// Mock the API
vi.mock('../../services/api', () => ({
  getCoins: vi.fn()
}))

describe('CoinList.vue', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('displays loading state initially', () => {
    const wrapper = mount(CoinList)
    expect(wrapper.find('.loading').exists()).toBe(true)
    expect(wrapper.find('.loading').text()).toContain('Loading coins')
  })

  it('displays error message when API fails', async () => {
    vi.mocked(api.getCoins).mockRejectedValueOnce(new Error('API error'))
    
    const wrapper = mount(CoinList)
    await vi.dynamicImportSettled()
    
    expect(wrapper.find('.error').exists()).toBe(true)
    expect(wrapper.find('.error').text()).toContain('Failed to load coins')
  })

  it('displays coins when API returns successfully', async () => {
    const mockCoins = [
      { id: 1, coingecko_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', logo_url: null, created_at: '2023-01-01', updated_at: '2023-01-01' },
      { id: 2, coingecko_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', logo_url: null, created_at: '2023-01-01', updated_at: '2023-01-01' }
    ]
    
    vi.mocked(api.getCoins).mockResolvedValueOnce(mockCoins)
    
    const wrapper = mount(CoinList)
    await vi.dynamicImportSettled()
    
    expect(wrapper.findAll('.coin-card').length).toBe(2)
    expect(wrapper.findAll('.coin-symbol')[0].text()).toBe('BTC')
    expect(wrapper.findAll('.coin-name')[0].text()).toBe('Bitcoin')
  })

  it('emits select-coin event when a coin is clicked', async () => {
    const mockCoins = [
      { id: 1, coingecko_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', logo_url: null, created_at: '2023-01-01', updated_at: '2023-01-01' }
    ]
    
    vi.mocked(api.getCoins).mockResolvedValueOnce(mockCoins)
    
    const wrapper = mount(CoinList)
    await vi.dynamicImportSettled()
    
    await wrapper.find('.coin-card').trigger('click')
    
    expect(wrapper.emitted('select-coin')).toBeTruthy()
    expect(wrapper.emitted('select-coin')![0]).toEqual(['bitcoin'])
  })
}) 