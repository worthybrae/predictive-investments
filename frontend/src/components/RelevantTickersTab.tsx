import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Briefcase, TrendingUp, ExternalLink } from 'lucide-react';

interface RelevantTickers {
  tickers: string[];
}

interface RelevantTickersTabProps {
  relevantTickers: RelevantTickers;
}

const RelevantTickersTab: React.FC<RelevantTickersTabProps> = ({
  relevantTickers
}) => {
  // Function to get ticket URL (e.g., for Yahoo Finance)
  const getTickerUrl = (ticker: string) => {
    return `https://finance.yahoo.com/quote/${ticker}`;
  };

  // Function to generate a random financial percentage for demo
  const getRandomChange = () => {
    return (Math.random() * 6 - 2).toFixed(2);
  };
  
  // Group tickers into rows for better display
  const tickerRows = [];
  for (let i = 0; i < relevantTickers.tickers.length; i += 3) {
    tickerRows.push(relevantTickers.tickers.slice(i, i + 3));
  }
  
  return (
    <Card className="overflow-hidden border-t-4 border-t-primary shadow-md">
      <CardHeader className="pb-3 bg-gradient-to-r from-primary/10 to-transparent border-b">
        <CardTitle className="text-xl md:text-2xl text-primary flex items-center gap-2">
          <Briefcase className="h-5 w-5" />
          Relevant Tickers
        </CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Companies and securities related to this prediction
        </p>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          {relevantTickers.tickers.map((ticker, i) => {
            const changeValue = getRandomChange();
            const isPositive = parseFloat(changeValue) >= 0;
            
            return (
              <a 
                key={i} 
                href={getTickerUrl(ticker)}
                target="_blank"
                rel="noopener noreferrer"
                className="group block"
              >
                <div className="bg-white p-4 rounded-lg border shadow-sm hover:border-primary hover:shadow-md transition-all flex flex-col h-full">
                  <div className="flex justify-between items-center mb-3">
                    <span className="font-bold text-lg text-primary">{ticker}</span>
                    <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <div className="flex items-center mt-auto">
                    <TrendingUp className={`h-4 w-4 mr-2 ${isPositive ? 'text-green-600' : 'text-red-600'}`} />
                    <span 
                      className={`text-sm font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}
                    >
                      {isPositive ? '+' : ''}{changeValue}%
                    </span>
                  </div>
                </div>
              </a>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default RelevantTickersTab;