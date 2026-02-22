import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
    baseURL: API_BASE,
    timeout: 10000,
});

// ── Sensor Data ─────────────────────────────────────────────────────────

export const getSensorData = async (params = {}) => {
    const { page = 1, pageSize = 20, topic, startTime, endTime } = params;
    const queryParams = new URLSearchParams();
    queryParams.set('page', page);
    queryParams.set('page_size', pageSize);
    if (topic) queryParams.set('topic', topic);
    if (startTime) queryParams.set('start_time', startTime);
    if (endTime) queryParams.set('end_time', endTime);

    const res = await api.get(`/sensor-data/?${queryParams.toString()}`);
    return res.data;
};

export const getLatestReadings = async () => {
    const res = await api.get('/sensor-data/latest');
    return res.data;
};

export const getSensorStats = async () => {
    const res = await api.get('/sensor-data/stats');
    return res.data;
};

export const getThresholds = async () => {
    const res = await api.get('/sensor-data/thresholds');
    return res.data;
};

export const getTopics = async () => {
    const res = await api.get('/sensor-data/topics');
    return res.data;
};

// ── Alerts ──────────────────────────────────────────────────────────────

export const getAlerts = async (params = {}) => {
    const { page = 1, pageSize = 20, topic, severity, startTime, endTime } = params;
    const queryParams = new URLSearchParams();
    queryParams.set('page', page);
    queryParams.set('page_size', pageSize);
    if (topic) queryParams.set('topic', topic);
    if (severity) queryParams.set('severity', severity);
    if (startTime) queryParams.set('start_time', startTime);
    if (endTime) queryParams.set('end_time', endTime);

    const res = await api.get(`/alerts/?${queryParams.toString()}`);
    return res.data;
};

export const getRecentAlerts = async (limit = 10) => {
    const res = await api.get(`/alerts/recent?limit=${limit}`);
    return res.data;
};

export const getAlertCounts = async () => {
    const res = await api.get('/alerts/count');
    return res.data;
};

export default api;
