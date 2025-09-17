import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AuthContainer from './components/Auth/AuthContainer';
import Chat from './components/Chat/Chat';
import ProtectedRoute from './components/ProtectedRoute';
import AlertsPage from "./components/Alerts/Alerts";

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route
            path="/login"
            element={<AuthContainer onAuthSuccess={() => window.location.href = '/chat'} />}
          />
          <Route
            path="/register"
            element={<AuthContainer onAuthSuccess={() => window.location.href = '/chat'} />}
          />
          <Route
            path="/chat"
            element={<Chat onLogout={() => window.location.href = '/login'} />}
          />
          <Route
            path="/chat/:sessionId"
            element={<Chat onLogout={() => window.location.href = '/login'} />}
          />
          <Route path="/" element={<Navigate to="/chat" replace />} />

          {/* Protected alerts page */}
          <Route
            path="/alerts"
            element={
              <ProtectedRoute>
                <AlertsPage onLogout={() => window.location.href = '/login'} />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
