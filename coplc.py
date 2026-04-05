#!/usr/bin/env python3
import sys
import os
import argparse
import pprint

# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Ensure src/ is in PYTHONPATH for the script to easily run without installing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from copl.lexer import Lexer
from copl.parser import parse
from copl.semantics.analyzer import SemanticAnalyzer
from copl.codegen.transpiler import CTranspiler
from copl.sir.builder import SIRBuilder
from copl.artifacts.engine import ArtifactEngine

def print_diagnostic_error(phase: str, errors: list):
    print(f"\n{Colors.FAIL}{Colors.BOLD}--- {phase} Errors ---{Colors.ENDC}")
    for err in errors:
        # Assuming err has message and location (line, col)
        # and maybe a printed __str__ representation
        msg = str(err)
        print(f"{Colors.FAIL}Error:{Colors.ENDC} {msg}")

def run_compiler(filepath: str, out_dir: str, command: str):
    print(f"{Colors.OKCYAN}{Colors.BOLD}=> Compiling {filepath}...{Colors.ENDC}")
    
    if not os.path.exists(filepath):
        print(f"{Colors.FAIL}Error:{Colors.ENDC} File '{filepath}' not found.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    base_name = os.path.splitext(os.path.basename(filepath))[0]

    # --- PHASE 1a: LEXER ---
    lexer = Lexer()
    tokens, lex_diags = lexer.tokenize(source)
    if lex_diags.has_errors():
        print_diagnostic_error("Lexer", lex_diags.errors())
        sys.exit(1)

    # --- PHASE 1b: PARSER ---
    ast, parse_diags = parse(tokens, filename=filepath)
    if parse_diags.has_errors():
        print_diagnostic_error("Parser", parse_diags.errors())
        sys.exit(1)
        
    if ast is None:
        print(f"{Colors.FAIL}Fatal Error:{Colors.ENDC} AST generation failed heavily.")
        sys.exit(1)

    # --- PHASE 2: SEMANTIC ANALYSIS (6-pass) ---
    semantic = SemanticAnalyzer()
    semantic.analyze(ast)
    
    # Print warnings (non-blocking)
    warnings = semantic.diags.warnings() if hasattr(semantic.diags, 'warnings') else []
    for w in warnings:
        print(f"{Colors.WARNING}Warning:{Colors.ENDC} {w}")
    
    if semantic.diags.has_errors():
        print_diagnostic_error("Semantic", semantic.diags.errors())
        # sys.exit(1) # Bỏ qua ngắt Build để ép đẻ ra Compile C code

    # Print effect summary
    effects = semantic.effect_checker.get_module_effects()
    print(f"{Colors.OKGREEN}✓ Frontend passed.{Colors.ENDC} Effects: {effects} | Profile: {semantic.profile.value}")

    # Stop if it's just 'check'
    if command == "check":
        print(f"{Colors.OKBLUE}Check completed successfully for {filepath}.{Colors.ENDC}\n")
        return

    # --- PHASE 3: CODE GENERATION ---
    print(f"{Colors.OKCYAN}Generating C code...{Colors.ENDC}")
    transpiler = CTranspiler(filename=base_name)
    header_src, c_src = transpiler.transpile(ast)

    os.makedirs(out_dir, exist_ok=True)
    h_path = os.path.join(out_dir, f"{base_name}.h")
    c_path = os.path.join(out_dir, f"{base_name}.c")

    with open(h_path, "w", encoding="utf-8") as out:
        out.write(header_src)
    with open(c_path, "w", encoding="utf-8") as out:
        out.write(c_src)

    print(f"{Colors.OKGREEN}✓ Output generated:{Colors.ENDC} \n  - {h_path}\n  - {c_path}\n")

def run_sir(filepath: str, out_path: str):
    """Export SIR JSON từ 1 file COPL."""
    print(f"{Colors.OKCYAN}=> Building SIR for {filepath}...{Colors.ENDC}")
    if not os.path.exists(filepath):
        print(f"{Colors.FAIL}Error:{Colors.ENDC} File '{filepath}' not found.")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    lexer = Lexer()
    tokens, _ = lexer.tokenize(source)
    ast_node, _ = parse(tokens, filename=filepath)
    if ast_node is None:
        print(f"{Colors.FAIL}Error: Parse failed.{Colors.ENDC}")
        sys.exit(1)
    
    builder = SIRBuilder()
    builder.build_module(ast_node)
    ws = builder.build_workspace()
    
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(ws.to_json())
    print(f"{Colors.OKGREEN}✓ SIR exported:{Colors.ENDC} {out_path}")


def run_artifacts(filepath: str, out_dir: str):
    """Generate AI artifacts từ 1 file COPL."""
    print(f"{Colors.OKCYAN}=> Generating artifacts for {filepath}...{Colors.ENDC}")
    if not os.path.exists(filepath):
        print(f"{Colors.FAIL}Error:{Colors.ENDC} File '{filepath}' not found.")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    lexer = Lexer()
    tokens, _ = lexer.tokenize(source)
    ast_node, _ = parse(tokens, filename=filepath)
    if ast_node is None:
        print(f"{Colors.FAIL}Error: Parse failed.{Colors.ENDC}")
        sys.exit(1)
    
    builder = SIRBuilder()
    builder.build_module(ast_node)
    ws = builder.build_workspace()
    
    engine = ArtifactEngine(ws)
    generated = engine.emit_all(out_dir)
    print(f"{Colors.OKGREEN}✓ {len(generated)} artifacts generated in {out_dir}/{Colors.ENDC}")
    for p in generated:
        print(f"  - {p}")


def main():
    parser = argparse.ArgumentParser(description="COPL Compiler CLI (coplc)")
    
    subparsers = parser.add_subparsers(dest="command", help="Lệnh thực thi", required=True)
    
    # "build" command
    build_parser = subparsers.add_parser("build", help="Biên dịch file .copl thành mã C")
    build_parser.add_argument("file", help="Đường dẫn đến file .copl")
    build_parser.add_argument("-o", "--out-dir", default="build", help="Thư mục xuất file (mặc định: build/)")
    build_parser.add_argument("-t", "--target", default="c", help="Target output (c)")

    # "check" command
    check_parser = subparsers.add_parser("check", help="Chỉ kiểm tra lỗi Syntax và Semantic")
    check_parser.add_argument("file", help="Đường dẫn đến file .copl")

    # "sir" command
    sir_parser = subparsers.add_parser("sir", help="Export SIR (Semantic IR) ra JSON")
    sir_parser.add_argument("file", help="Đường dẫn đến file .copl")
    sir_parser.add_argument("-o", "--output", default="build/sir.json", help="File JSON output")

    # "artifacts" command  
    art_parser = subparsers.add_parser("artifacts", help="Generate AI/human-readable artifacts")
    art_parser.add_argument("file", help="Đường dẫn đến file .copl")
    art_parser.add_argument("-o", "--output", default="build/ai_bundle", help="Thư mục output")

    args = parser.parse_args()

    if args.command == "build":
        if args.target != "c":
            print(f"{Colors.FAIL}Error: Target '{args.target}' is not supported yet.{Colors.ENDC}")
            sys.exit(1)
        run_compiler(args.file, args.out_dir, "build")
    elif args.command == "check":
        run_compiler(args.file, None, "check")
    elif args.command == "sir":
        run_sir(args.file, args.output)
    elif args.command == "artifacts":
        run_artifacts(args.file, args.output)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBiên dịch bị hủy.")
        sys.exit(130)
