import { shallowMount } from '@vue/test-utils'
import Timer from '@/components/common/Timer.vue'

describe('Timer Component', () => {
  it('renders correctly with given seconds', () => {
    const wrapper = shallowMount(Timer, {
      props: {
        seconds: 65
      }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.classes()).toContain('timer-component')
    expect(wrapper.classes()).toContain('active')
    expect(wrapper.text()).toBe('1:05')
  })
  
  it('formats time correctly for minutes and seconds', () => {
    const wrapper = shallowMount(Timer, {
      props: {
        seconds: 125
      }
    })
    expect(wrapper.text()).toBe('2:05')
  })
  
  it('formats time correctly when seconds is less than 10', () => {
    const wrapper = shallowMount(Timer, {
      props: {
        seconds: 65
      }
    })
    expect(wrapper.text()).toBe('1:05')
  })
  
  it('shows 0:00 when seconds is 0', () => {
    const wrapper = shallowMount(Timer, {
      props: {
        seconds: 0
      }
    })
    expect(wrapper.text()).toBe('0:00')
  })
  
  it('shows 0:00 when seconds is negative', () => {
    const wrapper = shallowMount(Timer, {
      props: {
        seconds: -10
      }
    })
    expect(wrapper.text()).toBe('0:00')
  })
  
  it('applies active class when seconds is greater than 0', () => {
    const wrapper = shallowMount(Timer, {
      props: {
        seconds: 30
      }
    })
    expect(wrapper.classes()).toContain('active')
  })
  
  it('does not apply active class when seconds is 0', () => {
    const wrapper = shallowMount(Timer, {
      props: {
        seconds: 0
      }
    })
    expect(wrapper.classes()).not.toContain('active')
  })
  
  it('updates when seconds prop changes', async () => {
    const wrapper = shallowMount(Timer, {
      props: {
        seconds: 30
      }
    })
    expect(wrapper.text()).toBe('0:30')
    
    await wrapper.setProps({ seconds: 60 })
    expect(wrapper.text()).toBe('1:00')
  })
})
