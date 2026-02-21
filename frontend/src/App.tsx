import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MasterData from './pages/MasterData';
import Scheduling from './pages/Scheduling';
import Export from './pages/Export';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-100">
        <Router>
          <Routes>
            <Route path="/" element={<MasterData />} />
            <Route path="/scheduling" element={<Scheduling />} />
            <Route path="/export" element={<Export />} />
          </Routes>
        </Router>
      </div>
    </QueryClientProvider>
  );
}

export default App;