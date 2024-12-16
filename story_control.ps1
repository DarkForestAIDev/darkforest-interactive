# Story Control Script

function Send-Command {
    param (
        [string]$action
    )
    
    $url = "http://localhost:5000/command/$action"
    $response = Invoke-RestMethod -Uri $url -Method Post
    return $response
}

function Show-Menu {
    Write-Host "`n=== Dark Forest Story Control ==="
    Write-Host "1. Start Chapter One"
    Write-Host "2. Start Chapter Two"
    Write-Host "3. Pause Story"
    Write-Host "4. Resume Story"
    Write-Host "5. Check Status"
    Write-Host "6. Exit"
    Write-Host "================================"
}

while ($true) {
    Show-Menu
    $choice = Read-Host "`nEnter your choice (1-6)"
    
    switch ($choice) {
        "1" {
            Write-Host "`nWarning: This will reset Chapter One from the beginning." -ForegroundColor Yellow
            $confirm = Read-Host "Are you sure? (y/n)"
            if ($confirm -eq 'y') {
                $response = Send-Command "start_chapter_one"
                Write-Host "`nResponse:" $response.message -ForegroundColor Green
            }
        }
        "2" {
            Write-Host "`nWarning: This will archive Chapter One and start Chapter Two." -ForegroundColor Yellow
            Write-Host "Make sure you're at a good stopping point in Chapter One!" -ForegroundColor Yellow
            $confirm = Read-Host "Are you sure? (y/n)"
            if ($confirm -eq 'y') {
                $response = Send-Command "start_chapter_two"
                Write-Host "`nResponse:" $response.message -ForegroundColor Green
            }
        }
        "3" {
            $response = Send-Command "pause"
            Write-Host "`nResponse:" $response.message -ForegroundColor Yellow
        }
        "4" {
            $response = Send-Command "resume"
            Write-Host "`nResponse:" $response.message -ForegroundColor Green
        }
        "5" {
            $response = Send-Command "status"
            Write-Host "`nCurrent Status:" -ForegroundColor Cyan
            Write-Host "Chapter:" $response.chapter
            Write-Host "Paused:" $response.is_paused
            Write-Host "Current Transmission:" $response.current_transmission
            Write-Host "Last Transmission Time:" $response.last_transmission_time
            Write-Host "Total Transmissions:" $response.total_transmissions
        }
        "6" {
            Write-Host "`nExiting..." -ForegroundColor Yellow
            exit
        }
        default {
            Write-Host "`nInvalid choice. Please try again." -ForegroundColor Red
        }
    }
    
    Start-Sleep -Seconds 1
} 