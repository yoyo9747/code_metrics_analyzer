#!/usr/bin/env python3
"""
Comprehensive Code Metrics Analyzer
Computes SLOC, Cyclomatic Complexity, Halstead Metrics, and Data-flow Analysis
Designed for COL740 - Software Engineering course project
"""

import os
import sys
import ast
import json
import math
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import re


@dataclass
class SLOCMetrics:
    """Source Lines of Code metrics"""
    total_lines: int
    source_lines: int  # Non-blank, non-comment
    comment_lines: int
    blank_lines: int
    files_analyzed: int


@dataclass
class CyclomaticMetrics:
    """Cyclomatic Complexity metrics per function/method"""
    function_name: str
    complexity: int
    line_number: int


@dataclass
class HalsteadMetrics:
    """Halstead Software Science metrics"""
    n1: int  # Unique operators
    n2: int  # Unique operands
    N1: int  # Total operators
    N2: int  # Total operands
    vocabulary: int  # n = n1 + n2
    length: int  # N = N1 + N2
    calculated_length: float  # N̂ = n1*log2(n1) + n2*log2(n2)
    volume: float  # V = N * log2(n)
    difficulty: float  # D = (n1/2) * (N2/n2)
    effort: float  # E = D * V
    time: float  # T = E / 18 (seconds)
    bugs: float  # B = V / 3000


@dataclass
class DataFlowMetrics:
    """Data-flow analysis metrics"""
    function_name: str
    variables_defined: Set[str]
    variables_used: Set[str]
    live_variables: Set[str]
    def_use_chains: Dict[str, List[int]]  # Variable -> line numbers where used after def
    reaching_definitions: int


class SLOCAnalyzer:
    """Analyzes Source Lines of Code"""
    
    def __init__(self):
        self.metrics = {
            'total_lines': 0,
            'source_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'files_analyzed': 0
        }
    
    def analyze_file(self, filepath: Path) -> None:
        """Analyze a single Python file for SLOC"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            self.metrics['files_analyzed'] += 1
            self.metrics['total_lines'] += len(lines)
            
            in_multiline_comment = False
            
            for line in lines:
                stripped = line.strip()
                
                # Check for blank lines
                if not stripped:
                    self.metrics['blank_lines'] += 1
                    continue
                
                # Handle multi-line strings/comments
                if '"""' in stripped or "'''" in stripped:
                    if in_multiline_comment:
                        self.metrics['comment_lines'] += 1
                        in_multiline_comment = False
                    else:
                        in_multiline_comment = True
                        self.metrics['comment_lines'] += 1
                    continue
                
                if in_multiline_comment:
                    self.metrics['comment_lines'] += 1
                    continue
                
                # Single-line comments
                if stripped.startswith('#'):
                    self.metrics['comment_lines'] += 1
                else:
                    self.metrics['source_lines'] += 1
                    
        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}", file=sys.stderr)
    
    def get_metrics(self) -> SLOCMetrics:
        return SLOCMetrics(**self.metrics)


class CyclomaticComplexityAnalyzer(ast.NodeVisitor):
    """Computes Cyclomatic Complexity using AST"""
    
    def __init__(self):
        self.complexities: List[CyclomaticMetrics] = []
        self.current_function = None
        self.current_complexity = 0
        self.current_line = 0
    
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        # Save previous function context
        prev_function = self.current_function
        prev_complexity = self.current_complexity
        
        # Start new function analysis
        self.current_function = node.name
        self.current_complexity = 1  # Base complexity
        self.current_line = node.lineno
        
        # Visit function body
        self.generic_visit(node)
        
        # Record metrics
        self.complexities.append(CyclomaticMetrics(
            function_name=self.current_function,
            complexity=self.current_complexity,
            line_number=self.current_line
        ))
        
        # Restore previous context
        self.current_function = prev_function
        self.current_complexity = prev_complexity
    
    visit_AsyncFunctionDef = visit_FunctionDef
    
    def visit_If(self, node):
        """Count if statements"""
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Count while loops"""
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Count for loops"""
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        """Count except handlers"""
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        """Count with statements"""
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_Assert(self, node):
        """Count assertions"""
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        """Count boolean operators (and/or)"""
        self.current_complexity += len(node.values) - 1
        self.generic_visit(node)
    
    def analyze_file(self, filepath: Path) -> List[CyclomaticMetrics]:
        """Analyze a file and return complexity metrics"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            self.visit(tree)
            return self.complexities
        except SyntaxError as e:
            print(f"Warning: Syntax error in {filepath}: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}", file=sys.stderr)
            return []


class HalsteadAnalyzer(ast.NodeVisitor):
    """Computes Halstead Software Science metrics"""
    
    # Define Python operators
    OPERATORS = {
        # Arithmetic
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
        # Bitwise
        ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd,
        # Comparison
        ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
        # Boolean
        ast.And, ast.Or, ast.Not,
        # Unary
        ast.UAdd, ast.USub, ast.Invert,
        # Membership
        ast.In, ast.NotIn, ast.Is, ast.IsNot,
    }
    
    def __init__(self):
        self.operators: List[str] = []
        self.operands: List[str] = []
    
    def visit_BinOp(self, node):
        self.operators.append(node.op.__class__.__name__)
        self.generic_visit(node)
    
    def visit_UnaryOp(self, node):
        self.operators.append(node.op.__class__.__name__)
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        self.operators.append(node.op.__class__.__name__)
        self.generic_visit(node)
    
    def visit_Compare(self, node):
        for op in node.ops:
            self.operators.append(op.__class__.__name__)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        self.operators.append('Call')
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.operators.append('FunctionDef')
        self.operands.append(node.name)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.operators.append('ClassDef')
        self.operands.append(node.name)
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.operators.append('If')
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.operators.append('For')
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.operators.append('While')
        self.generic_visit(node)
    
    def visit_Return(self, node):
        self.operators.append('Return')
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        self.operators.append('Assign')
        self.generic_visit(node)
    
    def visit_AugAssign(self, node):
        self.operators.append('AugAssign')
        self.generic_visit(node)
    
    def visit_Name(self, node):
        self.operands.append(node.id)
        self.generic_visit(node)
    
    def visit_Constant(self, node):
        self.operands.append(str(node.value))
        self.generic_visit(node)
    
    def visit_Num(self, node):  # For older Python versions
        self.operands.append(str(node.n))
        self.generic_visit(node)
    
    def visit_Str(self, node):  # For older Python versions
        self.operands.append(node.s)
        self.generic_visit(node)
    
    def analyze_file(self, filepath: Path) -> Optional[HalsteadMetrics]:
        """Analyze a file and return Halstead metrics"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            
            self.visit(tree)
            
            # Calculate metrics
            n1 = len(set(self.operators))
            n2 = len(set(self.operands))
            N1 = len(self.operators)
            N2 = len(self.operands)
            
            if n1 == 0 or n2 == 0:
                return None
            
            vocabulary = n1 + n2
            length = N1 + N2
            
            # Calculated length
            calc_length = 0
            if n1 > 0:
                calc_length += n1 * math.log2(n1)
            if n2 > 0:
                calc_length += n2 * math.log2(n2)
            
            # Volume
            volume = length * math.log2(vocabulary) if vocabulary > 0 else 0
            
            # Difficulty
            difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
            
            # Effort
            effort = difficulty * volume
            
            # Time (in seconds)
            time_seconds = effort / 18
            
            # Bugs
            bugs = volume / 3000
            
            return HalsteadMetrics(
                n1=n1, n2=n2, N1=N1, N2=N2,
                vocabulary=vocabulary,
                length=length,
                calculated_length=calc_length,
                volume=volume,
                difficulty=difficulty,
                effort=effort,
                time=time_seconds,
                bugs=bugs
            )
            
        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}", file=sys.stderr)
            return None


class DataFlowAnalyzer(ast.NodeVisitor):
    """Performs data-flow analysis"""
    
    def __init__(self):
        self.functions: List[DataFlowMetrics] = []
        self.current_function = None
        self.current_defs: Set[str] = set()
        self.current_uses: Set[str] = set()
        self.def_use_chains: Dict[str, List[int]] = defaultdict(list)
        self.current_line = 0
    
    def visit_FunctionDef(self, node):
        """Analyze function for data flow"""
        # Save previous context
        prev_function = self.current_function
        prev_defs = self.current_defs.copy()
        prev_uses = self.current_uses.copy()
        prev_chains = self.def_use_chains.copy()
        
        # Reset for new function
        self.current_function = node.name
        self.current_defs = set()
        self.current_uses = set()
        self.def_use_chains = defaultdict(list)
        self.current_line = node.lineno
        
        # Add parameters as initial definitions
        for arg in node.args.args:
            self.current_defs.add(arg.arg)
        
        # Visit function body
        for stmt in node.body:
            self.visit(stmt)
        
        # Calculate live variables (used but not necessarily defined in function)
        live_vars = self.current_uses - self.current_defs
        
        # Calculate reaching definitions
        reaching_defs = len(self.current_defs)
        
        # Record metrics
        self.functions.append(DataFlowMetrics(
            function_name=self.current_function,
            variables_defined=self.current_defs.copy(),
            variables_used=self.current_uses.copy(),
            live_variables=live_vars,
            def_use_chains=dict(self.def_use_chains),
            reaching_definitions=reaching_defs
        ))
        
        # Restore previous context
        self.current_function = prev_function
        self.current_defs = prev_defs
        self.current_uses = prev_uses
        self.def_use_chains = prev_chains
    
    visit_AsyncFunctionDef = visit_FunctionDef
    
    def visit_Assign(self, node):
        """Track variable assignments (definitions)"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.current_defs.add(target.id)
        # Visit the value to track uses
        self.visit(node.value)
    
    def visit_AugAssign(self, node):
        """Track augmented assignments"""
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            self.current_uses.add(var_name)  # Used on RHS
            self.current_defs.add(var_name)  # Defined as result
            self.def_use_chains[var_name].append(node.lineno)
        self.visit(node.value)
    
    def visit_Name(self, node):
        """Track variable uses"""
        if isinstance(node.ctx, ast.Load):
            self.current_uses.add(node.id)
            if node.id in self.current_defs:
                self.def_use_chains[node.id].append(node.lineno)
    
    def analyze_file(self, filepath: Path) -> List[DataFlowMetrics]:
        """Analyze a file for data flow"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            self.visit(tree)
            return self.functions
        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}", file=sys.stderr)
            return []


class CodebaseAnalyzer:
    """Main analyzer that coordinates all metrics"""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.python_files: List[Path] = []
        self.results = {
            'codebase': str(root_path),
            'sloc': None,
            'cyclomatic': [],
            'halstead': {},
            'dataflow': []
        }
    
    def find_python_files(self) -> None:
        """Recursively find all Python files"""
        for path in self.root_path.rglob('*.py'):
            if not any(part.startswith('.') for part in path.parts):
                self.python_files.append(path)
        
        print(f"Found {len(self.python_files)} Python files in {self.root_path}")
    
    def analyze(self) -> Dict[str, Any]:
        """Run all analyses"""
        self.find_python_files()
        
        if not self.python_files:
            print(f"No Python files found in {self.root_path}")
            return self.results
        
        # SLOC Analysis
        print("\n=== Analyzing SLOC ===")
        sloc_analyzer = SLOCAnalyzer()
        for filepath in self.python_files:
            sloc_analyzer.analyze_file(filepath)
        self.results['sloc'] = asdict(sloc_analyzer.get_metrics())
        
        # Cyclomatic Complexity
        print("\n=== Analyzing Cyclomatic Complexity ===")
        for filepath in self.python_files:
            analyzer = CyclomaticComplexityAnalyzer()
            complexities = analyzer.analyze_file(filepath)
            for metric in complexities:
                self.results['cyclomatic'].append({
                    'file': str(filepath.relative_to(self.root_path)),
                    **asdict(metric)
                })
        
        # Halstead Metrics
        print("\n=== Analyzing Halstead Metrics ===")
        for filepath in self.python_files:
            analyzer = HalsteadAnalyzer()
            metrics = analyzer.analyze_file(filepath)
            if metrics:
                self.results['halstead'][str(filepath.relative_to(self.root_path))] = asdict(metrics)
        
        # Data Flow Analysis
        print("\n=== Analyzing Data Flow ===")
        for filepath in self.python_files:
            analyzer = DataFlowAnalyzer()
            flows = analyzer.analyze_file(filepath)
            for flow in flows:
                # Convert sets to lists for JSON serialization
                flow_dict = asdict(flow)
                flow_dict['variables_defined'] = list(flow_dict['variables_defined'])
                flow_dict['variables_used'] = list(flow_dict['variables_used'])
                flow_dict['live_variables'] = list(flow_dict['live_variables'])
                flow_dict['file'] = str(filepath.relative_to(self.root_path))
                self.results['dataflow'].append(flow_dict)
        
        return self.results
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        summary = {
            'codebase': self.results['codebase'],
            'total_files': len(self.python_files),
            'sloc_summary': self.results['sloc'],
            'cyclomatic_summary': self._summarize_cyclomatic(),
            'halstead_summary': self._summarize_halstead(),
            'dataflow_summary': self._summarize_dataflow()
        }
        return summary
    
    def _summarize_cyclomatic(self) -> Dict[str, Any]:
        """Summarize cyclomatic complexity"""
        if not self.results['cyclomatic']:
            return {}
        
        complexities = [m['complexity'] for m in self.results['cyclomatic']]
        return {
            'total_functions': len(complexities),
            'average_complexity': sum(complexities) / len(complexities),
            'max_complexity': max(complexities),
            'min_complexity': min(complexities),
            'high_complexity_functions': [
                m for m in self.results['cyclomatic'] if m['complexity'] > 10
            ]
        }
    
    def _summarize_halstead(self) -> Dict[str, Any]:
        """Summarize Halstead metrics"""
        if not self.results['halstead']:
            return {}
        
        volumes = [m['volume'] for m in self.results['halstead'].values()]
        efforts = [m['effort'] for m in self.results['halstead'].values()]
        bugs = [m['bugs'] for m in self.results['halstead'].values()]
        
        return {
            'total_files_analyzed': len(self.results['halstead']),
            'average_volume': sum(volumes) / len(volumes),
            'total_effort': sum(efforts),
            'estimated_bugs': sum(bugs),
            'average_difficulty': sum(m['difficulty'] for m in self.results['halstead'].values()) / len(self.results['halstead'])
        }
    
    def _summarize_dataflow(self) -> Dict[str, Any]:
        """Summarize data flow metrics"""
        if not self.results['dataflow']:
            return {}
        
        return {
            'total_functions_analyzed': len(self.results['dataflow']),
            'total_variables_defined': sum(len(f['variables_defined']) for f in self.results['dataflow']),
            'total_variables_used': sum(len(f['variables_used']) for f in self.results['dataflow']),
            'average_live_variables': sum(len(f['live_variables']) for f in self.results['dataflow']) / len(self.results['dataflow'])
        }


def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive Code Metrics Analyzer for Software Engineering',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('codebase_path', type=str, help='Path to the codebase to analyze')
    parser.add_argument('-o', '--output', type=str, help='Output JSON file path', default='metrics_output.json')
    parser.add_argument('-s', '--summary', action='store_true', help='Print summary to console')
    
    args = parser.parse_args()
    
    codebase_path = Path(args.codebase_path)
    
    if not codebase_path.exists():
        print(f"Error: Path {codebase_path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    print(f"{'='*80}")
    print(f"CODE METRICS ANALYZER - COL740 Software Engineering")
    print(f"{'='*80}")
    print(f"Analyzing codebase: {codebase_path}")
    print(f"{'='*80}")
    
    # Run analysis
    analyzer = CodebaseAnalyzer(codebase_path)
    results = analyzer.analyze()
    
    # Save detailed results
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Detailed results saved to: {output_path}")
    
    # Generate and save summary
    summary = analyzer.generate_summary()
    summary_path = output_path.parent / f"{output_path.stem}_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary saved to: {summary_path}")
    
    # Print summary if requested
    if args.summary:
        print(f"\n{'='*80}")
        print("SUMMARY REPORT")
        print(f"{'='*80}")
        print(json.dumps(summary, indent=2))
    
    print(f"\n{'='*80}")
    print("Analysis Complete!")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
