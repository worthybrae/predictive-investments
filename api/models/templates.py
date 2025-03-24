# api/templates/templates.py
import json
from api.services.industry_mapper import IndustryMapperService
from api.models.predictions import PredictionAnalysis, InvestmentStrategy, RelevantTickers, FilterSelection, FilterValueSelection

# Get industry data for inclusion in templates
industry_data = IndustryMapperService.get_industries_for_prompt()
industry_list = json.dumps(industry_data["industries"], indent=2)

# Define template structure: each template has:
# - model: The pydantic model to use for structured output
# - system_prompt: The system prompt to use
# - user_prompt_template: The template for the user prompt with {variable} placeholders
# - required_vars: Variables that must be provided when using this template
# - optional_vars: Optional variables with default values

TEMPLATES = {
    "prediction_analysis": {
        "model": PredictionAnalysis,
        "system_prompt": """You are a financial prediction analyst with expertise in extracting key details from prediction statements.
        Analyze the prediction carefully, looking for explicit or implicit information about timing, confidence, risk tolerance, 
        industries, and potential outcomes. When information is not explicitly stated, make reasonable inferences based on the context.
        For confidence and tolerance values, use a scale from 0.0 (lowest) to 1.0 (highest) in 0.1 increments.
        
        When identifying related industries, select from the standardized industry list provided to ensure compatibility with stock screening tools.""",
        "user_prompt_template": """Analyze this prediction and extract key details: {prediction_text}

Available Industry Categories for Related Industries:
{industry_list}""",
        "required_vars": ["prediction_text"],
        "optional_vars": {"industry_list": industry_list}
    },
    
    "ticker_finder": {
        "model": RelevantTickers,
        "system_prompt": """You are a financial research assistant specializing in finding relevant stock tickers based on predictions.
        Your task is to extract and identify the most relevant publicly traded companies (with their ticker symbols) from the provided market research.
        
        Focus on these criteria:
        1. Companies directly mentioned in the market research with their ticker symbols
        2. Companies highly likely to be impacted by the prediction (positively or negatively)
        3. Industry leaders in the affected sectors
        
        Be precise and focus on quality over quantity - include only tickers with clear relevance to the prediction.
        Include at least 5-10 tickers if possible, but prioritize relevance over quantity.
        Provide a clear explanation for why each ticker was included.""",
        
        "user_prompt_template": """Extract relevant stock tickers from the following market research related to this prediction:
        
        Prediction: {prediction_text}
        
        Prediction Analysis: {prediction_analysis}
        
        {web_research}
        
        Available Industry Categories for Stock Screening:
        {industry_list}""",
        
        "required_vars": ["prediction_text", "prediction_analysis"],
        "optional_vars": {"web_research": "", "industry_list": industry_list}
    },
    
    "investment_strategy": {
        "model": InvestmentStrategy,
        "system_prompt": """You are an investment advisor creating actionable trading strategies based on market predictions.
        Design a comprehensive investment strategy that leverages the prediction, market research, and stock data provided.
        
        Your strategy should:
        1. Align with the prediction's timeframe and risk profile
        2. Include specific trades with price targets and allocation percentages
        3. Be based on concrete data from the market research and stock analysis
        4. Present a balanced assessment of potential risks and rewards
        5. Consider current market conditions and recent price movements
        
        Be realistic and precise - focus on actionable trades that directly relate to the prediction.
        For each trade, explain the rationale and how it aligns with the overall strategy.""",
        
        "user_prompt_template": """Create a detailed investment strategy based on this prediction and market information:
        
        Prediction: {prediction_text}
        
        Prediction Analysis: {prediction_analysis}
        
        Relevant Tickers: {relevant_tickers}
        
        {market_research}
        
        {stock_data}""",
        
        "required_vars": ["prediction_text", "prediction_analysis", "relevant_tickers"],
        "optional_vars": {"market_research": "", "stock_data": ""}
    },
    
    "market_research": {
        "model": None,
        "system_prompt": """You are a financial market researcher specializing in gathering relevant information about market predictions.
        Your task is to extract key insights and data points that provide context for a prediction about market movements, industry trends, 
        or company performance. Focus on factual information and avoid speculative content.""",
        
        "user_prompt_template": """Provide market research information about this prediction:
        "{prediction_text}"
        
        Focus on these industries: {industries}
        Timeframe: {timeframe}
        
        Include information about:
        - Public companies that might be affected (include stock tickers)
        - Specific stock tickers directly related to this prediction
        - Industry trends and recent developments
        - Market analysis and predictions
        - The liklihood of the prediction being correct
        
        IMPORTANT: Always include stock tickers when mentioning companies, and explain why each company/ticker is relevant to the prediction.""",
        
        "required_vars": ["prediction_text"],
        "optional_vars": {
            "industries": "relevant industries",
            "timeframe": "relevant timeframe"
        }
    },
    
    "finviz_filter_selection": {
        "model": FilterSelection,
        "system_prompt": """You are a financial screening assistant that helps create stock screeners based on predictions.
        Your task is to analyze a prediction and select the most relevant Finviz filter categories to use.
        Focus on understanding each filter's purpose and selecting ones that would best identify stocks related to the prediction.""",
        
        "user_prompt_template": """Select the most relevant Finviz filter categories for this prediction:
        
        Prediction: {prediction_text}
        
        Prediction Analysis: {prediction_analysis}
        
        Available Filters:
        {filter_info}
        
        Select 3-5 of the most relevant filters that would help find stocks related to this prediction.
        
        Important: Use the "id" field as the filter identifier in your response, not the "name" field.""",
        
        "required_vars": ["prediction_text", "prediction_analysis", "filter_info"],
        "optional_vars": {}
    },
    
    "finviz_filter_values": {
        "model": FilterValueSelection,
        "system_prompt": """You are a financial screening assistant that helps create stock screeners based on predictions.
        Your task is to analyze a prediction and select the most appropriate values for Finviz filters.
        For each filter, select the option that would best help identify stocks related to the prediction.""",
        
        "user_prompt_template": """Select the most appropriate values for these Finviz filters based on this prediction:
        
        Prediction: {prediction_text}
        
        Prediction Analysis: {prediction_analysis}
        
        Filter Options:
        {filter_options}
        
        For each filter, select the SINGLE most appropriate option value that aligns with the prediction.
        
        Important: Use the full "id" field from the options as the value in your "filters" object.""",
        
        "required_vars": ["prediction_text", "prediction_analysis", "filter_options"],
        "optional_vars": {}
    }
}