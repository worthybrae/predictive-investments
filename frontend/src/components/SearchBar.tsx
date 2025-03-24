import React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface SearchBarProps {
  predictionText: string;
  setPredictionText: (value: string) => void;
  handleSubmitPrediction: () => void;
  isSearching: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({
  predictionText,
  setPredictionText,
  handleSubmitPrediction,
  isSearching
}) => {
  return (
    <Card className="border shadow-md overflow-hidden mb-8 max-w-3xl mx-auto">
      <CardHeader className="pb-4 bg-white border-b">
        <CardTitle className="text-xl flex items-center gap-2">
          <div className="bg-primary/10 p-2 rounded-full">
            <Search className="h-5 w-5 text-primary" />
          </div>
          Market Prediction Analysis
        </CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Enter a market prediction to generate investment strategies
        </p>
      </CardHeader>
      <CardContent className="pt-6 pb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Input
              placeholder="E.g., 'Bitcoin will reach $100k by 2026'"
              value={predictionText}
              onChange={(e) => setPredictionText(e.target.value)}
              className="h-12 text-base focus:ring-2 focus:ring-primary focus:ring-offset-2"
            />
          </div>
          <Button 
            onClick={handleSubmitPrediction} 
            disabled={isSearching || !predictionText.trim()}
            className="bg-primary hover:bg-primary/90 shadow-md"
            size="lg"
          >
            {isSearching ? 'Processing...' : 'Analyze'}
            {!isSearching && <ArrowRight className="ml-2 h-4 w-4" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default SearchBar;