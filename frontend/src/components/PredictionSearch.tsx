import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { AlertCircle } from 'lucide-react';

import SearchBar from './SearchBar';
import StatusTracker from './StatusTracker';
import ResultTabs from './ResultTabs';

// Types for prediction API responses
interface Trade {
  ticker: string;
  price: number;
  volume: number;
  type: string;
  date: string;
}

interface InvestmentStrategy {
  name: string;
  description: string;
  pros: string[];
  cons: string[];
  timing: string;
  risk: number;
  estimated_return: number;
  involved_tickers: string[];
  trades: Trade[];
}

interface PredictionAnalysis {
  timing: string;
  confidence: number;
  tolerance: number;
  related_industries: string[];
  name: string;
  category: string;
  best_case_scenario: string;
  worst_case_scenario: string;
}

interface RelevantTickers {
  tickers: string[];
}

interface PredictionResults {
  prediction_text: string;
  success: boolean;
  analysis: PredictionAnalysis;
  market_research: string | null;
  relevant_tickers: RelevantTickers;
  investment_strategy: InvestmentStrategy;
}

interface PredictionStatusResponse {
  prediction_id: string;
  status: 'pending' | 'analyzing' | 'researching' | 'finding_tickers' | 'creating_strategy' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  message: string;
  progress: number;
  result: PredictionResults | null;
}

const PredictionSearch: React.FC = () => {
  // API base URL - change this to match your backend
  const API_BASE_URL = 'preferred-alex-personal-stingrae-a1a23113.koyeb.app:8000';
  
  // State for prediction input and results
  const [predictionText, setPredictionText] = useState<string>('');
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [predictionId, setPredictionId] = useState<string | null>(null);
  const [predictionStatus, setPredictionStatus] = useState<PredictionStatusResponse | null>(null);
  const [predictionResults, setPredictionResults] = useState<PredictionResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Function to submit prediction
  const handleSubmitPrediction = async (): Promise<void> => {
    if (!predictionText.trim()) return;
    
    setIsSearching(true);
    setError(null);
    setPredictionResults(null);
    
    try {
      // Full URL with API base
      const url = `${API_BASE_URL}/api/v1/ai/predict/async`;
      console.log('Submitting to:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prediction_text: predictionText,
          options: {
            model: "gpt-4o-mini",
            use_web_search: true,
            search_model: "sonar",
            use_finviz_screener: true,
            include_stock_data: true
          }
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error Response:', response.status, errorText);
        setError(`API error: ${response.status} - ${errorText || 'No error details available'}`);
        setIsSearching(false);
        return;
      }
      
      try {
        const data = await response.json();
        setPredictionId(data.prediction_id);
      } catch (jsonErr) {
        console.error('JSON Parse Error:', jsonErr);
        setError(`Error parsing API response: ${jsonErr instanceof Error ? jsonErr.message : 'Invalid JSON'}`);
        setIsSearching(false);
      }
    } catch (err) {
      console.error('Fetch Error:', err);
      setError(`Error submitting prediction: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setIsSearching(false);
    }
  };

  // Function to check prediction status
  const checkPredictionStatus = async (): Promise<void> => {
    if (!predictionId) return;
    
    try {
      // Full URL with API base
      const url = `${API_BASE_URL}/api/v1/ai/predict/async/${predictionId}`;
      console.log('Checking status at:', url);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Status API Error:', response.status, errorText);
        setError(`Status API error: ${response.status} - ${errorText || 'No error details available'}`);
        setIsSearching(false);
        return;
      }
      
      try {
        const data: PredictionStatusResponse = await response.json();
        setPredictionStatus(data);
        
        if (data.status === 'completed') {
          setPredictionResults(data.result);
          setIsSearching(false);
        } else if (data.status === 'failed') {
          setError(data.message || 'Prediction processing failed');
          setIsSearching(false);
        }
      } catch (jsonErr) {
        console.error('JSON Parse Error:', jsonErr);
        setError(`Error parsing status response: ${jsonErr instanceof Error ? jsonErr.message : 'Invalid JSON'}`);
        setIsSearching(false);
      }
    } catch (err) {
      console.error('Fetch Error:', err);
      setError(`Error checking prediction status: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setIsSearching(false);
    }
  };

  // Check status every 2 seconds when we have a prediction ID and are still searching
  useEffect(() => {
    let intervalId: number | undefined;
    
    if (predictionId && isSearching) {
      checkPredictionStatus(); // Check immediately
      intervalId = window.setInterval(checkPredictionStatus, 2000);
    }
    
    return () => {
      if (intervalId !== undefined) window.clearInterval(intervalId);
    };
  }, [predictionId, isSearching]);

  return (
    <div className="max-w-4xl mx-auto">
      <SearchBar 
        predictionText={predictionText}
        setPredictionText={setPredictionText}
        handleSubmitPrediction={handleSubmitPrediction}
        isSearching={isSearching}
      />
      
      {error && (
        <Alert variant="destructive" className="mt-4">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {isSearching && predictionStatus && (
        <StatusTracker 
          status={predictionStatus.status}
          progress={predictionStatus.progress}
          message={predictionStatus.message}
        />
      )}
      
      {predictionResults && (
        <ResultTabs predictionResults={predictionResults} />
      )}
    </div>
  );
};

export default PredictionSearch;