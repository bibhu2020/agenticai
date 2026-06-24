import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 15000 })

export const getScores = () => api.get('/scores').then(r => r.data)
export const getSchedule = () => api.get('/schedule').then(r => r.data)
export const getNews = () => api.get('/news').then(r => r.data)
export const getSummary = () => api.get('/summary').then(r => r.data)
export const getStandings = () => api.get('/standings').then(r => r.data)
export const getHighlights = () => api.get('/highlights').then(r => r.data)
export const refreshCache = () => api.post('/refresh').then(r => r.data)
