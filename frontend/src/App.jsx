import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import About from './pages/About';
import Contact from './pages/Contact';
import LiveMap from './pages/LiveMap';
import Dashboard from './pages/Dashboard';
import Report from './pages/Report';
import AdminDashboard from './pages/AdminDashboard';
import Sathi from './pages/Sathi';
import DisasterManagement from './pages/DisasterManagement';
import { RealTimeProvider } from './context/RealTimeContext';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  return (
    <RealTimeProvider>
      <BrowserRouter>
        <Header isLoggedIn={isLoggedIn} onLogout={handleLogout} />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/liveMap" element={<LiveMap />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/report" element={<Report />} />
          <Route path="/sathi" element={<Sathi />} />
          <Route path="/disaster" element={<DisasterManagement />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </BrowserRouter>
    </RealTimeProvider>
  );
}


