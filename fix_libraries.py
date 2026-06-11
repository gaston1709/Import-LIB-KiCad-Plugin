#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Setup paths to use kiutils included in the plugin
current_dir = Path(__file__).resolve().parent
kiutils_src = current_dir / "plugins" / "kiutils" / "src"
if kiutils_src.exists() and str(kiutils_src) not in sys.path:
    sys.path.insert(0, str(kiutils_src))

try:
    from kiutils.symbol import SymbolLib, Property, Effects, Font
except ImportError:
    print("Error: Could not import kiutils. Make sure this script is run from the root of the plugin repository.")
    sys.exit(1)

def fix_library(file_path: Path):
    try:
        symbol_lib = SymbolLib.from_file(str(file_path))
        modified = False
        
        for symbol in symbol_lib.symbols:
            for prop in symbol.properties:
                # Disable showName to hide field name label prefixes
                if prop.showName:
                    prop.showName = False
                    modified = True
                
                if prop.key not in ("Reference", "Value"):
                    # Check if it's already hidden to avoid unnecessary writes
                    if prop.effects is None:
                        prop.effects = Effects(
                            font=Font(
                                face="default",
                                height=1.27,
                                width=1.27,
                                bold=False,
                                italic=False,
                            )
                        )
                        prop.effects.hide = True
                        modified = True
                    elif not prop.effects.hide:
                        prop.effects.hide = True
                        modified = True
                        
        if modified:
            symbol_lib.to_file(str(file_path))
            print(f"  ✓ Updated: {file_path.name}")
        else:
            print(f"  (no changes needed): {file_path.name}")
            
    except Exception as e:
        print(f"  ✗ Error processing {file_path.name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fix KiCad symbol libraries (.kicad_sym) by hiding all properties except Reference and Value.")
    parser.add_argument("path", help="Path to a .kicad_sym file or a directory containing them")
    args = parser.parse_args()
    
    path = Path(args.path).resolve()
    if not path.exists():
        print(f"Error: Path {path} does not exist.")
        sys.exit(1)
        
    if path.is_file():
        if path.suffix == ".kicad_sym":
            fix_library(path)
        else:
            print("Error: The specified file is not a .kicad_sym file.")
    elif path.is_dir():
        kicad_syms = list(path.rglob("*.kicad_sym"))
        if not kicad_syms:
            print(f"No .kicad_sym files found in {path}")
            return
        print(f"Found {len(kicad_syms)} .kicad_sym files to process.")
        for filepath in kicad_syms:
            fix_library(filepath)

if __name__ == "__main__":
    main()
