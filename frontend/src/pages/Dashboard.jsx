import React, { useState, useEffect, useCallback } from 'react';
import {
    Activity, MessageSquare, AlertTriangle, Radio,
    Thermometer, Droplets, Zap, Gauge, Wind
} from 'lucide-react';
import { getLatestReadings, getSensorStats, getAlertCounts, getThresholds } from '../services/api';

const PARAM_CONFIG = {
    temperature: { icon: Thermometer, unit: '°C', label: 'Temperature', color: '#ef4444' },
    humidity: { icon: Droplets, unit: '%', label: 'Humidity', color: '#3b82f6' },
    voltage: { icon: Zap, unit: 'V', label: 'Voltage', color: '#f59e0b' },
    current: { icon: Gauge, unit: 'A', label: 'Current', color: '#8b5cf6' },
    pressure: { icon: Wind, unit: 'hPa', label: 'Pressure', color: '#10b981' },
};

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [latest, setLatest] = useState([]);
    const [alertCounts, setAlertCounts] = useState(null);
    const [thresholds, setThresholds] = useState({});
    const [loading, setLoading] = useState(true);

    const fetchAll = useCallback(async () => {
        try {
            const [stData, ltData, acData, thData] = await Promise.all([
                getSensorStats(),
                getLatestReadings(),
                getAlertCounts(),
                getThresholds(),
            ]);
            setStats(stData);
            setLatest(ltData);
            setAlertCounts(acData);
            setThresholds(thData.thresholds || {});
        } catch (err) {
            console.error('Dashboard fetch error:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchAll();
        const interval = setInterval(fetchAll, 5000);
        return () => clearInterval(interval);
    }, [fetchAll]);

    const isBreach = (key, value) => {
        const t = thresholds[key];
        if (!t) return false;
        return value < t.min || value > t.max;
    };

    const formatTime = (ts) => {
        if (!ts) return '—';
        return new Date(ts).toLocaleString();
    };

    const getTopicName = (topic) => {
        const parts = topic.split('/');
        return parts[parts.length - 1].replace(/_/g, ' ');
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner" />
                <p>Loading dashboard…</p>
            </div>
        );
    }

    return (
        <div>
            <div className="page-header">
                <h2>Dashboard</h2>
                <p>Real-time sensor monitoring & alert overview</p>
            </div>

            {/* ── Stat Cards ────────────────────────────────────────────────── */}
            <div className="stats-grid">
                <div className="stat-card blue">
                    <div className="stat-icon"><MessageSquare size={22} /></div>
                    <div className="stat-value">{stats?.total_messages ?? 0}</div>
                    <div className="stat-label">Total Messages</div>
                </div>
                <div className="stat-card green">
                    <div className="stat-icon"><Radio size={22} /></div>
                    <div className="stat-value">{stats?.total_topics ?? 0}</div>
                    <div className="stat-label">Active Topics</div>
                </div>
                <div className="stat-card red">
                    <div className="stat-icon"><AlertTriangle size={22} /></div>
                    <div className="stat-value">{alertCounts?.total_alerts ?? 0}</div>
                    <div className="stat-label">Total Alerts</div>
                </div>
                <div className="stat-card purple">
                    <div className="stat-icon"><Activity size={22} /></div>
                    <div className="stat-value">{alertCounts?.critical_count ?? 0}</div>
                    <div className="stat-label">Critical Alerts</div>
                </div>
            </div>

            {/* ── Latest Sensor Readings ────────────────────────────────────── */}
            <h3 className="section-title">
                <Radio size={18} /> Latest Sensor Readings
            </h3>
            {latest.length === 0 ? (
                <div className="empty-state">
                    <Radio size={48} />
                    <p>No sensor data yet. Start the MQTT simulator to generate data.</p>
                </div>
            ) : (
                <div className="sensor-grid">
                    {latest.map((reading) => (
                        <div className="sensor-card" key={reading.id}>
                            <div className="sensor-card-header">
                                <h3>{getTopicName(reading.topic)}</h3>
                                <span className="topic-badge">{reading.topic}</span>
                            </div>
                            <div className="sensor-values">
                                {Object.entries(PARAM_CONFIG).map(([key, cfg]) => {
                                    const value = reading[key];
                                    const breach = isBreach(key, value);
                                    const Icon = cfg.icon;
                                    return (
                                        <div className="sensor-param" key={key}>
                                            <span className="param-label">
                                                {cfg.label}
                                            </span>
                                            <span className={`param-value ${breach ? 'breach' : ''}`}>
                                                {value?.toFixed(2)}
                                                <span className="param-unit"> {cfg.unit}</span>
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                            <div style={{ marginTop: 10, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                {formatTime(reading.timestamp)}
                            </div>
                        </div>
                    ))}
                </div>
            )}


        </div>
    );
}

export default Dashboard;
