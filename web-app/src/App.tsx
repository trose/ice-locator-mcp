import PerformanceMonitorComponent from './components/PerformanceMonitor';
import DeckGlTest from './DeckGlTest';

function App() {
  return (
    <div className="h-screen w-screen">
      <DeckGlTest />

      {/* Performance Monitor - Only show in development */}
      {process.env.NODE_ENV === 'development' && (
        <PerformanceMonitorComponent showMetrics={false} position="bottom-right" />
      )}
    </div>
  );
}

export default App;