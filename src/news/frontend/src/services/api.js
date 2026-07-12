import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 15000 })

export const getAllNews = () => api.get('/news').then(r => r.data)
export const getCategoryNews = (category) => api.get(`/news/${category}`).then(r => r.data)
export const adminTrigger = (passphrase) => api.post('/admin/trigger', { passphrase }).then(r => r.data)
export const adminStatus = (passphrase) => api.post('/admin/status', { passphrase }).then(r => r.data)
export const getLocalZip = () => api.get('/local/zip').then(r => r.data)
export const adminUpdateLocalZip = (passphrase, zip) => api.post('/admin/local-zip', { passphrase, zip }).then(r => r.data)
