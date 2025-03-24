# api/services/ai_service.py
import json
import logging
from typing import Dict, Any, List, Optional
from services.openai import OpenAITemplateService
from services.perplexity import PerplexityService
from models.templates import TEMPLATES
from processors.prediction import PredictionProcessor
from processors.finviz import FinvizProcessor

logger = logging.getLogger(__name__)

class AIService:
    """Service for orchestrating AI operations."""
    
    @classmethod
    async def analyze_prediction(
        cls,
        prediction_text: str,
        model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """
        Analyze a prediction text to extract structured information.
        
        Args:
            prediction_text: The prediction to analyze
            model: OpenAI model to use
            
        Returns:
            Structured analysis of the prediction
        """
        try:
            result = await OpenAITemplateService.process_template(
                template_name="prediction_analysis",
                variables={"prediction_text": prediction_text},
                model=model
            )
            
            if not result.get("success"):
                logger.error(f"Failed to analyze prediction: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": f"Failed to analyze prediction: {result.get('error', 'Unknown error')}",
                    "result": None
                }
                
            return {
                "success": True,
                "result": result.get("result", {})
            }
            
        except Exception as e:
            logger.exception(f"Unexpected error analyzing prediction: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "result": None
            }
    
    @classmethod
    async def get_market_research(
        cls,
        prediction_text: str,
        industries: Optional[List[str]] = None,
        timeframe: Optional[str] = None,
        search_model: str = "sonar"
    ) -> Dict[str, Any]:
        """
        Get market research for a prediction using Perplexity.
        
        Args:
            prediction_text: The prediction statement
            industries: Specific industries to focus on
            timeframe: Timeframe of the prediction
            search_model: Perplexity model to use
            
        Returns:
            Market research for the prediction
        """
        try:
            # Build the query
            industries_str = ', '.join(industries) if industries else "relevant industries"
            timeframe_str = f"Timeframe: {timeframe}" if timeframe else ""
            
            # Use the market research template
            template = TEMPLATES["market_research"]
            
            # Format the prompt
            variables = {
                "prediction_text": prediction_text,
                "industries": industries_str,
                "timeframe": timeframe_str
            }
            
            market_query = template["user_prompt_template"].format(**variables)
            
            # Perform the search
            result = await PerplexityService.search_market_info(
                query=market_query,
                model=search_model
            )
            
            return result
            
        except Exception as e:
            logger.exception(f"Error getting market research: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "content": None
            }
    
    @classmethod
    async def find_relevant_tickers(
        cls,
        prediction_text: str,
        prediction_analysis: Optional[Dict[str, Any]] = None,
        use_web_search: bool = False,
        search_model: str = "sonar",
        model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """
        Find tickers relevant to a prediction.
        
        Args:
            prediction_text: The prediction text to analyze
            prediction_analysis: Optional pre-computed prediction analysis
            use_web_search: Whether to enhance analysis with web search
            search_model: Perplexity model to use for web search
            model: OpenAI model to use
            
        Returns:
            Relevant tickers for the prediction
        """
        try:
            variables = {"prediction_text": prediction_text}
            
            # Get prediction analysis if not provided
            local_prediction_analysis = prediction_analysis
            if not local_prediction_analysis:
                # Create an analysis first
                analysis_result = await cls.analyze_prediction(
                    prediction_text=prediction_text,
                    model=model
                )
                
                if not analysis_result["success"]:
                    return {
                        "success": False,
                        "error": f"Failed to analyze prediction: {analysis_result.get('error', 'Unknown error')}",
                        "result": None
                    }
                    
                local_prediction_analysis = analysis_result["result"]
            
            variables["prediction_analysis"] = json.dumps(local_prediction_analysis)
            
            # Add web search data if requested
            if use_web_search:
                # Get market research
                perplexity_result = await cls.get_market_research(
                    prediction_text=prediction_text,
                    industries=local_prediction_analysis.get("related_industries", []),
                    timeframe=local_prediction_analysis.get("timing", ""),
                    search_model=search_model
                )
                
                if perplexity_result["success"]:
                    variables["web_research"] = f"Web Research Results:\n\n{perplexity_result['content']}"
            
            # Find tickers using the template
            result = await OpenAITemplateService.process_template(
                template_name="ticker_finder",
                variables=variables,
                model=model
            )
            
            return result
            
        except Exception as e:
            logger.exception(f"Error finding relevant tickers: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "result": None
            }
    
    @classmethod
    async def create_investment_strategy(
        cls,
        prediction_text: str,
        prediction_analysis: Optional[Dict[str, Any]] = None,
        relevant_tickers: Optional[Dict[str, Any]] = None,
        market_research: Optional[str] = None,
        include_stock_data: bool = False,
        include_year_data: bool = False,
        include_week_data: bool = False,
        model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """
        Create an investment strategy based on a prediction.
        
        Args:
            prediction_text: The prediction statement
            prediction_analysis: Optional pre-computed prediction analysis
            relevant_tickers: Optional pre-computed relevant tickers
            market_research: Optional pre-computed market research
            include_stock_data: Whether to include stock data
            include_year_data: Whether to include 1-year historical data
            include_week_data: Whether to include 1-week hourly data
            model: OpenAI model to use
            
        Returns:
            Investment strategy for the prediction
        """
        try:
            # Prepare variables for template
            variables = {"prediction_text": prediction_text}
            
            # Get prediction analysis if not provided
            local_prediction_analysis = prediction_analysis
            if not local_prediction_analysis:
                # Create an analysis first
                analysis_result = await cls.analyze_prediction(
                    prediction_text=prediction_text,
                    model=model
                )
                
                if not analysis_result["success"]:
                    return {
                        "success": False,
                        "error": f"Failed to analyze prediction: {analysis_result.get('error', 'Unknown error')}",
                        "result": None
                    }
                    
                local_prediction_analysis = analysis_result["result"]
            
            variables["prediction_analysis"] = json.dumps(local_prediction_analysis)
            
            # Get relevant tickers if not provided
            local_relevant_tickers = relevant_tickers
            if not local_relevant_tickers:
                # Find relevant tickers
                tickers_result = await cls.find_relevant_tickers(
                    prediction_text=prediction_text,
                    prediction_analysis=local_prediction_analysis,
                    model=model
                )
                
                if not tickers_result["success"]:
                    return {
                        "success": False,
                        "error": f"Failed to find relevant tickers: {tickers_result.get('error', 'Unknown error')}",
                        "result": None
                    }
                    
                local_relevant_tickers = tickers_result["result"]
            
            variables["relevant_tickers"] = json.dumps(local_relevant_tickers)
            
            # Add market research if provided or fetch if not
            if market_research:
                variables["market_research"] = f"Market Research:\n\n{market_research}"
            
            # Get stock data if requested
            if include_stock_data and local_relevant_tickers:
                tickers = PredictionProcessor.extract_tickers_from_result(local_relevant_tickers)
                
                if tickers:
                    # Get stock data
                    stock_data = await PredictionProcessor.get_stock_data(
                        tickers=tickers,
                        include_year_data=include_year_data,
                        include_week_data=include_week_data
                    )
                    
                    if stock_data:
                        variables["stock_data"] = f"Stock Data:\n\n{json.dumps(stock_data, indent=2)}"
            
            # Process template
            result = await OpenAITemplateService.process_template(
                template_name="investment_strategy",
                variables=variables,
                model=model
            )
            
            return result
            
        except Exception as e:
            logger.exception(f"Error creating investment strategy: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "result": None
            }
    
    @classmethod
    async def generate_finviz_filters(
        cls,
        prediction_text: str,
        prediction_analysis: Dict[str, Any],
        model: str = "gpt-4o-mini-mini"
    ) -> Dict[str, Any]:
        """
        Generate Finviz screener filters for a prediction.
        
        Args:
            prediction_text: The prediction text
            prediction_analysis: Structured analysis of the prediction
            model: OpenAI model to use
            
        Returns:
            Generated Finviz filters and reasoning
        """
        try:
            # Step 1: Get filter info
            filter_info = await FinvizProcessor.get_filter_info()
            
            if not filter_info:
                return {
                    "success": False,
                    "error": "Failed to get filter info",
                    "filters": {},
                    "reasoning": {}
                }
            
            # Step 2: Select filter categories
            filter_selection_result = await OpenAITemplateService.process_template(
                template_name="finviz_filter_selection",
                variables={
                    "prediction_text": prediction_text,
                    "prediction_analysis": json.dumps(prediction_analysis),
                    "filter_info": json.dumps(filter_info)
                },
                model=model
            )
            
            if not filter_selection_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to select filter categories: {filter_selection_result.get('error', 'Unknown error')}",
                    "filters": {},
                    "reasoning": {}
                }
                
            filter_selection = filter_selection_result.get("result", {})
            selected_filters = filter_selection.get("selected_filters", [])
            filter_reasoning = filter_selection.get("reasoning", {})
            
            if not selected_filters:
                return {
                    "success": False,
                    "error": "No filters selected",
                    "filters": {},
                    "reasoning": filter_reasoning
                }
            
            # Step 3: Get filter options
            filter_options = await FinvizProcessor.get_filter_options(selected_filters)
            
            if not filter_options:
                return {
                    "success": False,
                    "error": "Failed to get filter options",
                    "filters": {},
                    "reasoning": filter_reasoning
                }
            
            # Step 4: Select filter values
            filter_values_result = await OpenAITemplateService.process_template(
                template_name="finviz_filter_values",
                variables={
                    "prediction_text": prediction_text,
                    "prediction_analysis": json.dumps(prediction_analysis),
                    "filter_options": json.dumps(filter_options)
                },
                model=model
            )
            
            if not filter_values_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to select filter values: {filter_values_result.get('error', 'Unknown error')}",
                    "filters": {},
                    "reasoning": {
                        "filter_selection": filter_reasoning
                    }
                }
                
            filter_values = filter_values_result.get("result", {})
            filters = filter_values.get("filters", {})
            value_selections = filter_values.get("selections", {})
            
            # Combine reasoning
            combined_reasoning = {
                "filter_selection": filter_reasoning,
                "value_selection": value_selections
            }
            
            return {
                "success": True,
                "filters": filters,
                "reasoning": combined_reasoning
            }
            
        except Exception as e:
            logger.exception(f"Error generating Finviz filters: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "filters": {},
                "reasoning": {}
            }
    
    @classmethod
    async def run_finviz_screener(
        cls,
        filters: Dict[str, str]
    ) -> List[str]:
        """
        Run the Finviz screener with the given filters.
        
        Args:
            filters: Dictionary of filter name-value pairs
            
        Returns:
            List of tickers from the screener results
        """
        return await FinvizProcessor.run_screener(filters)
    
    @classmethod
    async def full_prediction_analysis(
        cls,
        prediction_text: str,
        model: str = "gpt-4o-mini",
        use_web_search: bool = False,
        search_model: str = "sonar",
        use_finviz_screener: bool = True,
        include_stock_data: bool = False,
        include_year_data: bool = False,
        include_week_data: bool = False
    ) -> Dict[str, Any]:
        """
        Run a complete prediction analysis pipeline.
        
        Args:
            prediction_text: The prediction to analyze
            model: OpenAI model to use
            use_web_search: Whether to use web search for market research
            search_model: Perplexity model to use for web search
            use_finviz_screener: Whether to use Finviz screener
            include_stock_data: Whether to include stock data
            include_year_data: Whether to include 1-year data
            include_week_data: Whether to include 1-week data
            
        Returns:
            Complete prediction analysis results
        """
        try:
            # Step 1: Analyze the prediction
            analysis_result = await cls.analyze_prediction(
                prediction_text=prediction_text,
                model=model
            )
            
            if not analysis_result["success"]:
                return {
                    "prediction_text": prediction_text,
                    "success": False,
                    "error": analysis_result["error"],
                    "analysis": None,
                    "market_research": None,
                    "relevant_tickers": None,
                    "investment_strategy": None
                }
            
            prediction_analysis = analysis_result["result"]
            
            # Step 2: Get market research if requested
            market_research = None
            if use_web_search:
                perplexity_result = await cls.get_market_research(
                    prediction_text=prediction_text,
                    industries=prediction_analysis.get("related_industries", []),
                    timeframe=prediction_analysis.get("timing", ""),
                    search_model=search_model
                )
                
                if perplexity_result["success"]:
                    market_research = perplexity_result["content"]
            
            # Step 3: Get relevant tickers
            tickers_result = await cls.find_relevant_tickers(
                prediction_text=prediction_text,
                prediction_analysis=prediction_analysis,
                use_web_search=use_web_search,
                search_model=search_model,
                model=model
            )
            
            if not tickers_result["success"]:
                return {
                    "prediction_text": prediction_text,
                    "success": False,
                    "error": tickers_result["error"],
                    "analysis": prediction_analysis,
                    "market_research": market_research,
                    "relevant_tickers": None,
                    "investment_strategy": None
                }
            
            relevant_tickers = tickers_result["result"]
            
            # Step 4: Create investment strategy
            strategy_result = await cls.create_investment_strategy(
                prediction_text=prediction_text,
                prediction_analysis=prediction_analysis,
                relevant_tickers=relevant_tickers,
                market_research=market_research,
                include_stock_data=include_stock_data,
                include_year_data=include_year_data,
                include_week_data=include_week_data,
                model=model
            )
            
            if not strategy_result["success"]:
                return {
                    "prediction_text": prediction_text,
                    "success": False,
                    "error": strategy_result["error"],
                    "analysis": prediction_analysis,
                    "market_research": market_research,
                    "relevant_tickers": relevant_tickers,
                    "investment_strategy": None
                }
            
            investment_strategy = strategy_result["result"]
            
            # Return the complete response
            return {
                "prediction_text": prediction_text,
                "success": True,
                "analysis": prediction_analysis,
                "market_research": market_research,
                "relevant_tickers": relevant_tickers,
                "investment_strategy": investment_strategy
            }
            
        except Exception as e:
            logger.exception(f"Error in full prediction analysis: {str(e)}")
            return {
                "prediction_text": prediction_text,
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "analysis": None,
                "market_research": None,
                "relevant_tickers": None,
                "investment_strategy": None
            }