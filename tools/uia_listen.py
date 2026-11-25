"""Keep a live UI Automation subscription on the player window.

Flutter only builds (and keeps updating) its semantics tree when an
accessibility client is attached *and listening*. Subscribing to
StructureChanged / PropertyChanged is what makes the engine push AXTree
updates — and therefore what reproduces

  [ERROR:flutter/shell/platform/common/accessibility_bridge.cc(114)]
  Failed to update ui::AXTree, error: NNN will not be in the tree ...

Usage: python tools/uia_listen.py --process lazer_nextgen --seconds 30
"""
import argparse
import subprocess
import sys
import time

SCRIPT = r"""
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$proc = Get-Process -Name {proc} -ErrorAction SilentlyContinue |
        Where-Object {{ $_.MainWindowHandle -ne 0 }} | Select-Object -First 1
if (-not $proc) {{ Write-Output 'no-window'; exit 2 }}
$root = [System.Windows.Automation.AutomationElement]::FromHandle($proc.MainWindowHandle)

# Two subscriptions: structure changes are what force AXTree rebuilds.
$handlers = @()
$handlers += [System.Windows.Automation.StructureChangedEventHandler]{{ param($s, $e) }}
$handlers += [System.Windows.Automation.AutomationPropertyChangedEventHandler]{{ param($s, $e) }}
[System.Windows.Automation.Automation]::AddStructureChangedEventHandler(
  $root,
  [System.Windows.Automation.TreeScope]::Subtree,
  $handlers[0])
[System.Windows.Automation.Automation]::AddAutomationPropertyChangedEventHandler(
  $root,
  [System.Windows.Automation.TreeScope]::Subtree,
  $handlers[1],
  [System.Windows.Automation.AutomationProperty[]]@(
    [System.Windows.Automation.AutomationElement]::NameProperty,
    [System.Windows.Automation.AutomationElement]::IsOffscreenProperty))

$deadline = (Get-Date).AddSeconds({seconds})
while ((Get-Date) -lt $deadline) {{
  $all = $root.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)
  Write-Output "descendants=$($all.Count)"
  Start-Sleep -Milliseconds {delay}
}}
[System.Windows.Automation.Automation]::RemoveAllEventHandlers($root)
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--process", default="lazer_nextgen")
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--delay", type=int, default=1000)
    args = parser.parse_args()

    script = SCRIPT.format(proc=args.process, seconds=args.seconds, delay=args.delay)
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
    )
    print(result.stdout.strip()[-2000:])
    if result.returncode != 0:
        print(result.stderr.strip()[-800:], file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
