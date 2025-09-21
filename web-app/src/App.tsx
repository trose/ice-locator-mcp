import React, { Suspense, lazy } from 'react';
import PerformanceMonitorComponent from './components/PerformanceMonitor';

// Lazy load the main component for better initial load performance
const DeckGlTest = lazy(() => import('./DeckGlTest'));

const App: React.FC = () => {
  return (
    <div className="h-screen w-screen">
      <Suspense fallback={
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="mt-4 text-white text-lg">Loading ICE Facility Heatmap...</p>
        </div>
      }>
        <DeckGlTest />
      </Suspense>

      {/* Performance Monitor - Only show in development */}
      {process.env.NODE_ENV === 'development' && (
        <PerformanceMonitorComponent showMetrics={false} position="bottom-right" />
      )}
    </div>
  );
};

export default App;