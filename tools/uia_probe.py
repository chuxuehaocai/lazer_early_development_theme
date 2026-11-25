"""Attach a UI Automation client to a window and walk its tree.

Flutter only builds its semantics tree when an accessibility client is
attached, so this is the switch that reproduces the AXTree error flood.

Usage: python tools/uia_probe.py --process lazer_nextgen --rounds 6
"""
import argparse
import subprocess
import sys
import time

try:
    import comtypes.client  # noqa: F401
except ImportError:
    comtypes = None


PS_TEMPLATE = r"""
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$ErrorActionPreference = 'Stop'
$proc = Get-Process -Name {proc} -ErrorAction SilentlyContinue |
        Where-Object {{ $_.MainWindowHandle -ne 0 }} | Select-Object -First 1
if (-not $proc) {{ Write-Output 'no-window'; exit 2 }}
$root = [System.Windows.Automation.AutomationElement]::FromHandle($proc.MainWindowHandle)
for ($i = 0; $i -lt {rounds}; $i++) {{
  $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
  $child = $walker.GetFirstChild($root)
  $n = 0
  while ($child -ne $null -and $n -lt 400) {{
    $null = $child.Current.Name
    $null = $child.Current.ControlType
    $child = $walker.GetNextSibling($child)
    $n++
  }}
  $desc = $root.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)
  Write-Output "round $i descendants=$($desc.Count)"
  Start-Sleep -Milliseconds {delay}
}}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--process", default="lazer_nextgen")
    parser.add_argument("--rounds", type=int, default=6)
    parser.add_argument("--delay", type=int, default=400)
    args = parser.parse_args()

    script = PS_TEMPLATE.format(proc=args.process, rounds=args.rounds, delay=args.delay)
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
    )
    print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip()[-800:], file=sys.stderr)
        return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
