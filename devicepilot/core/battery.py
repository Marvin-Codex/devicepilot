"""
Advanced Battery Monitoring and Health Analysis
Generates detailed battery reports and provides health recommendations
"""

import subprocess
import os
import re
import json
import time
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta


class BatteryManager:
    def __init__(self):
        self.report_path = Path("battery_reports")
        self.report_path.mkdir(exist_ok=True)

    def generate_battery_report(self, duration_days=30) -> Optional[Path]:
        """Generate Windows battery report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.report_path / f"battery_report_{timestamp}.html"
            
            cmd = ["powercfg", "/batteryreport", "/output", str(output_file)]
            if duration_days:
                cmd.extend(["/duration", str(duration_days)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if output_file.exists():
                return output_file
            else:
                print("Battery report file was not created")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate battery report: {e}")
            print(f"Error output: {e.stderr}")
            return None
        except Exception as e:
            print(f"Error generating battery report: {e}")
            return None

    def parse_battery_report(self, report_path: Path) -> Dict:
        """Parse battery report HTML and extract key information"""
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            report_data = {
                "system_info": self._extract_system_info(content),
                "battery_info": self._extract_battery_info(content),
                "usage_history": self._extract_usage_history(content),
                "capacity_history": self._extract_capacity_history(content),
                "health_analysis": {}
            }
            
            # Perform health analysis
            report_data["health_analysis"] = self._analyze_battery_health(report_data)
            
            return report_data
            
        except Exception as e:
            print(f"Error parsing battery report: {e}")
            return {}

    def _extract_system_info(self, content: str) -> Dict:
        """Extract system information from report"""
        info = {}
        
        # Computer name
        match = re.search(r'Computer name</td>\s*<td>([^<]+)</td>', content, re.IGNORECASE)
        if match:
            info['computer_name'] = match.group(1).strip()
        
        # Platform role
        match = re.search(r'Platform role</td>\s*<td>([^<]+)</td>', content, re.IGNORECASE)
        if match:
            info['platform_role'] = match.group(1).strip()
        
        # Report time
        match = re.search(r'Report generated at</td>\s*<td>([^<]+)</td>', content, re.IGNORECASE)
        if match:
            info['report_time'] = match.group(1).strip()
        
        return info

    def _extract_battery_info(self, content: str) -> List[Dict]:
        """Extract battery information for all batteries"""
        batteries = []
        
        # Find battery sections
        battery_sections = re.findall(
            r'<h3>Battery\s+(\d+)</h3>.*?(?=<h3>|$)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        for i, section in enumerate(battery_sections):
            battery = {"id": i + 1}
            
            # Name
            match = re.search(r'Name</td>\s*<td>([^<]+)</td>', section, re.IGNORECASE)
            if match:
                battery['name'] = match.group(1).strip()
            
            # Manufacturer
            match = re.search(r'Manufacturer</td>\s*<td>([^<]+)</td>', section, re.IGNORECASE)
            if match:
                battery['manufacturer'] = match.group(1).strip()
            
            # Serial number
            match = re.search(r'Serial number</td>\s*<td>([^<]+)</td>', section, re.IGNORECASE)
            if match:
                battery['serial_number'] = match.group(1).strip()
            
            # Chemistry
            match = re.search(r'Chemistry</td>\s*<td>([^<]+)</td>', section, re.IGNORECASE)
            if match:
                battery['chemistry'] = match.group(1).strip()
            
            # Design capacity
            match = re.search(r'Design capacity</td>\s*<td>([0-9,]+)\s*mWh</td>', section, re.IGNORECASE)
            if match:
                battery['design_capacity_mwh'] = int(match.group(1).replace(',', ''))
            
            # Full charge capacity
            match = re.search(r'Full charge capacity</td>\s*<td>([0-9,]+)\s*mWh</td>', section, re.IGNORECASE)
            if match:
                battery['full_charge_capacity_mwh'] = int(match.group(1).replace(',', ''))
            
            # Cycle count
            match = re.search(r'Cycle count</td>\s*<td>([0-9,]+)</td>', section, re.IGNORECASE)
            if match:
                battery['cycle_count'] = int(match.group(1).replace(',', ''))
            
            batteries.append(battery)
        
        return batteries

    def _extract_usage_history(self, content: str) -> List[Dict]:
        """Extract battery usage history"""
        usage_history = []
        
        # Find usage history table
        usage_match = re.search(
            r'<h2>Recent usage</h2>.*?<table[^>]*>(.*?)</table>', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if usage_match:
            table_content = usage_match.group(1)
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_content, re.DOTALL)
            
            for row in rows[1:]:  # Skip header row
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if len(cells) >= 4:
                    usage_entry = {
                        'start_time': cells[0].strip(),
                        'state': cells[1].strip(),
                        'source': cells[2].strip(),
                        'capacity_remaining': cells[3].strip()
                    }
                    usage_history.append(usage_entry)
        
        return usage_history

    def _extract_capacity_history(self, content: str) -> List[Dict]:
        """Extract battery capacity history"""
        capacity_history = []
        
        # Find capacity history table
        capacity_match = re.search(
            r'<h2>Capacity history</h2>.*?<table[^>]*>(.*?)</table>', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if capacity_match:
            table_content = capacity_match.group(1)
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_content, re.DOTALL)
            
            for row in rows[1:]:  # Skip header row
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if len(cells) >= 3:
                    # Extract numeric values from capacity strings
                    full_charge_match = re.search(r'([0-9,]+)', cells[1])
                    design_capacity_match = re.search(r'([0-9,]+)', cells[2])
                    
                    capacity_entry = {
                        'period': cells[0].strip(),
                        'full_charge_capacity': int(full_charge_match.group(1).replace(',', '')) if full_charge_match else 0,
                        'design_capacity': int(design_capacity_match.group(1).replace(',', '')) if design_capacity_match else 0
                    }
                    
                    if capacity_entry['design_capacity'] > 0:
                        capacity_entry['health_percentage'] = round(
                            (capacity_entry['full_charge_capacity'] / capacity_entry['design_capacity']) * 100, 1
                        )
                    
                    capacity_history.append(capacity_entry)
        
        return capacity_history

    def _analyze_battery_health(self, report_data: Dict) -> Dict:
        """Analyze battery health and provide recommendations"""
        analysis = {
            'overall_health': 'Unknown',
            'health_score': 0,
            'recommendations': [],
            'warnings': [],
            'statistics': {}
        }
        
        batteries = report_data.get('battery_info', [])
        if not batteries:
            return analysis
        
        primary_battery = batteries[0]  # Analyze first battery
        
        # Calculate health percentage
        design_capacity = primary_battery.get('design_capacity_mwh', 0)
        full_charge_capacity = primary_battery.get('full_charge_capacity_mwh', 0)
        
        if design_capacity > 0 and full_charge_capacity > 0:
            health_percentage = (full_charge_capacity / design_capacity) * 100
            analysis['health_score'] = round(health_percentage, 1)
            
            # Determine overall health category
            if health_percentage >= 90:
                analysis['overall_health'] = 'Excellent'
            elif health_percentage >= 80:
                analysis['overall_health'] = 'Good'
            elif health_percentage >= 70:
                analysis['overall_health'] = 'Fair'
            elif health_percentage >= 60:
                analysis['overall_health'] = 'Poor'
            else:
                analysis['overall_health'] = 'Critical'
            
            # Generate recommendations
            if health_percentage < 70:
                analysis['recommendations'].append(
                    "Consider replacing the battery as capacity has degraded significantly."
                )
            
            if health_percentage < 80:
                analysis['warnings'].append(
                    f"Battery capacity is at {health_percentage:.1f}% of original design capacity."
                )
        
        # Cycle count analysis
        cycle_count = primary_battery.get('cycle_count')
        if cycle_count:
            analysis['statistics']['cycle_count'] = cycle_count
            
            if cycle_count > 1000:
                analysis['warnings'].append(
                    f"High cycle count ({cycle_count}). Battery may be nearing end of life."
                )
            elif cycle_count > 500:
                analysis['recommendations'].append(
                    "Monitor battery performance closely due to moderate cycle count."
                )
        
        # Capacity history trend analysis
        capacity_history = report_data.get('capacity_history', [])
        if len(capacity_history) > 1:
            recent_health = capacity_history[-1].get('health_percentage', 0)
            older_health = capacity_history[0].get('health_percentage', 0)
            
            if recent_health < older_health:
                degradation_rate = older_health - recent_health
                analysis['statistics']['degradation_rate'] = round(degradation_rate, 1)
                
                if degradation_rate > 10:
                    analysis['warnings'].append(
                        f"Rapid battery degradation detected ({degradation_rate:.1f}% decline)."
                    )
        
        # Usage pattern analysis
        usage_history = report_data.get('usage_history', [])
        if usage_history:
            ac_usage_count = len([u for u in usage_history if 'AC' in u.get('source', '')])
            battery_usage_count = len([u for u in usage_history if 'Battery' in u.get('source', '')])
            
            if battery_usage_count > 0:
                ac_ratio = ac_usage_count / (ac_usage_count + battery_usage_count)
                if ac_ratio < 0.3:
                    analysis['recommendations'].append(
                        "Consider using AC power more often to reduce battery wear."
                    )
        
        return analysis

    def get_live_battery_status(self) -> Dict:
        """Get current battery status using system commands"""
        try:
            # Use WMIC to get battery information
            cmd = ['wmic', 'path', 'win32_battery', 'get', '/format:list']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            battery_info = {}
            for line in result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    battery_info[key.strip()] = value.strip()
            
            return {
                'charge_percentage': battery_info.get('EstimatedChargeRemaining', 0),
                'status': battery_info.get('BatteryStatus', 'Unknown'),
                'chemistry': battery_info.get('Chemistry', 'Unknown'),
                'design_capacity': battery_info.get('DesignCapacity', 0),
                'full_charge_capacity': battery_info.get('FullChargeCapacity', 0)
            }
        
        except Exception as e:
            print(f"Error getting live battery status: {e}")
            return {}

    def export_battery_data(self, report_data: Dict, output_file: Path) -> bool:
        """Export battery analysis to JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting battery data: {e}")
            return False

    def get_battery_recommendations(self, health_score: float, cycle_count: int = None) -> List[str]:
        """Get personalized battery care recommendations"""
        recommendations = []
        
        if health_score < 70:
            recommendations.extend([
                "🔋 Consider battery replacement - capacity below 70%",
                "⚠️ Backup important data regularly",
                "🔌 Keep device plugged in when possible"
            ])
        elif health_score < 85:
            recommendations.extend([
                "🔋 Monitor battery performance closely",
                "🌡️ Avoid extreme temperatures",
                "⚡ Use battery saver mode when on battery"
            ])
        
        if cycle_count:
            if cycle_count > 1000:
                recommendations.append("🔄 High cycle count - consider replacement soon")
            elif cycle_count > 500:
                recommendations.append("🔄 Moderate usage - good battery maintenance")
        
        # General recommendations
        recommendations.extend([
            "🌡️ Keep device in cool, dry environment",
            "⚡ Avoid deep discharge cycles",
            "🔌 Unplug when fully charged occasionally",
            "📱 Use power management settings"
        ])
        
        return recommendations
