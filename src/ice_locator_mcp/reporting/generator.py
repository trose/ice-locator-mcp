"""
Reporting tools for generating comprehensive search reports and analytics.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import structlog

from ..core.config import Config


@dataclass
class SearchReport:
    """Comprehensive search report."""
    report_id: str
    generated_at: str
    search_criteria: Dict[str, Any]
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    summary: Dict[str, Any]
    recommendations: List[str]
    legal_guidance: List[str]
    resources: List[Dict[str, str]]


@dataclass
class ReportTemplate:
    """Report template configuration."""
    name: str
    format: str  # markdown, html, json, pdf
    sections: List[str]
    language: str = "en"
    legal_disclaimers: bool = True
    include_metadata: bool = True


class ReportGenerator:
    """Generates comprehensive reports for search results."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Report templates
        self.templates = {
            "legal": ReportTemplate(
                name="Legal Report",
                format="markdown",
                sections=[
                    "executive_summary",
                    "search_details", 
                    "results_analysis",
                    "legal_guidance",
                    "next_steps",
                    "resources",
                    "disclaimers"
                ],
                legal_disclaimers=True
            ),
            "family": ReportTemplate(
                name="Family Assistance Report",
                format="markdown",
                sections=[
                    "summary",
                    "search_results",
                    "facility_information",
                    "visiting_information",
                    "support_resources",
                    "contact_information"
                ],
                language="bilingual"
            ),
            "advocacy": ReportTemplate(
                name="Advocacy Report",
                format="markdown",
                sections=[
                    "executive_summary",
                    "methodology",
                    "findings",
                    "analysis",
                    "recommendations",
                    "data_sources"
                ]
            ),
            "technical": ReportTemplate(
                name="Technical Analysis",
                format="json",
                sections=[
                    "search_metadata",
                    "performance_metrics",
                    "data_quality",
                    "system_status"
                ],
                legal_disclaimers=False
            )
        }
    
    async def generate_report(
        self,
        search_criteria: Dict[str, Any],
        results: List[Dict[str, Any]],
        report_type: str = "legal",
        language: str = "en",
        **kwargs
    ) -> SearchReport:
        """Generate comprehensive search report."""
        
        if report_type not in self.templates:
            raise ValueError(f"Unknown report type: {report_type}")
        
        template = self.templates[report_type]
        
        # Generate report ID
        report_id = f"{report_type}_{int(time.time())}"
        
        # Create metadata
        metadata = await self._generate_metadata(search_criteria, results, **kwargs)
        
        # Create summary
        summary = await self._generate_summary(results, report_type)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            search_criteria, results, report_type
        )
        
        # Generate legal guidance
        legal_guidance = await self._generate_legal_guidance(results, report_type)
        
        # Generate resources
        resources = await self._generate_resources(results, report_type, language)
        
        report = SearchReport(
            report_id=report_id,
            generated_at=datetime.now().isoformat(),
            search_criteria=search_criteria,
            results=results,
            metadata=metadata,
            summary=summary,
            recommendations=recommendations,
            legal_guidance=legal_guidance,
            resources=resources
        )
        
        self.logger.info(
            "Report generated",
            report_id=report_id,
            report_type=report_type,
            results_count=len(results)
        )
        
        return report
    
    async def format_report(
        self,
        report: SearchReport,
        format_type: str = "markdown",
        template_name: str = "legal"
    ) -> str:
        """Format report according to template."""
        
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.templates[template_name]
        
        if format_type == "markdown":
            return await self._format_markdown(report, template)
        elif format_type == "html":
            return await self._format_html(report, template)
        elif format_type == "json":
            return await self._format_json(report, template)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    async def _generate_metadata(
        self,
        search_criteria: Dict[str, Any],
        results: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate report metadata."""
        
        return {
            "search_type": self._determine_search_type(search_criteria),
            "results_count": len(results),
            "search_timestamp": datetime.now().isoformat(),
            "processing_time_ms": kwargs.get("processing_time_ms", 0),
            "confidence_scores": [
                r.get("confidence_score", 0) for r in results
            ],
            "facilities_found": list(set(
                r.get("facility_name", "") for r in results if r.get("facility_name")
            )),
            "data_source": "ICE Online Detainee Locator",
            "search_quality": self._assess_search_quality(search_criteria, results)
        }
    
    async def _generate_summary(
        self,
        results: List[Dict[str, Any]],
        report_type: str
    ) -> Dict[str, Any]:
        """Generate report summary."""
        
        if not results:
            return {
                "status": "no_results",
                "message": "No matching records found in the ICE database.",
                "suggestions": [
                    "Verify spelling of names",
                    "Try alternative name spellings or nicknames",
                    "Check if A-Number is correct",
                    "Contact local ICE field office for assistance"
                ]
            }
        
        # Analyze results
        facilities = {}
        statuses = {}
        
        for result in results:
            facility = result.get("facility_name", "Unknown")
            status = result.get("custody_status", "Unknown")
            
            facilities[facility] = facilities.get(facility, 0) + 1
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "status": "found",
            "total_results": len(results),
            "facilities_breakdown": facilities,
            "status_breakdown": statuses,
            "highest_confidence": max(
                (r.get("confidence_score", 0) for r in results), default=0
            ),
            "most_recent_update": max(
                (r.get("last_updated", "") for r in results), default=""
            )
        }
    
    async def _generate_recommendations(
        self,
        search_criteria: Dict[str, Any],
        results: List[Dict[str, Any]],
        report_type: str
    ) -> List[str]:
        """Generate recommendations based on results."""
        
        recommendations = []
        
        if not results:
            recommendations.extend([
                "Consider using fuzzy name matching if exact names don't yield results",
                "Verify the spelling and format of names and identification numbers",
                "Contact the ICE field office directly for additional assistance",
                "Check if the person may have been released or transferred"
            ])
        else:
            if report_type == "legal":
                recommendations.extend([
                    "Contact the detention facility directly to verify current status",
                    "Schedule a legal visit if representing the detainee",
                    "Gather additional documentation for case preparation",
                    "Review facility policies and visiting procedures"
                ])
            elif report_type == "family":
                recommendations.extend([
                    "Contact the facility to schedule a visit",
                    "Prepare necessary identification for facility visits",
                    "Consider contacting local legal aid organizations",
                    "Connect with family support groups in your area"
                ])
            elif report_type == "advocacy":
                recommendations.extend([
                    "Document facility conditions and policies",
                    "Connect with other advocacy organizations",
                    "Consider broader systemic analysis",
                    "Maintain regular monitoring of detainee status"
                ])
        
        return recommendations
    
    async def _generate_legal_guidance(
        self,
        results: List[Dict[str, Any]],
        report_type: str
    ) -> List[str]:
        """Generate legal guidance and considerations."""
        
        guidance = []
        
        if report_type in ["legal", "family"]:
            guidance.extend([
                "This information is based on publicly available ICE data",
                "Detainee status can change rapidly - verify current information",
                "Legal representation rights apply to all immigration proceedings",
                "Family members have rights to visitation subject to facility policies",
                "Emergency situations may require immediate legal intervention"
            ])
            
            if results:
                guidance.extend([
                    "Contact the facility directly to confirm current custody status",
                    "Be prepared to provide identification when visiting or calling",
                    "Understand that some information may be restricted for privacy",
                    "Consider consulting with an immigration attorney"
                ])
        
        return guidance
    
    async def _generate_resources(
        self,
        results: List[Dict[str, Any]],
        report_type: str,
        language: str
    ) -> List[Dict[str, str]]:
        """Generate relevant resources and contacts."""
        
        resources = []
        
        # General resources
        resources.extend([
            {
                "name": "ICE Online Detainee Locator",
                "url": "https://locator.ice.gov",
                "description": "Official ICE database for locating detainees"
            },
            {
                "name": "American Immigration Lawyers Association",
                "url": "https://aila.org",
                "description": "Find qualified immigration attorneys"
            },
            {
                "name": "National Immigration Legal Services Directory",
                "url": "https://nipnlg.org/PILdirectory",
                "description": "Free and low-cost legal services"
            }
        ])
        
        if language in ["es", "bilingual"]:
            resources.extend([
                {
                    "name": "Línea Nacional de Inmigración",
                    "phone": "1-855-234-1317",
                    "description": "Asistencia legal gratuita en español"
                },
                {
                    "name": "Unidos US",
                    "url": "https://unidosus.org",
                    "description": "Recursos y apoyo para la comunidad latina"
                }
            ])
        
        if report_type == "family":
            resources.extend([
                {
                    "name": "Family Case Management Program",
                    "description": "ICE program for alternative to detention"
                },
                {
                    "name": "Local Family Support Groups",
                    "description": "Connect with other families in similar situations"
                }
            ])
        
        # Add facility-specific resources if results found
        if results:
            facilities = set(r.get("facility_name", "") for r in results)
            for facility in facilities:
                if facility:
                    resources.append({
                        "name": f"{facility} Information",
                        "description": f"Contact information and policies for {facility}",
                        "type": "facility"
                    })
        
        return resources
    
    def _determine_search_type(self, search_criteria: Dict[str, Any]) -> str:
        """Determine type of search performed."""
        if "alien_number" in search_criteria:
            return "alien_number"
        elif "first_name" in search_criteria or "last_name" in search_criteria:
            return "name"
        elif "facility_name" in search_criteria:
            return "facility"
        else:
            return "unknown"
    
    def _assess_search_quality(
        self,
        search_criteria: Dict[str, Any],
        results: List[Dict[str, Any]]
    ) -> str:
        """Assess the quality of search results."""
        
        if not results:
            return "no_results"
        
        # Check confidence scores if available
        confidence_scores = [r.get("confidence_score", 0) for r in results]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        if avg_confidence > 0.9:
            return "high_confidence"
        elif avg_confidence > 0.7:
            return "medium_confidence"
        elif avg_confidence > 0.5:
            return "low_confidence"
        else:
            return "uncertain"
    
    async def _format_markdown(
        self,
        report: SearchReport,
        template: ReportTemplate
    ) -> str:
        """Format report as Markdown."""
        
        md_parts = []
        
        # Title
        md_parts.append(f"# {template.name}")
        md_parts.append(f"**Generated:** {report.generated_at}")
        md_parts.append(f"**Report ID:** {report.report_id}")
        md_parts.append("")
        
        for section in template.sections:
            if section == "executive_summary":
                md_parts.extend(await self._format_executive_summary(report))
            elif section == "search_details":
                md_parts.extend(await self._format_search_details(report))
            elif section == "results_analysis":
                md_parts.extend(await self._format_results_analysis(report))
            elif section == "legal_guidance":
                md_parts.extend(await self._format_legal_guidance_section(report))
            elif section == "next_steps":
                md_parts.extend(await self._format_next_steps(report))
            elif section == "resources":
                md_parts.extend(await self._format_resources_section(report))
            elif section == "disclaimers" and template.legal_disclaimers:
                md_parts.extend(await self._format_disclaimers())
        
        return "\n".join(md_parts)
    
    async def _format_executive_summary(self, report: SearchReport) -> List[str]:
        """Format executive summary section."""
        lines = [
            "## Executive Summary",
            ""
        ]
        
        summary = report.summary
        if summary.get("status") == "found":
            lines.extend([
                f"**Search Results:** {summary['total_results']} records found",
                f"**Facilities:** {len(summary.get('facilities_breakdown', {}))} detention facilities",
                f"**Confidence:** {summary.get('highest_confidence', 0):.1%}",
                ""
            ])
        else:
            lines.extend([
                "**Search Results:** No matching records found",
                "**Recommendation:** Review search criteria and try alternative approaches",
                ""
            ])
        
        return lines
    
    async def _format_search_details(self, report: SearchReport) -> List[str]:
        """Format search details section."""
        lines = [
            "## Search Details",
            ""
        ]
        
        criteria = report.search_criteria
        for key, value in criteria.items():
            if value:
                lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        
        lines.extend(["", f"**Search Type:** {report.metadata.get('search_type', 'Unknown')}", ""])
        
        return lines
    
    async def _format_results_analysis(self, report: SearchReport) -> List[str]:
        """Format results analysis section."""
        lines = [
            "## Results Analysis",
            ""
        ]
        
        if not report.results:
            lines.extend([
                "No matching records were found in the ICE database.",
                "",
                "This could mean:",
                "- The person is not currently in ICE custody",
                "- There may be spelling variations in the name",
                "- The person may have been released or transferred",
                ""
            ])
        else:
            lines.append("### Found Records")
            lines.append("")
            
            for i, result in enumerate(report.results, 1):
                lines.extend([
                    f"#### Record {i}",
                    f"- **Name:** {result.get('name', 'N/A')}",
                    f"- **A-Number:** {result.get('alien_number', 'N/A')}",
                    f"- **Facility:** {result.get('facility_name', 'N/A')}",
                    f"- **Status:** {result.get('custody_status', 'N/A')}",
                    f"- **Last Updated:** {result.get('last_updated', 'N/A')}",
                    ""
                ])
        
        return lines
    
    async def _format_legal_guidance_section(self, report: SearchReport) -> List[str]:
        """Format legal guidance section."""
        lines = [
            "## Legal Guidance",
            ""
        ]
        
        for guidance in report.legal_guidance:
            lines.append(f"- {guidance}")
        
        lines.append("")
        return lines
    
    async def _format_next_steps(self, report: SearchReport) -> List[str]:
        """Format next steps section."""
        lines = [
            "## Recommended Next Steps",
            ""
        ]
        
        for i, recommendation in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {recommendation}")
        
        lines.append("")
        return lines
    
    async def _format_resources_section(self, report: SearchReport) -> List[str]:
        """Format resources section."""
        lines = [
            "## Resources and Contacts",
            ""
        ]
        
        for resource in report.resources:
            lines.append(f"### {resource['name']}")
            if 'url' in resource:
                lines.append(f"- **Website:** {resource['url']}")
            if 'phone' in resource:
                lines.append(f"- **Phone:** {resource['phone']}")
            if 'description' in resource:
                lines.append(f"- **Description:** {resource['description']}")
            lines.append("")
        
        return lines
    
    async def _format_disclaimers(self) -> List[str]:
        """Format legal disclaimers section."""
        return [
            "## Important Disclaimers",
            "",
            "- This report is based on publicly available information from the ICE Online Detainee Locator",
            "- Information may not be current and should be verified directly with facilities",
            "- This tool is not affiliated with ICE or any government agency",
            "- Users are responsible for compliance with applicable laws and regulations",
            "- This information should not be considered legal advice",
            ""
        ]
    
    async def _format_html(self, report: SearchReport, template: ReportTemplate) -> str:
        """Format report as HTML."""
        # Convert markdown to HTML (simplified)
        markdown_content = await self._format_markdown(report, template)
        
        # Basic HTML wrapper
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{template.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        .metadata {{ background: #f5f5f5; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <pre>{markdown_content}</pre>
</body>
</html>
        """
        
        return html.strip()
    
    async def _format_json(self, report: SearchReport, template: ReportTemplate) -> str:
        """Format report as JSON."""
        return json.dumps(asdict(report), indent=2)
    
    async def save_report(
        self,
        report: SearchReport,
        file_path: Union[str, Path],
        format_type: str = "markdown",
        template_name: str = "legal"
    ) -> None:
        """Save report to file."""
        
        content = await self.format_report(report, format_type, template_name)
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(
            "Report saved",
            report_id=report.report_id,
            file_path=str(file_path),
            format=format_type
        )