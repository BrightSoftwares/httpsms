#!/usr/bin/env python3
"""
AI Codebase Analyzer - Extract Repository Information for AI Understanding
Designed to create resumable context for AI code generation and feature addition
"""

import os
import json
import ast
import re
import hashlib
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse

@dataclass
class FileInfo:
    """Information about a single file"""
    path: str
    size: int
    lines: int
    file_type: str
    language: str
    imports: List[str]
    classes: List[str]
    functions: List[str]
    exports: List[str]
    key_patterns: List[str]
    complexity_score: int
    last_modified: str

@dataclass
class ProjectStructure:
    """Overall project structure and metadata"""
    name: str
    root_path: str
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    frameworks: List[str]
    dependencies: Dict[str, str]
    entry_points: List[str]
    config_files: List[str]
    documentation: List[str]

@dataclass
class ResumableContext:
    """Context that can be saved and restored"""
    project_overview: str
    technical_stack: Dict[str, str]
    architecture_patterns: List[str]
    key_components: List[Dict]
    api_endpoints: List[Dict]
    database_models: List[Dict]
    ui_components: List[Dict]
    external_services: List[str]
    critical_files: List[str]
    analysis_timestamp: str
    progress_markers: Dict[str, bool]

class CodebaseAnalyzer:
    """Main analyzer class for extracting codebase information"""
    
    def __init__(self, repo_path: str, output_dir: str = "ai_analysis"):
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # File patterns to analyze
        self.code_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react',
            '.vue': 'vue',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sql': 'sql'
        }
        
        # Patterns to ignore
        self.ignore_patterns = {
            'node_modules', '.git', '__pycache__', '.venv', 'venv',
            'dist', 'build', '.next', '.nuxt', 'target', 'bin',
            'obj', '.DS_Store', '*.pyc', '*.class', '*.o'
        }
        
        # Framework detection patterns
        self.framework_patterns = {
            'React': [r'import.*react', r'from ["\']react["\']', r'<.*jsx.*>'],
            'Vue': [r'import.*vue', r'<template>', r'export default.*Vue'],
            'Angular': [r'@angular', r'@Component', r'@Injectable'],
            'Django': [r'from django', r'django.urls', r'models.Model'],
            'Flask': [r'from flask', r'Flask(__name__)', r'@app.route'],
            'Express': [r'express\(\)', r'app.get\(', r'require\(["\']express["\']'],
            'FastAPI': [r'from fastapi', r'FastAPI\(\)', r'@app.get'],
            'Spring': [r'@RestController', r'@Service', r'@Entity'],
            'Next.js': [r'next/head', r'next/router', r'getStaticProps'],
            'Nuxt': [r'nuxt.config', r'<nuxt-', r'@nuxtjs'],
            'Svelte': [r'<script>', r'export let', r'svelte/store']
        }

    def should_ignore_path(self, path: Path) -> bool:
        """Check if a path should be ignored"""
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str or path.name.startswith('.'):
                return True
        return False

    def detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        suffix = file_path.suffix.lower()
        return self.code_extensions.get(suffix, 'text')

    def extract_python_info(self, file_path: Path) -> Tuple[List[str], List[str], List[str]]:
        """Extract imports, classes, and functions from Python files"""
        imports, classes, functions = [], [], []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(f"{node.module}.{node.names[0].name if node.names else ''}")
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    functions.append(node.name)
                    
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}")
            
        return imports, classes, functions

    def extract_javascript_info(self, file_path: Path) -> Tuple[List[str], List[str], List[str]]:
        """Extract imports, exports, and functions from JavaScript/TypeScript files"""
        imports, exports, functions = [], [], []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Import patterns
            import_patterns = [
                r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',
                r'import\s+["\']([^"\']+)["\']',
                r'require\(["\']([^"\']+)["\']\)'
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imports.extend(matches)
            
            # Export patterns
            export_patterns = [
                r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)',
                r'export\s*\{\s*([^}]+)\s*\}',
                r'module\.exports\s*=\s*(\w+)'
            ]
            
            for pattern in export_patterns:
                matches = re.findall(pattern, content)
                if isinstance(matches, list) and matches:
                    exports.extend([match.strip() for match in str(matches[0]).split(',') if match.strip()])
            
            # Function patterns
            function_patterns = [
                r'function\s+(\w+)\s*\(',
                r'const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
                r'(\w+)\s*:\s*(?:async\s+)?function',
                r'async\s+function\s+(\w+)'
            ]
            
            for pattern in function_patterns:
                matches = re.findall(pattern, content)
                functions.extend(matches)
                
        except Exception as e:
            print(f"Error parsing JavaScript file {file_path}: {e}")
            
        return imports, exports, functions

    def calculate_complexity_score(self, file_path: Path, content: str) -> int:
        """Calculate a simple complexity score for the file"""
        score = 0
        
        # Base score on file size and lines
        lines = content.count('\n') + 1
        score += min(lines // 10, 50)
        
        # Add points for complex patterns
        complex_patterns = [
            r'class\s+\w+', r'function\s+\w+', r'def\s+\w+',  # Definitions
            r'if\s*\(', r'for\s*\(', r'while\s*\(',  # Control structures
            r'try\s*{', r'catch\s*\(', r'except\s*:',  # Error handling
            r'async\s+', r'await\s+', r'Promise',  # Async patterns
            r'@\w+', r'#\[.*\]',  # Decorators/attributes
        ]
        
        for pattern in complex_patterns:
            score += len(re.findall(pattern, content)) * 2
            
        return min(score, 100)  # Cap at 100

    def detect_frameworks(self, content: str) -> List[str]:
        """Detect frameworks used in the content"""
        detected = []
        
        for framework, patterns in self.framework_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detected.append(framework)
                    break
                    
        return detected

    def extract_key_patterns(self, content: str, language: str) -> List[str]:
        """Extract key patterns that indicate important functionality"""
        patterns = []
        
        # API endpoint patterns
        api_patterns = [
            r'@app\.route\(["\']([^"\']+)["\']',  # Flask
            r'@PostMapping\(["\']([^"\']+)["\']',  # Spring
            r'@GetMapping\(["\']([^"\']+)["\']',   # Spring
            r'router\.get\(["\']([^"\']+)["\']',   # Express
            r'app\.get\(["\']([^"\']+)["\']',      # Express
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            patterns.extend([f"API_ENDPOINT: {match}" for match in matches])
        
        # Database model patterns
        db_patterns = [
            r'class\s+(\w+)\s*\([^)]*Model[^)]*\)',  # Django/SQLAlchemy
            r'@Entity\s+.*?class\s+(\w+)',           # JPA
            r'CREATE TABLE\s+(\w+)',                 # SQL
        ]
        
        for pattern in db_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            patterns.extend([f"DB_MODEL: {match}" for match in matches])
        
        # React component patterns
        if language in ['javascript', 'typescript', 'react']:
            component_patterns = [
                r'(?:function|const)\s+([A-Z]\w+).*?(?:return\s*\(|\s*=>)',
                r'class\s+([A-Z]\w+)\s+extends\s+(?:React\.)?Component'
            ]
            
            for pattern in component_patterns:
                matches = re.findall(pattern, content)
                patterns.extend([f"REACT_COMPONENT: {match}" for match in matches])
        
        return patterns

    def analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        """Analyze a single file and extract relevant information"""
        if self.should_ignore_path(file_path) or not file_path.is_file():
            return None
            
        try:
            stat_info = file_path.stat()
            language = self.detect_language(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.count('\n') + 1
            
            # Extract language-specific information
            imports, classes, functions = [], [], []
            
            if language == 'python':
                imports, classes, functions = self.extract_python_info(file_path)
            elif language in ['javascript', 'typescript', 'react']:
                imports, classes, functions = self.extract_javascript_info(file_path)
            
            # Calculate complexity and extract patterns
            complexity = self.calculate_complexity_score(file_path, content)
            key_patterns = self.extract_key_patterns(content, language)
            
            return FileInfo(
                path=str(file_path.relative_to(self.repo_path)),
                size=stat_info.st_size,
                lines=lines,
                file_type=file_path.suffix,
                language=language,
                imports=imports[:20],  # Limit to prevent overflow
                classes=classes[:20],
                functions=functions[:20],
                exports=functions[:20],  # Reuse functions for exports
                key_patterns=key_patterns[:10],
                complexity_score=complexity,
                last_modified=datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            )
            
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return None

    def find_entry_points(self) -> List[str]:
        """Find potential entry points for the application"""
        entry_points = []
        common_entries = [
            'main.py', 'app.py', 'index.js', 'server.js', 'main.js',
            'index.ts', 'main.ts', 'App.js', 'App.tsx', 'index.html'
        ]
        
        for entry in common_entries:
            entry_path = self.repo_path / entry
            if entry_path.exists():
                entry_points.append(entry)
                
        return entry_points

    def find_config_files(self) -> List[str]:
        """Find configuration files"""
        config_files = []
        config_patterns = [
            'package.json', 'requirements.txt', 'Pipfile', 'pom.xml',
            'build.gradle', 'Cargo.toml', 'composer.json', 'setup.py',
            '.env*', 'config.*', 'settings.*', '*.config.*', 'docker*',
            'webpack.config.*', 'vite.config.*', 'next.config.*'
        ]
        
        for pattern in config_patterns:
            for config_file in self.repo_path.rglob(pattern):
                if not self.should_ignore_path(config_file):
                    config_files.append(str(config_file.relative_to(self.repo_path)))
                    
        return config_files

    def extract_dependencies(self) -> Dict[str, str]:
        """Extract project dependencies from various config files"""
        dependencies = {}
        
        # Package.json
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    dependencies.update({f"npm:{k}": v for k, v in {**deps, **dev_deps}.items()})
            except Exception as e:
                print(f"Error reading package.json: {e}")
        
        # Requirements.txt
        requirements_txt = self.repo_path / 'requirements.txt'
        if requirements_txt.exists():
            try:
                with open(requirements_txt, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dep = line.split('==')[0].split('>=')[0].split('<=')[0]
                            dependencies[f"pip:{dep}"] = line
            except Exception as e:
                print(f"Error reading requirements.txt: {e}")
                
        return dependencies

    def generate_project_overview(self, files: List[FileInfo], structure: ProjectStructure) -> str:
        """Generate a comprehensive project overview"""
        overview = f"""# Project Analysis: {structure.name}

## Project Statistics
- **Total Files**: {structure.total_files}
- **Total Lines of Code**: {structure.total_lines:,}
- **Primary Languages**: {', '.join([f"{lang} ({count} files)" for lang, count in sorted(structure.languages.items(), key=lambda x: x[1], reverse=True)[:5]])}

## Detected Frameworks & Technologies
{', '.join(structure.frameworks) if structure.frameworks else 'No specific frameworks detected'}

## Project Structure
- **Entry Points**: {', '.join(structure.entry_points) if structure.entry_points else 'Not clearly identified'}
- **Configuration Files**: {len(structure.config_files)} config files found
- **Documentation Files**: {len(structure.documentation)} documentation files

## Key Dependencies
{chr(10).join([f"- {dep}" for dep in list(structure.dependencies.keys())[:10]]) if structure.dependencies else 'No dependencies file found'}

## Critical Files (High Complexity)
"""
        
        # Add critical files based on complexity
        critical_files = sorted([f for f in files if f.complexity_score > 30], 
                              key=lambda x: x.complexity_score, reverse=True)[:10]
        
        for file_info in critical_files:
            overview += f"- **{file_info.path}** ({file_info.language}, {file_info.lines} lines, complexity: {file_info.complexity_score})\n"
            if file_info.key_patterns:
                overview += f"  - Key patterns: {', '.join(file_info.key_patterns[:3])}\n"
        
        return overview

    def create_resumable_context(self, files: List[FileInfo], structure: ProjectStructure) -> ResumableContext:
        """Create resumable context for AI understanding"""
        
        # Extract API endpoints
        api_endpoints = []
        for file_info in files:
            for pattern in file_info.key_patterns:
                if pattern.startswith("API_ENDPOINT:"):
                    api_endpoints.append({
                        'endpoint': pattern.replace("API_ENDPOINT: ", ""),
                        'file': file_info.path,
                        'language': file_info.language
                    })
        
        # Extract database models
        db_models = []
        for file_info in files:
            for pattern in file_info.key_patterns:
                if pattern.startswith("DB_MODEL:"):
                    db_models.append({
                        'model': pattern.replace("DB_MODEL: ", ""),
                        'file': file_info.path,
                        'language': file_info.language
                    })
        
        # Extract UI components
        ui_components = []
        for file_info in files:
            for pattern in file_info.key_patterns:
                if pattern.startswith("REACT_COMPONENT:"):
                    ui_components.append({
                        'component': pattern.replace("REACT_COMPONENT: ", ""),
                        'file': file_info.path,
                        'language': file_info.language
                    })
        
        # Identify key components
        key_components = []
        critical_files = sorted([f for f in files if f.complexity_score > 25], 
                              key=lambda x: x.complexity_score, reverse=True)[:15]
        
        for file_info in critical_files:
            component = {
                'name': Path(file_info.path).stem,
                'path': file_info.path,
                'type': file_info.language,
                'complexity': file_info.complexity_score,
                'lines': file_info.lines,
                'classes': file_info.classes[:5],
                'functions': file_info.functions[:10],
                'key_patterns': file_info.key_patterns[:5]
            }
            key_components.append(component)
        
        # Detect architecture patterns
        patterns = []
        if any('models' in f.path.lower() for f in files):
            patterns.append("Model-View Architecture")
        if any('controller' in f.path.lower() for f in files):
            patterns.append("MVC Pattern")
        if any('service' in f.path.lower() for f in files):
            patterns.append("Service Layer Pattern")
        if any('component' in f.path.lower() for f in files):
            patterns.append("Component-Based Architecture")
        
        return ResumableContext(
            project_overview=self.generate_project_overview(files, structure),
            technical_stack={
                'languages': structure.languages,
                'frameworks': structure.frameworks,
                'dependencies': dict(list(structure.dependencies.items())[:20])
            },
            architecture_patterns=patterns,
            key_components=key_components,
            api_endpoints=api_endpoints[:20],
            database_models=db_models[:15],
            ui_components=ui_components[:20],
            external_services=[dep for dep in structure.dependencies.keys() 
                             if any(service in dep.lower() for service in 
                                   ['api', 'http', 'request', 'axios', 'fetch'])],
            critical_files=[f.path for f in files if f.complexity_score > 40][:10],
            analysis_timestamp=datetime.now().isoformat(),
            progress_markers={
                'structure_analyzed': True,
                'dependencies_extracted': True,
                'patterns_identified': True,
                'components_mapped': True
            }
        )

    def analyze_repository(self) -> Tuple[List[FileInfo], ProjectStructure, ResumableContext]:
        """Analyze the entire repository"""
        print(f"Analyzing repository at: {self.repo_path}")
        
        files = []
        languages = {}
        total_lines = 0
        all_frameworks = set()
        
        # Analyze all code files
        for file_path in self.repo_path.rglob('*'):
            if file_path.suffix.lower() in self.code_extensions:
                file_info = self.analyze_file(file_path)
                if file_info:
                    files.append(file_info)
                    
                    # Update statistics
                    languages[file_info.language] = languages.get(file_info.language, 0) + 1
                    total_lines += file_info.lines
                    
                    # Detect frameworks from file content
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            frameworks = self.detect_frameworks(content)
                            all_frameworks.update(frameworks)
                    except Exception:
                        pass
        
        # Create project structure
        structure = ProjectStructure(
            name=self.repo_path.name,
            root_path=str(self.repo_path),
            total_files=len(files),
            total_lines=total_lines,
            languages=languages,
            frameworks=list(all_frameworks),
            dependencies=self.extract_dependencies(),
            entry_points=self.find_entry_points(),
            config_files=self.find_config_files(),
            documentation=[str(p.relative_to(self.repo_path)) for p in self.repo_path.rglob('*.md')][:10]
        )
        
        # Create resumable context
        context = self.create_resumable_context(files, structure)
        
        return files, structure, context

    def save_analysis(self, files: List[FileInfo], structure: ProjectStructure, context: ResumableContext):
        """Save analysis results to files"""
        
        # Save detailed file analysis
        with open(self.output_dir / 'files_analysis.json', 'w') as f:
            json.dump([asdict(file_info) for file_info in files], f, indent=2)
        
        # Save project structure
        with open(self.output_dir / 'project_structure.json', 'w') as f:
            json.dump(asdict(structure), f, indent=2)
        
        # Save resumable context (main output for AI)
        with open(self.output_dir / 'ai_context.json', 'w') as f:
            json.dump(asdict(context), f, indent=2)
        
        # Save AI-friendly summary
        with open(self.output_dir / 'ai_summary.md', 'w') as f:
            f.write(self.generate_ai_summary(context))
        
        print(f"Analysis saved to {self.output_dir}/")
        print(f"Main AI context file: {self.output_dir}/ai_context.json")
        print(f"Human-readable summary: {self.output_dir}/ai_summary.md")

    def generate_ai_summary(self, context: ResumableContext) -> str:
        """Generate AI-friendly summary for immediate use"""
        summary = f"""# AI Codebase Context

{context.project_overview}

## Technical Stack Summary
**Languages**: {', '.join([f"{k} ({v} files)" for k, v in context.technical_stack['languages'].items()])}
**Frameworks**: {', '.join(context.technical_stack['frameworks'])}
**Architecture Patterns**: {', '.join(context.architecture_patterns)}

## Critical Components for AI Understanding

### Top Priority Files (High Complexity)
"""
        
        for component in context.key_components[:5]:
            summary += f"**{component['name']}** (`{component['path']}`)\n"
            summary += f"- Type: {component['type']}, Complexity: {component['complexity']}, Lines: {component['lines']}\n"
            summary += f"- Key functions: {', '.join(component['functions'][:5])}\n"
            if component['classes']:
                summary += f"- Key classes: {', '.join(component['classes'][:3])}\n"
            summary += "\n"

        if context.api_endpoints:
            summary += "\n### API Endpoints Discovered\n"
            for endpoint in context.api_endpoints[:10]:
                summary += f"- `{endpoint['endpoint']}` (in {endpoint['file']})\n"

        if context.database_models:
            summary += "\n### Database Models\n"
            for model in context.database_models[:8]:
                summary += f"- `{model['model']}` (in {model['file']})\n"

        if context.ui_components:
            summary += "\n### UI Components\n"
            for component in context.ui_components[:10]:
                summary += f"- `{component['component']}` (in {component['file']})\n"

        summary += f"""
## External Dependencies & Services
{chr(10).join([f"- {dep}" for dep in list(context.technical_stack['dependencies'].keys())[:15]])}

## For AI Development Tasks:
1. **Start with these critical files**: {', '.join(context.critical_files[:5])}
2. **Main architecture patterns**: {', '.join(context.architecture_patterns)}
3. **Entry points to understand**: Check project structure for main files
4. **Key integration points**: API endpoints and database models listed above

---
*Analysis completed: {context.analysis_timestamp}*
*This context is designed to be resumable - save this file to maintain context across AI conversations.*
"""
        
        return summary


def main():
    parser = argparse.ArgumentParser(description='Analyze codebase for AI understanding')
    parser.add_argument('repo_path', help='Path to the repository to analyze')
    parser.add_argument('--output', '-o', default='ai_analysis', 
                       help='Output directory for analysis results')
    parser.add_argument('--summary-only', action='store_true',
                       help='Generate only the AI summary file')
    
    args = parser.parse_args()
    
    if not Path(args.repo_path).exists():
        print(f"Error: Repository path '{args.repo_path}' does not exist")
        return 1
    
    analyzer = CodebaseAnalyzer(args.repo_path, args.output)
    
    try:
        print("Starting repository analysis...")
        files, structure, context = analyzer.analyze_repository()
        
        if args.summary_only:
            # Quick summary for immediate AI use
            with open(Path(args.output) / 'ai_summary.md', 'w') as f:
                f.write(analyzer.generate_ai_summary(context))
            print(f"AI summary saved to: {args.output}/ai_summary.md")
        else:
            # Full analysis
            analyzer.save_analysis(files, structure, context)
        
        print(f"✅ Analysis complete! Found {len(files)} files across {len(structure.languages)} languages.")
        print(f"💡 Use the generated context files to provide comprehensive codebase understanding to AI.")
        
        return 0
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
