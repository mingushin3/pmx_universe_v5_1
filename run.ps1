param([string]$cmd = "test")

switch ($cmd) {
    "test" {
        python -m pytest tests/ -v
    }
    "validate" {
        python scripts/config_validation/validate_config.py --config-dir config
    }
    "generate" {
        python scripts/scenario_generator/generate_scenarios.py
    }
    "all" {
        python -m pytest tests/ -v
        if ($LASTEXITCODE -eq 0) {
            python scripts/config_validation/validate_config.py --config-dir config
        }
    }
    default {
        Write-Host "Usage: .\run.ps1 {test|validate|generate|all}"
        exit 1
    }
}
