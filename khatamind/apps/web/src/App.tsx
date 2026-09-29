import { Routes, Route, Link } from 'react-router-dom';
import Today from './components/Today';
import ActionInbox from './components/ActionInbox';
import Customer360 from './components/Customer360';
import AgentCenter from './components/AgentCenter';
import SimulationLab from './components/SimulationLab';
import Impact from './components/Impact';
import { Home, Inbox, Users, Settings, Beaker, TrendingUp } from 'lucide-react';

function App() {
  return (
    <div className="flex h-screen bg-gray-50 text-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-blue-600">KhataMind</h1>
          <p className="text-sm text-gray-500">Agent Memory System</p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link to="/" className="flex items-center gap-3 p-2 hover:bg-gray-100 rounded-md">
            <Home size={20} /> Today
          </Link>
          <Link to="/inbox" className="flex items-center gap-3 p-2 hover:bg-gray-100 rounded-md">
            <Inbox size={20} /> Action Inbox
          </Link>
          <Link to="/customers" className="flex items-center gap-3 p-2 hover:bg-gray-100 rounded-md">
            <Users size={20} /> Customers
          </Link>
          <Link to="/agent-center" className="flex items-center gap-3 p-2 hover:bg-gray-100 rounded-md">
            <Settings size={20} /> Agent Center
          </Link>
          <Link to="/simulation" className="flex items-center gap-3 p-2 hover:bg-gray-100 rounded-md">
            <Beaker size={20} /> Simulation Lab
          </Link>
          <Link to="/impact" className="flex items-center gap-3 p-2 hover:bg-gray-100 rounded-md">
            <TrendingUp size={20} /> Impact
          </Link>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Today />} />
          <Route path="/inbox" element={<ActionInbox />} />
          <Route path="/customers" element={<Customer360 />} />
          <Route path="/agent-center" element={<AgentCenter />} />
          <Route path="/simulation" element={<SimulationLab />} />
          <Route path="/impact" element={<Impact />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
