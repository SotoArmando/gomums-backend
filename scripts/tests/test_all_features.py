"""
Test All Features
Run all test files for the 22 completed features
"""
import subprocess
import sys
import os
from datetime import datetime
from time import time
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich import box
from rich.text import Text
from rich.pager import Pager
from rich.syntax import Syntax
from rich.columns import Columns
from rich.layout import Layout

# Initialize Rich console
console = Console()

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()

# Test files to run
TEST_FILES = [
    ("test_stats.py", "User Stats System"),
    ("test_achievements.py", "Achievements System"),
    ("test_meal_plans.py", "Meal Planning System"),
    ("test_smart_suggestions.py", "Smart Suggestions System"),
    ("test_home_sections.py", "Home Sections System"),
    ("test_content.py", "Content System"),
]

def run_test(filename, description):
    """Run a single test file and return success status with timing"""
    console.rule(f"[bold blue]Testing: {description}", style="blue")
    console.print(f"[dim]File: {filename}[/dim]\n")
    
    start_time = time()
    
    # Get full path to test file
    test_file_path = SCRIPT_DIR / filename
    
    try:
        result = subprocess.run(
            ["python3", str(test_file_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        elapsed = time() - start_time
        
        # Always show output with proper formatting
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[red]{result.stderr}[/red]")
        
        if result.returncode == 0:
            console.print(f"\n[green]✅ {description} - PASSED[/green] [dim]({elapsed:.2f}s)[/dim]\n")
            return True, elapsed, result.stdout, result.stderr
        else:
            console.print(f"\n[red]❌ {description} - FAILED[/red] [dim](exit code: {result.returncode}, {elapsed:.2f}s)[/dim]\n")
            return False, elapsed, result.stdout, result.stderr
            
    except subprocess.TimeoutExpired:
        elapsed = time() - start_time
        console.print(f"[yellow]⏱️  {description} - TIMEOUT[/yellow] [dim](60s limit)[/dim]\n")
        return False, elapsed, "", "Timeout"
    except Exception as e:
        elapsed = time() - start_time
        console.print(f"[red]💥 {description} - ERROR:[/red] {str(e)}\n")
        return False, elapsed, "", str(e)

def create_summary_table(results):
    """Create a beautiful summary table with rich"""
    table = Table(
        title="Test Results Summary",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        title_style="bold magenta"
    )
    
    table.add_column("Status", style="bold", width=10, justify="center")
    table.add_column("Test Case", style="cyan", width=40)
    table.add_column("Time", justify="right", style="yellow")
    
    for description, success, elapsed in results:
        if success:
            status = Text("✅ PASS", style="green bold")
        else:
            status = Text("❌ FAIL", style="red bold")
        
        time_str = f"{elapsed:.2f}s"
        table.add_row(status, description, time_str)
    
    return table

def create_result_panels(results):
    """Create panels for two-column display"""
    panels = []
    for description, success, elapsed in results:
        if success:
            title_style = "green"
            icon = "✅"
        else:
            title_style = "red"
            icon = "❌"
        
        panel = Panel(
            f"[bold]{description}[/bold]\n"
            f"[yellow]Time:[/yellow] {elapsed:.2f}s\n"
            f"[cyan]Status:[/cyan] {'Passed' if success else 'Failed'}",
            title=f"[{title_style}]{icon} Test Result[/{title_style}]",
            border_style=title_style,
            box=box.ROUNDED
        )
        panels.append(panel)
    
    return panels

def main():
    """Run all tests and provide summary"""
    # Header
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]GOMUMS BACKEND - FEATURE TEST SUITE[/bold cyan]\n"
        f"[dim]Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n"
        f"[dim]Total Tests: {len(TEST_FILES)}[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    
    # Setup test users first
    console.print("\n[bold yellow]⚙️  Setting up test users...[/bold yellow]")
    try:
        setup_script = SCRIPT_DIR / "setup_test_users.py"
        setup_result = subprocess.run(
            ["python3", str(setup_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if setup_result.returncode == 0:
            console.print("[green]✓ Test users ready[/green]\n")
        else:
            console.print("[yellow]⚠️  Warning: Test user setup had issues[/yellow]\n")
    except Exception as e:
        console.print(f"[yellow]⚠️  Warning: Could not setup test users: {e}[/yellow]\n")
    
    results = []
    total_time = 0
    
    # Run tests
    for filename, description in TEST_FILES:
        success, elapsed, stdout, stderr = run_test(filename, description)
        results.append((description, success, elapsed))
        total_time += elapsed
    
    # Summary
    console.print("\n")
    
    # Display results in two columns
    console.print(Panel("[bold cyan]Test Results - Two Column View[/bold cyan]", border_style="cyan"))
    panels = create_result_panels(results)
    
    # Group panels into pairs for two-column display
    for i in range(0, len(panels), 2):
        if i + 1 < len(panels):
            # Two panels side by side
            console.print(Columns([panels[i], panels[i + 1]], equal=True, expand=True))
        else:
            # Odd number, show last one alone
            console.print(panels[i])
    
    console.print("\n")
    console.print(create_summary_table(results))
    
    # Statistics
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    success_rate = (passed / len(results) * 100) if results else 0
    
    # Final summary panel
    if failed == 0:
        summary_style = "green"
        summary_icon = "🎉"
        summary_text = "ALL TESTS PASSED"
    else:
        summary_style = "red"
        summary_icon = "⚠️"
        summary_text = "SOME TESTS FAILED"
    
    console.print("\n")
    console.print(Panel.fit(
        f"[bold {summary_style}]{summary_icon} {summary_text}[/bold {summary_style}]\n\n"
        f"[white]Total Tests:[/white] [bold]{len(results)}[/bold]\n"
        f"[green]Passed:[/green] [bold]{passed}[/bold]\n"
        f"[red]Failed:[/red] [bold]{failed}[/bold]\n"
        f"[cyan]Success Rate:[/cyan] [bold]{success_rate:.1f}%[/bold]\n"
        f"[yellow]Total Time:[/yellow] [bold]{total_time:.2f}s[/bold]\n"
        f"[dim]Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style=summary_style,
        box=box.DOUBLE
    ))
    console.print("\n")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
