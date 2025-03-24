import React from 'react';
import './App.css';
import PredictionSearch from './components/PredictionSearch';
import { LineChart } from 'lucide-react';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Simplified Header */}
      <header className="border-b sticky top-0 bg-background z-10 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2">
            <div className="bg-primary p-2 rounded text-primary-foreground">
              <LineChart className="h-5 w-5" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">Market Prediction Analyzer</h1>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="container mx-auto py-8 px-4">
        <PredictionSearch />
      </main>
      
      {/* Footer */}
      <footer className="border-t py-6 bg-muted/20">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-muted-foreground">
            Market Prediction Analyzer &copy; 2025 | AI-Powered Investment Strategy Generator
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;