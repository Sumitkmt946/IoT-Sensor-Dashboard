import React, { useState, useEffect, useCallback } from 'react';
import { Database } from 'lucide-react';
import { getSensorData, getTopics, getThresholds } from '../services/api';

function RawData() {
    const [data, setData] = useState(null);
    const [page, setPage] = useState(1);
    const [topic, setTopic] = useState('');
    const [topics, setTopics] = useState([]);
    const [thresholds, setThresholds] = useState({});
    const [loading, setLoading] = useState(true);
    const pageSize = 20;

    const fetchData = useCallback(async () => {
        try {
            const res = await getSensorData({ page, pageSize, topic: topic || undefined });
            setData(res);
        } catch (err) {
            console.error('Error fetching sensor data:', err);
        } finally {
            setLoading(false);
        }
    }, [page, topic]);

    useEffect(() => {
        Promise.all([
            getTopics().then(setTopics),
            getThresholds().then(r => setThresholds(r.thresholds || {})),
        ]).catch(() => { });
    }, []);

    useEffect(() => {
        setLoading(true);
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [fetchData]);

    const isBreach = (key, value) => {
        const t = thresholds[key];
        if (!t) return false;
        return value < t.min || value > t.max;
    };

    const formatTime = (ts) => new Date(ts).toLocaleString();

    const PARAMS = ['temperature', 'humidity', 'voltage', 'current', 'pressure'];
    const UNITS = { temperature: '°C', humidity: '%', voltage: 'V', current: 'A', pressure: 'hPa' };

    if (loading && !data) {
        return (
            <div className="loading-container">
                <div className="spinner" />
                <p>Loading sensor data…</p>
            </div>
        );
    }

    return (
        <div>
            <div className="page-header">
                <h2>Raw Data</h2>
                <p>All incoming sensor readings in tabular format</p>
            </div>

            <div className="data-table-container">
                <div className="table-header">
                    <h3>
                        <Database size={18} style={{ marginRight: 8, verticalAlign: 'middle' }} />
                        Sensor Readings ({data?.total ?? 0})
                    </h3>
                    <div className="table-filters">
                        <select value={topic} onChange={e => { setTopic(e.target.value); setPage(1); }}>
                            <option value="">All Topics</option>
                            {topics.map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                    </div>
                </div>

                {(!data || data.items.length === 0) ? (
                    <div className="empty-state">
                        <Database size={48} />
                        <p>No sensor data found</p>
                    </div>
                ) : (
                    <>
                        <div style={{ overflowX: 'auto' }}>
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Timestamp</th>
                                        <th>Topic</th>
                                        {PARAMS.map(p => (
                                            <th key={p}>{p.charAt(0).toUpperCase() + p.slice(1)} ({UNITS[p]})</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.items.map((row) => (
                                        <tr key={row.id}>
                                            <td style={{ color: 'var(--text-muted)' }}>{row.id}</td>
                                            <td style={{ whiteSpace: 'nowrap' }}>{formatTime(row.timestamp)}</td>
                                            <td>
                                                <span className="topic-badge">{row.topic}</span>
                                            </td>
                                            {PARAMS.map(p => (
                                                <td
                                                    key={p}
                                                    className={isBreach(p, row[p]) ? 'value-breach' : ''}
                                                >
                                                    {row[p]?.toFixed(2)}
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Pagination */}
                        <div className="pagination">
                            <div className="pagination-info">
                                Page {data.page} of {data.total_pages} ({data.total} total)
                            </div>
                            <div className="pagination-buttons">
                                <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                                    Previous
                                </button>
                                {Array.from({ length: Math.min(data.total_pages, 5) }, (_, i) => {
                                    const startPage = Math.max(1, page - 2);
                                    const p = startPage + i;
                                    if (p > data.total_pages) return null;
                                    return (
                                        <button
                                            key={p}
                                            className={p === page ? 'active' : ''}
                                            onClick={() => setPage(p)}
                                        >
                                            {p}
                                        </button>
                                    );
                                })}
                                <button disabled={page >= data.total_pages} onClick={() => setPage(p => p + 1)}>
                                    Next
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default RawData;
