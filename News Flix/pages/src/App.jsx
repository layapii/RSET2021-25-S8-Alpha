import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Auth from './pages/Auth';
import HomePage from './pages/HomePage';
import VideoPage from './pages/VideoPage';
import HistoryPage from './pages/HistoryPage';
import PdfProcessing from './pages/PdfProcessing';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Auth />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/video" element={<VideoPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/pdf" element={<PdfProcessing />} />
      </Routes>
    </Router>
  );
};

export default App;
