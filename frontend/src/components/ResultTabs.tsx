import React from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import InvestmentStrategyTab from './InvestmentStrategyTab';
import PredictionAnalysisTab from './PredictionAnalysisTab';
import RelevantTickersTab from './RelevantTickersTab';
import { Briefcase, BarChart3, PieChart } from 'lucide-react';

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

interface ResultTabsProps {
  predictionResults: PredictionResults;
}

const ResultTabs: React.FC<ResultTabsProps> = ({
  predictionResults
}) => {
  const { analysis, investment_strategy, relevant_tickers } = predictionResults;
  
  return (
    <div className="mt-8">
      <Tabs defaultValue="strategy" className="w-full">
        <TabsList className="grid grid-cols-3 mb-6 bg-white border rounded-lg p-1 shadow-sm">
          <TabsTrigger 
            value="strategy" 
            className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:font-medium rounded-md"
          >
            <div className="flex items-center gap-2">
              <PieChart className="h-4 w-4" />
              <span className="hidden sm:inline">Investment Strategy</span>
              <span className="sm:hidden">Strategy</span>
            </div>
          </TabsTrigger>
          <TabsTrigger 
            value="analysis"
            className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:font-medium rounded-md"
          >
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Prediction Analysis</span>
              <span className="sm:hidden">Analysis</span>
            </div>
          </TabsTrigger>
          <TabsTrigger 
            value="tickers"
            className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:font-medium rounded-md"
          >
            <div className="flex items-center gap-2">
              <Briefcase className="h-4 w-4" />
              <span className="hidden sm:inline">Relevant Tickers</span>
              <span className="sm:hidden">Tickers</span>
            </div>
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="strategy">
          <InvestmentStrategyTab strategy={investment_strategy} />
        </TabsContent>
        
        <TabsContent value="analysis">
          <PredictionAnalysisTab analysis={analysis} />
        </TabsContent>
        
        <TabsContent value="tickers">
          <RelevantTickersTab relevantTickers={relevant_tickers} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ResultTabs;