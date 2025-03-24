# api/services/industry_mapper.py
import json
import os
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class IndustryMapperService:
    """Service for mapping industries to Finviz industry filters."""
    
    _industry_map = None
    
    @classmethod
    def _load_industry_map(cls) -> Dict[str, Dict[str, str]]:
        """
        Load the industry mapping from the JSON file.
        
        Returns:
            Dictionary mapping industry names to Finviz filter values
        """
        if cls._industry_map is not None:
            return cls._industry_map
        
        try:
            # Try to load from finviz.json first
            if os.path.exists("finviz.json"):
                with open("finviz.json", "r") as f:
                    filters = json.load(f)
                    
                for filter_def in filters:
                    if filter_def.get("metric_name") == "ind":
                        cls._industry_map = {
                            "name": filter_def.get("metric_name"),
                            "title": filter_def.get("metric_title"),
                            "description": filter_def.get("metric_description"),
                            "values": filter_def.get("values", {})
                        }
                        return cls._industry_map
            
            # If not found in finviz.json, try the hardcoded mapping from paste.txt
            hardcoded_map = {
                "name": "ind",
                "title": "Industry",
                "description": "The industry which a stock belongs to.",
                "values": {
                    "ind_stocksonly": "Stocks only (ex-Funds)",
                    "ind_exchangetradedfund": "Exchange Traded Fund",
                    "ind_advertisingagencies": "Advertising Agencies",
                    "ind_aerospacedefense": "Aerospace & Defense",
                    "ind_agriculturalinputs": "Agricultural Inputs",
                    "ind_airlines": "Airlines",
                    "ind_airportsairservices": "Airports & Air Services",
                    "ind_aluminum": "Aluminum",
                    "ind_apparelmanufacturing": "Apparel Manufacturing",
                    "ind_apparelretail": "Apparel Retail",
                    "ind_assetmanagement": "Asset Management",
                    "ind_automanufacturers": "Auto Manufacturers",
                    "ind_autoparts": "Auto Parts",
                    "ind_autotruckdealerships": "Auto & Truck Dealerships",
                    "ind_banksdiversified": "Banks - Diversified",
                    "ind_banksregional": "Banks - Regional",
                    "ind_beveragesbrewers": "Beverages - Brewers",
                    "ind_beveragesnonalcoholic": "Beverages - Non-Alcoholic",
                    "ind_beverageswineriesdistilleries": "Beverages - Wineries & Distilleries",
                    "ind_biotechnology": "Biotechnology",
                    "ind_broadcasting": "Broadcasting",
                    "ind_buildingmaterials": "Building Materials",
                    "ind_buildingproductsequipment": "Building Products & Equipment",
                    "ind_businessequipmentsupplies": "Business Equipment & Supplies",
                    "ind_capitalmarkets": "Capital Markets",
                    "ind_chemicals": "Chemicals",
                    "ind_closedendfunddebt": "Closed-End Fund - Debt",
                    "ind_closedendfundequity": "Closed-End Fund - Equity",
                    "ind_closedendfundforeign": "Closed-End Fund - Foreign",
                    "ind_cokingcoal": "Coking Coal",
                    "ind_communicationequipment": "Communication Equipment",
                    "ind_computerhardware": "Computer Hardware",
                    "ind_confectioners": "Confectioners",
                    "ind_conglomerates": "Conglomerates",
                    "ind_consultingservices": "Consulting Services",
                    "ind_consumerelectronics": "Consumer Electronics",
                    "ind_copper": "Copper",
                    "ind_creditservices": "Credit Services",
                    "ind_departmentstores": "Department Stores",
                    "ind_diagnosticsresearch": "Diagnostics & Research",
                    "ind_discountstores": "Discount Stores",
                    "ind_drugmanufacturersgeneral": "Drug Manufacturers - General",
                    "ind_drugmanufacturersspecialtygeneric": "Drug Manufacturers - Specialty & Generic",
                    "ind_educationtrainingservices": "Education & Training Services",
                    "ind_electricalequipmentparts": "Electrical Equipment & Parts",
                    "ind_electroniccomponents": "Electronic Components",
                    "ind_electronicgamingmultimedia": "Electronic Gaming & Multimedia",
                    "ind_electronicscomputerdistribution": "Electronics & Computer Distribution",
                    "ind_engineeringconstruction": "Engineering & Construction",
                    "ind_entertainment": "Entertainment",
                    "ind_farmheavyconstructionmachinery": "Farm & Heavy Construction Machinery",
                    "ind_farmproducts": "Farm Products",
                    "ind_financialconglomerates": "Financial Conglomerates",
                    "ind_financialdatastockexchanges": "Financial Data & Stock Exchanges",
                    "ind_fooddistribution": "Food Distribution",
                    "ind_footwearaccessories": "Footwear & Accessories",
                    "ind_furnishingsfixturesappliances": "Furnishings, Fixtures & Appliances",
                    "ind_gambling": "Gambling",
                    "ind_gold": "Gold",
                    "ind_grocerystores": "Grocery Stores",
                    "ind_healthcareplans": "Healthcare Plans",
                    "ind_healthinformationservices": "Health Information Services",
                    "ind_homeimprovementretail": "Home Improvement Retail",
                    "ind_householdpersonalproducts": "Household & Personal Products",
                    "ind_industrialdistribution": "Industrial Distribution",
                    "ind_informationtechnologyservices": "Information Technology Services",
                    "ind_infrastructureoperations": "Infrastructure Operations",
                    "ind_insurancebrokers": "Insurance Brokers",
                    "ind_insurancediversified": "Insurance - Diversified",
                    "ind_insurancelife": "Insurance - Life",
                    "ind_insurancepropertycasualty": "Insurance - Property & Casualty",
                    "ind_insurancereinsurance": "Insurance - Reinsurance",
                    "ind_insurancespecialty": "Insurance - Specialty",
                    "ind_integratedfreightlogistics": "Integrated Freight & Logistics",
                    "ind_internetcontentinformation": "Internet Content & Information",
                    "ind_internetretail": "Internet Retail",
                    "ind_leisure": "Leisure",
                    "ind_lodging": "Lodging",
                    "ind_lumberwoodproduction": "Lumber & Wood Production",
                    "ind_luxurygoods": "Luxury Goods",
                    "ind_marineshipping": "Marine Shipping",
                    "ind_medicalcarefacilities": "Medical Care Facilities",
                    "ind_medicaldevices": "Medical Devices",
                    "ind_medicaldistribution": "Medical Distribution",
                    "ind_medicalinstrumentssupplies": "Medical Instruments & Supplies",
                    "ind_metalfabrication": "Metal Fabrication",
                    "ind_mortgagefinance": "Mortgage Finance",
                    "ind_oilgasdrilling": "Oil & Gas Drilling",
                    "ind_oilgasep": "Oil & Gas E&P",
                    "ind_oilgasequipmentservices": "Oil & Gas Equipment & Services",
                    "ind_oilgasintegrated": "Oil & Gas Integrated",
                    "ind_oilgasmidstream": "Oil & Gas Midstream",
                    "ind_oilgasrefiningmarketing": "Oil & Gas Refining & Marketing",
                    "ind_otherindustrialmetalsmining": "Other Industrial Metals & Mining",
                    "ind_otherpreciousmetalsmining": "Other Precious Metals & Mining",
                    "ind_packagedfoods": "Packaged Foods",
                    "ind_packagingcontainers": "Packaging & Containers",
                    "ind_paperpaperproducts": "Paper & Paper Products",
                    "ind_personalservices": "Personal Services",
                    "ind_pharmaceuticalretailers": "Pharmaceutical Retailers",
                    "ind_pollutiontreatmentcontrols": "Pollution & Treatment Controls",
                    "ind_publishing": "Publishing",
                    "ind_railroads": "Railroads",
                    "ind_realestatedevelopment": "Real Estate - Development",
                    "ind_realestatediversified": "Real Estate - Diversified",
                    "ind_realestateservices": "Real Estate Services",
                    "ind_recreationalvehicles": "Recreational Vehicles",
                    "ind_reitdiversified": "REIT - Diversified",
                    "ind_reithealthcarefacilities": "REIT - Healthcare Facilities",
                    "ind_reithotelmotel": "REIT - Hotel & Motel",
                    "ind_reitindustrial": "REIT - Industrial",
                    "ind_reitmortgage": "REIT - Mortgage",
                    "ind_reitoffice": "REIT - Office",
                    "ind_reitresidential": "REIT - Residential",
                    "ind_reitretail": "REIT - Retail",
                    "ind_reitspecialty": "REIT - Specialty",
                    "ind_rentalleasingservices": "Rental & Leasing Services",
                    "ind_residentialconstruction": "Residential Construction",
                    "ind_resortscasinos": "Resorts & Casinos",
                    "ind_restaurants": "Restaurants",
                    "ind_scientifictechnicalinstruments": "Scientific & Technical Instruments",
                    "ind_securityprotectionservices": "Security & Protection Services",
                    "ind_semiconductorequipmentmaterials": "Semiconductor Equipment & Materials",
                    "ind_semiconductors": "Semiconductors",
                    "ind_shellcompanies": "Shell Companies",
                    "ind_silver": "Silver",
                    "ind_softwareapplication": "Software - Application",
                    "ind_softwareinfrastructure": "Software - Infrastructure",
                    "ind_solar": "Solar",
                    "ind_specialtybusinessservices": "Specialty Business Services",
                    "ind_specialtychemicals": "Specialty Chemicals",
                    "ind_specialtyindustrialmachinery": "Specialty Industrial Machinery",
                    "ind_specialtyretail": "Specialty Retail",
                    "ind_staffingemploymentservices": "Staffing & Employment Services",
                    "ind_steel": "Steel",
                    "ind_telecomservices": "Telecom Services",
                    "ind_textilemanufacturing": "Textile Manufacturing",
                    "ind_thermalcoal": "Thermal Coal",
                    "ind_tobacco": "Tobacco",
                    "ind_toolsaccessories": "Tools & Accessories",
                    "ind_travelservices": "Travel Services",
                    "ind_trucking": "Trucking",
                    "ind_uranium": "Uranium",
                    "ind_utilitiesdiversified": "Utilities - Diversified",
                    "ind_utilitiesindependentpowerproducers": "Utilities - Independent Power Producers",
                    "ind_utilitiesregulatedelectric": "Utilities - Regulated Electric",
                    "ind_utilitiesregulatedgas": "Utilities - Regulated Gas",
                    "ind_utilitiesregulatedwater": "Utilities - Regulated Water",
                    "ind_utilitiesrenewable": "Utilities - Renewable",
                    "ind_wastemanagement": "Waste Management"
                }
            }
            
            cls._industry_map = hardcoded_map
            return cls._industry_map
            
        except Exception as e:
            logger.error(f"Error loading industry map: {str(e)}")
            # Return empty mapping if there's an error
            cls._industry_map = {"name": "ind", "title": "Industry", "description": "", "values": {}}
            return cls._industry_map
    
    @classmethod
    def get_all_industries(cls) -> Dict[str, str]:
        """
        Get a dictionary of all industries and their display names.
        
        Returns:
            Dictionary mapping filter values to industry names
        """
        industry_map = cls._load_industry_map()
        return industry_map.get("values", {})
    
    @classmethod
    def get_industry_filters(cls, industries: List[str]) -> Dict[str, str]:
        """
        Map a list of industry names to their Finviz filter values.
        
        Args:
            industries: List of industry names or keywords
            
        Returns:
            Dictionary of Finviz filters to apply
        """
        industry_map = cls._load_industry_map()
        industry_values = industry_map.get("values", {})
        
        # Create a reverse mapping (display name -> filter value)
        reverse_map = {v.lower(): k for k, v in industry_values.items()}
        
        filters = {}
        
        # Try exact matches first
        for industry in industries:
            industry_lower = industry.lower()
            
            # Check for exact match
            if industry_lower in reverse_map:
                filters["industry"] = reverse_map[industry_lower]
                return filters
            
            # Check for partial match in keys
            for display_name, filter_value in reverse_map.items():
                if industry_lower in display_name:
                    filters["industry"] = filter_value
                    return filters
        
        # If no direct matches, look for keyword matches
        keywords = []
        for industry in industries:
            # Split industry into keywords
            words = industry.lower().replace("-", " ").replace("&", " ").replace(",", " ").split()
            keywords.extend(words)
        
        # Look for matches for each keyword
        for keyword in keywords:
            if len(keyword) < 4:  # Skip very short keywords
                continue
                
            for display_name, filter_value in reverse_map.items():
                if keyword in display_name:
                    filters["industry"] = filter_value
                    return filters
        
        # No matches found
        return filters
    
    @classmethod
    def get_industries_for_prompt(cls) -> Dict[str, Any]:
        """
        Get the industry information formatted for inclusion in a prompt.
        
        Returns:
            Dictionary with industry information for the prompt
        """
        industry_map = cls._load_industry_map()
        
        # Format for easy inclusion in a prompt
        return {
            "industry_filter_name": industry_map.get("name", "ind"),
            "industry_filter_description": industry_map.get("description", ""),
            "industries": industry_map.get("values", {})
        }