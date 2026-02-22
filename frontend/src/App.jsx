import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, AlertTriangle, Database, Activity, Menu, X } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import RawData from './pages/RawData';

function App() {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <Router>
            <div className="app-layout">
                {/* Mobile overlay */}
                <div
                    className={`overlay ${sidebarOpen ? 'active' : ''}`}
                    onClick={() => setSidebarOpen(false)}
                />

                {/* Sidebar */}
                <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                    <div className="sidebar-header">
                        <div className="sidebar-logo">
                            <div className="logo-icon">
                                <Activity size={22} color="white" />
                            </div>
                            <div>
                                <h1>SensorHub</h1>
                                <p>IoT Dashboard</p>
                            </div>
                        </div>
                    </div>

                    <nav className="sidebar-nav">
                        <NavLink
                            to="/"
                            end
                            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                            onClick={() => setSidebarOpen(false)}
                        >
                            <LayoutDashboard size={20} />
                            Dashboard
                        </NavLink>
                        <NavLink
                            to="/alerts"
                            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                            onClick={() => setSidebarOpen(false)}
                        >
                            <AlertTriangle size={20} />
                            Alerts
                        </NavLink>
                        <NavLink
                            to="/raw-data"
                            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                            onClick={() => setSidebarOpen(false)}
                        >
                            <Database size={20} />
                            Raw Data
                        </NavLink>
                    </nav>

                    <div className="sidebar-footer">
                        <div className="mqtt-status">
                            <span className="dot"></span>
                            MQTT Connected
                        </div>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="main-content">
                    {/* Mobile header */}
                    <div className="mobile-header">
                        <button onClick={() => setSidebarOpen(true)}>
                            <Menu size={24} />
                        </button>
                        <h2 style={{ fontSize: '1rem', fontWeight: 700 }}>SensorHub</h2>
                        <div style={{ width: 40 }} />
                    </div>

                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/alerts" element={<Alerts />} />
                        <Route path="/raw-data" element={<RawData />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
