import React, { useEffect, useState } from 'react';
import { PerformanceMonitor, reportWebVitals, type PerformanceMetrics } from '../utils/performance';

interface PerformanceMonitorProps {
  showMetrics?: boolean;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}

const PerformanceMonitorComponent: React.FC<PerformanceMonitorProps> = ({
  showMetrics = false,
  position = 'bottom-right'
}) => {
  const [metrics, setMetrics] = useState<Partial<PerformanceMetrics>>({});
  const [isVisible, setIsVisible] = useState(showMetrics);

  useEffect(() => {
    const monitor = PerformanceMonitor.getInstance();

    // Monitor performance metrics
    const updateMetrics = () => {
      const currentMetrics = monitor.getMetrics();
      setMetrics(currentMetrics);

      // Report to analytics
      reportWebVitals(currentMetrics);
    };

    // Update metrics periodically
    const interval = setInterval(updateMetrics, 5000);

    // Initial metrics update
    updateMetrics();

    return () => {
      clearInterval(interval);
      monitor.disconnect();
    };
  }, []);

  const getScoreColor = (value: number, thresholds: { good: number; poor: number }) => {
    if (value <= thresholds.good) return 'text-green-500';
    if (value <= thresholds.poor) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreText = (value: number, thresholds: { good: number; poor: number }) => {
    if (value <= thresholds.good) return 'Good';
    if (value <= thresholds.poor) return 'Needs Improvement';
    return 'Poor';
  };

  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4'
  };

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className={`fixed ${positionClasses[position]} z-50 bg-blue-600 text-white p-2 rounded-full shadow-lg hover:bg-blue-700 transition-colors`}
        title="Show Performance Metrics"
      >
        📊
      </button>
    );
  }

  return (
    <div className={`fixed ${positionClasses[position]} z-50 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900">Core Web Vitals</h3>
        <button
          onClick={() => setIsVisible(false)}
          className="text-gray-400 hover:text-gray-600"
        >
          ×
        </button>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">LCP:</span>
          <div className="flex items-center gap-2">
            <span className={`font-medium ${getScoreColor(metrics.lcp || 0, { good: 2500, poor: 4000 })}`}>
              {metrics.lcp ? `${(metrics.lcp / 1000).toFixed(2)}s` : 'N/A'}
            </span>
            <span className={`text-xs px-1 py-0.5 rounded ${getScoreColor(metrics.lcp || 0, { good: 2500, poor: 4000 }).replace('text-', 'bg-').replace('-500', '-100')}`}>
              {metrics.lcp ? getScoreText(metrics.lcp, { good: 2500, poor: 4000 }) : 'Unknown'}
            </span>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-600">FID:</span>
          <div className="flex items-center gap-2">
            <span className={`font-medium ${getScoreColor(metrics.fid || 0, { good: 100, poor: 300 })}`}>
              {metrics.fid ? `${metrics.fid.toFixed(0)}ms` : 'N/A'}
            </span>
            <span className={`text-xs px-1 py-0.5 rounded ${getScoreColor(metrics.fid || 0, { good: 100, poor: 300 }).replace('text-', 'bg-').replace('-500', '-100')}`}>
              {metrics.fid ? getScoreText(metrics.fid, { good: 100, poor: 300 }) : 'Unknown'}
            </span>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-600">CLS:</span>
          <div className="flex items-center gap-2">
            <span className={`font-medium ${getScoreColor(metrics.cls || 0, { good: 0.1, poor: 0.25 })}`}>
              {metrics.cls ? metrics.cls.toFixed(3) : 'N/A'}
            </span>
            <span className={`text-xs px-1 py-0.5 rounded ${getScoreColor(metrics.cls || 0, { good: 0.1, poor: 0.25 }).replace('text-', 'bg-').replace('-500', '-100')}`}>
              {metrics.cls ? getScoreText(metrics.cls, { good: 0.1, poor: 0.25 }) : 'Unknown'}
            </span>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-600">FCP:</span>
          <span className="font-medium text-blue-600">
            {metrics.fcp ? `${(metrics.fcp / 1000).toFixed(2)}s` : 'N/A'}
          </span>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <div>Updated: {new Date().toLocaleTimeString()}</div>
          <div className="mt-1">
            <button
              onClick={() => window.location.reload()}
              className="text-blue-600 hover:text-blue-800 underline"
            >
              Refresh Page
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMonitorComponent;