import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { ChevronRight, LineChart, TrendingUp, AlertCircle } from 'lucide-react';

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

interface InvestmentStrategyTabProps {
  strategy: InvestmentStrategy;
}

const InvestmentStrategyTab: React.FC<InvestmentStrategyTabProps> = ({ 
  strategy 
}) => {
  return (
    <Card className="overflow-hidden border-t-4 border-t-primary shadow-md">
      <CardHeader className="pb-4 bg-gradient-to-r from-primary/10 to-transparent border-b">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
          <div>
            <CardTitle className="text-xl md:text-2xl text-primary flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              {strategy.name}
            </CardTitle>
            <CardDescription className="mt-1">
              Timing: {strategy.timing}
            </CardDescription>
          </div>
          <div className="flex gap-4">
            <div className="bg-background rounded-lg px-4 py-2 shadow-sm border flex flex-col items-center">
              <span className="text-xs text-muted-foreground">Return</span>
              <span className="font-bold text-green-600">{(strategy.estimated_return * 100).toFixed(1)}%</span>
            </div>
            <div className="bg-background rounded-lg px-4 py-2 shadow-sm border flex flex-col items-center">
              <span className="text-xs text-muted-foreground">Risk</span>
              <span className={`font-bold ${strategy.risk > 0.7 ? 'text-red-600' : strategy.risk > 0.4 ? 'text-amber-600' : 'text-green-600'}`}>
                {(strategy.risk * 10).toFixed(1)}/10
              </span>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-6 space-y-6">
        <div>
          <p className="mb-6 text-base leading-relaxed">{strategy.description}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg border shadow-sm hover:border-primary/40 transition-all">
              <h4 className="font-medium mb-3 text-primary flex items-center">
                <LineChart className="h-4 w-4 mr-2" />
                Pros
              </h4>
              <ul className="space-y-3">
                {strategy.pros.map((pro, i) => (
                  <li key={i} className="flex items-start">
                    <ChevronRight className="h-4 w-4 mr-2 mt-1 text-green-600 flex-shrink-0" />
                    <span>{pro}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-white p-6 rounded-lg border shadow-sm hover:border-primary/40 transition-all">
              <h4 className="font-medium mb-3 text-primary flex items-center">
                <AlertCircle className="h-4 w-4 mr-2" />
                Cons
              </h4>
              <ul className="space-y-3">
                {strategy.cons.map((con, i) => (
                  <li key={i} className="flex items-start">
                    <ChevronRight className="h-4 w-4 mr-2 mt-1 text-red-600 flex-shrink-0" />
                    <span>{con}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
        
        <div>
          <div className="rounded-lg overflow-hidden border shadow-md">
            <h4 className="font-medium p-4 bg-primary text-primary-foreground flex items-center">
              Recommended Trades
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-muted/30 border-b">
                    <th className="text-left p-3 font-medium">Ticker</th>
                    <th className="text-left p-3 font-medium">Type</th>
                    <th className="text-left p-3 font-medium">Price</th>
                    <th className="text-left p-3 font-medium">Allocation</th>
                    <th className="text-left p-3 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {strategy.trades.map((trade, i) => (
                    <tr key={i} className={`${i % 2 === 0 ? 'bg-background' : 'bg-muted/10'} hover:bg-muted/20 transition-colors`}>
                      <td className="p-3 font-medium text-primary">{trade.ticker}</td>
                      <td className="p-3 capitalize">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          trade.type === 'buy' ? 'bg-green-100 text-green-800' : 
                          trade.type === 'sell' ? 'bg-red-100 text-red-800' : 
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {trade.type}
                        </span>
                      </td>
                      <td className="p-3">${trade.price.toFixed(2)}</td>
                      <td className="p-3">{(trade.volume * 100).toFixed(1)}%</td>
                      <td className="p-3">{trade.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className="bg-muted/10 border-t py-4">
        <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
          <div>
            <span className="font-medium">Involved Tickers:</span> {strategy.involved_tickers.join(', ')}
          </div>
        </div>
      </CardFooter>
    </Card>
  );
};

export default InvestmentStrategyTab;