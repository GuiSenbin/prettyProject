import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const toast = ref({ show: false, msg: '', type: 'info' })
  let timer = null

  function showToast(msg, type = 'info') {
    if (timer) clearTimeout(timer)
    toast.value = { show: true, msg, type }
    timer = setTimeout(() => {
      toast.value.show = false
    }, 2500)
  }

  return { toast, showToast }
})
