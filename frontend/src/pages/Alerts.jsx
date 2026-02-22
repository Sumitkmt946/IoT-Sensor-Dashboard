import React, { useState, useEffect, useCallback } from 'react';
import { AlertTriangle, Filter } from 'lucide-react';
import { getAlerts, getTopics } from '../services/api';

function Alerts() {
    const [data, setData] = useState(null);
    const [page, setPage] = useState(1);
    const [topic, setTopic] = useState('');
    const [severity, setSeverity] = useState('');
    const [topics, setTopics] = useState([]);
    const [loading, setLoading] = useState(true);
    const pageSize = 15;

    const fetchAlerts = useCallback(async () => {
        try {
            const res = await getAlerts({ page, pageSize, topic: topic || undefined, severity: severity || undefined });
            setData(res);
        } catch (err) {
            console.error('Error fetching alerts:', err);
        } finally {
            setLoading(false);
        }
    }, [page, topic, severity]);

    useEffect(() => {
        getTopics().then(setTopics).catch(() => { });
    }, []);

    useEffect(() => {
        setLoading(true);
        fetchAlerts();
        const interval = setInterval(fetchAlerts, 5000);
        return () => clearInterval(interval);
    }, [fetchAlerts]);

    const formatTime = (ts) => new Date(ts).toLocaleString();

    if (loading && !data) {
        return (
            <div className="loading-container">
                <div className="spinner" />
                <p>Loading alerts…</p>
            </div>
        );
    }

    return (
        <div>
            <div className="page-header">
                <h2>Alerts</h2>
                <p>Threshold breach alerts from all sensor topics</p>
            </div>

            <div className="data-table-container">
                <div className="table-header">
                    <h3>
                        <AlertTriangle size={18} style={{ marginRight: 8, verticalAlign: 'middle' }} />
                        All Alerts ({data?.total ?? 0})
                    </h3>
                    <div className="table-filters">
                        <select value={topic} onChange={e => { setTopic(e.target.value); setPage(1); }}>
                            <option value="">All Topics</option>
                            {topics.map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                        <select value={severity} onChange={e => { setSeverity(e.target.value); setPage(1); }}>
                            <option value="">All Severities</option>
                            <option value="warning">Warning</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>
                </div>

                {(!data || data.items.length === 0) ? (
                    <div className="empty-state">
                        <AlertTriangle size={48} />
                        <p>No alerts found</p>
                    </div>
                ) : (
                    <>
                        <div style={{ overflowX: 'auto' }}>
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Timestamp</th>
                                        <th>Topic</th>
                                        <th>Severity</th>
                                        <th>Violated Parameters</th>
                                        <th>Actual Values</th>
                                        <th>Threshold Limits</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.items.map((alert) => (
                                        <tr key={alert.id} className={`alert-row ${alert.severity}`}>
                                            <td style={{ whiteSpace: 'nowrap' }}>{formatTime(alert.timestamp)}</td>
                                            <td>
                                                <span className="topic-badge">{alert.topic}</span>
                                            </td>
                                            <td>
                                                <span className={`severity-badge ${alert.severity}`}>
                                                    {alert.severity}
                                                </span>
                                            </td>
                                            <td>
                                                {alert.violated_keys.map(k => (
                                                    <span className="violated-key" key={k}>{k}</span>
                                                ))}
                                            </td>
                                            <td>
                                                {alert.violated_keys.map(k => (
                                                    <div key={k} style={{ fontSize: '0.8rem', marginBottom: 2 }}>
                                                        <strong style={{ color: 'var(--accent-red)' }}>{k}</strong>: {alert.actual_values[k]?.toFixed?.(2) ?? alert.actual_values[k]}
                                                    </div>
                                                ))}
                                            </td>
                                            <td>
                                                {alert.violated_keys.map(k => {
                                                    const t = alert.threshold_values[k];
                                                    return (
                                                        <div key={k} style={{ fontSize: '0.8rem', marginBottom: 2 }}>
                                                            <strong>{k}</strong>: {t?.min} – {t?.max}
                                                        </div>
                                                    );
                                                })}
                                            </td>
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

export default Alerts;
