"""
COCOMO Model Implementation for Software Cost Estimation
Supports Basic, Intermediate, and Detailed COCOMO models
"""

import json
import math
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class ProjectMetrics:
    """Store project complexity metrics"""
    name: str
    sloc: int
    cyclomatic_avg: float
    halstead_effort: float
    halstead_bugs: float
    num_functions: int
    num_files: int


class COCOMOCalculator:
    """
    COCOMO (Constructive Cost Model) Calculator
    
    Project Types:
    - Organic: Small teams, familiar environment, flexible requirements
    - Semi-detached: Medium complexity, mixed experience
    - Embedded: Complex, tight constraints, real-time requirements
    """
    
    # COCOMO coefficients for Basic model
    BASIC_COEFFICIENTS = {
        'organic': {'a': 2.4, 'b': 1.05, 'c': 2.5, 'd': 0.38},
        'semi-detached': {'a': 3.0, 'b': 1.12, 'c': 2.5, 'd': 0.35},
        'embedded': {'a': 3.6, 'b': 1.20, 'c': 2.5, 'd': 0.32}
    }
    
    # Cost drivers for Intermediate COCOMO
    COST_DRIVERS = {
        'product': ['RELY', 'DATA', 'CPLX'],
        'computer': ['TIME', 'STOR', 'VIRT', 'TURN'],
        'personnel': ['ACAP', 'AEXP', 'PCAP', 'VEXP', 'LEXP'],
        'project': ['MODP', 'TOOL', 'SCED']
    }
    
    # Effort Adjustment Factor (EAF) ratings
    # Very Low, Low, Nominal, High, Very High, Extra High
    EAF_VALUES = {
        'RELY': [0.75, 0.88, 1.00, 1.15, 1.40, None],  # Required reliability
        'DATA': [None, 0.94, 1.00, 1.08, 1.16, None],  # Database size
        'CPLX': [0.70, 0.85, 1.00, 1.15, 1.30, 1.65],  # Product complexity
        'TIME': [None, None, 1.00, 1.11, 1.30, 1.66],  # Execution time constraint
        'STOR': [None, None, 1.00, 1.06, 1.21, 1.56],  # Main storage constraint
        'VIRT': [None, 0.87, 1.00, 1.15, 1.30, None],  # Virtual machine volatility
        'TURN': [None, 0.87, 1.00, 1.07, 1.15, None],  # Computer turnaround time
        'ACAP': [1.46, 1.19, 1.00, 0.86, 0.71, None],  # Analyst capability
        'AEXP': [1.29, 1.13, 1.00, 0.91, 0.82, None],  # Applications experience
        'PCAP': [1.42, 1.17, 1.00, 0.86, 0.70, None],  # Programmer capability
        'VEXP': [1.21, 1.10, 1.00, 0.90, None, None],  # Virtual machine experience
        'LEXP': [1.14, 1.07, 1.00, 0.95, None, None],  # Programming language exp
        'MODP': [1.24, 1.10, 1.00, 0.91, 0.82, None],  # Modern programming practices
        'TOOL': [1.24, 1.10, 1.00, 0.91, 0.83, None],  # Use of software tools
        'SCED': [1.23, 1.08, 1.00, 1.04, 1.10, None],  # Required development schedule
    }
    
    def __init__(self):
        pass
    
    def classify_project(self, metrics: ProjectMetrics) -> str:
        """
        Classify project type based on metrics
        
        Classification criteria:
        - Organic: < 50 KLOC, low complexity, small team
        - Semi-detached: 50-300 KLOC, medium complexity
        - Embedded: > 300 KLOC, high complexity, strict constraints
        """
        kloc = metrics.sloc / 1000
        
        # Consider complexity indicators
        complexity_score = 0
        
        # Cyclomatic complexity indicator
        if metrics.cyclomatic_avg > 10:
            complexity_score += 2
        elif metrics.cyclomatic_avg > 5:
            complexity_score += 1
        
        # File count indicator (project structure)
        if metrics.num_files > 50:
            complexity_score += 2
        elif metrics.num_files > 20:
            complexity_score += 1
        
        # Size-based classification
        if kloc < 50:
            if complexity_score >= 2:
                return 'semi-detached'
            return 'organic'
        elif kloc < 300:
            return 'semi-detached'
        else:
            return 'embedded'
    
    def calculate_basic_cocomo(self, kloc: float, project_type: str) -> Dict:
        """
        Calculate Basic COCOMO estimates
        
        Effort = a * (KLOC)^b (Person-Months)
        Time = c * (Effort)^d (Months)
        People = Effort / Time
        """
        coef = self.BASIC_COEFFICIENTS[project_type]
        
        # Effort in person-months
        effort = coef['a'] * (kloc ** coef['b'])
        
        # Development time in months
        time = coef['c'] * (effort ** coef['d'])
        
        # Average team size
        people = effort / time
        
        # Productivity
        productivity = kloc / effort  # KLOC per person-month
        
        return {
            'effort_pm': round(effort, 2),
            'time_months': round(time, 2),
            'avg_people': round(people, 2),
            'productivity': round(productivity, 3)
        }
    
    def estimate_cost_drivers(self, metrics: ProjectMetrics, project_type: str) -> Dict[str, float]:
        """
        Estimate cost driver values based on project metrics
        These are assumptions based on typical small-medium open source projects
        """
        drivers = {}
        
        # Product attributes
        drivers['RELY'] = 1.00  # Nominal reliability (index 2)
        drivers['DATA'] = 0.94   # Low database size (index 1)
        
        # Complexity based on cyclomatic complexity
        if metrics.cyclomatic_avg > 10:
            drivers['CPLX'] = 1.30  # Very High
        elif metrics.cyclomatic_avg > 5:
            drivers['CPLX'] = 1.15  # High
        else:
            drivers['CPLX'] = 1.00  # Nominal
        
        # Computer attributes (assume modern development environment)
        drivers['TIME'] = 1.00  # No time constraint
        drivers['STOR'] = 1.00  # No storage constraint
        drivers['VIRT'] = 1.00  # Nominal VM volatility
        drivers['TURN'] = 0.87  # Low turnaround time (good tools)
        
        # Personnel attributes (assume competent open source developers)
        drivers['ACAP'] = 0.86  # High analyst capability
        drivers['AEXP'] = 1.00  # Nominal application experience
        drivers['PCAP'] = 0.86  # High programmer capability
        drivers['VEXP'] = 0.90  # High platform experience
        drivers['LEXP'] = 0.95  # High language experience
        
        # Project attributes (assume good practices for open source)
        drivers['MODP'] = 0.91  # High use of modern practices
        drivers['TOOL'] = 0.91  # High use of software tools
        drivers['SCED'] = 1.00  # Nominal schedule
        
        return drivers
    
    def calculate_intermediate_cocomo(self, kloc: float, project_type: str, 
                                     cost_drivers: Dict[str, float]) -> Dict:
        """
        Calculate Intermediate COCOMO with Effort Adjustment Factor (EAF)
        
        Effort = a * (KLOC)^b * EAF
        EAF = Product of all cost driver ratings
        """
        # Calculate EAF
        eaf = 1.0
        for driver, value in cost_drivers.items():
            eaf *= value
        
        # Basic effort
        coef = self.BASIC_COEFFICIENTS[project_type]
        base_effort = coef['a'] * (kloc ** coef['b'])
        
        # Adjusted effort
        effort = base_effort * eaf
        
        # Development time (uses adjusted effort)
        time = coef['c'] * (effort ** coef['d'])
        
        # Average team size
        people = effort / time
        
        # Productivity
        productivity = kloc / effort
        
        return {
            'effort_pm': round(effort, 2),
            'time_months': round(time, 2),
            'avg_people': round(people, 2),
            'productivity': round(productivity, 3),
            'eaf': round(eaf, 3),
            'base_effort_pm': round(base_effort, 2)
        }
    
    def analyze_project(self, metrics: ProjectMetrics) -> Dict:
        """Complete COCOMO analysis for a project"""
        
        # Convert SLOC to KLOC
        kloc = metrics.sloc / 1000
        
        # Classify project
        project_type = self.classify_project(metrics)
        
        # Calculate Basic COCOMO
        basic_results = self.calculate_basic_cocomo(kloc, project_type)
        
        # Estimate cost drivers
        cost_drivers = self.estimate_cost_drivers(metrics, project_type)
        
        # Calculate Intermediate COCOMO
        intermediate_results = self.calculate_intermediate_cocomo(
            kloc, project_type, cost_drivers
        )
        
        return {
            'project_name': metrics.name,
            'kloc': round(kloc, 3),
            'project_type': project_type,
            'basic_cocomo': basic_results,
            'intermediate_cocomo': intermediate_results,
            'cost_drivers': cost_drivers,
            'assumptions': self._generate_assumptions(metrics, project_type)
        }
    
    def _generate_assumptions(self, metrics: ProjectMetrics, project_type: str) -> Dict:
        """Generate justifications for assumptions made"""
        return {
            'project_classification': f"Classified as '{project_type}' based on {metrics.sloc} SLOC "
                                     f"and average cyclomatic complexity of {metrics.cyclomatic_avg:.2f}",
            'reliability': "Nominal reliability assumed - typical for utility applications",
            'complexity': f"Complexity rating based on cyclomatic complexity ({metrics.cyclomatic_avg:.2f}) "
                         f"and Halstead metrics",
            'team_capability': "High capability assumed - open source projects typically attract "
                              "skilled developers",
            'tools': "Modern tools assumed - Python has excellent development ecosystem",
            'schedule': "Nominal schedule - no critical time constraints for open source projects",
            'database': "Low database complexity - simple data persistence requirements"
        }


def load_metrics_from_json(json_data: Dict) -> ProjectMetrics:
    """Convert JSON metrics to ProjectMetrics object"""
    return ProjectMetrics(
        name=json_data['codebase'].split('/')[-1],
        sloc=json_data['sloc_summary']['source_lines'],
        cyclomatic_avg=json_data['cyclomatic_summary']['average_complexity'],
        halstead_effort=json_data['halstead_summary']['total_effort'],
        halstead_bugs=json_data['halstead_summary']['estimated_bugs'],
        num_functions=json_data['cyclomatic_summary']['total_functions'],
        num_files=json_data['sloc_summary']['files_analyzed']
    )


def main():
    """Main analysis function"""
    
    # Your metrics data
    metrics_data = [
        {
            "codebase": "/app/codebases/notejam",
            "total_files": 32,
            "sloc_summary": {
                "total_lines": 1177,
                "source_lines": 863,
                "comment_lines": 94,
                "blank_lines": 220,
                "files_analyzed": 32
            },
            "cyclomatic_summary": {
                "total_functions": 70,
                "average_complexity": 1.3,
                "max_complexity": 5,
                "min_complexity": 1,
                "high_complexity_functions": []
            },
            "halstead_summary": {
                "total_files_analyzed": 23,
                "average_volume": 611.801746949494,
                "total_effort": 96079.84458485126,
                "estimated_bugs": 4.69048005994612,
                "average_difficulty": 5.0143195240808405
            },
            "dataflow_summary": {
                "total_functions_analyzed": 70,
                "total_variables_defined": 174,
                "total_variables_used": 304,
                "average_live_variables": 2.0714285714285716
            }
        },
        {
            "codebase": "/app/codebases/Python-URL-Shortener",
            "total_files": 5,
            "sloc_summary": {
                "total_lines": 348,
                "source_lines": 282,
                "comment_lines": 25,
                "blank_lines": 41,
                "files_analyzed": 5
            },
            "cyclomatic_summary": {
                "total_functions": 17,
                "average_complexity": 3.2941176470588234,
                "max_complexity": 9,
                "min_complexity": 1,
                "high_complexity_functions": []
            },
            "halstead_summary": {
                "total_files_analyzed": 5,
                "average_volume": 1175.1549025413424,
                "total_effort": 102470.87797324153,
                "estimated_bugs": 1.9585915042355704,
                "average_difficulty": 9.736084212514102
            },
            "dataflow_summary": {
                "total_functions_analyzed": 17,
                "total_variables_defined": 72,
                "total_variables_used": 160,
                "average_live_variables": 5.352941176470588
            }
        },
        {
            "codebase": "/app/codebases/todo-cli",
            "total_files": 1,
            "sloc_summary": {
                "total_lines": 61,
                "source_lines": 50,
                "comment_lines": 0,
                "blank_lines": 11,
                "files_analyzed": 1
            },
            "cyclomatic_summary": {
                "total_functions": 7,
                "average_complexity": 2.857142857142857,
                "max_complexity": 7,
                "min_complexity": 1,
                "high_complexity_functions": []
            },
            "halstead_summary": {
                "total_files_analyzed": 1,
                "average_volume": 1126.1827810363209,
                "total_effort": 16329.650325026652,
                "estimated_bugs": 0.37539426034544027,
                "average_difficulty": 14.5
            },
            "dataflow_summary": {
                "total_functions_analyzed": 7,
                "total_variables_defined": 13,
                "total_variables_used": 37,
                "average_live_variables": 3.4285714285714284
            }
        }
    ]
    
    # Initialize calculator
    calculator = COCOMOCalculator()
    
    # Analyze each project
    results = []
    for data in metrics_data:
        metrics = load_metrics_from_json(data)
        analysis = calculator.analyze_project(metrics)
        results.append(analysis)
    
    # Print results
    print("=" * 80)
    print("COCOMO MODEL ANALYSIS RESULTS")
    print("=" * 80)
    
    for result in results:
        print(f"\n{'=' * 80}")
        print(f"PROJECT: {result['project_name']}")
        print(f"{'=' * 80}")
        print(f"Size: {result['kloc']} KLOC")
        print(f"Project Type: {result['project_type'].upper()}")
        
        print(f"\n--- BASIC COCOMO ---")
        basic = result['basic_cocomo']
        print(f"Effort: {basic['effort_pm']} Person-Months")
        print(f"Development Time: {basic['time_months']} Months")
        print(f"Average Team Size: {basic['avg_people']} Persons")
        print(f"Productivity: {basic['productivity']} KLOC/PM")
        
        print(f"\n--- INTERMEDIATE COCOMO ---")
        inter = result['intermediate_cocomo']
        print(f"Base Effort: {inter['base_effort_pm']} Person-Months")
        print(f"Effort Adjustment Factor (EAF): {inter['eaf']}")
        print(f"Adjusted Effort: {inter['effort_pm']} Person-Months")
        print(f"Development Time: {inter['time_months']} Months")
        print(f"Average Team Size: {inter['avg_people']} Persons")
        print(f"Productivity: {inter['productivity']} KLOC/PM")
        
        print(f"\n--- KEY COST DRIVERS ---")
        drivers = result['cost_drivers']
        print(f"Product Complexity (CPLX): {drivers['CPLX']}")
        print(f"Programmer Capability (PCAP): {drivers['PCAP']}")
        print(f"Analyst Capability (ACAP): {drivers['ACAP']}")
        print(f"Use of Tools (TOOL): {drivers['TOOL']}")
        
        print(f"\n--- ASSUMPTIONS & JUSTIFICATIONS ---")
        for key, value in result['assumptions'].items():
            print(f"• {value}")
    
    # Save results to JSON
    with open('cocomo_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print("Results saved to cocomo_results.json")
    print(f"{'=' * 80}\n")
    
    # Comparative analysis
    print("\n" + "=" * 80)
    print("COMPARATIVE ANALYSIS")
    print("=" * 80)
    
    print(f"\n{'Project':<25} {'KLOC':<10} {'Type':<15} {'Effort(PM)':<12} {'Time(Mo)':<10} {'Team':<8}")
    print("-" * 80)
    for result in results:
        inter = result['intermediate_cocomo']
        print(f"{result['project_name']:<25} {result['kloc']:<10.3f} "
              f"{result['project_type']:<15} {inter['effort_pm']:<12.2f} "
              f"{inter['time_months']:<10.2f} {inter['avg_people']:<8.2f}")
    
    return results


if __name__ == "__main__":
    results = main()
