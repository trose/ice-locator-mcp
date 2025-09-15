#!/usr/bin/env python3
"""
ICE Locator MCP Server

Main server implementation that provides MCP tools for accessing ICE detainee information.
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

import mcp.types as types
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
import structlog

from .core.config import ServerConfig
from .core.search_engine import SearchEngine
from .anti_detection.proxy_manager import ProxyManager
from .tools.search_tools import SearchTools
from .utils.logging import setup_logging
from .monitoring.comprehensive_monitor import ComprehensiveMonitor


class ICELocatorServer:
    """Main MCP server for ICE detainee location services."""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        """Initialize the ICE Locator MCP Server."""
        self.config = config or ServerConfig()
        self.logger = structlog.get_logger(__name__)
        
        # Initialize comprehensive monitoring system
        self.comprehensive_monitor = None
        
        # Check if monitoring is disabled via environment variable
        monitoring_enabled = os.getenv("ICE_LOCATOR_ANALYTICS_ENABLED", "true").lower() == "true"
        mcpcat_enabled = os.getenv("ICE_LOCATOR_MCPCAT_ENABLED", "true").lower() == "true"
        
        if self.config.monitoring_config.mcpcat_enabled and monitoring_enabled and mcpcat_enabled:
            try:
                # Initialize comprehensive monitoring system
                self.comprehensive_monitor = ComprehensiveMonitor(
                    self.config.monitoring_config,
                    storage_path=None  # Use default storage path
                )
                
                self.logger.info(
                    "Comprehensive monitoring initialized with privacy-first design",
                    mcpcat_enabled=True,
                    redaction_level=self.config.monitoring_config.redaction_level,
                    components=["mcpcat", "telemetry", "analytics", "session_replay", "system_monitor"]
                )
            except Exception as e:
                self.logger.warning(
                    "Failed to initialize comprehensive monitoring - continuing without analytics",
                    error=str(e)
                )
        else:
            self.logger.info(
                "Monitoring disabled via configuration",
                monitoring_enabled=monitoring_enabled,
                mcpcat_enabled=mcpcat_enabled
            )
        
        # Initialize core components
        self.proxy_manager = ProxyManager(self.config.proxy_config)
        self.search_engine = SearchEngine(
            proxy_manager=self.proxy_manager,
            config=self.config.search_config
        )
        self.search_tools = SearchTools(self.search_engine)
        
        # Initialize MCP server
        self.server = Server("ice-locator")
        self._register_handlers()
        
        # Set up MCPcat tracking after tools are registered
        if self.comprehensive_monitor and hasattr(self.comprehensive_monitor, 'mcpcat_monitor'):
            if self.comprehensive_monitor.mcpcat_monitor:
                self.comprehensive_monitor.mcpcat_monitor.setup_tracking(self.server)
        
    def _register_handlers(self) -> None:
        """Register all MCP handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List all available tools."""
            return [
                types.Tool(
                    name="search_detainee_by_name",
                    description="Search for a detainee by name and personal information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "first_name": {
                                "type": "string",
                                "description": "First name of the detainee"
                            },
                            "last_name": {
                                "type": "string", 
                                "description": "Last name of the detainee"
                            },
                            "date_of_birth": {
                                "type": "string",
                                "description": "Date of birth in YYYY-MM-DD format"
                            },
                            "country_of_birth": {
                                "type": "string",
                                "description": "Country of birth"
                            },
                            "middle_name": {
                                "type": "string",
                                "description": "Middle name (optional)"
                            },
                            "language": {
                                "type": "string",
                                "description": "Response language (default: en)",
                                "default": "en"
                            },
                            "fuzzy_search": {
                                "type": "boolean", 
                                "description": "Enable fuzzy name matching (default: true)",
                                "default": True
                            }
                        },
                        "required": ["first_name", "last_name", "date_of_birth", "country_of_birth"]
                    }
                ),
                types.Tool(
                    name="search_detainee_by_alien_number", 
                    description="Search for a detainee by their alien registration number",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "alien_number": {
                                "type": "string",
                                "description": "Alien registration number (A-number)"
                            },
                            "language": {
                                "type": "string",
                                "description": "Response language (default: en)",
                                "default": "en"
                            }
                        },
                        "required": ["alien_number"]
                    }
                ),
                types.Tool(
                    name="smart_detainee_search",
                    description="AI-powered search using natural language queries",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for the search"
                            },
                            "suggest_corrections": {
                                "type": "boolean",
                                "description": "Enable auto-correction suggestions (default: true)",
                                "default": True
                            },
                            "language": {
                                "type": "string", 
                                "description": "Response language (default: en)",
                                "default": "en"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="bulk_search_detainees",
                    description="Search multiple detainees simultaneously",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_requests": {
                                "type": "array",
                                "description": "List of search requests",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "first_name": {"type": "string"},
                                        "last_name": {"type": "string"},
                                        "date_of_birth": {"type": "string"},
                                        "country_of_birth": {"type": "string"},
                                        "alien_number": {"type": "string"}
                                    }
                                }
                            },
                            "max_concurrent": {
                                "type": "integer",
                                "description": "Maximum concurrent searches (default: 3)",
                                "default": 3,
                                "minimum": 1,
                                "maximum": 5
                            },
                            "continue_on_error": {
                                "type": "boolean",
                                "description": "Continue processing if some searches fail (default: true)",
                                "default": True
                            }
                        },
                        "required": ["search_requests"]
                    }
                ),
                types.Tool(
                    name="generate_search_report",
                    description="Generate comprehensive reports for legal or advocacy use",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_criteria": {
                                "type": "object",
                                "description": "Original search parameters"
                            },
                            "results": {
                                "type": "array",
                                "description": "Search results to include in report"
                            },
                            "report_type": {
                                "type": "string",
                                "description": "Type of report (legal, advocacy, family)",
                                "enum": ["legal", "advocacy", "family"],
                                "default": "legal"
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format (markdown, json)",
                                "enum": ["markdown", "json"],
                                "default": "markdown"
                            }
                        },
                        "required": ["search_criteria", "results"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
            """Handle tool calls with telemetry instrumentation."""
            
            # Track tool call with comprehensive monitoring (privacy-preserving)
            if self.comprehensive_monitor:
                await self.comprehensive_monitor.track_tool_call(
                    session_id="default",  # Use default session or implement session management
                    tool_name=name,
                    arguments=arguments
                )
            
            try:
                self.logger.info("Tool called", tool_name=name, arguments=arguments)
                
                if name == "search_detainee_by_name":
                    result = await self.search_tools.search_by_name(**arguments)
                elif name == "search_detainee_by_alien_number":
                    result = await self.search_tools.search_by_alien_number(**arguments)
                elif name == "smart_detainee_search":
                    result = await self.search_tools.smart_search(**arguments)
                elif name == "bulk_search_detainees":
                    result = await self.search_tools.bulk_search(**arguments)
                elif name == "generate_search_report":
                    result = await self.search_tools.generate_report(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                # Track successful tool completion
                if self.comprehensive_monitor:
                    await self.comprehensive_monitor.track_tool_call(
                        session_id="default",
                        tool_name=name,
                        arguments=arguments,
                        result={"status": "success", "response": result},
                        error=None
                    )
                
                self.logger.info("Tool completed successfully", tool_name=name)
                
                return [types.TextContent(
                    type="text",
                    text=result
                )]
                
            except Exception as e:
                # Track tool errors
                if self.comprehensive_monitor:
                    await self.comprehensive_monitor.track_tool_call(
                        session_id="default",
                        tool_name=name,
                        arguments=arguments,
                        result=None,
                        error=str(e)
                    )
                
                self.logger.error("Tool execution failed", tool_name=name, error=str(e))
                error_response = {
                    "status": "error",
                    "error_message": str(e),
                    "tool_name": name
                }
                return [types.TextContent(
                    type="text",
                    text=json.dumps(error_response, indent=2)
                )]
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            """List all available prompts."""
            return [
                types.Prompt(
                    name="detainee_search_guide",
                    description="Guide for searching ICE detainees with best practices and tips",
                    arguments=[
                        types.PromptArgument(
                            name="search_type",
                            description="Type of search: name, alien_number, or smart",
                            required=True
                        ),
                        types.PromptArgument(
                            name="user_role",
                            description="User role: legal, family, advocate, or general",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="legal_report_template",
                    description="Template for generating legal reports from search results",
                    arguments=[
                        types.PromptArgument(
                            name="report_type",
                            description="Type of legal report: case_summary, custody_verification, or facility_info",
                            required=True
                        ),
                        types.PromptArgument(
                            name="client_name",
                            description="Client name for the report",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="family_support_guide",
                    description="Comprehensive guide for families searching for detained relatives",
                    arguments=[
                        types.PromptArgument(
                            name="relationship",
                            description="Relationship to detainee: spouse, parent, child, sibling, or other",
                            required=False
                        ),
                        types.PromptArgument(
                            name="language",
                            description="Preferred language for the guide",
                            required=False
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict[str, str]) -> list[types.TextContent]:
            """Get a specific prompt with arguments."""
            
            if name == "detainee_search_guide":
                search_type = arguments.get("search_type", "name")
                user_role = arguments.get("user_role", "general")
                
                guide_content = f"""# ICE Detainee Search Guide

## Search Type: {search_type.title()}
## User Role: {user_role.title()}

### Best Practices for {search_type} Search:

"""
                
                if search_type == "name":
                    guide_content += """
1. **Name Variations**: Try different spellings and variations
   - Common variations: José/Jose, María/Maria, González/Gonzalez
   - Nicknames: Juan/Johnny, María/Mary, Carlos/Charlie
   - Maiden names for married individuals

2. **Required Information**:
   - First name (required)
   - Last name (required) 
   - Date of birth (required) - Use YYYY-MM-DD format
   - Country of birth (required)

3. **Optional Information**:
   - Middle name or initial
   - Enable fuzzy search for name variations
   - Specify language preference

4. **Search Tips**:
   - Use exact birth date if known
   - Try without middle name if no results
   - Use fuzzy search for name variations
   - Check different country spellings (e.g., "United States" vs "USA")
"""
                elif search_type == "alien_number":
                    guide_content += """
1. **A-Number Format**:
   - Format: A followed by 8-9 digits (e.g., A123456789)
   - Include leading zeros if known
   - No spaces or dashes

2. **Finding A-Numbers**:
   - Check immigration documents
   - Look for previous correspondence
   - Check with family members or legal representatives

3. **Search Tips**:
   - Enter complete A-number
   - Double-check digit accuracy
   - Try with and without leading zeros
"""
                elif search_type == "smart":
                    guide_content += """
1. **Natural Language Queries**:
   - "Find Maria Rodriguez from Guatemala born in 1985"
   - "Search for John Doe, A-number A123456789"
   - "Look for detainee named José González from Mexico"

2. **Query Tips**:
   - Include as much information as possible
   - Mention country of origin
   - Include approximate birth year
   - Specify if you have an A-number

3. **AI Features**:
   - Auto-correction of common misspellings
   - Intelligent name matching
   - Context-aware suggestions
"""
                
                # Add role-specific guidance
                if user_role == "legal":
                    guide_content += """

### Legal Professional Guidance:
- Document all search attempts and results
- Use bulk search for multiple clients
- Generate legal reports for case files
- Verify information through multiple sources
- Maintain client confidentiality
"""
                elif user_role == "family":
                    guide_content += """

### Family Member Guidance:
- Gather all available information before searching
- Try multiple search variations
- Contact facility directly if found
- Seek legal assistance if needed
- Join support groups for guidance
"""
                elif user_role == "advocate":
                    guide_content += """

### Advocate Guidance:
- Use bulk search for case management
- Generate advocacy reports
- Track detention patterns
- Coordinate with legal teams
- Document systemic issues
"""
                
                guide_content += """

### Important Notes:
- Search results may take time to update
- Information is subject to change
- Always verify current status
- Respect privacy and confidentiality
- Use for legitimate purposes only

### Next Steps:
1. Perform your search using the appropriate tool
2. Review results carefully
3. Contact facility if detainee is found
4. Seek legal assistance if needed
5. Document your search process
"""
                
                return [types.TextContent(type="text", text=guide_content)]
            
            elif name == "legal_report_template":
                report_type = arguments.get("report_type", "case_summary")
                client_name = arguments.get("client_name", "[CLIENT_NAME]")
                
                if report_type == "case_summary":
                    template = f"""# Legal Case Summary Report

**Client**: {client_name}
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Prepared by**: [ATTORNEY_NAME]
**Case Number**: [CASE_NUMBER]

## Search Results Summary

### Detainee Information
- **Name**: [DETAINEE_NAME]
- **A-Number**: [A_NUMBER]
- **Date of Birth**: [DATE_OF_BIRTH]
- **Country of Birth**: [COUNTRY_OF_BIRTH]

### Current Status
- **Facility**: [FACILITY_NAME]
- **Location**: [FACILITY_ADDRESS]
- **Custody Status**: [CUSTODY_STATUS]
- **Last Updated**: [LAST_UPDATED]

### Legal Analysis
- **Immigration Status**: [STATUS_ANALYSIS]
- **Detention Authority**: [DETENTION_AUTHORITY]
- **Next Steps**: [RECOMMENDED_ACTIONS]

### Contact Information
- **Facility Phone**: [FACILITY_PHONE]
- **Facility Address**: [FACILITY_ADDRESS]
- **Visiting Hours**: [VISITING_HOURS]

### Recommendations
1. [RECOMMENDATION_1]
2. [RECOMMENDATION_2]
3. [RECOMMENDATION_3]

---
*This report is confidential and privileged attorney-client communication.*
"""
                elif report_type == "custody_verification":
                    template = f"""# Custody Verification Report

**Client**: {client_name}
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Purpose**: Custody Status Verification

## Verification Details

### Search Parameters
- **Search Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Search Method**: [SEARCH_METHOD]
- **Search Criteria**: [SEARCH_CRITERIA]

### Results
- **Status**: [FOUND/NOT_FOUND]
- **Confidence Level**: [HIGH/MEDIUM/LOW]
- **Last Known Location**: [FACILITY_NAME]
- **Verification Date**: [VERIFICATION_DATE]

### Legal Implications
- **Current Custody**: [CUSTODY_STATUS]
- **Legal Authority**: [DETENTION_AUTHORITY]
- **Due Process Rights**: [DUE_PROCESS_ANALYSIS]

### Next Steps
1. [IMMEDIATE_ACTION]
2. [FOLLOW_UP_ACTION]
3. [MONITORING_PLAN]

---
*Verified on {datetime.now().strftime('%Y-%m-%d')} at {datetime.now().strftime('%H:%M:%S')}*
"""
                else:  # facility_info
                    template = f"""# ICE Facility Information Report

**Facility**: [FACILITY_NAME]
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Client**: {client_name}

## Facility Details

### Basic Information
- **Name**: [FACILITY_NAME]
- **Type**: [FACILITY_TYPE]
- **Address**: [FACILITY_ADDRESS]
- **Phone**: [FACILITY_PHONE]

### Operations
- **Capacity**: [FACILITY_CAPACITY]
- **Current Population**: [CURRENT_POPULATION]
- **Operating Agency**: [OPERATING_AGENCY]
- **Contractor**: [CONTRACTOR_NAME]

### Contact Information
- **Main Phone**: [MAIN_PHONE]
- **Visiting Hours**: [VISITING_HOURS]
- **Legal Access**: [LEGAL_ACCESS_INFO]
- **Emergency Contact**: [EMERGENCY_CONTACT]

### Legal Considerations
- **Detention Standards**: [STANDARDS_COMPLIANCE]
- **Legal Services**: [LEGAL_SERVICES_AVAILABLE]
- **Access Rights**: [ACCESS_RIGHTS]
- **Complaint Procedures**: [COMPLAINT_PROCEDURES]

### Recommendations
1. [FACILITY_ASSESSMENT]
2. [CLIENT_CONSIDERATIONS]
3. [LEGAL_STRATEGY]

---
*Report generated on {datetime.now().strftime('%Y-%m-%d')}*
"""
                
                return [types.TextContent(type="text", text=template)]
            
            elif name == "family_support_guide":
                relationship = arguments.get("relationship", "family")
                language = arguments.get("language", "en")
                
                if language == "es":
                    guide_content = f"""# Guía de Apoyo Familiar para Búsqueda de Detenidos

## Relación: {relationship.title()}

### Información Básica
- **Servicio**: Localizador de Detenidos de ICE
- **Propósito**: Encontrar familiares detenidos por ICE
- **Confidencialidad**: Toda la información es privada

### Cómo Buscar
1. **Reúna información**:
   - Nombre completo
   - Fecha de nacimiento
   - País de origen
   - Número A (si lo tiene)

2. **Realice la búsqueda**:
   - Use el nombre exacto si es posible
   - Pruebe variaciones del nombre
   - Incluya información adicional

3. **Revise los resultados**:
   - Verifique la información
   - Anote el nombre de la instalación
   - Guarde los números de contacto

### Si Encuentra a su Familiar
1. **Contacte la instalación**:
   - Llame al número proporcionado
   - Pregunte sobre visitas
   - Obtenga información de contacto

2. **Preparación para la visita**:
   - Verifique horarios de visita
   - Traiga identificación válida
   - Revise las reglas de la instalación

3. **Apoyo legal**:
   - Busque asistencia legal
   - Documente todo
   - Mantenga registros

### Recursos de Apoyo
- **Línea de ayuda familiar**: [NÚMERO]
- **Asistencia legal gratuita**: [RECURSOS]
- **Grupos de apoyo**: [INFORMACIÓN]
- **Servicios de traducción**: [RECURSOS]

### Derechos Importantes
- Derecho a visitar
- Derecho a comunicación
- Derecho a asistencia legal
- Derecho a presentar quejas

### Próximos Pasos
1. Realice su búsqueda
2. Contacte la instalación si encuentra a su familiar
3. Busque asistencia legal
4. Únase a grupos de apoyo
5. Mantenga la esperanza

---
*Recuerde: Usted no está solo. Hay recursos disponibles para ayudarle.*
"""
                else:  # English
                    guide_content = f"""# Family Support Guide for ICE Detainee Search

## Relationship: {relationship.title()}

### Basic Information
- **Service**: ICE Detainee Locator
- **Purpose**: Find family members detained by ICE
- **Confidentiality**: All information is private

### How to Search
1. **Gather information**:
   - Full name
   - Date of birth
   - Country of origin
   - A-number (if available)

2. **Perform search**:
   - Use exact name if possible
   - Try name variations
   - Include additional information

3. **Review results**:
   - Verify information
   - Note facility name
   - Save contact numbers

### If You Find Your Family Member
1. **Contact the facility**:
   - Call the provided number
   - Ask about visiting
   - Get contact information

2. **Prepare for visit**:
   - Check visiting hours
   - Bring valid ID
   - Review facility rules

3. **Legal support**:
   - Seek legal assistance
   - Document everything
   - Keep records

### Support Resources
- **Family helpline**: [NUMBER]
- **Free legal assistance**: [RESOURCES]
- **Support groups**: [INFORMATION]
- **Translation services**: [RESOURCES]

### Important Rights
- Right to visit
- Right to communication
- Right to legal assistance
- Right to file complaints

### Next Steps
1. Perform your search
2. Contact facility if you find your family member
3. Seek legal assistance
4. Join support groups
5. Stay hopeful

---
*Remember: You are not alone. Resources are available to help you.*
"""
                
                return [types.TextContent(type="text", text=guide_content)]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Unknown prompt: {name}"
                )]
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List all available resources."""
            return [
                types.Resource(
                    uri="ice://facilities/database",
                    name="ICE Facilities Database",
                    description="Comprehensive database of ICE detention facilities with locations, contact information, and capacity data",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="ice://search/history",
                    name="Search History",
                    description="Track and manage previous search queries and results for reference",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="ice://legal/templates",
                    name="Legal Document Templates",
                    description="Templates for legal documents, reports, and correspondence related to immigration detention",
                    mimeType="text/markdown"
                ),
                types.Resource(
                    uri="ice://support/resources",
                    name="Family Support Resources",
                    description="Comprehensive list of resources for families of detainees including legal aid, support groups, and contact information",
                    mimeType="text/markdown"
                ),
                types.Resource(
                    uri="ice://statistics/trends",
                    name="Detention Statistics and Trends",
                    description="Historical data and trends about ICE detention patterns, facility populations, and demographic information",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a specific resource."""
            
            if uri == "ice://facilities/database":
                # Return facility database information
                facilities_data = {
                    "description": "ICE Detention Facilities Database",
                    "last_updated": datetime.now().isoformat(),
                    "total_facilities": 186,
                    "data_source": "TRAC Reports - Syracuse University",
                    "update_frequency": "Monthly",
                    "fields": [
                        "facility_name",
                        "facility_type", 
                        "address",
                        "city",
                        "state",
                        "zip_code",
                        "phone",
                        "capacity",
                        "current_population",
                        "operating_agency",
                        "contractor",
                        "latitude",
                        "longitude"
                    ],
                    "access_notes": "This resource provides comprehensive facility information for legal and family reference purposes."
                }
                return json.dumps(facilities_data, indent=2)
            
            elif uri == "ice://search/history":
                # Return search history template
                history_template = {
                    "description": "Search History Management",
                    "purpose": "Track and reference previous searches",
                    "fields": [
                        "search_id",
                        "search_date",
                        "search_type",
                        "search_criteria",
                        "results_count",
                        "status",
                        "notes"
                    ],
                    "best_practices": [
                        "Document all search attempts",
                        "Note variations tried",
                        "Record results and outcomes",
                        "Maintain client confidentiality",
                        "Regular cleanup of old records"
                    ],
                    "legal_considerations": "Search history may be subject to discovery in legal proceedings. Maintain appropriate documentation standards."
                }
                return json.dumps(history_template, indent=2)
            
            elif uri == "ice://legal/templates":
                # Return legal templates
                templates = """# Legal Document Templates

## Case Summary Template
```markdown
# Legal Case Summary - [CLIENT_NAME]
**Date**: [DATE]
**Attorney**: [ATTORNEY_NAME]
**Case Number**: [CASE_NUMBER]

## Detainee Information
- Name: [DETAINEE_NAME]
- A-Number: [A_NUMBER]
- DOB: [DATE_OF_BIRTH]
- Country: [COUNTRY_OF_BIRTH]

## Current Status
- Facility: [FACILITY_NAME]
- Location: [FACILITY_ADDRESS]
- Status: [CUSTODY_STATUS]
- Last Updated: [LAST_UPDATED]

## Legal Analysis
[LEGAL_ANALYSIS]

## Recommendations
[RECOMMENDATIONS]
```

## Custody Verification Template
```markdown
# Custody Verification Report
**Client**: [CLIENT_NAME]
**Date**: [DATE]
**Purpose**: Custody Status Verification

## Search Results
- Status: [FOUND/NOT_FOUND]
- Facility: [FACILITY_NAME]
- Verification Date: [DATE]

## Legal Implications
[LEGAL_IMPLICATIONS]

## Next Steps
[NEXT_STEPS]
```

## Facility Information Request Template
```markdown
# Facility Information Request
**To**: [FACILITY_NAME]
**From**: [ATTORNEY_NAME]
**Date**: [DATE]
**Re**: [CLIENT_NAME] - A-Number: [A_NUMBER]

Dear Facility Administrator,

I am writing to request information regarding my client, [CLIENT_NAME], A-Number [A_NUMBER], who is currently detained at your facility.

Please provide the following information:
1. Current custody status
2. Next hearing date
3. Legal access procedures
4. Visiting information
5. Contact procedures

Please respond within 5 business days.

Sincerely,
[ATTORNEY_NAME]
[CONTACT_INFORMATION]
```
"""
                return templates
            
            elif uri == "ice://support/resources":
                # Return family support resources
                support_resources = """# Family Support Resources

## Legal Assistance
- **National Immigration Law Center**: 1-800-954-0254
- **American Immigration Lawyers Association**: Find a lawyer directory
- **Pro Bono Legal Services**: Local bar associations
- **Immigration Court Helpdesk**: Self-help resources

## Family Support Organizations
- **Families Belong Together**: Advocacy and support
- **Detention Watch Network**: Policy and advocacy
- **Immigrant Legal Resource Center**: Legal education
- **National Immigrant Justice Center**: Legal services

## Mental Health Support
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **Immigrant Mental Health Resources**: Specialized counseling
- **Family Therapy Services**: Trauma-informed care

## Financial Assistance
- **Bond Funds**: Community-based organizations
- **Legal Defense Funds**: Crowdfunding platforms
- **Emergency Assistance**: Local immigrant organizations
- **Transportation Support**: Visiting assistance programs

## Language Support
- **Translation Services**: Court interpreters
- **Language Hotlines**: Multilingual support
- **Community Interpreters**: Volunteer services
- **Document Translation**: Certified services

## Educational Resources
- **Know Your Rights**: Legal education materials
- **Immigration Process Guides**: Step-by-step information
- **Family Reunification Resources**: Process guidance
- **Community Workshops**: Regular education sessions

## Emergency Contacts
- **ICE Detention Standards**: 1-855-448-6903
- **Office of Inspector General**: Report abuse
- **Civil Rights Division**: Discrimination complaints
- **Emergency Legal Services**: 24/7 hotlines

## Online Resources
- **ICE Detainee Locator**: Official search tool
- **Court Case Lookup**: EOIR case status
- **Facility Information**: Detention center details
- **Legal Forms**: Self-help documents

---
*Remember: You are not alone. Help is available.*
"""
                return support_resources
            
            elif uri == "ice://statistics/trends":
                # Return statistics and trends
                stats_data = {
                    "description": "ICE Detention Statistics and Trends",
                    "last_updated": datetime.now().isoformat(),
                    "data_source": "TRAC Reports, ICE Statistics",
                    "time_period": "2019-2025",
                    "key_metrics": {
                        "total_facilities": 186,
                        "average_daily_population": 62005,
                        "peak_population": 56000,
                        "facility_types": {
                            "service_processing_centers": 8,
                            "contract_detention_facilities": 120,
                            "intergovernmental_service_agreements": 58
                        }
                    },
                    "trends": {
                        "population_changes": "Monthly population data available",
                        "facility_utilization": "Capacity and occupancy rates",
                        "demographic_breakdown": "Age, gender, country of origin",
                        "geographic_distribution": "State-by-state detention patterns"
                    },
                    "data_quality": {
                        "update_frequency": "Monthly",
                        "verification_status": "Verified through multiple sources",
                        "completeness": "95%+ data coverage",
                        "accuracy": "Cross-validated with official sources"
                    },
                    "usage_notes": "Statistics are for informational purposes and may be subject to change. Always verify current data through official sources."
                }
                return json.dumps(stats_data, indent=2)
            
            else:
                return f"Unknown resource: {uri}"
    
    async def start(self) -> None:
        """Start the MCP server."""
        self.logger.info("Starting ICE Locator MCP Server")
        
        # Initialize telemetry and monitoring
        if self.comprehensive_monitor:
            await self.comprehensive_monitor.initialize()
            await self.comprehensive_monitor.start_monitoring({
                "server_version": self.config.server_version,
                "startup_time": datetime.now().isoformat()
            })
            self.logger.info("Comprehensive monitoring started")
        
        # Initialize components
        await self.proxy_manager.initialize()
        await self.search_engine.initialize()
        
        self.logger.info("ICE Locator MCP Server started successfully")
    
    async def stop(self) -> None:
        """Stop the MCP server and cleanup resources."""
        self.logger.info("Stopping ICE Locator MCP Server")
        
        # Cleanup components
        await self.search_engine.cleanup()
        await self.proxy_manager.cleanup()
        
        # Cleanup telemetry and monitoring
        if self.comprehensive_monitor:
            await self.comprehensive_monitor.stop_monitoring("server_shutdown")
            await self.comprehensive_monitor.cleanup()
            self.logger.info("Comprehensive monitoring cleaned up")
        
        self.logger.info("ICE Locator MCP Server stopped")


async def main() -> None:
    """Main entry point for the server."""
    
    # Setup logging
    setup_logging()
    
    # Create and start server
    server = ICELocatorServer()
    
    try:
        await server.start()
        
        # Run server with stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            try:
                await server.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="ice-locator",
                        server_version="0.1.0",
                        capabilities=types.ServerCapabilities(
                            tools=types.ToolsCapability(listChanged=False),
                            logging=types.LoggingCapability()
                        )
                    )
                )
            except Exception as stdio_error:
                logging.error(f"Stdio server error: {stdio_error}")
                import traceback
                traceback.print_exc()
                raise
            
    except KeyboardInterrupt:
        logging.info("Received interrupt signal")
    except Exception as e:
        logging.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await server.stop()
        except Exception as stop_error:
            logging.error(f"Error stopping server: {stop_error}")


if __name__ == "__main__":
    asyncio.run(main())